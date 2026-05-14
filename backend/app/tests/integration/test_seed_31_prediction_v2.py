"""Valide l'amorçage canonique du référentiel de prédiction v2."""

import json
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.infra.db.models import (
    AspectProfileModel,
    AstralAspectOrbRuleModel,
    AstralDignityTypeModel,
    AstralElementModel,
    AstralModalityModel,
    AstralPlanetSignDignityModel,
    AstralPolarityModel,
    AstralSignModel,
    AstralSignProfileModel,
    AstralSystemModel,
    AstroPointModel,
    HouseCategoryWeightModel,
    HouseInterpretationProfileModel,
    HouseModel,
    HouseProfileModel,
    PlanetCategoryWeightModel,
    PlanetModel,
    PlanetProfileModel,
    PointCategoryWeightModel,
    PredictionCategoryModel,
    PredictionRulesetModel,
    ReferenceVersionModel,
    RulesetEventTypeModel,
    RulesetParameterModel,
)
from app.services.prediction.reference_seed_service import (
    _ensure_no_complete_inherited_orb_rule_copy,
    _resolve_aspect_orb_rule_groups,
)
from app.services.reference_data_service import ReferenceDataService
from scripts.seed_31_prediction_reference_v2 import SeedAbortError, run_seed

EXPECTED_SIGN_PROFILE_MAPPING = {
    "aries": ("fire", "cardinal", "yang"),
    "taurus": ("earth", "fixed", "yin"),
    "gemini": ("air", "mutable", "yang"),
    "cancer": ("water", "cardinal", "yin"),
    "leo": ("fire", "fixed", "yang"),
    "virgo": ("earth", "mutable", "yin"),
    "libra": ("air", "cardinal", "yang"),
    "scorpio": ("water", "fixed", "yin"),
    "sagittarius": ("fire", "mutable", "yang"),
    "capricorn": ("earth", "cardinal", "yin"),
    "aquarius": ("air", "fixed", "yang"),
    "pisces": ("water", "mutable", "yin"),
}

EXPECTED_TRADITIONAL_RULERSHIPS = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}


def test_seed_rejects_complete_inherited_orb_rule_copy() -> None:
    """Le seed refuse qu'un enfant stocke une copie complete des règles héritées."""
    parent_rule = {
        "aspect_code": "square",
        "calculation_context": "natal",
        "source_body_type": "luminary",
        "target_body_type": "any",
        "orb_deg": 8.0,
        "priority": 800,
        "is_enabled": True,
    }

    with pytest.raises(ValueError, match="duplicate inherited parent"):
        _ensure_no_complete_inherited_orb_rule_copy(
            {
                "traditional": [parent_rule],
                "hellenistic": [dict(parent_rule)],
            },
            {
                "traditional": None,
                "hellenistic": "traditional",
            },
        )


def test_seed_rejects_unknown_inherited_orb_rule_parent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Le JSON d'orbes échoue si un parent d'héritage est inconnu."""
    monkeypatch.setattr(
        "app.services.prediction.reference_seed_service._load_aspect_orb_rule_groups",
        lambda: [
            {
                "reference_version_id": 1,
                "astral_system_code": "hellenistic",
                "inherits_from": "traditonal",
                "rules": [],
            }
        ],
    )

    with pytest.raises(ValueError, match="unknown inherited aspect orb rule system"):
        _resolve_aspect_orb_rule_groups()


def _alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[3]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    return config


def _sqlite_engine(database_url: str) -> Engine:
    engine = create_engine(database_url, future=True)

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection: object, _: object) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def _setup_engine(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, db_name: str) -> Engine:
    db_path = tmp_path / db_name
    database_url = f"sqlite:///{db_path.as_posix()}"
    monkeypatch.setattr(settings, "database_url", database_url)
    # Upgrade to the latest migration before seed
    command.upgrade(_alembic_config(), "head")
    return _sqlite_engine(database_url)


def test_seed_31_prediction_v2_full_flow(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    engine = _setup_engine(monkeypatch, tmp_path, "test-seed-v2.db")

    with Session(engine) as session:
        # 1. Setup V1.0.0
        ReferenceDataService.seed_reference_version(session, "1.0.0")
        session.commit()

        # 2. Run seed script logic
        run_seed(session)
        session.commit()

        # 3. Verify counts
        v2 = session.scalar(
            select(ReferenceVersionModel).where(ReferenceVersionModel.version == "2.0.0")
        )
        assert v2 is not None
        assert v2.is_locked is True
        assert v2.description == (
            "Moteur de prédiction quotidienne v1 — référentiel sémantique complet"
        )

        assert (
            session.scalar(
                select(func.count())
                .select_from(PredictionCategoryModel)
                .where(PredictionCategoryModel.reference_version_id == v2.id)
            )
            == 12
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(PlanetProfileModel)
                .where(PlanetProfileModel.reference_version_id == v2.id)
            )
            == 10
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(HouseProfileModel)
                .where(HouseProfileModel.reference_version_id == v2.id)
            )
            == 12
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(HouseInterpretationProfileModel)
                .where(HouseInterpretationProfileModel.reference_version_id == v2.id)
            )
            == 12
        )
        house_10_profile = session.scalar(
            select(HouseInterpretationProfileModel)
            .where(
                HouseInterpretationProfileModel.reference_version_id == v2.id,
                HouseInterpretationProfileModel.language == "en",
            )
            .join(HouseInterpretationProfileModel.house)
            .join(HouseInterpretationProfileModel.astral_system)
            .where(HouseModel.number == 10)
            .where(AstralSystemModel.name == "modern")
        )
        assert house_10_profile is not None
        assert house_10_profile.title == "Career and Public Role"
        assert "career" in json.loads(house_10_profile.core_keywords_json or "[]")
        assert (
            session.scalar(
                select(func.count())
                .select_from(AspectProfileModel)
                .where(AspectProfileModel.reference_version_id == v2.id)
            )
            == 20
        )
        assert session.scalar(select(func.count()).select_from(AstroPointModel)) == 4
        assert session.scalar(select(func.count()).select_from(AstralDignityTypeModel)) == 4
        assert session.scalar(select(func.count()).select_from(AstralElementModel)) == 4
        assert session.scalar(select(func.count()).select_from(AstralModalityModel)) == 3
        assert session.scalar(select(func.count()).select_from(AstralPolarityModel)) == 2
        assert session.scalar(select(func.count()).select_from(AstralSystemModel)) == 4
        assert session.scalar(select(func.count()).select_from(AstralPlanetSignDignityModel)) == 50
        assert session.scalar(select(func.count()).select_from(AstralSignProfileModel)) == 12
        assert {row.code for row in session.scalars(select(AstralElementModel)).all()} == {
            "fire",
            "earth",
            "air",
            "water",
        }
        assert {row.code for row in session.scalars(select(AstralModalityModel)).all()} == {
            "cardinal",
            "fixed",
            "mutable",
        }
        assert {row.code for row in session.scalars(select(AstralPolarityModel)).all()} == {
            "yang",
            "yin",
        }
        assert {row.code for row in session.scalars(select(AstralDignityTypeModel)).all()} == {
            "domicile",
            "detriment",
            "exaltation",
            "fall",
        }
        assert {row.name for row in session.scalars(select(AstralSystemModel)).all()} == {
            "traditional",
            "modern",
            "hellenistic",
            "medieval",
        }
        assert {
            system.name: (None if system.inherits_from is None else system.inherits_from.name)
            for system in session.scalars(select(AstralSystemModel)).all()
        } == {
            "hellenistic": "traditional",
            "medieval": "traditional",
            "modern": None,
            "traditional": None,
        }
        orb_rule_counts_by_system = dict(
            session.execute(
                select(AstralSystemModel.name, func.count(AstralAspectOrbRuleModel.id))
                .outerjoin(
                    AstralAspectOrbRuleModel,
                    AstralAspectOrbRuleModel.astral_system_id == AstralSystemModel.id,
                )
                .where(
                    (AstralAspectOrbRuleModel.reference_version_id == v2.id)
                    | (AstralAspectOrbRuleModel.id.is_(None))
                )
                .group_by(AstralSystemModel.name)
            ).all()
        )
        assert orb_rule_counts_by_system == {
            "hellenistic": 0,
            "medieval": 0,
            "modern": 39,
            "traditional": 40,
        }
        domicile_traditional_count = session.scalar(
            select(func.count())
            .select_from(AstralPlanetSignDignityModel)
            .join(
                AstralDignityTypeModel,
                AstralPlanetSignDignityModel.astral_dignity_type_id == AstralDignityTypeModel.id,
            )
            .join(
                AstralSystemModel,
                AstralPlanetSignDignityModel.astral_system_id == AstralSystemModel.id,
            )
            .where(
                AstralDignityTypeModel.code == "domicile",
                AstralSystemModel.name == "traditional",
            )
        )
        assert domicile_traditional_count == 12
        profile_rows = session.execute(
            select(
                AstralSignProfileModel,
                AstralElementModel,
                AstralModalityModel,
                AstralSignModel.code,
                AstralPolarityModel.code,
            )
            .join(AstralSignModel, AstralSignProfileModel.astral_sign_id == AstralSignModel.id)
            .join(
                AstralElementModel,
                AstralSignProfileModel.astral_element_id == AstralElementModel.id,
            )
            .join(
                AstralModalityModel,
                AstralSignProfileModel.astral_modality_id == AstralModalityModel.id,
            )
            .join(
                AstralPolarityModel,
                AstralSignProfileModel.astral_polarity_id == AstralPolarityModel.id,
            )
        ).all()
        assert {
            sign_code: (element.code, modality.code, polarity_code)
            for profile, element, modality, sign_code, polarity_code in profile_rows
        } == EXPECTED_SIGN_PROFILE_MAPPING
        for profile, _element, _modality, _sign_code, _polarity_code in profile_rows:
            assert profile.keywords_json is not None
            assert profile.shadow_keywords_json is not None
            assert json.loads(profile.keywords_json)
            assert json.loads(profile.shadow_keywords_json)
        assert any(
            sign_code == "aries" and "initiative" in json.loads(profile.keywords_json or "[]")
            for profile, _element, _modality, sign_code, _polarity_code in profile_rows
        )
        traditional_rulership_rows = session.execute(
            select(AstralSignModel.code, PlanetModel.code)
            .select_from(AstralPlanetSignDignityModel)
            .join(
                AstralSignModel,
                AstralPlanetSignDignityModel.astral_sign_id == AstralSignModel.id,
            )
            .join(PlanetModel, AstralPlanetSignDignityModel.astral_planet_id == PlanetModel.id)
            .join(
                AstralDignityTypeModel,
                AstralPlanetSignDignityModel.astral_dignity_type_id == AstralDignityTypeModel.id,
            )
            .join(
                AstralSystemModel,
                AstralPlanetSignDignityModel.astral_system_id == AstralSystemModel.id,
            )
            .where(
                AstralDignityTypeModel.code == "domicile",
                AstralSystemModel.name == "traditional",
                AstralPlanetSignDignityModel.is_primary.is_(True),
            )
        ).all()
        assert dict(traditional_rulership_rows) == EXPECTED_TRADITIONAL_RULERSHIPS
        assert (
            session.scalar(
                select(func.count())
                .select_from(PlanetCategoryWeightModel)
                .where(PlanetCategoryWeightModel.reference_version_id == v2.id)
            )
            >= 30
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(HouseCategoryWeightModel)
                .where(HouseCategoryWeightModel.reference_version_id == v2.id)
            )
            >= 20
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(PointCategoryWeightModel)
                .where(PointCategoryWeightModel.reference_version_id == v2.id)
            )
            == 8
        )

        ruleset_v1 = session.scalar(
            select(PredictionRulesetModel).where(
                PredictionRulesetModel.reference_version_id == v2.id,
                PredictionRulesetModel.version == "1.0.0",
            )
        )
        assert ruleset_v1 is not None

        ruleset_v2 = session.scalar(
            select(PredictionRulesetModel).where(
                PredictionRulesetModel.reference_version_id == v2.id,
                PredictionRulesetModel.version == "2.0.0",
            )
        )
        assert ruleset_v2 is not None

        assert (
            session.scalar(
                select(func.count())
                .select_from(RulesetEventTypeModel)
                .where(RulesetEventTypeModel.ruleset_id.in_([ruleset_v1.id, ruleset_v2.id]))
            )
            == 16
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(RulesetParameterModel)
                .where(RulesetParameterModel.ruleset_id.in_([ruleset_v1.id, ruleset_v2.id]))
            )
            == 16
        )

        # 4. Verify idempotence (already seeded and locked)
        # Should not raise any error and just return
        run_seed(session)

        session.query(AstralSignProfileModel).delete()
        session.query(AstralElementModel).delete()
        session.query(AstralModalityModel).delete()
        session.query(AstralPolarityModel).delete()
        session.commit()
        run_seed(session)
        session.commit()
        assert session.scalar(select(func.count()).select_from(AstralSignProfileModel)) == 12
        assert session.scalar(select(func.count()).select_from(AstralElementModel)) == 4
        assert session.scalar(select(func.count()).select_from(AstralModalityModel)) == 3
        assert session.scalar(select(func.count()).select_from(AstralPolarityModel)) == 2

    engine.dispose()


def test_seed_31_prediction_v2_idempotence_corrupted_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    engine = _setup_engine(monkeypatch, tmp_path, "test-seed-v2-corrupted.db")

    with Session(engine) as session:
        # 1. Setup V1.0.0
        ReferenceDataService.seed_reference_version(session, "1.0.0")

        # 2. Partially seed V2.0.0 manually (LOCKED)
        v2 = ReferenceVersionModel(version="2.0.0", description="Corrupted", is_locked=True)
        session.add(v2)
        session.commit()

        # 3. Running run_seed should raise SeedAbortError as per AC15 case 3
        with pytest.raises(SeedAbortError, match="LOCKED"):
            run_seed(session)

    engine.dispose()


def test_seed_31_prediction_v2_repair_unlocked_proceeds(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    engine = _setup_engine(monkeypatch, tmp_path, "test-seed-v2-repair.db")

    with Session(engine) as session:
        # 1. Setup V1.0.0
        ReferenceDataService.seed_reference_version(session, "1.0.0")
        session.commit()

        # 2. Partially seed V2.0.0 manually (unlocked)
        v2 = ReferenceVersionModel(
            version="2.0.0", description="Unlocked but partial", is_locked=False
        )
        session.add(v2)
        session.commit()

        # Add a dummy category to simulate partial seeding
        session.add(
            PredictionCategoryModel(
                reference_version_id=v2.id,
                code="partial",
                name="Partial",
                display_name="Partial",
                sort_order=1,
            )
        )
        session.commit()

        # 3. Running run_seed should proceed with repair
        run_seed(session)
        session.commit()

        # 4. Verify repair successful (original counts expected)
        assert (
            session.scalar(
                select(func.count())
                .select_from(PredictionCategoryModel)
                .where(PredictionCategoryModel.reference_version_id == v2.id)
            )
            == 12
        )
        # Ensure the 'partial' category was removed
        assert (
            session.scalar(
                select(func.count())
                .select_from(PredictionCategoryModel)
                .where(
                    PredictionCategoryModel.reference_version_id == v2.id,
                    PredictionCategoryModel.code == "partial",
                )
            )
            == 0
        )
        assert v2.is_locked is True

    engine.dispose()
