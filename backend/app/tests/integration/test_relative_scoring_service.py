from datetime import date, datetime
from unittest.mock import MagicMock, call, patch

from sqlalchemy.orm import Session

from app.prediction.persisted_baseline import PersistedUserBaseline, V3Granularity
from app.prediction.persisted_snapshot import (
    PersistedCategoryScore,
    PersistedPredictionSnapshot,
)
from app.services.relative_scoring_service import RelativeScoringService


def test_relative_scoring_service_enrichment():
    # 1. Setup mock snapshot
    snapshot = PersistedPredictionSnapshot(
        run_id=1,
        user_id=42,
        local_date=date(2026, 3, 10),
        timezone="UTC",
        computed_at=datetime.now(),
        input_hash="hash",
        reference_version_id=1,
        ruleset_id=1,
        house_system_effective="placidus",
        is_provisional_calibration=False,
        calibration_label="v1",
        overall_summary="test",
        overall_tone="neutral",
        category_scores=[
            PersistedCategoryScore(1, "love", 15, 10.0, 1.0, 1.0, 1, False, None),
        ],
    )

    # 2. Setup mock baseline
    mock_baseline = PersistedUserBaseline(
        id=1,
        user_id=42,
        category_id=1,
        category_code="love",
        reference_version_id=1,
        ruleset_id=1,
        house_system_effective="placidus",
        window_days=365,
        window_start_date=None,
        window_end_date=None,
        mean_raw_score=5.0,
        std_raw_score=2.0,  # Z = (10 - 5) / 2 = 2.5
        mean_note_20=12.0,
        std_note_20=1.0,
        p10=2.0,
        p50=5.0,
        p90=8.0,
        sample_size_days=365,
        computed_at=datetime.now(),
    )

    # 3. Mock Repository
    patch_path = "app.services.relative_scoring_service.UserPredictionBaselineRepository"
    with patch(patch_path) as MockRepo:
        repo_instance = MockRepo.return_value
        repo_instance.get_latest_baselines_for_user.return_value = [mock_baseline]

        service = RelativeScoringService()
        db = MagicMock(spec=Session)

        # 4. Execute
        enriched = service.enrich_snapshot(db, snapshot)

        # 5. Verify
        assert "love" in enriched.relative_scores
        rel_score = enriched.relative_scores["love"]
        assert rel_score.relative_z_score == 2.5
        assert rel_score.is_available is True
        assert rel_score.relative_rank == 1

        # Verify original data is preserved (AC3)
        assert enriched.category_scores[0].note_20 == 15
        assert enriched.category_scores[0].raw_score == 10.0


def test_relative_scoring_service_uses_latest_compatible_baseline():
    snapshot = PersistedPredictionSnapshot(
        run_id=1,
        user_id=42,
        local_date=date(2026, 3, 10),
        timezone="UTC",
        computed_at=datetime.now(),
        input_hash="hash",
        reference_version_id=1,
        ruleset_id=1,
        house_system_effective="placidus",
        is_provisional_calibration=False,
        calibration_label="v1",
        overall_summary="test",
        overall_tone="neutral",
        category_scores=[
            PersistedCategoryScore(1, "love", 15, 10.0, 1.0, 1.0, 1, False, None),
        ],
    )

    patch_path = "app.services.relative_scoring_service.UserPredictionBaselineRepository"
    with patch(patch_path) as MockRepo:
        repo_instance = MockRepo.return_value
        repo_instance.get_latest_baselines_for_user.return_value = []

        service = RelativeScoringService()
        db = MagicMock(spec=Session)

        enriched = service.enrich_snapshot(db, snapshot)

        assert repo_instance.get_latest_baselines_for_user.call_args_list == [
            call(
                user_id=42,
                reference_version_id=1,
                ruleset_id=1,
                house_system_effective="placidus",
                window_days=365,
                as_of_date=date(2026, 3, 10),
                granularity_type=V3Granularity.DAY,
            ),
            call(
                user_id=42,
                reference_version_id=1,
                ruleset_id=1,
                house_system_effective="placidus",
                window_days=365,
                as_of_date=date(2026, 3, 10),
                granularity_type=V3Granularity.SEASON,
            ),
            call(
                user_id=42,
                reference_version_id=1,
                ruleset_id=1,
                house_system_effective="placidus",
                window_days=365,
                as_of_date=date(2026, 3, 10),
                granularity_type=V3Granularity.SLOT,
            ),
        ]
        assert enriched.relative_scores["love"].fallback_reason == "baseline_missing"
