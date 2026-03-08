# backend/app/tests/unit/test_percentile_calculator.py
import random
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import select

from app.infra.db.models.calibration import CalibrationRawDayModel
from app.infra.db.models.prediction_reference import PredictionCategoryModel
from app.infra.db.models.prediction_ruleset import CategoryCalibrationModel, PredictionRulesetModel
from app.infra.db.repositories.calibration_repository import CalibrationRepository
from app.infra.db.repositories.prediction_ruleset_repository import PredictionRulesetRepository
from app.jobs.calibration.percentile_calculator import (
    PercentileCalculatorService,
    compute_percentile,
    compute_percentiles,
)
from app.tests.regression.helpers import create_session


@pytest.fixture
def db_session():
    session = create_session()
    yield session
    if "engine" in session.info:
        session.info["engine"].dispose()


def test_compute_percentile_known_values():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    # Median (P50) of [1, 2, 3, 4, 5] is 3.0
    assert compute_percentile(data, 50) == 3.0

    data = [1.0, 2.0, 3.0, 4.0]
    # Median (P50) of [1, 2, 3, 4] is 2.5
    assert compute_percentile(data, 50) == 2.5

    # Type 7 interpolation: idx = (p/100)*(n-1)
    # n=2, p=75 => idx = 0.75 * 1 = 0.75
    # val = data[0] + 0.75*(data[1]-data[0]) = 1 + 0.75*1 = 1.75
    assert compute_percentile([1.0, 2.0], 75) == 1.75


def test_percentiles_monotone():
    data = [random.uniform(-10, 10) for _ in range(1000)]
    res = compute_percentiles("test", data)
    assert res.p05 <= res.p25 <= res.p50 <= res.p75 <= res.p95
    assert res.sample_size == 1000


def test_sample_size_correct():
    data = [1.0, 2.0, 3.0]
    res = compute_percentiles("test", data)
    assert res.sample_size == 3


def test_calibration_injected_in_db(db_session):
    repo = CalibrationRepository(db_session)
    service = PercentileCalculatorService(db_session, repo)

    # 1. Setup metadata
    ref_v = "2.0.0"
    ruleset_v = "1.0.0"
    valid_from = date(2024, 1, 1)
    valid_to = date(2024, 12, 31)

    # ruleset and categories are already seeded by create_session() / run_seed()
    ruleset = db_session.scalar(
        select(PredictionRulesetModel).where(PredictionRulesetModel.version == ruleset_v)
    )
    assert ruleset is not None

    # 2. Seed raw scores
    cat_love = db_session.scalar(
        select(PredictionCategoryModel).where(PredictionCategoryModel.code == "love")
    )
    assert cat_love is not None

    scores = [10.0, 20.0, 30.0, 40.0, 50.0]
    for i, val in enumerate(scores):
        raw_day = CalibrationRawDayModel(
            profile_label="p1",
            local_date=date(2024, 1, 1 + i),
            category_code="love",
            raw_score=val,
            reference_version=ref_v,
            ruleset_version=ruleset_v,
        )
        repo.save(raw_day)
    db_session.commit()

    # 3. Run service
    results = service.run(ref_v, ruleset_v, valid_from, valid_to)
    assert len(results) >= 1
    res_love = next(r for r in results if r.category_code == "love")
    assert res_love.p50 == 30.0
    assert res_love.sample_size == 5

    # 4. Verify DB injection
    calibs = db_session.scalars(
        select(CategoryCalibrationModel).where(CategoryCalibrationModel.ruleset_id == ruleset.id)
    ).all()
    assert len(calibs) >= 1
    c = next(c for c in calibs if c.category_id == cat_love.id)
    assert c.p50 == 30.0
    assert c.sample_size == 5
    assert c.valid_from == valid_from


def test_motor_uses_real_calibration(db_session):
    repo = CalibrationRepository(db_session)
    ruleset_repo = PredictionRulesetRepository(db_session)
    service = PercentileCalculatorService(db_session, repo)

    ref_v = "2.0.0"
    ruleset_v = "1.0.0"

    ruleset = db_session.scalar(
        select(PredictionRulesetModel).where(PredictionRulesetModel.version == ruleset_v)
    )
    cat_love = db_session.scalar(
        select(PredictionCategoryModel).where(PredictionCategoryModel.code == "love")
    )

    # 1. Seed some raw scores
    scores = [10.0, 20.0, 30.0, 40.0, 50.0]
    for i, val in enumerate(scores):
        raw_day = CalibrationRawDayModel(
            profile_label="p1",
            local_date=date(2024, 1, 1 + i),
            category_code="love",
            raw_score=val,
            reference_version=ref_v,
            ruleset_version=ruleset_v,
        )
        repo.save(raw_day)
    db_session.commit()

    # 2. Run calibration
    service.run(ref_v, ruleset_v, date(2024, 1, 1), date(2024, 12, 31))

    # 3. Fetch calibrations via repository
    # We use a date within the valid range
    calib = ruleset_repo.get_calibrations(ruleset.id, cat_love.id, date(2024, 6, 1))

    # Verify that 'love' has the real calibration
    assert calib is not None
    assert calib.p50 == 30.0
    assert calib.sample_size == 5


def test_run_rejects_reference_ruleset_version_mismatch(db_session):
    repo = CalibrationRepository(db_session)
    service = PercentileCalculatorService(db_session, repo)

    with pytest.raises(ValueError, match="ruleset 1.0.0"):
        service.run("1.0.0", "1.0.0", date(2024, 1, 1), date(2024, 12, 31))


def test_run_rolls_back_all_calibrations_when_a_category_fails(
    db_session, monkeypatch: pytest.MonkeyPatch
):
    repo = CalibrationRepository(db_session)
    service = PercentileCalculatorService(db_session, repo)

    ruleset = db_session.scalar(
        select(PredictionRulesetModel).where(PredictionRulesetModel.version == "1.0.0")
    )
    love = db_session.scalar(
        select(PredictionCategoryModel).where(PredictionCategoryModel.code == "love")
    )
    work = db_session.scalar(
        select(PredictionCategoryModel).where(PredictionCategoryModel.code == "work")
    )
    assert ruleset is not None
    assert love is not None
    assert work is not None

    raw_days = [
        CalibrationRawDayModel(
            profile_label="p1",
            local_date=date(2024, 1, 1),
            category_code="love",
            raw_score=10.0,
            reference_version="2.0.0",
            ruleset_version="1.0.0",
        ),
        CalibrationRawDayModel(
            profile_label="p1",
            local_date=date(2024, 1, 2),
            category_code="work",
            raw_score=20.0,
            reference_version="2.0.0",
            ruleset_version="1.0.0",
        ),
    ]
    for raw_day in raw_days:
        repo.save(raw_day)
    db_session.commit()

    original_compute_percentiles = compute_percentiles

    def failing_compute_percentiles(category_code: str, raw_scores: list[float]):
        if category_code == "work":
            raise ValueError("boom")
        return original_compute_percentiles(category_code, raw_scores)

    monkeypatch.setattr(
        "app.jobs.calibration.percentile_calculator.compute_percentiles",
        failing_compute_percentiles,
    )

    with pytest.raises(ValueError, match="boom"):
        service.run("2.0.0", "1.0.0", date(2024, 1, 1), date(2024, 12, 31))

    calibrations = db_session.scalars(
        select(CategoryCalibrationModel).where(CategoryCalibrationModel.ruleset_id == ruleset.id)
    ).all()
    assert all(calibration.category_id not in {love.id, work.id} for calibration in calibrations)


def test_generate_report_includes_outlier_values(tmp_path: Path):
    result = compute_percentiles("love", [0.0] * 10 + [100.0])
    output_path = tmp_path / "percentile_report.json"

    service = PercentileCalculatorService(db=None, calibration_repo=None)  # type: ignore[arg-type]
    service.generate_report(
        [result],
        output_path,
        {
            "reference_version": "2.0.0",
            "ruleset_version": "1.0.0",
            "valid_from": "2024-01-01",
            "valid_to": "2024-12-31",
        },
    )

    report = output_path.read_text(encoding="utf-8")
    assert '"outliers"' in report
    assert "100.0" in report
