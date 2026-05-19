"""Factories de tests pour le referentiel runtime astrologique.

Les tests construisent des contrats immutables complets au lieu de faire passer
des dictionnaires metier dans le domaine.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference
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
        }
    )


def missing_planet_definition() -> AstrologyRuntimeReference:
    """Retourne une reference invalide sans planete requise."""
    reference = complete_reference()
    return type(reference)(
        reference_version_id=reference.reference_version_id,
        reference_version=reference.reference_version,
        planets=type(reference.planets)(items=reference.planets.items[1:]),
        signs=reference.signs,
        aspects=reference.aspects,
        houses=reference.houses,
        house_axes=reference.house_axes,
        dignities=reference.dignities,
        dignity_reference=reference.dignity_reference,
        condition_signal_profiles=reference.condition_signal_profiles,
        angle_points=reference.angle_points,
        astral_points=reference.astral_points,
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
        signs=reference.signs,
        aspects=reference.aspects,
        houses=reference.houses,
        house_axes=reference.house_axes,
        dignities=type(reference.dignities)(items=(), sign_rulerships={}),
        dignity_reference=reference.dignity_reference,
        condition_signal_profiles=reference.condition_signal_profiles,
        angle_points=reference.angle_points,
        astral_points=reference.astral_points,
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
        signs=reference.signs,
        aspects=type(reference.aspects)(items=reference.aspects.items, orb_rules=(orphan_rule,)),
        houses=reference.houses,
        house_axes=reference.house_axes,
        dignities=reference.dignities,
        dignity_reference=reference.dignity_reference,
        condition_signal_profiles=reference.condition_signal_profiles,
        angle_points=reference.angle_points,
        astral_points=reference.astral_points,
        house_systems=reference.house_systems,
        systems=reference.systems,
    )


def minimal_valid_natal_reference() -> AstrologyRuntimeReference:
    """Retourne la reference minimale valide pour le calcul natal."""
    return complete_reference()
