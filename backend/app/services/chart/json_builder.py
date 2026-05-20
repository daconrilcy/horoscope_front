"""Construction du JSON public utilisé pour restituer un thème natal."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from app.domain.astrology.planet_catalog import planet_codes
from app.domain.astrology.zodiac import sign_from_longitude
from app.services.reference_data.astrology_translation_resolver import AstrologyLabels

if TYPE_CHECKING:
    from app.domain.astrology.natal_calculation import NatalResult
    from app.services.user_profile.birth_profile_service import UserBirthProfileData

# Regex for evidence IDs as per Story 29.1 AC4
EVIDENCE_ID_PATTERN = re.compile(r"^[A-Z0-9_\.:-]{3,80}$")
_CATALOG_PLANET_PREFIXES = tuple(f"{code.upper()}_" for code in planet_codes())
_LUMINARY_EVIDENCE_PREFIXES = (*_CATALOG_PLANET_PREFIXES[:2], "ASC_", "MC_", "IC_", "DSC_")


def _longitude_to_sign(longitude: float) -> str:
    """Retourne le signe correspondant à une longitude zodiacale."""
    return sign_from_longitude(longitude)


def _longitude_in_sign(longitude: float) -> float:
    """Retourne la position en degrés à l'intérieur du signe."""
    return round(longitude % 30.0, 2)


def _serialize_house_runtime(house: Any, labels: AstrologyLabels) -> dict[str, Any]:
    """Projette une maison runtime sans calcul astrologique métier."""
    cusp_longitude = float(house.cusp_longitude)
    cusp_sign = getattr(house, "cusp_sign", None)
    if not isinstance(cusp_sign, str):
        cusp_sign = _longitude_to_sign(cusp_longitude)

    contained_signs = getattr(house, "contained_signs", None)
    if not isinstance(contained_signs, list):
        contained_signs = [cusp_sign]

    intercepted_signs = getattr(house, "intercepted_signs", None)
    if not isinstance(intercepted_signs, list):
        intercepted_signs = []

    return {
        "number": house.number,
        "cusp_longitude": round(cusp_longitude, 2),
        "cusp_sign": cusp_sign,
        "cusp_sign_label": labels.sign_label(cusp_sign),
        # TODO legacy compatibility field planned removal: use `cusp_sign`.
        "sign": cusp_sign,
        "contained_signs": contained_signs,
        "intercepted_signs": intercepted_signs,
        "ruler": _serialize_house_ruler(getattr(house, "ruler", None)),
        "occupants": _serialize_house_occupants(getattr(house, "occupants", None)),
        "axis": _serialize_house_axis(getattr(house, "axis", None)),
        "strength": _serialize_house_strength(getattr(house, "strength", None)),
    }


def _serialize_house_ruler(ruler: Any) -> dict[str, Any] | None:
    """Projette le maître runtime déjà résolu de la maison."""
    if ruler is None or not isinstance(getattr(ruler, "planet", None), str):
        return None
    return {
        "planet": ruler.planet,
        "sign": ruler.sign,
        "house": ruler.house,
    }


def serialize_legacy_house_rulers_from_houses(
    houses: list[dict[str, Any]], labels: AstrologyLabels | None = None
) -> list[dict[str, Any]]:
    """Projette le champ historique depuis la maison runtime canonique."""
    labels = labels or AstrologyLabels.technical_fallback()
    house_rulers: list[dict[str, Any]] = []
    for house in houses:
        ruler = house.get("ruler")
        if not isinstance(ruler, dict):
            continue
        planet = ruler.get("planet")
        if not isinstance(planet, str):
            continue
        house_rulers.append(
            {
                "house_number": house["number"],
                "cusp_sign": house["cusp_sign"],
                "cusp_sign_label": labels.sign_label(str(house["cusp_sign"])),
                "ruler_planet": planet,
                "ruler_planet_sign": ruler.get("sign"),
                "ruler_planet_sign_label": labels.sign_label(ruler.get("sign")),
                "ruler_planet_house": ruler.get("house"),
            }
        )
    return house_rulers


def _serialize_house_occupants(occupants: Any) -> list[dict[str, Any]]:
    """Projette les occupants runtime déjà attachés à la maison."""
    if not isinstance(occupants, list):
        return []
    return [
        {
            "planet": occupant.planet,
            "sign": occupant.sign,
            "longitude": round(float(occupant.longitude), 2),
            "is_dominant": bool(occupant.is_dominant),
        }
        for occupant in occupants
    ]


def _serialize_house_axis(axis: Any) -> dict[str, Any] | None:
    """Projette l'axe runtime déjà attaché à la maison."""
    if axis is None or not isinstance(getattr(axis, "theme", None), str):
        return None
    return {
        "opposite_house": axis.opposite_house,
        "theme": axis.theme,
    }


def _serialize_house_strength(strength: Any) -> dict[str, Any] | None:
    """Projette le score normalisee runtime deja calcule de la maison."""
    raw_reasons = getattr(strength, "reasons", None) if strength is not None else None
    if not isinstance(raw_reasons, list | tuple):
        return None
    level = getattr(strength, "level", None)
    if hasattr(level, "value"):
        level = level.value
    if not isinstance(level, str):
        return None
    return {
        "score": strength.score,
        "level": level,
        "dominant": strength.dominant,
        "reasons": [
            reason.value if hasattr(reason, "value") else str(reason) for reason in raw_reasons
        ],
    }


def _serialize_aspect_runtime(aspect: Any) -> dict[str, Any]:
    """Projette un aspect public depuis son runtime canonique si disponible."""
    from app.domain.astrology.builders.aspect_runtime_builder import build_aspect_runtime_data

    orb_value = aspect.orb_used if aspect.orb_used is not None else aspect.orb
    payload = {
        "type": aspect.aspect_code,
        "aspect_code": aspect.aspect_code,
        "planet_a": aspect.planet_a,
        "planet_b": aspect.planet_b,
        "angle": round(float(aspect.angle), 2),
        "orb": round(orb_value, 2) if orb_value is not None else None,
        "orb_used": round(orb_value, 2) if orb_value is not None else None,
        "orb_max": (
            round(float(aspect.orb_max), 2)
            if getattr(aspect, "orb_max", None) is not None
            else None
        ),
        "applying": None,
    }
    runtime = getattr(aspect, "aspect_runtime", None)
    if runtime is None:
        runtime = build_aspect_runtime_data(aspect)
    interpretation = getattr(runtime, "interpretation", None)
    payload.update(
        {
            "family": runtime.aspect.family,
            "strength_level": runtime.strength.level.value,
            "normalized_strength": runtime.strength.normalized_score,
            "phase_type": runtime.phase.type if runtime.phase is not None else None,
            "interpretive_valence": (
                interpretation.interpretive_valence if interpretation is not None else None
            ),
            "energy_type": interpretation.energy_type if interpretation is not None else None,
            "is_exact": runtime.metadata.is_exact,
            "is_tight": runtime.metadata.is_tight,
        }
    )
    return payload


def _serialize_chart_balance(balance: Any) -> dict[str, Any] | None:
    """Projette une signature deja calculee sans recalculer les scores."""
    if balance is None:
        return None
    synthesis = getattr(balance, "synthesis", None)
    return {
        "version": balance.version,
        "elements": [_serialize_rank(item) for item in balance.elements],
        "modalities": [_serialize_rank(item) for item in balance.modalities],
        "dominant_signs": [_serialize_dominance(item) for item in balance.dominant_signs],
        "dominant_planets": [_serialize_dominance(item) for item in balance.dominant_planets],
        "dominant_houses": [_serialize_dominance(item) for item in balance.dominant_houses],
        "dominant_aspects": [_serialize_dominance(item) for item in balance.dominant_aspects],
        "chart_signature": (
            {
                "primary_element": synthesis.primary_element,
                "primary_modality": synthesis.primary_modality,
                "primary_sign": synthesis.primary_sign,
                "primary_planet": synthesis.primary_planet,
                "primary_house": synthesis.primary_house,
            }
            if synthesis is not None
            else None
        ),
    }


def _serialize_rank(item: Any) -> dict[str, Any]:
    """Projette un score classe deja normalise."""
    return {"code": item.code, "score": item.score, "rank": item.rank}


def _serialize_dominance(item: Any) -> dict[str, Any]:
    """Projette une dominance classee deja sourcee."""
    payload = _serialize_rank(item)
    payload["source"] = item.source
    return payload


def _serialize_dignity_match(match: Any) -> dict[str, Any]:
    """Projette un match de dignite factuel."""
    payload = {
        "type": match.dignity_type_code,
        "score": match.score_value,
        "source": match.source,
        "reason": match.reason,
    }
    if hasattr(match, "sign_code"):
        payload["sign"] = match.sign_code
        payload["degree_start"] = match.degree_start
        payload["degree_end"] = match.degree_end
    if hasattr(match, "condition"):
        payload["condition"] = match.condition
    return payload


def _serialize_chart_sect(chart_sect: Any) -> dict[str, Any] | None:
    """Projette le contrat de secte deja calcule au niveau du theme."""
    required_fields = (
        "chart_sect",
        "sun_horizon_position",
        "sun_above_horizon",
        "calculation_basis",
        "reference_system",
    )
    if chart_sect is None:
        return None
    if any(not hasattr(chart_sect, field) for field in required_fields):
        raise ValueError("dignity sect contract is incomplete")
    chart_sect_value = getattr(chart_sect, "chart_sect")
    horizon_position = getattr(chart_sect, "sun_horizon_position")
    sun_above_horizon = getattr(chart_sect, "sun_above_horizon")
    calculation_basis = getattr(chart_sect, "calculation_basis")
    reference_system = getattr(chart_sect, "reference_system")
    if chart_sect_value not in {"day", "night"}:
        raise ValueError("dignity sect chart_sect is invalid")
    if horizon_position not in {"above_horizon", "below_horizon"}:
        raise ValueError("dignity sect sun_horizon_position is invalid")
    if not isinstance(sun_above_horizon, bool):
        raise ValueError("dignity sect sun_above_horizon is invalid")
    if not isinstance(calculation_basis, str) or not calculation_basis.strip():
        raise ValueError("dignity sect calculation_basis is required")
    if not isinstance(reference_system, str) or not reference_system.strip():
        raise ValueError("dignity sect reference_system is required")
    if (chart_sect_value == "day") != sun_above_horizon:
        raise ValueError("dignity sect sun_above_horizon is inconsistent")
    expected_horizon = "above_horizon" if chart_sect_value == "day" else "below_horizon"
    if horizon_position != expected_horizon:
        raise ValueError("dignity sect sun_horizon_position is inconsistent")
    return {
        "chart_sect": chart_sect_value,
        "sun_horizon_position": horizon_position,
        "sun_above_horizon": sun_above_horizon,
        "calculation_basis": calculation_basis,
        "reference_system": reference_system,
    }


def _serialize_planet_sect_condition(sect_condition: Any) -> dict[str, Any]:
    """Projette la condition de secte planetaire deja calculee."""
    required_fields = (
        "planet_code",
        "chart_sect",
        "intrinsic_sect",
        "planet_sect_condition",
        "is_in_sect",
        "is_out_of_sect",
        "calculation_basis",
        "reference_system",
    )
    if sect_condition is None or any(
        not hasattr(sect_condition, field) for field in required_fields
    ):
        raise ValueError("planet sect condition contract is incomplete")
    payload = {field: getattr(sect_condition, field) for field in required_fields}
    if payload["chart_sect"] not in {"day", "night"}:
        raise ValueError("planet sect condition chart_sect is invalid")
    if payload["intrinsic_sect"] not in {
        "diurnal",
        "nocturnal",
        "common",
        "neutral",
        "unknown",
    }:
        raise ValueError("planet sect condition intrinsic_sect is invalid")
    if payload["planet_sect_condition"] not in {
        "in_sect",
        "out_of_sect",
        "neutral_to_sect",
        "variable_by_condition",
        "unknown",
    }:
        raise ValueError("planet sect condition value is invalid")
    if not isinstance(payload["is_in_sect"], bool) or not isinstance(
        payload["is_out_of_sect"], bool
    ):
        raise ValueError("planet sect condition booleans are invalid")
    if payload["is_in_sect"] and payload["is_out_of_sect"]:
        raise ValueError("planet sect condition booleans are inconsistent")
    expected_booleans = {
        "in_sect": (True, False),
        "out_of_sect": (False, True),
        "neutral_to_sect": (False, False),
        "variable_by_condition": (False, False),
        "unknown": (False, False),
    }[payload["planet_sect_condition"]]
    if (payload["is_in_sect"], payload["is_out_of_sect"]) != expected_booleans:
        raise ValueError("planet sect condition flags are inconsistent")
    if (
        not isinstance(payload["calculation_basis"], str)
        or not payload["calculation_basis"].strip()
    ):
        raise ValueError("planet sect condition calculation_basis is required")
    if not isinstance(payload["reference_system"], str) or not payload["reference_system"].strip():
        raise ValueError("planet sect condition reference_system is required")
    return payload


def _serialize_dignities(dignities: Any, chart_sect: Any = None) -> dict[str, Any]:
    """Projette les resultats de dignites par code planete."""
    planets: dict[str, Any] = {}
    score_profile = ""
    tradition = ""
    reference_version = ""
    sect = _serialize_chart_sect(chart_sect)
    if not isinstance(dignities, (list, tuple)):
        dignities = []
    for result in dignities:
        score_profile = result.score_profile
        tradition = result.tradition
        reference_version = result.reference_version
        if sect is None:
            sect = _serialize_chart_sect(getattr(result, "chart_sect", None))
        if sect is None:
            raise ValueError("dignity sect contract is required")
        planets[result.planet_code] = {
            "sect_condition": _serialize_planet_sect_condition(
                getattr(result, "sect_condition", None)
            ),
            "essential_score": result.essential_score,
            "accidental_score": result.accidental_score,
            "total_score": result.total_score,
            "functional_strength_score": result.functional_strength_score,
            "expression_quality_score": result.expression_quality_score,
            "intensity_score": result.intensity_score,
            "essential_breakdown": [
                _serialize_dignity_match(match) for match in result.essential_breakdown
            ],
            "accidental_breakdown": [
                _serialize_dignity_match(match) for match in result.accidental_breakdown
            ],
        }
    return {
        "score_profile": score_profile,
        "tradition": tradition,
        "reference_version": reference_version,
        "sect": sect,
        "planets": planets,
    }


def _serialize_condition_profiles(profiles: Any) -> dict[str, Any]:
    """Projette les profils conditionnels deja calcules par le domaine."""
    planets: dict[str, Any] = {}
    score_profile = ""
    tradition = ""
    reference_version = ""
    sect = ""
    if not isinstance(profiles, (list, tuple)):
        profiles = []
    for profile in profiles:
        score_profile = profile.score_profile
        tradition = profile.tradition
        reference_version = profile.reference_version
        sect = profile.sect
        planets[profile.planet_code] = {
            "planet_code": profile.planet_code,
            "score_profile": profile.score_profile,
            "tradition": profile.tradition,
            "reference_version": profile.reference_version,
            "sect": profile.sect,
            "functional_strength": profile.functional_strength,
            "visibility": profile.visibility,
            "stability": profile.stability,
            "intensity": profile.intensity,
            "coherence": profile.coherence,
            "support": profile.support,
            "constraint": profile.constraint,
            "ranking_score": profile.ranking_score,
            "condition_level": profile.condition_level,
            "breakdown": [
                {
                    "dignity_family": item.dignity_family,
                    "dignity_type_code": item.dignity_type_code,
                    "source": item.source,
                    "reason": item.reason,
                    "score_value": item.score_value,
                    "functional_strength": item.functional_strength,
                    "visibility": item.visibility,
                    "stability": item.stability,
                    "intensity": item.intensity,
                    "coherence": item.coherence,
                    "support": item.support,
                    "constraint": item.constraint,
                }
                for item in profile.breakdown
            ],
            "explanation_facts": [
                {"fact_type": fact.fact_type, "value": fact.value}
                for fact in profile.explanation_facts
            ],
        }
    return {
        "score_profile": score_profile,
        "tradition": tradition,
        "reference_version": reference_version,
        "sect": sect,
        "planets": planets,
    }


def _serialize_condition_signals(signal_sets: Any) -> dict[str, Any]:
    """Projette les signaux conditionnels deja calcules par le domaine."""
    planets: dict[str, Any] = {}
    score_profile = ""
    tradition = ""
    reference_version = ""
    if not isinstance(signal_sets, (list, tuple)):
        signal_sets = []
    for signal_set in signal_sets:
        score_profile = signal_set.score_profile
        tradition = signal_set.tradition
        reference_version = signal_set.reference_version
        planets[signal_set.planet_code] = {
            "planet_code": signal_set.planet_code,
            "score_profile": signal_set.score_profile,
            "tradition": signal_set.tradition,
            "reference_version": signal_set.reference_version,
            "signals": [
                {
                    "code": signal.code,
                    "label": signal.label,
                    "axis": signal.axis,
                    "level": signal.level,
                    "level_min": signal.level_min,
                    "level_max": signal.level_max,
                    "axis_value": signal.axis_value,
                    "interpretation_use": signal.interpretation_use,
                    "priority_weight": signal.priority_weight,
                    "prompt_hint": signal.prompt_hint,
                }
                for signal in signal_set.signals
            ],
        }
    return {
        "score_profile": score_profile,
        "tradition": tradition,
        "reference_version": reference_version,
        "planets": planets,
    }


def _serialize_dominant_planets(dominant_planets: Any) -> dict[str, Any] | None:
    """Projette les planetes dominantes deja calculees par le domaine."""
    if dominant_planets is None:
        return None
    return {
        "score_profile": dominant_planets.score_profile_code,
        "tradition": dominant_planets.tradition_code,
        "reference_version": dominant_planets.reference_version_code,
        "chart_ruler": dominant_planets.chart_ruler_code,
        "most_elevated_planet": dominant_planets.most_elevated_planet_code,
        "top_planet": dominant_planets.top_planet_code,
        "planets": [
            {
                "planet": planet.planet_code,
                "rank": planet.rank,
                "total_score": planet.total_score,
                "dominance_level": planet.dominance_level,
                "factors": [
                    {
                        "factor": factor.factor_code,
                        "raw_value": factor.raw_value,
                        "normalized_value": factor.normalized_value,
                        "weight": factor.weight,
                        "weighted_score": factor.weighted_score,
                        "reason": factor.reason,
                    }
                    for factor in planet.factors
                ],
                "explanation_facts": list(planet.explanation_facts),
            }
            for planet in dominant_planets.planets
        ],
    }


def _serialize_advanced_conditions(advanced_conditions: Any) -> list[dict[str, Any]]:
    """Projette les conditions avancees deja calculees par le domaine."""
    if not isinstance(advanced_conditions, (list, tuple)):
        advanced_conditions = []
    return [
        {
            "condition_code": condition.condition_code,
            "condition_type_code": condition.condition_type_code,
            "source_planet_code": condition.source_planet_code,
            "target_planet_code": condition.target_planet_code,
            "score_profile": condition.score_profile,
            "reference_version": condition.reference_version,
            "score_impact": condition.score_impact,
            "ranking_weight": condition.ranking_weight,
            "axes_impact": {
                "functional_strength": condition.axes_impact.functional_strength_delta,
                "visibility": condition.axes_impact.visibility_delta,
                "stability": condition.axes_impact.stability_delta,
                "intensity": condition.axes_impact.intensity_delta,
                "coherence": condition.axes_impact.coherence_delta,
                "support": condition.axes_impact.support_delta,
                "constraint": condition.axes_impact.constraint_delta,
            },
            "reason": condition.reason,
        }
        for condition in advanced_conditions
    ]


def _serialize_interpretation_adapter(adapter: Any) -> dict[str, Any] | None:
    """Projette le resultat d'adaptation deja calcule par le domaine."""
    if adapter is None:
        return None
    return {
        "signals": [
            {
                "signal": signal.signal_code,
                "theme": signal.theme_code,
                "source_type": signal.source_type,
                "source_code": signal.source_code,
                "priority": signal.priority,
                "priority_rank": signal.priority_rank,
                "weight": signal.weight,
                "semantic_category": signal.semantic_category,
                "theme_category": signal.theme_category,
                "explanation_fact": signal.explanation_fact,
            }
            for signal in adapter.signals
        ],
        "activated_themes": [
            {
                "theme": theme.theme_code,
                "theme_category": theme.theme_category,
                "activation_score": theme.activation_score,
                "priority": theme.priority,
                "priority_rank": theme.priority_rank,
                "contributing_signals": list(theme.contributing_signals),
            }
            for theme in adapter.activated_themes
        ],
        "dominant_topics": list(adapter.dominant_topics),
        "dominant_axes": list(adapter.dominant_axes),
        "tension_patterns": list(adapter.tension_patterns),
        "support_patterns": list(adapter.support_patterns),
        "critical_patterns": list(adapter.critical_patterns),
        "narrative_priorities": list(adapter.narrative_priorities),
    }


def build_chart_json(
    natal_result: NatalResult,
    birth_profile: UserBirthProfileData,
    degraded_mode: str | None = None,
    labels: AstrologyLabels | None = None,
) -> dict[str, Any]:
    """
    Construit le payload public canonique du thème natal.

    Le payload regroupe les placements nécessaires aux restitutions publiques,
    dont les maisons, les planètes et les maîtres de maisons.
    """
    labels = labels or AstrologyLabels.technical_fallback()
    # Auto-derive degraded_mode if not provided
    if degraded_mode is None:
        no_time = birth_profile.birth_time is None
        no_location = birth_profile.birth_lat is None or birth_profile.birth_lon is None
        if no_time and no_location:
            degraded_mode = "no_location_no_time"
        elif no_time:
            degraded_mode = "no_time"
        elif no_location:
            degraded_mode = "no_location"

    is_no_time = degraded_mode in {"no_time", "no_location_no_time"}
    is_no_location = degraded_mode in {"no_location", "no_location_no_time"}

    # Meta information
    birth_timezone = birth_profile.birth_timezone
    if hasattr(natal_result, "prepared_input"):
        birth_timezone = natal_result.prepared_input.birth_timezone

    zodiac = str(natal_result.zodiac)
    if hasattr(natal_result.zodiac, "value"):
        zodiac = str(natal_result.zodiac.value)

    house_system = str(natal_result.house_system)
    if hasattr(natal_result.house_system, "value"):
        house_system = str(natal_result.house_system.value)

    meta = {
        "birth_date": birth_profile.birth_date,
        "birth_time": None if is_no_time else birth_profile.birth_time,
        "birth_place": None if is_no_location else birth_profile.birth_place,
        "birth_timezone": birth_timezone,
        "degraded_mode": degraded_mode,
        "engine": natal_result.engine,
        "zodiac": zodiac,
        "house_system": house_system,
        "reference_version": natal_result.reference_version,
        "ruleset_version": natal_result.ruleset_version,
        "chart_json_version": "1",
        "aspects_applying_available": False,
    }

    # Planets
    planets = []
    for p in natal_result.planet_positions:
        planets.append(
            {
                "code": p.planet_code,
                "sign": p.sign_code,
                "sign_label": labels.sign_label(p.sign_code),
                "longitude": round(p.longitude, 2),
                "longitude_in_sign": _longitude_in_sign(p.longitude),
                "house": None if is_no_time else p.house_number,
                "is_retrograde": p.is_retrograde,
                "speed": round(p.speed_longitude, 2) if p.speed_longitude is not None else None,
            }
        )

    # Houses
    houses = []
    if not is_no_time:
        for h in natal_result.houses:
            houses.append(_serialize_house_runtime(h, labels))

    # Maîtres de maisons
    house_rulers = [] if is_no_time else serialize_legacy_house_rulers_from_houses(houses, labels)

    # Aspects
    aspects = []
    for a in natal_result.aspects:
        # Filter for major aspects only as per Epic 29 requirements.
        # Minor aspects are currently calculated by the engine
        # but not supported by the JSON contract.
        if a.is_major:
            aspects.append(_serialize_aspect_runtime(a))

    # Angles
    angles = {
        "ASC": None,
        "MC": None,
        "DSC": None,
        "IC": None,
    }

    if not (is_no_time or is_no_location):
        house_dict = {h.number: h for h in natal_result.houses}
        map_angles = {"ASC": 1, "MC": 10, "DSC": 7, "IC": 4}
        for angle_key, house_num in map_angles.items():
            h = house_dict.get(house_num)
            if h:
                angles[angle_key] = {
                    "longitude": round(h.cusp_longitude, 2),
                    "sign": _longitude_to_sign(h.cusp_longitude),
                }
                angles[angle_key]["sign_label"] = labels.sign_label(angles[angle_key]["sign"])

    chart_balance = _serialize_chart_balance(getattr(natal_result, "chart_balance", None))
    dominant_planets = None
    if not is_no_time:
        dominant_planets = _serialize_dominant_planets(
            getattr(natal_result, "dominant_planets", None)
        )
    payload = {
        "meta": meta,
        "planets": planets,
        "houses": houses,
        "house_rulers": house_rulers,
        "aspects": aspects,
        "angles": angles,
        "dignities": _serialize_dignities(
            getattr(natal_result, "dignities", []),
            getattr(natal_result, "dignity_sect", None),
        ),
        "planet_condition_profiles": _serialize_condition_profiles(
            getattr(natal_result, "condition_profiles", [])
        ),
        "planet_condition_signals": _serialize_condition_signals(
            getattr(natal_result, "condition_signals", [])
        ),
        "advanced_conditions": _serialize_advanced_conditions(
            getattr(natal_result, "advanced_conditions", [])
        ),
        "dominant_planets": dominant_planets,
        "interpretation_adapter": (
            None
            if is_no_time
            else _serialize_interpretation_adapter(
                getattr(natal_result, "interpretation_adapter", None)
            )
        ),
    }
    if chart_balance is not None:
        payload["chart_balance"] = chart_balance
        payload["chart_signature"] = chart_balance["chart_signature"]
    return payload


def _get_evidence_priority(eid: str) -> int:
    """Détermine la priorité de tri des identifiants d'évidence."""
    # Priority 0: Luminaries and Angles
    if any(eid.startswith(p) for p in _LUMINARY_EVIDENCE_PREFIXES):
        return 0
    # Priority 1: Positions (Signs, Houses, Retrograde)
    planets = [
        *_CATALOG_PLANET_PREFIXES[2:],
        "CHIRON_",
        "LILITH_",
        "NODE_",
    ]
    if any(eid.startswith(p) for p in planets):
        return 1
    # Priority 2: Aspects
    if eid.startswith("ASPECT_"):
        return 2
    # Priority 3: Others (House cusps in signs, etc.)
    return 3


def build_evidence_catalog(chart_json: dict[str, Any]) -> list[str]:
    """Retourne la liste triée des identifiants d'évidence historiques."""
    enriched = build_enriched_evidence_catalog(chart_json)
    return sorted(list(enriched.keys()), key=lambda x: (_get_evidence_priority(x), x))


def build_enriched_evidence_catalog(
    chart_json: dict[str, Any],
    labels: AstrologyLabels | None = None,
) -> dict[str, list[str]]:
    r"""
    Produit les libellés autorisés pour chaque identifiant d'évidence.

    Ce catalogue sert à valider les références entre le JSON technique et le
    texte généré par les restitutions natales.
    """
    labels = labels or AstrologyLabels.technical_fallback()
    # Map of ID -> list of labels
    catalog: dict[str, list[str]] = {}

    def add(eid: str, labels: list[str]):
        clean_id = eid.replace(" ", "_").upper()
        if EVIDENCE_ID_PATTERN.match(clean_id):
            if clean_id not in catalog:
                catalog[clean_id] = []
            for label in labels:
                if label and label not in catalog[clean_id]:
                    catalog[clean_id].append(label)

    # 1. Planets
    for p in chart_json.get("planets", []):
        p_code = p["code"]
        s_code = p["sign"]
        p_name = labels.planet_label(p_code)
        s_name = p.get("sign_label") or s_code

        # PLANET_SIGN
        add(
            f"{p_code.upper()}_{s_code.upper()}",
            [f"{p_name} en {s_name}", f"{p_name} en signe du {s_name}"],
        )  # noqa: E501

        # PLANET_H{house}
        house = p.get("house")
        if house is not None:
            add(f"{p_code.upper()}_H{house}", [f"{p_name} en Maison {house}"])
            add(
                f"{p_code.upper()}_{s_code.upper()}_H{house}",
                [f"{p_name} en {s_name} en Maison {house}"],
            )

        if p.get("is_retrograde"):
            add(f"{p_code.upper()}_RETROGRADE", [f"{p_name} rétrograde"])

    # 2. Aspects
    for a in chart_json.get("aspects", []):
        p1 = a["planet_a"]
        p2 = a["planet_b"]
        asp_type = a["type"]
        p1_name = labels.planet_label(p1)
        p2_name = labels.planet_label(p2)
        asp_name = labels.aspect_label(asp_type)

        pair = sorted([p1.upper(), p2.upper()])
        base_id = f"ASPECT_{pair[0]}_{pair[1]}_{asp_type.upper()}"

        aspect_labels = [
            f"{asp_name} entre {p1_name} et {p2_name}",
            f"{p1_name} {asp_name} {p2_name}",
        ]
        add(base_id, aspect_labels)

        orb = a.get("orb")
        if orb is not None:
            orb_int = int(round(orb))
            add(f"{base_id}_ORB{orb_int}", aspect_labels)

    # 3. Angles
    angles = chart_json.get("angles", {})
    angle_names = {
        "ASC": "Ascendant",
        "MC": "Milieu du Ciel",
        "DSC": "Descendant",
        "IC": "Fond du Ciel",
    }  # noqa: E501
    if angles:
        for angle_key, data in angles.items():
            if data and data.get("sign"):
                s_code = data["sign"]
                s_name = data.get("sign_label") or s_code
                a_name = angle_names.get(angle_key, angle_key)
                add(f"{angle_key}_{s_code.upper()}", [f"{a_name} en {s_name}"])

    # 4. Houses
    for h in chart_json.get("houses", []):
        num = h["number"]
        s_code = h.get("cusp_sign") or h["sign"]
        s_name = h.get("cusp_sign_label") or s_code
        add(f"HOUSE_{num}_IN_{s_code.upper()}", [f"Maison {num} en {s_name}"])

    # 5. House rulers
    for ruler in chart_json.get("house_rulers", []):
        house_num = ruler["house_number"]
        planet_code = ruler["ruler_planet"]
        planet_name = labels.planet_label(planet_code)
        base_labels = [f"Maître de Maison {house_num} : {planet_name}"]
        add(f"HOUSE_{house_num}_RULER_{planet_code.upper()}", base_labels)

        ruler_house = ruler.get("ruler_planet_house")
        if ruler_house is not None:
            add(
                f"HOUSE_{house_num}_RULER_{planet_code.upper()}_H{ruler_house}",
                [*base_labels, f"Maître de Maison {house_num} en Maison {ruler_house}"],
            )

        ruler_sign = ruler.get("ruler_planet_sign")
        if ruler_sign:
            sign_name = ruler.get("ruler_planet_sign_label") or str(ruler_sign)
            add(
                f"HOUSE_{house_num}_RULER_{planet_code.upper()}_{str(ruler_sign).upper()}",
                [*base_labels, f"Maître de Maison {house_num} en {sign_name}"],
            )

    return catalog
