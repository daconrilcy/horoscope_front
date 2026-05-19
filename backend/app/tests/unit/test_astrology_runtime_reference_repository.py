"""Tests du repository de reference astrologique runtime."""

from copy import copy
from dataclasses import replace

import pytest
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.dignity_reference import AstralPlanetConditionSignalProfileModel
from app.infra.db.models.reference import (
    AspectModel,
    AstralSignModel,
    AstralSignProfileModel,
    HouseModel,
    PlanetModel,
    ReferenceVersionModel,
)
from app.infra.db.repositories.astrology_runtime_reference_mapper import (
    AstrologyRuntimeReferenceMapper,
)
from app.infra.db.repositories.astrology_runtime_reference_repository import (
    AstrologyRuntimeReferenceError,
    AstrologyRuntimeReferenceRepository,
)
from app.services.reference_data_service import ReferenceDataService
from app.tests.helpers.db_session import app_test_engine, open_app_test_db_session
from tests.factories.astrology_runtime_reference_factory import (
    complete_reference,
    invalid_orphan_aspect_rule,
    missing_dignity,
)


def _cleanup_reference_tables() -> None:
    """Reconstruit une DB de test propre pour charger le referentiel runtime."""
    ReferenceDataService._clear_cache_for_tests()
    Base.metadata.drop_all(bind=app_test_engine())
    Base.metadata.create_all(bind=app_test_engine())
    with open_app_test_db_session() as db:
        for model in (
            ChartResultModel,
            AspectModel,
            HouseModel,
            AstralSignModel,
            PlanetModel,
            ReferenceVersionModel,
        ):
            db.execute(delete(model))
        db.commit()


def test_mapper_returns_immutable_runtime_reference() -> None:
    """Le mapper infra convertit un payload DB-like en contrat domaine type."""
    reference = complete_reference()

    assert reference.reference_version == "test"
    assert reference.planets.codes[:2] == ("sun", "moon")
    assert len(reference.signs.items) == 12
    assert len(reference.houses.items) == 12


def test_mapper_rejects_missing_condition_weight_axes() -> None:
    """Le mapper ne doit pas neutraliser un axe conditionnel absent."""
    mapper = AstrologyRuntimeReferenceMapper()

    with pytest.raises(KeyError):
        mapper.map_dignity_reference(
            {
                "score_profiles": [
                    {
                        "code": "traditional_standard",
                        "tradition": "traditional",
                        "is_default": True,
                    }
                ],
                "essential_weights": {
                    "traditional_standard": [
                        {
                            "dignity_type_code": "domicile",
                            "score_value": 5,
                            "functional_weight": 1,
                            "expression_weight": 0.7,
                            "intensity_weight": 0.6,
                        }
                    ]
                },
            }
        )


def test_repository_integrity_rejects_missing_dignities() -> None:
    """L'integrite runtime bloque les references incompletes."""
    repository = AstrologyRuntimeReferenceRepository(
        db=None, mapper=AstrologyRuntimeReferenceMapper()
    )  # type: ignore[arg-type]

    with pytest.raises(AstrologyRuntimeReferenceError) as error:
        repository._validate(missing_dignity())

    assert error.value.code == "invalid_astrology_runtime_reference"
    assert error.value.details == {"field": "sign_rulerships", "reason": "missing"}


def test_repository_loads_complete_runtime_reference_from_db() -> None:
    """Le repository charge une photographie runtime complete depuis SQLAlchemy."""
    _cleanup_reference_tables()

    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        reference = AstrologyRuntimeReferenceRepository(db).load("1.0.0")

    assert reference.reference_version == "1.0.0"
    assert len(reference.signs.items) == 12
    assert {
        (sign.code, sign.element, sign.modality, sign.polarity) for sign in reference.signs.items
    } >= {
        ("aries", "fire", "cardinal", "yang"),
        ("taurus", "earth", "fixed", "yin"),
        ("libra", "air", "cardinal", "yang"),
        ("pisces", "water", "mutable", "yin"),
    }
    assert len(reference.houses.items) == 12
    assert set(reference.dignities.sign_rulerships) == set(reference.signs.codes)
    assert reference.dignity_reference.default_score_profile == "traditional_standard"
    assert {item.code for item in reference.dignity_reference.essential_types} >= {
        "domicile",
        "exaltation",
        "detriment",
        "fall",
        "triplicity",
        "term",
        "face",
        "peregrine",
    }
    assert {item.code for item in reference.dignity_reference.accidental_types} >= {
        "angular_house",
        "retrograde",
        "cazimi",
        "planetary_joy",
    }
    assert reference.dignity_reference.term_systems
    assert reference.dignity_reference.decan_systems
    assert len(reference.dignity_reference.essential_rules) == 38
    assert len(reference.dignity_reference.term_bounds) == 60
    assert len(reference.dignity_reference.face_decans) == 36
    assert reference.dignity_reference.accidental_rules
    assert reference.condition_signal_profiles
    condition_signal = reference.condition_signal_profiles[0]
    assert condition_signal.condition_axis == "functional_strength"
    assert condition_signal.level_min == 1.0
    assert condition_signal.level_max == 100.0
    assert condition_signal.signal_code == "functional_strength_high"
    assert condition_signal.interpretation_use == "prioritize_condition_axis"
    assert condition_signal.prompt_hint == "functional_strength_positive"
    first_weight = reference.dignity_reference.essential_weights["traditional_standard"][0]
    assert first_weight.condition_visibility == 0.0
    assert first_weight.condition_stability == 0.0
    assert first_weight.condition_coherence == 0.0
    assert first_weight.condition_support == 0.0
    assert first_weight.condition_constraint == 0.0
    assert {item.code for item in reference.angle_points.items} >= {"asc", "dsc", "mc", "ic"}
    assert reference.aspects.items
    assert reference.aspects.orb_rules


def test_repository_integrity_rejects_missing_condition_signal_profiles() -> None:
    """L'integrite runtime exige les profils de signaux conditionnels."""
    repository = AstrologyRuntimeReferenceRepository(
        db=None, mapper=AstrologyRuntimeReferenceMapper()
    )  # type: ignore[arg-type]
    reference = replace(complete_reference(), condition_signal_profiles=())

    with pytest.raises(AstrologyRuntimeReferenceError) as error:
        repository._validate(reference)

    assert error.value.details == {
        "field": "condition_signal_profiles",
        "reason": "missing",
    }


def test_repository_integrity_rejects_unknown_condition_signal_axis() -> None:
    """L'integrite runtime exige des axes portes par PlanetConditionProfile."""
    repository = AstrologyRuntimeReferenceRepository(
        db=None, mapper=AstrologyRuntimeReferenceMapper()
    )  # type: ignore[arg-type]
    reference = complete_reference()
    invalid_signal_profile = replace(
        reference.condition_signal_profiles[0],
        condition_axis="expression_quality",
    )
    reference = replace(reference, condition_signal_profiles=(invalid_signal_profile,))

    with pytest.raises(AstrologyRuntimeReferenceError) as error:
        repository._validate(reference)

    assert error.value.details == {
        "field": "condition_signal_profiles",
        "reason": "unknown_axis:expression_quality",
    }


def test_repository_loads_condition_signal_profiles_from_db() -> None:
    """Le repository charge les plages de signaux depuis la table versionnee."""
    _cleanup_reference_tables()

    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        rows = db.scalars(
            select(AstralPlanetConditionSignalProfileModel).order_by(
                AstralPlanetConditionSignalProfileModel.priority_weight
            )
        ).all()

    assert rows
    assert rows[0].condition_axis == "functional_strength"
    assert rows[0].signal_code == "functional_strength_high"


def test_public_reference_payload_keeps_sign_contract_unchanged() -> None:
    """Le payload public reference-data ne projette pas les profils runtime internes."""
    _cleanup_reference_tables()

    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        payload = ReferenceDataService.get_active_reference_data(db, version="1.0.0")

    assert payload["signs"][0] == {"code": "aries", "name": "Aries"}
    assert all("element" not in sign for sign in payload["signs"])
    assert all("modality" not in sign for sign in payload["signs"])
    assert all("polarity" not in sign for sign in payload["signs"])


def test_repository_rejects_missing_sign_profile_from_db() -> None:
    """Le chargement runtime bloque une DB sans douze profils de signes."""
    _cleanup_reference_tables()

    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        profile_id = db.scalar(
            select(AstralSignProfileModel.id)
            .join(AstralSignModel, AstralSignProfileModel.astral_sign_id == AstralSignModel.id)
            .where(AstralSignModel.code == "aries")
        )
        assert profile_id is not None
        db.execute(delete(AstralSignProfileModel).where(AstralSignProfileModel.id == profile_id))
        db.commit()

        with pytest.raises(AstrologyRuntimeReferenceError) as error:
            AstrologyRuntimeReferenceRepository(db).load("1.0.0")

    assert error.value.code == "invalid_astrology_runtime_reference"
    assert error.value.details == {
        "field": "sign_profiles",
        "reason": "missing required sign profile field element for aries",
    }


def test_repository_integrity_rejects_unknown_sign_sentinel() -> None:
    """L'integrite runtime refuse les sentinelles unknown hors planetes aussi."""
    repository = AstrologyRuntimeReferenceRepository(
        db=None, mapper=AstrologyRuntimeReferenceMapper()
    )  # type: ignore[arg-type]
    reference = complete_reference()
    first_sign = copy(reference.signs.items[0])
    object.__setattr__(first_sign, "code", "unknown")
    invalid_reference = replace(
        reference,
        signs=replace(reference.signs, items=(first_sign, *reference.signs.items[1:])),
    )

    with pytest.raises(AstrologyRuntimeReferenceError) as error:
        repository._validate(invalid_reference)

    assert error.value.details == {"field": "signs", "reason": "unknown_forbidden"}


def test_repository_integrity_rejects_orphan_aspect_rule() -> None:
    """L'integrite runtime refuse les regles d'orbe sans aspect canonique."""
    repository = AstrologyRuntimeReferenceRepository(
        db=None, mapper=AstrologyRuntimeReferenceMapper()
    )  # type: ignore[arg-type]

    with pytest.raises(AstrologyRuntimeReferenceError) as error:
        repository._validate(invalid_orphan_aspect_rule())

    assert error.value.details == {
        "field": "aspect_orb_rules",
        "reason": "orphan_aspect:nonexistent",
    }


def test_repository_integrity_rejects_orphan_aspect_point_rule() -> None:
    """L'integrite runtime refuse les regles d'orbe ciblant un point absent."""
    repository = AstrologyRuntimeReferenceRepository(
        db=None, mapper=AstrologyRuntimeReferenceMapper()
    )  # type: ignore[arg-type]
    reference = complete_reference()
    rule = replace(reference.aspects.orb_rules[0], source_point_code="ghost_point")
    invalid_reference = replace(
        reference,
        aspects=replace(reference.aspects, orb_rules=(rule,)),
    )

    with pytest.raises(AstrologyRuntimeReferenceError) as error:
        repository._validate(invalid_reference)

    assert error.value.details == {
        "field": "aspect_orb_rules",
        "reason": "orphan_source_point_code:ghost_point",
    }
