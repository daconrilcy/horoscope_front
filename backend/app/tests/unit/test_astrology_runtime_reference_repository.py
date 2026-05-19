"""Tests du repository de reference astrologique runtime."""

from copy import copy
from dataclasses import replace

import pytest
from sqlalchemy import delete, select

from app.infra.db.base import Base
from app.infra.db.models.chart_result import ChartResultModel
from app.infra.db.models.dignity_reference import (
    AstralAdvancedConditionScoreProfileModel,
    AstralAdvancedConditionTypeModel,
    AstralAdvancedConditionWeightModel,
    AstralDominanceFactorTypeModel,
    AstralDominanceScoreProfileModel,
    AstralDominanceScoreWeightModel,
    AstralInterpretationAdapterRuleModel,
    AstralInterpretationSignalTypeModel,
    AstralInterpretationThemeModel,
    AstralPlanetConditionSignalProfileModel,
)
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
    assert {(item.code, item.planet_codes) for item in reference.planet_natures.items} == {
        ("benefic", ("venus", "jupiter")),
        ("malefic", ("mars", "saturn")),
    }
    assert reference.planet_natures.nature_for_planet("venus") == "benefic"
    assert reference.planet_natures.nature_for_planet("saturn") == "malefic"
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
    assert [item.code for item in reference.dominance_factor_types] == [
        "chart_ruler",
        "angularity",
        "condition_strength",
        "visibility",
        "most_elevated",
        "luminary_emphasis",
        "house_rulership_load",
        "aspect_centrality",
    ]
    assert reference.dominance_factor_types[0].default_weight == 1.4
    assert reference.dominance_reference.default_score_profile.code == "natal_standard_v1"
    assert [
        (item.factor_type_code, item.weight)
        for item in reference.dominance_reference.weights_for_profile("natal_standard_v1")
    ] == [
        ("chart_ruler", 1.4),
        ("angularity", 1.3),
        ("condition_strength", 1.2),
        ("visibility", 1.1),
        ("most_elevated", 1.0),
        ("luminary_emphasis", 0.9),
        ("house_rulership_load", 0.8),
        ("aspect_centrality", 0.8),
    ]
    assert [item.code for item in reference.advanced_condition_reference.condition_types] == [
        "mutual_reception",
        "hayz",
        "out_of_sect",
        "stationary",
        "besiegement",
        "bonification",
        "maltreatment",
        "fast_motion",
        "slow_motion",
        "heliacal_rising",
        "heliacal_setting",
        "oriental",
        "occidental",
    ]
    assert (
        reference.advanced_condition_reference.condition_types[0].description
        == "Deux planetes occupent les domiciles ou dignites l'une de l'autre."
    )
    assert (
        reference.advanced_condition_reference.default_score_profile.code
        == "traditional_advanced_v1"
    )
    assert [
        item.condition_type_code
        for item in reference.advanced_condition_reference.weights_for_profile(
            "traditional_advanced_v1"
        )
    ] == [
        "mutual_reception",
        "hayz",
        "out_of_sect",
        "stationary",
        "besiegement",
        "bonification",
        "maltreatment",
        "fast_motion",
        "slow_motion",
        "heliacal_rising",
        "heliacal_setting",
        "oriental",
        "occidental",
    ]
    advanced_weight = reference.advanced_condition_reference.weights_for_profile(
        "traditional_advanced_v1"
    )[0]
    assert advanced_weight.visibility_weight == 0.0
    assert [item.code for item in reference.interpretation_adapter_reference.signal_types] == [
        "dominant_mars_signature",
        "high_externalization",
        "constraint_on_action",
        "structural_endurance",
    ]
    assert {item.code for item in reference.interpretation_adapter_reference.themes} == {
        "drive_assertion_action",
        "visibility_expression",
        "frustration_pressure",
        "responsibility_structure",
    }
    assert [item.code for item in reference.interpretation_adapter_reference.adapter_rules] == [
        "dominant_mars_to_signature",
        "high_visibility_to_externalization",
        "saturn_stability_to_endurance",
        "constraint_to_action_pressure",
    ]
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


def test_repository_integrity_rejects_missing_dominance_factor() -> None:
    """L'integrite runtime exige les facteurs de dominance contractuels."""
    repository = AstrologyRuntimeReferenceRepository(
        db=None, mapper=AstrologyRuntimeReferenceMapper()
    )  # type: ignore[arg-type]
    reference = complete_reference()
    reference = replace(
        reference,
        dominance_factor_types=reference.dominance_factor_types[1:],
    )

    with pytest.raises(AstrologyRuntimeReferenceError) as error:
        repository._validate(reference)

    assert error.value.details == {
        "field": "dominance_factor_types",
        "reason": "missing:chart_ruler;extra:",
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


def test_repository_loads_dominance_factor_types_from_db() -> None:
    """Le repository charge les facteurs de dominance depuis la table versionnee."""
    _cleanup_reference_tables()

    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        rows = db.scalars(
            select(AstralDominanceFactorTypeModel).order_by(
                AstralDominanceFactorTypeModel.sort_order
            )
        ).all()

    assert [
        {
            "code": row.code,
            "label": row.label,
            "category": row.category,
            "default_weight": row.default_weight,
            "sort_order": row.sort_order,
            "is_active": row.is_active,
            "description": row.description,
        }
        for row in rows
    ] == [
        {
            "code": "chart_ruler",
            "label": "Chart ruler",
            "category": "rulership",
            "default_weight": 1.4,
            "sort_order": 1,
            "is_active": True,
            "description": "Planete gouvernant le signe de l'Ascendant.",
        },
        {
            "code": "angularity",
            "label": "Angularity",
            "category": "house_position",
            "default_weight": 1.3,
            "sort_order": 2,
            "is_active": True,
            "description": "Planete situee en maison angulaire ou proche d'un angle.",
        },
        {
            "code": "condition_strength",
            "label": "Condition strength",
            "category": "planet_condition",
            "default_weight": 1.2,
            "sort_order": 3,
            "is_active": True,
            "description": "Force issue du PlanetConditionProfile.",
        },
        {
            "code": "visibility",
            "label": "Visibility",
            "category": "planet_condition",
            "default_weight": 1.1,
            "sort_order": 4,
            "is_active": True,
            "description": "Visibilite issue du PlanetConditionProfile.",
        },
        {
            "code": "most_elevated",
            "label": "Most elevated planet",
            "category": "chart_position",
            "default_weight": 1.0,
            "sort_order": 5,
            "is_active": True,
            "description": (
                "Planete la plus proche du Milieu du Ciel ou la plus elevee selon le modele retenu."
            ),
        },
        {
            "code": "luminary_emphasis",
            "label": "Luminary emphasis",
            "category": "luminary",
            "default_weight": 0.9,
            "sort_order": 6,
            "is_active": True,
            "description": (
                "Poids specifique du Soleil et de la Lune dans la structure globale du theme."
            ),
        },
        {
            "code": "house_rulership_load",
            "label": "House rulership load",
            "category": "rulership",
            "default_weight": 0.8,
            "sort_order": 7,
            "is_active": True,
            "description": "Nombre et importance des maisons gouvernees par une planete.",
        },
        {
            "code": "aspect_centrality",
            "label": "Aspect centrality",
            "category": "aspects",
            "default_weight": 0.8,
            "sort_order": 8,
            "is_active": True,
            "description": "Centralite d'une planete dans le reseau d'aspects.",
        },
    ]


def test_repository_loads_dominance_score_profiles_and_weights_from_db() -> None:
    """Le repository charge le profil et les poids de dominance du brief."""
    _cleanup_reference_tables()

    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        profile = db.scalar(select(AstralDominanceScoreProfileModel))
        assert profile is not None
        rows = db.execute(
            select(
                AstralDominanceScoreProfileModel.code,
                AstralDominanceFactorTypeModel.code.label("factor_type_code"),
                AstralDominanceScoreWeightModel.weight,
                AstralDominanceScoreWeightModel.normalization_method,
            )
            .join(
                AstralDominanceScoreProfileModel,
                AstralDominanceScoreWeightModel.score_profile_id
                == AstralDominanceScoreProfileModel.id,
            )
            .join(
                AstralDominanceFactorTypeModel,
                AstralDominanceScoreWeightModel.factor_type_id == AstralDominanceFactorTypeModel.id,
            )
            .order_by(AstralDominanceFactorTypeModel.sort_order)
        ).all()

    assert profile.code == "natal_standard_v1"
    assert profile.tradition_code == "modern"
    assert [(row.factor_type_code, row.weight) for row in rows] == [
        ("chart_ruler", 1.4),
        ("angularity", 1.3),
        ("condition_strength", 1.2),
        ("visibility", 1.1),
        ("most_elevated", 1.0),
        ("luminary_emphasis", 0.9),
        ("house_rulership_load", 0.8),
        ("aspect_centrality", 0.8),
    ]
    assert rows[0].normalization_method == "binary"


def test_repository_loads_advanced_condition_references_from_db() -> None:
    """Le repository charge les types, profil et poids avances du brief."""
    _cleanup_reference_tables()

    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        profile = db.scalar(select(AstralAdvancedConditionScoreProfileModel))
        assert profile is not None
        rows = db.execute(
            select(
                AstralAdvancedConditionScoreProfileModel.code,
                AstralAdvancedConditionTypeModel.code.label("condition_type_code"),
                AstralAdvancedConditionTypeModel.description,
                AstralAdvancedConditionWeightModel.ranking_weight,
                AstralAdvancedConditionWeightModel.uses_default_weight,
            )
            .join(
                AstralAdvancedConditionScoreProfileModel,
                AstralAdvancedConditionWeightModel.score_profile_id
                == AstralAdvancedConditionScoreProfileModel.id,
            )
            .join(
                AstralAdvancedConditionTypeModel,
                AstralAdvancedConditionWeightModel.condition_type_id
                == AstralAdvancedConditionTypeModel.id,
            )
            .order_by(AstralAdvancedConditionTypeModel.sort_order)
        ).all()

    assert profile.code == "traditional_advanced_v1"
    assert profile.tradition_code == "traditional"
    assert rows[0].condition_type_code == "mutual_reception"
    assert (
        rows[0].description == "Deux planetes occupent les domiciles ou dignites l'une de l'autre."
    )
    assert rows[0].ranking_weight == 1.2
    assert all(row.uses_default_weight is False for row in rows)


def test_repository_loads_interpretation_adapter_references_from_db() -> None:
    """Le repository charge les signaux, themes et regles d'adaptation du brief."""
    _cleanup_reference_tables()

    with open_app_test_db_session() as db:
        ReferenceDataService.seed_reference_version(db, version="1.0.0")
        signal_rows = db.scalars(
            select(AstralInterpretationSignalTypeModel).order_by(
                AstralInterpretationSignalTypeModel.sort_order
            )
        ).all()
        theme_rows = db.scalars(
            select(AstralInterpretationThemeModel).order_by(AstralInterpretationThemeModel.code)
        ).all()
        rule_rows = db.scalars(
            select(AstralInterpretationAdapterRuleModel).order_by(
                AstralInterpretationAdapterRuleModel.priority_override_rank,
                AstralInterpretationAdapterRuleModel.code,
            )
        ).all()

    assert [row.code for row in signal_rows] == [
        "dominant_mars_signature",
        "high_externalization",
        "constraint_on_action",
        "structural_endurance",
    ]
    assert [
        {
            "code": row.code,
            "category": row.category,
            "theme_code": row.theme_code,
            "priority_default": row.priority_default,
            "priority_default_rank": row.priority_default_rank,
            "sort_order": row.sort_order,
            "is_active": row.is_active,
        }
        for row in signal_rows
    ] == [
        {
            "code": "dominant_mars_signature",
            "category": "planetary_signature",
            "theme_code": "drive_assertion_action",
            "priority_default": "critical",
            "priority_default_rank": 10,
            "sort_order": 1,
            "is_active": True,
        },
        {
            "code": "high_externalization",
            "category": "expression_pattern",
            "theme_code": "visibility_expression",
            "priority_default": "high",
            "priority_default_rank": 20,
            "sort_order": 2,
            "is_active": True,
        },
        {
            "code": "constraint_on_action",
            "category": "tension_pattern",
            "theme_code": "frustration_pressure",
            "priority_default": "medium",
            "priority_default_rank": 30,
            "sort_order": 3,
            "is_active": True,
        },
        {
            "code": "structural_endurance",
            "category": "planetary_signature",
            "theme_code": "responsibility_structure",
            "priority_default": "high",
            "priority_default_rank": 20,
            "sort_order": 4,
            "is_active": True,
        },
    ]
    assert [
        {"code": row.code, "category": row.category, "is_active": row.is_active}
        for row in theme_rows
    ] == [
        {"code": "drive_assertion_action", "category": "behavioral", "is_active": True},
        {"code": "frustration_pressure", "category": "tension", "is_active": True},
        {"code": "responsibility_structure", "category": "functional", "is_active": True},
        {"code": "visibility_expression", "category": "expression", "is_active": True},
    ]
    assert [row.code for row in rule_rows] == [
        "dominant_mars_to_signature",
        "high_visibility_to_externalization",
        "saturn_stability_to_endurance",
        "constraint_to_action_pressure",
    ]
    assert [
        {
            "code": row.code,
            "source_type": row.source_type,
            "source_code": row.source_code,
            "condition_json": row.condition_json,
            "signal_code": row.signal_code,
            "priority_override": row.priority_override,
            "priority_override_rank": row.priority_override_rank,
            "weight": row.weight,
            "is_active": row.is_active,
            "reference_version_code": row.reference_version_code,
        }
        for row in rule_rows
    ] == [
        {
            "code": "dominant_mars_to_signature",
            "source_type": "dominant_planet",
            "source_code": "mars",
            "condition_json": {"dominance_level": "dominant"},
            "signal_code": "dominant_mars_signature",
            "priority_override": "critical",
            "priority_override_rank": 10,
            "weight": 1.0,
            "is_active": True,
            "reference_version_code": "v1",
        },
        {
            "code": "high_visibility_to_externalization",
            "source_type": "condition_axis",
            "source_code": "visibility",
            "condition_json": {"min": 0.7},
            "signal_code": "high_externalization",
            "priority_override": "high",
            "priority_override_rank": 20,
            "weight": 0.8,
            "is_active": True,
            "reference_version_code": "v1",
        },
        {
            "code": "saturn_stability_to_endurance",
            "source_type": "compound",
            "source_code": "saturn_stability",
            "condition_json": {"min": 0.7},
            "signal_code": "structural_endurance",
            "priority_override": "high",
            "priority_override_rank": 20,
            "weight": 0.9,
            "is_active": True,
            "reference_version_code": "v1",
        },
        {
            "code": "constraint_to_action_pressure",
            "source_type": "condition_axis",
            "source_code": "constraint",
            "condition_json": {"min": 0.6},
            "signal_code": "constraint_on_action",
            "priority_override": "medium",
            "priority_override_rank": 30,
            "weight": 0.7,
            "is_active": True,
            "reference_version_code": "v1",
        },
    ]


def test_repository_rejects_additional_active_interpretation_adapter_rows() -> None:
    """Le contrat V1 bloque les extensions runtime non decidees."""
    repository = AstrologyRuntimeReferenceRepository(
        db=None, mapper=AstrologyRuntimeReferenceMapper()
    )  # type: ignore[arg-type]
    reference = complete_reference()
    extra_theme = replace(
        reference.interpretation_adapter_reference.themes[0],
        code="initiative_focus",
    )
    extra_signal = replace(
        reference.interpretation_adapter_reference.signal_types[0],
        code="initiative_signature",
        theme_code="initiative_focus",
    )
    extra_rule = replace(
        reference.interpretation_adapter_reference.adapter_rules[0],
        code="mars_to_initiative_signature",
        signal_code="initiative_signature",
    )
    adapter_reference = replace(
        reference.interpretation_adapter_reference,
        themes=(*reference.interpretation_adapter_reference.themes, extra_theme),
        signal_types=(*reference.interpretation_adapter_reference.signal_types, extra_signal),
        adapter_rules=(*reference.interpretation_adapter_reference.adapter_rules, extra_rule),
    )

    with pytest.raises(AstrologyRuntimeReferenceError) as error:
        repository._validate(replace(reference, interpretation_adapter_reference=adapter_reference))

    assert error.value.details == {
        "field": "interpretation_signal_types",
        "reason": "missing:;extra:initiative_signature",
    }


def test_repository_rejects_unknown_interpretation_priority() -> None:
    """Le contrat V1 limite les priorites aux valeurs gouvernees."""
    repository = AstrologyRuntimeReferenceRepository(
        db=None, mapper=AstrologyRuntimeReferenceMapper()
    )  # type: ignore[arg-type]
    reference = complete_reference()
    invalid_signal = replace(
        reference.interpretation_adapter_reference.signal_types[0],
        priority_default="urgent",
    )
    adapter_reference = replace(
        reference.interpretation_adapter_reference,
        signal_types=(invalid_signal, *reference.interpretation_adapter_reference.signal_types[1:]),
    )

    with pytest.raises(AstrologyRuntimeReferenceError) as error:
        repository._validate(replace(reference, interpretation_adapter_reference=adapter_reference))

    assert error.value.details == {
        "field": "interpretation_signal_types",
        "reason": "unknown_priority:urgent",
    }


def test_repository_rejects_unknown_interpretation_rule_override_priority() -> None:
    """Les overrides de regles utilisent le meme vocabulaire de priorite."""
    repository = AstrologyRuntimeReferenceRepository(
        db=None, mapper=AstrologyRuntimeReferenceMapper()
    )  # type: ignore[arg-type]
    reference = complete_reference()
    invalid_rule = replace(
        reference.interpretation_adapter_reference.adapter_rules[0],
        priority_override="urgent",
    )
    adapter_reference = replace(
        reference.interpretation_adapter_reference,
        adapter_rules=(invalid_rule, *reference.interpretation_adapter_reference.adapter_rules[1:]),
    )

    with pytest.raises(AstrologyRuntimeReferenceError) as error:
        repository._validate(replace(reference, interpretation_adapter_reference=adapter_reference))

    assert error.value.details == {
        "field": "interpretation_adapter_rules",
        "reason": "unknown_priority:urgent",
    }


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
