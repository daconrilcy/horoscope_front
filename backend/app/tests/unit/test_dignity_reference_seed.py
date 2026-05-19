"""Tests du seed et du repository des dignités astrologiques."""

from sqlalchemy import func, select

from app.infra.db.base import Base
from app.infra.db.models import (
    AstralAccidentalDignityRuleModel,
    AstralAccidentalDignityScoreWeightModel,
    AstralChartPlanetDignityResultModel,
    AstralDiginityScoreProfileModel,
    AstralEssentialDignityRuleModel,
    AstralEssentialDignityScoreWeightModel,
    AstralFaceDecanModel,
    AstralSourceModel,
    AstralTermBoundModel,
    ChartResultModel,
    ReferenceVersionModel,
)
from app.infra.db.repositories.dignity_reference_repository import (
    ChartPlanetDignityResultInput,
    DignityReferenceRepository,
)
from app.services.reference_data_service import ReferenceDataService
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session


def _reset_database() -> None:
    """Reconstruit une base isolée pour le seed de dignités."""
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())


def test_reference_seed_populates_astral_dignity_tables() -> None:
    """Le seed de référence alimente les tables JSON de dignités attendues."""
    _reset_database()

    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        version_id = db.scalar(
            select(ReferenceVersionModel.id).where(ReferenceVersionModel.version == "1.0.0")
        )

        assert db.scalar(select(func.count()).select_from(AstralSourceModel)) == 6
        assert db.scalar(select(func.count()).select_from(AstralDiginityScoreProfileModel)) == 5
        assert db.scalar(select(func.count()).select_from(AstralTermBoundModel)) == 60
        assert db.scalar(select(func.count()).select_from(AstralFaceDecanModel)) == 36
        assert db.scalar(select(func.count()).select_from(AstralEssentialDignityRuleModel)) == 38
        assert db.scalar(select(func.count()).select_from(AstralAccidentalDignityRuleModel)) == 41
        assert (
            db.scalar(select(func.count()).select_from(AstralEssentialDignityScoreWeightModel)) == 8
        )
        assert (
            db.scalar(select(func.count()).select_from(AstralAccidentalDignityScoreWeightModel))
            == 22
        )
        assert set(db.scalars(select(AstralTermBoundModel.reference_version_id)).all()) == {
            version_id
        }


def test_dignity_repository_reads_weights_and_upserts_runtime_result() -> None:
    """Le repository lit les poids seedés et persiste un résultat runtime unique."""
    _reset_database()

    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        chart_result = ChartResultModel(
            chart_id="dignity-result-test",
            reference_version="1.0.0",
            ruleset_version="test",
            input_hash="hash",
            result_payload={},
        )
        db.add(chart_result)
        db.flush()

        repository = DignityReferenceRepository(db)
        assert len(repository.list_score_profiles()) == 5
        assert len(repository.list_essential_score_weights("traditional_standard")) == 8
        assert len(repository.list_accidental_score_weights("traditional_standard")) == 22

        payload = ChartPlanetDignityResultInput(
            chart_result_id=chart_result.id,
            planet_code="mars",
            score_profile_code="traditional_standard",
            astral_system_code="traditional",
            reference_version="1.0.0",
            essential_score=5,
            accidental_score=3,
            total_score=8,
            functional_strength_score=1.2,
            expression_quality_score=0.8,
            intensity_score=0.7,
            essential_breakdown_json=[{"type": "domicile"}],
            accidental_breakdown_json=[{"type": "angular_house"}],
            condition_summary_json={"detected": 2},
            calculation_context_json={"engine": "unit"},
        )
        first_result = repository.upsert_chart_planet_dignity_result(payload)
        second_result = repository.upsert_chart_planet_dignity_result(
            ChartPlanetDignityResultInput(**{**payload.__dict__, "total_score": 9})
        )

        assert first_result.id == second_result.id
        assert second_result.total_score == 9
        assert db.scalar(select(func.count()).select_from(AstralChartPlanetDignityResultModel)) == 1
        assert (
            repository.get_chart_planet_dignity_result(
                chart_result.id, "mars", "traditional_standard", "1.0.0"
            )
            is not None
        )
