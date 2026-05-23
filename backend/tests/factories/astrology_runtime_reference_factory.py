"""Factories de tests pour le referentiel runtime astrologique.

Les tests construisent des contrats immutables complets au lieu de faire passer
des dictionnaires metier dans le domaine.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import replace

from app.domain.astrology.runtime.runtime_reference import (
    AccidentalDignityRuleReferenceData,
    AstrologyRuntimeReference,
    DignityConditionValue,
)
from app.infra.db.repositories.astrology_runtime_reference_mapper import (
    AstrologyRuntimeReferenceMapper,
)

_CANONICAL_SIGN_CODES = (
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
)

_CANONICAL_SIGN_PROFILES = {
    "aries": {"element": "fire", "modality": "cardinal", "polarity": "yang"},
    "taurus": {"element": "earth", "modality": "fixed", "polarity": "yin"},
    "gemini": {"element": "air", "modality": "mutable", "polarity": "yang"},
    "cancer": {"element": "water", "modality": "cardinal", "polarity": "yin"},
    "leo": {"element": "fire", "modality": "fixed", "polarity": "yang"},
    "virgo": {"element": "earth", "modality": "mutable", "polarity": "yin"},
    "libra": {"element": "air", "modality": "cardinal", "polarity": "yang"},
    "scorpio": {"element": "water", "modality": "fixed", "polarity": "yin"},
    "sagittarius": {"element": "fire", "modality": "mutable", "polarity": "yang"},
    "capricorn": {"element": "earth", "modality": "cardinal", "polarity": "yin"},
    "aquarius": {"element": "air", "modality": "fixed", "polarity": "yang"},
    "pisces": {"element": "water", "modality": "mutable", "polarity": "yin"},
}


def complete_sign_payloads(codes: Iterable[str] = _CANONICAL_SIGN_CODES) -> list[dict[str, object]]:
    """Construit des signes de fixture avec profils structurels explicites."""
    signs: list[dict[str, object]] = []
    for raw_code in codes:
        code = raw_code.strip().lower()
        profile = _CANONICAL_SIGN_PROFILES.get(code)
        if profile is None:
            raise ValueError(f"unknown sign fixture code: {raw_code}")
        signs.append({"code": code, "name": code.title(), **profile})
    return signs


def runtime_reference_from_mapping(
    payload: Mapping[str, object],
    *,
    reference_version_id: int = 1,
) -> AstrologyRuntimeReference:
    """Convertit un ancien payload de fixture en runtime reference type."""
    payload = dict(payload)
    payload["signs"] = _complete_sign_payload(payload.get("signs"))
    sign_rulerships = payload.get("sign_rulerships")
    if not isinstance(sign_rulerships, Mapping):
        sign_rulerships = {
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
    version = str(payload.get("version") or "test")
    if not payload.get("aspect_orb_rules"):
        payload["aspect_orb_rules"] = list(_default_aspect_orb_rules(payload))
    if not payload.get("house_axes"):
        payload["house_axes"] = [
            {
                "house_number": number,
                "opposite_house": number + 6 if number <= 6 else number - 6,
                "theme": f"axis_{number}",
            }
            for number in range(1, 13)
        ]
    return AstrologyRuntimeReferenceMapper().map_payload(
        reference_version_id=reference_version_id,
        reference_version=version,
        payload=payload,
        dignities=tuple(
            {
                "sign_code": sign,
                "planet_code": planet,
                "dignity_type": "domicile",
                "system": "traditional",
                "weight": 1.0,
                "is_primary": True,
            }
            for sign, planet in sign_rulerships.items()
        ),
        sign_rulerships={str(sign): str(planet) for sign, planet in sign_rulerships.items()},
        dignity_reference=_default_dignity_reference(),
        condition_signal_profiles=_default_condition_signal_profiles(version),
        dominance_factor_types=_default_dominance_factor_types(version),
        dominance_score_profiles=_default_dominance_score_profiles(),
        dominance_score_weights=_default_dominance_score_weights(),
        advanced_condition_types=_default_advanced_condition_types(version),
        advanced_condition_score_profiles=_default_advanced_condition_score_profiles(),
        advanced_condition_weights=_default_advanced_condition_weights(),
        interpretation_signal_types=_default_interpretation_signal_types(version),
        interpretation_themes=_default_interpretation_themes(version),
        interpretation_adapter_rules=_default_interpretation_adapter_rules(),
        planet_natures=_default_planet_natures(),
        planet_definitions={
            "sun": {"body_class": "luminary", "is_luminary": True},
            "moon": {"body_class": "luminary", "is_luminary": True},
            "mercury": {"body_class": "personal_planet", "is_luminary": False},
            "venus": {"body_class": "personal_planet", "is_luminary": False},
            "mars": {"body_class": "personal_planet", "is_luminary": False},
            "jupiter": {"body_class": "social_planet", "is_luminary": False},
            "saturn": {"body_class": "social_planet", "is_luminary": False},
            "uranus": {"body_class": "transpersonal_planet", "is_luminary": False},
            "neptune": {"body_class": "transpersonal_planet", "is_luminary": False},
            "pluto": {"body_class": "transpersonal_planet", "is_luminary": False},
        },
        angle_points=(
            {
                "code": "asc",
                "short_label": "ASC",
                "full_name": "Ascendant",
                "axis": "horizontal",
                "associated_house": 1,
            },
            {
                "code": "dsc",
                "short_label": "DSC",
                "full_name": "Descendant",
                "axis": "horizontal",
                "associated_house": 7,
            },
            {
                "code": "mc",
                "short_label": "MC",
                "full_name": "Midheaven",
                "axis": "vertical",
                "associated_house": 10,
            },
            {
                "code": "ic",
                "short_label": "IC",
                "full_name": "Imum Coeli",
                "axis": "vertical",
                "associated_house": 4,
            },
        ),
        astral_points=(
            {
                "code": "north_node",
                "display_name": "North Node",
                "family_code": "lunar_nodes",
                "astronomical_type": "orbital_intersection",
                "is_physical_body": False,
                "variants": [
                    {
                        "variant_code": "true",
                        "display_name": "True North Node",
                        "calculation_mode": "true",
                        "engine_key": "SE_TRUE_NODE",
                        "is_default": True,
                    }
                ],
                "aliases": [],
            },
            {
                "code": "south_node",
                "display_name": "South Node",
                "family_code": "lunar_nodes",
                "astronomical_type": "orbital_intersection",
                "is_physical_body": False,
                "variants": [
                    {
                        "variant_code": "true",
                        "display_name": "True South Node",
                        "calculation_mode": "true_opposition",
                        "engine_key": None,
                        "is_default": True,
                    }
                ],
                "aliases": [],
            },
        ),
        house_systems=(
            {"code": "placidus", "name": "Placidus", "is_active": True},
            {"code": "whole_sign", "name": "Whole Sign", "is_active": True},
            {"code": "equal", "name": "Equal", "is_active": True},
            {"code": "porphyry", "name": "Porphyry", "is_active": True},
        ),
    )


def _default_condition_signal_profiles(reference_version: str) -> tuple[dict[str, object], ...]:
    """Crée des profils de signaux conditionnels gouvernes pour les fixtures."""
    return (
        {
            "condition_axis": "functional_strength",
            "level_min": 1.0,
            "level_max": 100.0,
            "signal_code": "functional_strength_high",
            "signal_label": "Functional strength high",
            "signal_level": "high",
            "interpretation_use": "prioritize_condition_axis",
            "priority_weight": 10.0,
            "prompt_hint": "functional_strength_positive",
            "reference_version": reference_version,
        },
        {
            "condition_axis": "visibility",
            "level_min": 0.5,
            "level_max": 100.0,
            "signal_code": "visibility_high",
            "signal_label": "Visibility high",
            "signal_level": "high",
            "interpretation_use": "surface_condition_axis",
            "priority_weight": 30.0,
            "prompt_hint": "visibility_emphasized",
            "reference_version": reference_version,
        },
        {
            "condition_axis": "constraint",
            "level_min": 0.5,
            "level_max": 100.0,
            "signal_code": "constraint_high",
            "signal_label": "Constraint high",
            "signal_level": "high",
            "interpretation_use": "temper_condition_axis",
            "priority_weight": 80.0,
            "prompt_hint": "constraint_present",
            "reference_version": reference_version,
        },
    )


def _default_dominance_factor_types(reference_version: str) -> tuple[dict[str, object], ...]:
    """Crée les facteurs de dominance gouvernes pour les fixtures runtime."""
    return (
        {
            "code": "chart_ruler",
            "label": "Chart ruler",
            "category": "rulership",
            "default_weight": 1.4,
            "sort_order": 1,
            "is_active": True,
            "description": "Planete gouvernant le signe de l'Ascendant.",
            "reference_version": reference_version,
        },
        {
            "code": "angularity",
            "label": "Angularity",
            "category": "house_position",
            "default_weight": 1.3,
            "sort_order": 2,
            "is_active": True,
            "description": "Planete situee en maison angulaire ou proche d'un angle.",
            "reference_version": reference_version,
        },
        {
            "code": "condition_strength",
            "label": "Condition strength",
            "category": "planet_condition",
            "default_weight": 1.2,
            "sort_order": 3,
            "is_active": True,
            "description": "Force issue du PlanetConditionProfile.",
            "reference_version": reference_version,
        },
        {
            "code": "visibility",
            "label": "Visibility",
            "category": "planet_condition",
            "default_weight": 1.1,
            "sort_order": 4,
            "is_active": True,
            "description": "Visibilite issue du PlanetConditionProfile.",
            "reference_version": reference_version,
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
            "reference_version": reference_version,
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
            "reference_version": reference_version,
        },
        {
            "code": "house_rulership_load",
            "label": "House rulership load",
            "category": "rulership",
            "default_weight": 0.8,
            "sort_order": 7,
            "is_active": True,
            "description": "Nombre et importance des maisons gouvernees par une planete.",
            "reference_version": reference_version,
        },
        {
            "code": "aspect_centrality",
            "label": "Aspect centrality",
            "category": "aspects",
            "default_weight": 0.8,
            "sort_order": 8,
            "is_active": True,
            "description": "Centralite d'une planete dans le reseau d'aspects.",
            "reference_version": reference_version,
        },
    )


def _default_dominance_score_profiles() -> tuple[dict[str, object], ...]:
    """Crée le profil standard de scoring des dominantes pour les fixtures."""
    return (
        {
            "code": "natal_standard_v1",
            "label": "Natal standard dominance profile v1",
            "tradition_code": "modern",
            "description": (
                "Profil standard pour calculer les planetes dominantes d'un theme natal."
            ),
            "reference_version_code": "v1",
            "is_active": True,
        },
    )


def _default_dominance_score_weights() -> tuple[dict[str, object], ...]:
    """Crée les poids standard de scoring des dominantes pour les fixtures."""
    return (
        {
            "score_profile_code": "natal_standard_v1",
            "factor_type_code": "chart_ruler",
            "weight": 1.4,
            "min_value": 0,
            "max_value": 1,
            "normalization_method": "binary",
            "notes": "Bonus si la planete est maitre de l'Ascendant.",
        },
        {
            "score_profile_code": "natal_standard_v1",
            "factor_type_code": "angularity",
            "weight": 1.3,
            "min_value": 0,
            "max_value": 1,
            "normalization_method": "normalized_axis",
            "notes": "Utilise l'angularite ou la visibilite deja calculee.",
        },
        {
            "score_profile_code": "natal_standard_v1",
            "factor_type_code": "condition_strength",
            "weight": 1.2,
            "min_value": 0,
            "max_value": 1,
            "normalization_method": "normalized_axis",
            "notes": "Utilise functional_strength du PlanetConditionProfile.",
        },
        {
            "score_profile_code": "natal_standard_v1",
            "factor_type_code": "visibility",
            "weight": 1.1,
            "min_value": 0,
            "max_value": 1,
            "normalization_method": "normalized_axis",
            "notes": "Utilise visibility du PlanetConditionProfile.",
        },
        {
            "score_profile_code": "natal_standard_v1",
            "factor_type_code": "most_elevated",
            "weight": 1.0,
            "min_value": 0,
            "max_value": 1,
            "normalization_method": "rank_bonus",
            "notes": "Bonus pour la planete la plus elevee ou proche du MC.",
        },
        {
            "score_profile_code": "natal_standard_v1",
            "factor_type_code": "luminary_emphasis",
            "weight": 0.9,
            "min_value": 0,
            "max_value": 1,
            "normalization_method": "binary_or_scaled",
            "notes": "Accent specifique pour Soleil/Lune selon visibilite et condition.",
        },
        {
            "score_profile_code": "natal_standard_v1",
            "factor_type_code": "house_rulership_load",
            "weight": 0.8,
            "min_value": 0,
            "max_value": 1,
            "normalization_method": "scaled_count",
            "notes": "Score base sur le nombre et le type de maisons gouvernees.",
        },
        {
            "score_profile_code": "natal_standard_v1",
            "factor_type_code": "aspect_centrality",
            "weight": 0.8,
            "min_value": 0,
            "max_value": 1,
            "normalization_method": "scaled_count",
            "notes": "Score base sur les aspects significatifs recus ou emis.",
        },
    )


def _default_advanced_condition_types(reference_version: str) -> tuple[dict[str, object], ...]:
    """Crée les types parents avances gouvernes pour les fixtures runtime."""
    rows = (
        ("mutual_reception", 1.2, 10),
        ("hayz", 1.1, 20),
        ("out_of_sect", -1.0, 30),
        ("stationary", 1.0, 40),
        ("besiegement", -1.3, 50),
        ("bonification", 1.0, 60),
        ("maltreatment", -1.2, 70),
        ("fast_motion", 0.7, 80),
        ("slow_motion", -0.6, 90),
        ("heliacal_rising", 0.9, 100),
        ("heliacal_setting", -0.8, 110),
        ("oriental", 0.4, 120),
        ("occidental", 0.4, 130),
        ("sect_nature_mitigation", 0.0, 140),
    )
    return tuple(
        {
            "code": code,
            "label": code.replace("_", " ").title(),
            "category": "advanced",
            "description": f"Condition avancee fixture {code}.",
            "functional_effect": "contextual",
            "expression_effect": "contextual",
            "intensity_effect": "contextual",
            "visibility_effect": "neutral",
            "default_weight": weight,
            "sort_order": sort_order,
            "is_active": True,
            "reference_version": reference_version,
        }
        for code, weight, sort_order in rows
    )


def _default_advanced_condition_score_profiles() -> tuple[dict[str, object], ...]:
    """Crée le profil standard des conditions avancees pour les fixtures."""
    return (
        {
            "code": "traditional_advanced_v1",
            "label": "Traditional advanced planetary conditions v1",
            "tradition_code": "traditional",
            "description": "Profil standard des conditions avancees.",
            "reference_version_code": "v1",
            "is_active": True,
        },
    )


def _default_advanced_condition_weights() -> tuple[dict[str, object], ...]:
    """Crée les poids avances alignes sur les types de fixture."""
    return tuple(
        {
            "score_profile_code": "traditional_advanced_v1",
            "condition_type_code": item["code"],
            "functional_strength_weight": float(item["default_weight"]),
            "visibility_weight": 0.0,
            "stability_weight": 0.0,
            "intensity_weight": 0.0,
            "coherence_weight": 0.0,
            "support_weight": max(float(item["default_weight"]), 0.0),
            "constraint_weight": abs(min(float(item["default_weight"]), 0.0)),
            "ranking_weight": float(item["default_weight"]),
            "uses_default_weight": False,
            "notes": f"Poids fixture {item['code']}.",
        }
        for item in _default_advanced_condition_types("test")
    )


def _default_planet_natures() -> tuple[dict[str, object], ...]:
    """Crée les natures planetaires traditionnelles depuis le runtime de fixture."""
    return (
        {
            "code": "benefic",
            "label": "Benefic",
            "planet_codes": ("venus", "jupiter"),
            "sort_order": 1,
        },
        {
            "code": "malefic",
            "label": "Malefic",
            "planet_codes": ("mars", "saturn"),
            "sort_order": 2,
        },
    )


def _default_interpretation_signal_types(reference_version: str) -> tuple[dict[str, object], ...]:
    """Crée les types de signaux d'adaptation pour les fixtures runtime."""
    return (
        {
            "code": "dominant_mars_signature",
            "label": "Dominant Mars Signature",
            "category": "planetary_signature",
            "theme_code": "drive_assertion_action",
            "description": "Dominance martienne structurante.",
            "priority_default": "critical",
            "priority_default_rank": 10,
            "is_active": True,
            "sort_order": 1,
            "reference_version": reference_version,
        },
        {
            "code": "high_externalization",
            "label": "High Externalization",
            "category": "expression_pattern",
            "theme_code": "visibility_expression",
            "description": "Signal de forte exteriorisation de l'energie planetaire.",
            "priority_default": "high",
            "priority_default_rank": 20,
            "is_active": True,
            "sort_order": 2,
            "reference_version": reference_version,
        },
        {
            "code": "constraint_on_action",
            "label": "Constraint On Action",
            "category": "tension_pattern",
            "theme_code": "frustration_pressure",
            "description": "Signal de contrainte ou de pression sur l'action.",
            "priority_default": "medium",
            "priority_default_rank": 30,
            "is_active": True,
            "sort_order": 3,
            "reference_version": reference_version,
        },
        {
            "code": "structural_endurance",
            "label": "Structural Endurance",
            "category": "planetary_signature",
            "theme_code": "responsibility_structure",
            "description": "Signal de persistance structurelle liee a Saturne.",
            "priority_default": "high",
            "priority_default_rank": 20,
            "is_active": True,
            "sort_order": 4,
            "reference_version": reference_version,
        },
    )


def _default_interpretation_themes(reference_version: str) -> tuple[dict[str, object], ...]:
    """Crée les themes d'adaptation pour les fixtures runtime."""
    return (
        {
            "code": "drive_assertion_action",
            "label": "Drive / Assertion / Action",
            "category": "behavioral",
            "description": "Thematique liee a l'action, l'affirmation et l'impulsion.",
            "is_active": True,
            "reference_version": reference_version,
        },
        {
            "code": "visibility_expression",
            "label": "Visibility / Expression",
            "category": "expression",
            "description": "Thematique liee a l'expression visible et exterieure.",
            "is_active": True,
            "reference_version": reference_version,
        },
        {
            "code": "frustration_pressure",
            "label": "Frustration / Pressure",
            "category": "tension",
            "description": "Thematique de tension, pression ou limitation.",
            "is_active": True,
            "reference_version": reference_version,
        },
        {
            "code": "responsibility_structure",
            "label": "Responsibility / Structure",
            "category": "functional",
            "description": "Thematique de responsabilite, stabilite et structuration.",
            "is_active": True,
            "reference_version": reference_version,
        },
    )


def _default_interpretation_adapter_rules() -> tuple[dict[str, object], ...]:
    """Crée les règles d'adaptation pour les fixtures runtime."""
    return (
        {
            "code": "dominant_mars_to_signature",
            "source_type": "dominant_planet",
            "source_code": "mars",
            "conditions": [{"key": "dominance_level", "value": "dominant"}],
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
            "conditions": [{"key": "min", "value": 0.7}],
            "signal_code": "high_externalization",
            "priority_override": "high",
            "priority_override_rank": 20,
            "weight": 0.8,
            "is_active": True,
            "reference_version_code": "v1",
        },
        {
            "code": "constraint_to_action_pressure",
            "source_type": "condition_axis",
            "source_code": "constraint",
            "conditions": [{"key": "min", "value": 0.6}],
            "signal_code": "constraint_on_action",
            "priority_override": "medium",
            "priority_override_rank": 30,
            "weight": 0.7,
            "is_active": True,
            "reference_version_code": "v1",
        },
        {
            "code": "saturn_stability_to_endurance",
            "source_type": "compound",
            "source_code": "saturn_stability",
            "conditions": [{"key": "min", "value": 0.7}],
            "signal_code": "structural_endurance",
            "priority_override": "high",
            "priority_override_rank": 20,
            "weight": 0.9,
            "is_active": True,
            "reference_version_code": "v1",
        },
    )


def _default_dignity_reference() -> dict[str, object]:
    """Crée un referentiel de dignites minimal pour les fixtures runtime."""
    return {
        "essential_types": [
            {
                "code": "domicile",
                "label": "Domicile",
                "description": "Planete en domicile.",
                "sort_order": 1,
            },
            {
                "code": "exaltation",
                "label": "Exaltation",
                "description": "Planete en exaltation.",
                "sort_order": 2,
            },
            {
                "code": "detriment",
                "label": "Detriment",
                "description": "Planete en exil.",
                "sort_order": 3,
            },
            {
                "code": "fall",
                "label": "Fall",
                "description": "Planete en chute.",
                "sort_order": 4,
            },
            {
                "code": "triplicity",
                "label": "Triplicity",
                "description": "Planete maitresse de triplicite.",
                "sort_order": 5,
            },
            {
                "code": "term",
                "label": "Term",
                "description": "Planete maitresse de terme.",
                "sort_order": 6,
            },
            {
                "code": "face",
                "label": "Face",
                "description": "Planete maitresse de face.",
                "sort_order": 7,
            },
            {
                "code": "peregrine",
                "label": "Peregrine",
                "description": "Planete sans dignite essentielle positive.",
                "sort_order": 8,
            },
        ],
        "accidental_types": [
            {
                "code": code,
                "label": code.replace("_", " ").title(),
                "description": f"Type accidentel {code}.",
                "sort_order": index,
            }
            for index, code in enumerate(
                (
                    "angular_house",
                    "succedent_house",
                    "cadent_house",
                    "planetary_joy",
                    "direct_motion",
                    "retrograde",
                    "cazimi",
                    "combust",
                    "under_sunbeams",
                    "above_horizon",
                    "below_horizon",
                ),
                start=1,
            )
        ],
        "term_systems": [
            {
                "code": "egyptian",
                "label": "Egyptian",
                "description": "Termes egyptiens.",
                "sort_order": 1,
            }
        ],
        "decan_systems": [
            {
                "code": "chaldean",
                "label": "Chaldean",
                "description": "Decans chaldeens.",
                "sort_order": 1,
            }
        ],
        "score_profiles": [
            {"code": "traditional_standard", "tradition": "traditional", "is_default": True}
        ],
        "essential_weights": {
            "traditional_standard": [
                {
                    "dignity_type_code": "domicile",
                    "score_value": 5,
                    "functional_weight": 1,
                    "expression_weight": 0.7,
                    "intensity_weight": 0.6,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "exaltation",
                    "score_value": 4,
                    "functional_weight": 0.8,
                    "expression_weight": 0.7,
                    "intensity_weight": 0.5,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "detriment",
                    "score_value": -5,
                    "functional_weight": -0.8,
                    "expression_weight": -0.7,
                    "intensity_weight": 0.5,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "fall",
                    "score_value": -4,
                    "functional_weight": -0.7,
                    "expression_weight": -0.6,
                    "intensity_weight": 0.4,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "triplicity",
                    "score_value": 3,
                    "functional_weight": 0.6,
                    "expression_weight": 0.7,
                    "intensity_weight": 0.3,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "term",
                    "score_value": 2,
                    "functional_weight": 0.4,
                    "expression_weight": 0.5,
                    "intensity_weight": 0.2,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "face",
                    "score_value": 1,
                    "functional_weight": 0.2,
                    "expression_weight": 0.4,
                    "intensity_weight": 0.1,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "peregrine",
                    "score_value": -5,
                    "functional_weight": -0.6,
                    "expression_weight": -0.5,
                    "intensity_weight": 0.2,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
            ]
        },
        "accidental_weights": {
            "traditional_standard": [
                {
                    "dignity_type_code": "angular_house",
                    "score_value": 4,
                    "functional_weight": 0.9,
                    "expression_weight": 0.8,
                    "intensity_weight": 0.9,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "succedent_house",
                    "score_value": 2,
                    "functional_weight": 0.5,
                    "expression_weight": 0.5,
                    "intensity_weight": 0.4,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "cadent_house",
                    "score_value": -2,
                    "functional_weight": -0.4,
                    "expression_weight": -0.4,
                    "intensity_weight": -0.2,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "direct_motion",
                    "score_value": 1,
                    "functional_weight": 0.3,
                    "expression_weight": 0.3,
                    "intensity_weight": 0.2,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "retrograde",
                    "score_value": -2,
                    "functional_weight": -0.4,
                    "expression_weight": -0.5,
                    "intensity_weight": 0.5,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "cazimi",
                    "score_value": 5,
                    "functional_weight": 1,
                    "expression_weight": 0.9,
                    "intensity_weight": 1,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "combust",
                    "score_value": -5,
                    "functional_weight": -0.9,
                    "expression_weight": -0.8,
                    "intensity_weight": 0.8,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "under_sunbeams",
                    "score_value": -4,
                    "functional_weight": -0.7,
                    "expression_weight": -0.7,
                    "intensity_weight": 0.5,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                {
                    "dignity_type_code": "planetary_joy",
                    "score_value": 3,
                    "functional_weight": 0.6,
                    "expression_weight": 0.7,
                    "intensity_weight": 0.4,
                    "visibility_weight": 0.0,
                    "stability_weight": 0.0,
                    "coherence_weight": 0.0,
                    "support_weight": 0.0,
                    "constraint_weight": 0.0,
                },
                *[
                    {
                        "dignity_type_code": code,
                        "score_value": score,
                        "functional_weight": functional,
                        "expression_weight": functional,
                        "intensity_weight": 0.1,
                        "visibility_weight": 0.0,
                        "stability_weight": 0.0,
                        "coherence_weight": 0.0,
                        "support_weight": 0.0,
                        "constraint_weight": 0.0,
                    }
                    for code, score, functional in (
                        ("stationary", 2, 0.3),
                        ("swift_motion", 1, 0.2),
                        ("slow_motion", -1, -0.2),
                        ("oriental", 1, 0.1),
                        ("occidental", 1, 0.1),
                        ("in_sect", 1, 0.2),
                        ("out_of_sect", -1, -0.2),
                        ("hayz", 2, 0.4),
                    )
                ],
            ]
        },
        "essential_rules": [
            {
                "planet_code": "sun",
                "sign_code": "leo",
                "dignity_type_code": "domicile",
                "degree_start": 0,
                "degree_end": 30,
                "system_code": "traditional",
            },
            {
                "planet_code": "sun",
                "sign_code": "aries",
                "dignity_type_code": "exaltation",
                "degree_start": 0,
                "degree_end": 30,
                "system_code": "traditional",
            },
            {
                "planet_code": "sun",
                "sign_code": "aquarius",
                "dignity_type_code": "detriment",
                "degree_start": 0,
                "degree_end": 30,
                "system_code": "traditional",
            },
            {
                "planet_code": "sun",
                "sign_code": "libra",
                "dignity_type_code": "fall",
                "degree_start": 0,
                "degree_end": 30,
                "system_code": "traditional",
            },
        ],
        "triplicity_rulers": [
            {
                "element_code": "fire",
                "sect_code": "day",
                "planet_code": "jupiter",
                "role_code": "principal",
                "system_code": "traditional",
            },
            {
                "element_code": "fire",
                "sect_code": "all",
                "planet_code": "saturn",
                "role_code": "participating",
                "system_code": "traditional",
            },
        ],
        "term_bounds": [
            {
                "term_system_code": "egyptian",
                "sign_code": "aries",
                "planet_code": "jupiter",
                "degree_start": 0,
                "degree_end": 6,
                "order_index": 1,
            }
        ],
        "face_decans": [
            {
                "decan_system_code": "chaldean",
                "sign_code": "aries",
                "planet_code": "mars",
                "decan_index": 1,
                "degree_start": 0,
                "degree_end": 10,
            }
        ],
        "accidental_rules": [
            {
                "dignity_type_code": "angular_house",
                "planet_code": None,
                "condition_schema_code": "house_modality",
                "conditions": [{"key": "house_codes", "value": [1, 4, 7, 10]}],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "succedent_house",
                "planet_code": None,
                "condition_schema_code": "house_modality",
                "conditions": [{"key": "house_codes", "value": [2, 5, 8, 11]}],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "cadent_house",
                "planet_code": None,
                "condition_schema_code": "house_modality",
                "conditions": [{"key": "house_codes", "value": [3, 6, 9, 12]}],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "direct_motion",
                "planet_code": None,
                "condition_schema_code": "motion_state",
                "conditions": [{"key": "motion_state_code", "value": "direct"}],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "retrograde",
                "planet_code": None,
                "condition_schema_code": "motion_state",
                "conditions": [{"key": "motion_state_code", "value": "retrograde"}],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "planetary_joy",
                "planet_code": "moon",
                "condition_schema_code": "planetary_joy_house",
                "conditions": [{"key": "house_code", "value": 3}],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "cazimi",
                "planet_code": None,
                "condition_schema_code": "solar_distance",
                "conditions": [
                    {"key": "relative_planet_code", "value": "sun"},
                    {"key": "angular_distance_min_deg", "value": 0},
                    {"key": "angular_distance_max_deg", "value": 0.283},
                ],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "combust",
                "planet_code": None,
                "condition_schema_code": "solar_distance",
                "conditions": [
                    {"key": "relative_planet_code", "value": "sun"},
                    {"key": "angular_distance_min_deg", "value": 0.283},
                    {"key": "angular_distance_max_deg", "value": 8.5},
                ],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "under_sunbeams",
                "planet_code": None,
                "condition_schema_code": "solar_distance",
                "conditions": [
                    {"key": "relative_planet_code", "value": "sun"},
                    {"key": "angular_distance_min_deg", "value": 8.5},
                    {"key": "angular_distance_max_deg", "value": 17},
                ],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "above_horizon",
                "planet_code": None,
                "condition_schema_code": "horizon_position",
                "conditions": [{"key": "house_codes", "value": [7, 8, 9, 10, 11, 12]}],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "below_horizon",
                "planet_code": None,
                "condition_schema_code": "horizon_position",
                "conditions": [{"key": "house_codes", "value": [1, 2, 3, 4, 5, 6]}],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "stationary",
                "planet_code": None,
                "condition_schema_code": "planet_motion_state",
                "conditions": [
                    {"key": "motion_state_code", "value": "stationary"},
                    {"key": "absolute_speed_max_deg_per_day", "value": 0.05},
                ],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "swift_motion",
                "planet_code": None,
                "condition_schema_code": "mean_speed_relation",
                "conditions": [{"key": "speed_relation_code", "value": "greater_than_mean"}],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "slow_motion",
                "planet_code": None,
                "condition_schema_code": "mean_speed_relation",
                "conditions": [{"key": "speed_relation_code", "value": "less_than_mean"}],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "oriental",
                "planet_code": None,
                "condition_schema_code": "heliacal_phase",
                "conditions": [
                    {"key": "relative_planet_code", "value": "sun"},
                    {"key": "heliacal_condition_code", "value": "rising_before_sun"},
                ],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "occidental",
                "planet_code": None,
                "condition_schema_code": "heliacal_phase",
                "conditions": [
                    {"key": "relative_planet_code", "value": "sun"},
                    {"key": "heliacal_condition_code", "value": "setting_after_sun"},
                ],
                "system_code": "traditional",
            },
            {
                "dignity_type_code": "hayz",
                "planet_code": "sun",
                "condition_schema_code": "hayz",
                "conditions": [
                    {"key": "chart_sect_code", "value": "day"},
                    {"key": "horizon_position_code", "value": "above"},
                    {"key": "sign_gender_code", "value": "masculine"},
                ],
                "system_code": "traditional",
            },
        ],
    }


def _default_aspect_orb_rules(payload: Mapping[str, object]) -> tuple[dict[str, object], ...]:
    """Crée des règles d'orbe neutres pour les anciennes fixtures sans table dédiée."""
    aspects = payload.get("aspects")
    if not isinstance(aspects, list):
        return ()

    rules: list[dict[str, object]] = []
    for item in aspects:
        if not isinstance(item, Mapping):
            continue
        code = item.get("code")
        orb = item.get("default_orb_deg")
        if code is None or orb is None:
            continue
        rules.append(
            {
                "aspect_code": str(code),
                "system_code": "modern",
                "calculation_context": "natal",
                "source_body_type": "any",
                "source_planet_code": None,
                "source_point_code": None,
                "target_body_type": "any",
                "target_planet_code": None,
                "target_point_code": None,
                "orb_deg": max(float(orb), 0.1),
                "priority": 1,
                "is_enabled": True,
            }
        )
    return tuple(rules)


def _complete_sign_payload(raw_signs: object) -> list[dict[str, object]]:
    """Complete les anciennes fixtures partielles avec le catalogue zodiacal canonique."""
    existing: dict[str, dict[str, object]] = {}
    if isinstance(raw_signs, list):
        for item in raw_signs:
            if not isinstance(item, Mapping):
                continue
            code = str(item.get("code") or "").strip().lower()
            if code:
                existing[code] = dict(item)

    signs: list[dict[str, object]] = []
    for code in _CANONICAL_SIGN_CODES:
        payload = dict(existing.get(code) or {})
        payload.setdefault("code", code)
        payload.setdefault("name", code.title())
        missing_profile_fields = {
            field_name
            for field_name in ("element", "modality", "polarity")
            if not str(payload.get(field_name) or "").strip()
        }
        if missing_profile_fields:
            raise ValueError(
                f"sign fixture {code} requires profile fields: "
                + ",".join(sorted(missing_profile_fields))
            )
        signs.append(payload)
    return signs


def complete_reference() -> AstrologyRuntimeReference:
    """Retourne une reference minimale complete pour les tests de garde."""
    planets = (
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    )
    return runtime_reference_from_mapping(
        {
            "version": "test",
            "planets": [{"code": code, "name": code.title()} for code in planets],
            "signs": complete_sign_payloads(),
            "houses": [{"number": number, "name": f"House {number}"} for number in range(1, 13)],
            "house_axes": [
                {
                    "house_number": number,
                    "opposite_house": number + 6 if number <= 6 else number - 6,
                    "theme": f"axis_{number}",
                }
                for number in range(1, 13)
            ],
            "astral_systems": [
                {"code": "traditional", "inherits_from_system_code": None},
                {"code": "modern", "inherits_from_system_code": "traditional"},
            ],
            "aspects": [
                {
                    "code": "conjunction",
                    "name": "Conjunction",
                    "angle": 0.0,
                    "family": "major",
                    "is_enabled": True,
                    "is_major": True,
                    "is_minor": False,
                    "default_orb_deg": 8.0,
                    "default_valence": "contextual",
                    "interpretive_valence": "fusion",
                    "energy_type": "fusion",
                }
            ],
            "aspect_orb_rules": [
                {
                    "aspect_code": "conjunction",
                    "system_code": "modern",
                    "calculation_context": "natal",
                    "source_body_type": "any",
                    "source_planet_code": None,
                    "source_point_code": None,
                    "target_body_type": "any",
                    "target_planet_code": None,
                    "target_point_code": None,
                    "orb_deg": 8.0,
                    "priority": 1,
                    "is_enabled": True,
                }
            ],
            "fixed_stars": [
                {
                    "code": "regulus",
                    "display_name": "Regulus",
                    "longitude": 150.0,
                    "reference_system": "tropical_catalog",
                    "source_code": "runtime_reference",
                    "constellation_code": "leo",
                    "magnitude": 1.35,
                    "reference_epoch": "J2000",
                    "categories": ["royal"],
                }
            ],
        }
    )


def complete_reference_with_planet_sect_rules() -> AstrologyRuntimeReference:
    """Retourne une reference complete avec les regles de secte planetaires."""
    reference = complete_reference()
    dignity_reference = reference.dignity_reference
    rules = tuple(
        AccidentalDignityRuleReferenceData(
            dignity_type_code="in_sect",
            planet_code=planet_code,
            condition_schema_code="sect_condition",
            conditions=(DignityConditionValue("chart_sect_code", sect_code),),
            system_code="traditional",
        )
        for planet_code, sect_code in (
            ("sun", "day"),
            ("jupiter", "day"),
            ("saturn", "day"),
            ("moon", "night"),
            ("venus", "night"),
            ("mars", "night"),
            ("mercury", "all"),
        )
    )
    return replace(
        reference,
        dignity_reference=replace(
            dignity_reference,
            accidental_rules=(*dignity_reference.accidental_rules, *rules),
        ),
    )


def missing_planet_definition() -> AstrologyRuntimeReference:
    """Retourne une reference invalide sans planete requise."""
    reference = complete_reference()
    return type(reference)(
        reference_version_id=reference.reference_version_id,
        reference_version=reference.reference_version,
        planets=type(reference.planets)(items=reference.planets.items[1:]),
        planet_natures=reference.planet_natures,
        signs=reference.signs,
        aspects=reference.aspects,
        houses=reference.houses,
        house_axes=reference.house_axes,
        dignities=reference.dignities,
        dignity_reference=reference.dignity_reference,
        condition_signal_profiles=reference.condition_signal_profiles,
        dominance_factor_types=reference.dominance_factor_types,
        dominance_reference=reference.dominance_reference,
        advanced_condition_reference=reference.advanced_condition_reference,
        interpretation_adapter_reference=reference.interpretation_adapter_reference,
        angle_points=reference.angle_points,
        astral_points=reference.astral_points,
        fixed_stars=reference.fixed_stars,
        house_systems=reference.house_systems,
        systems=reference.systems,
    )


def missing_dignity() -> AstrologyRuntimeReference:
    """Retourne une reference complete avec dignites absentes pour tests negatifs."""
    reference = complete_reference()
    return type(reference)(
        reference_version_id=reference.reference_version_id,
        reference_version=reference.reference_version,
        planets=reference.planets,
        planet_natures=reference.planet_natures,
        signs=reference.signs,
        aspects=reference.aspects,
        houses=reference.houses,
        house_axes=reference.house_axes,
        dignities=type(reference.dignities)(items=(), sign_rulerships={}),
        dignity_reference=reference.dignity_reference,
        condition_signal_profiles=reference.condition_signal_profiles,
        dominance_factor_types=reference.dominance_factor_types,
        dominance_reference=reference.dominance_reference,
        advanced_condition_reference=reference.advanced_condition_reference,
        interpretation_adapter_reference=reference.interpretation_adapter_reference,
        angle_points=reference.angle_points,
        astral_points=reference.astral_points,
        fixed_stars=reference.fixed_stars,
        house_systems=reference.house_systems,
        systems=reference.systems,
    )


def invalid_orphan_aspect_rule() -> AstrologyRuntimeReference:
    """Retourne une reference minimale destinee aux tests d'orbe orpheline."""
    reference = complete_reference()
    orphan_rule = type(reference.aspects.orb_rules[0])(
        aspect_code="nonexistent",
        system_code=reference.aspects.orb_rules[0].system_code,
        calculation_context=reference.aspects.orb_rules[0].calculation_context,
        source_body_type=reference.aspects.orb_rules[0].source_body_type,
        source_planet_code=reference.aspects.orb_rules[0].source_planet_code,
        source_point_code=reference.aspects.orb_rules[0].source_point_code,
        target_body_type=reference.aspects.orb_rules[0].target_body_type,
        target_planet_code=reference.aspects.orb_rules[0].target_planet_code,
        target_point_code=reference.aspects.orb_rules[0].target_point_code,
        orb_deg=reference.aspects.orb_rules[0].orb_deg,
        priority=reference.aspects.orb_rules[0].priority,
        is_enabled=reference.aspects.orb_rules[0].is_enabled,
    )
    return type(reference)(
        reference_version_id=reference.reference_version_id,
        reference_version=reference.reference_version,
        planets=reference.planets,
        planet_natures=reference.planet_natures,
        signs=reference.signs,
        aspects=type(reference.aspects)(
            structural_definitions=reference.aspects.structural_definitions,
            interpretive_profiles=reference.aspects.interpretive_profiles,
            orb_rules=(orphan_rule,),
        ),
        houses=reference.houses,
        house_axes=reference.house_axes,
        dignities=reference.dignities,
        dignity_reference=reference.dignity_reference,
        condition_signal_profiles=reference.condition_signal_profiles,
        dominance_factor_types=reference.dominance_factor_types,
        dominance_reference=reference.dominance_reference,
        advanced_condition_reference=reference.advanced_condition_reference,
        interpretation_adapter_reference=reference.interpretation_adapter_reference,
        angle_points=reference.angle_points,
        astral_points=reference.astral_points,
        fixed_stars=reference.fixed_stars,
        house_systems=reference.house_systems,
        systems=reference.systems,
    )


def minimal_valid_natal_reference() -> AstrologyRuntimeReference:
    """Retourne la reference minimale valide pour le calcul natal."""
    return complete_reference()
