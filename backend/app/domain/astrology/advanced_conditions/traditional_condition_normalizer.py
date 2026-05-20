"""Normalisation des contrats traditionnels publics depuis les faits calcules."""

from __future__ import annotations

from typing import Any

from app.domain.astrology.advanced_conditions.contracts import (
    AdvancedPlanetaryCondition,
    HayzCondition,
    RejoicingCondition,
    TraditionalConditionsResult,
    TraditionalPlanetCondition,
)
from app.domain.astrology.advanced_conditions.hayz_calculator import HayzCalculator
from app.domain.astrology.dignities.contracts import PlanetDignityResult
from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference


class TraditionalConditionNormalizer:
    """Construit les contrats hayz et rejoicing sans recalcul doctrinal."""

    def normalize(
        self,
        *,
        dignities: list[PlanetDignityResult] | tuple[PlanetDignityResult, ...],
        planet_positions: list[Any] | tuple[Any, ...],
        advanced_conditions: list[AdvancedPlanetaryCondition]
        | tuple[AdvancedPlanetaryCondition, ...],
        runtime_reference: AstrologyRuntimeReference,
    ) -> TraditionalConditionsResult:
        """Retourne les conditions traditionnelles explicites par planete."""
        position_by_planet = {position.planet_code: position for position in planet_positions}
        advanced_by_planet = {
            (condition.source_planet_code, condition.condition_code): condition
            for condition in advanced_conditions
        }
        planets: list[TraditionalPlanetCondition] = []
        for dignity in dignities:
            sect_condition = dignity.sect_condition
            if sect_condition is None:
                raise ValueError("planet sect condition contract is required")
            planet_code = dignity.planet_code
            hayz_condition = advanced_by_planet.get((planet_code, "hayz"))
            hayz_facts = dict(getattr(hayz_condition, "calculation_facts", {}) or {})
            joy_match = _first_match_by_type(dignity.accidental_breakdown, "planetary_joy")
            rejoicing_house = _joy_house_from_runtime(
                runtime_reference,
                planet_code=planet_code,
                tradition=dignity.tradition,
            )
            position = position_by_planet.get(planet_code)
            if not hayz_facts and position is not None:
                hayz_facts = HayzCalculator().non_sect_hayz_factors(
                    position,
                    dignity,
                    runtime_reference,
                )
            planets.append(
                TraditionalPlanetCondition(
                    planet_code=planet_code,
                    hayz=HayzCondition(
                        is_hayz=hayz_condition is not None,
                        sect_match=bool(sect_condition.is_in_sect),
                        hemisphere_match=_optional_bool(hayz_facts.get("hemisphere_match")),
                        sign_gender_match=_optional_bool(hayz_facts.get("sign_gender_match")),
                        calculation_basis=str(
                            hayz_facts.get(
                                "calculation_basis",
                                "sect_hemisphere_sign_gender",
                            )
                        ),
                        reference_system=str(hayz_facts.get("reference_system", dignity.tradition)),
                        evidence=_hayz_evidence(
                            planet_code,
                            hayz_condition=hayz_condition,
                            hayz_facts=hayz_facts,
                        ),
                    ),
                    rejoicing=RejoicingCondition(
                        is_rejoicing=joy_match is not None,
                        current_house=getattr(position, "house_number", None),
                        rejoicing_house=rejoicing_house
                        if rejoicing_house is not None
                        else _condition_int(joy_match, "house_code"),
                        calculation_basis="planetary_joy_house",
                        reference_system=dignity.tradition,
                        evidence=(
                            (joy_match.reason,)
                            if joy_match is not None and joy_match.reason
                            else ()
                        ),
                    ),
                )
            )
        return TraditionalConditionsResult(planets=tuple(planets))


def _first_match_by_type(matches: Any, dignity_type_code: str) -> Any | None:
    """Retourne le premier match deja calcule pour un type de dignite."""
    if not isinstance(matches, (list, tuple)):
        return None
    for match in matches:
        if getattr(match, "dignity_type_code", None) == dignity_type_code:
            return match
    return None


def _hayz_evidence(
    planet_code: str,
    *,
    hayz_condition: AdvancedPlanetaryCondition | None,
    hayz_facts: dict[str, object],
) -> tuple[str, ...]:
    """Retourne une preuve factuelle courte pour les cas hayz vrais ou faux."""
    if hayz_condition is not None and hayz_condition.reason:
        return (hayz_condition.reason,)
    if not hayz_facts:
        return ()
    return (
        f"{planet_code} hayz factors: "
        f"hemisphere_match={_bool_fact_label(hayz_facts.get('hemisphere_match'))};"
        f"sign_gender_match={_bool_fact_label(hayz_facts.get('sign_gender_match'))}",
    )


def _bool_fact_label(value: object) -> str:
    """Encode un fait booleen optionnel dans l'evidence technique."""
    if isinstance(value, bool):
        return str(value).lower()
    return "unknown"


def _joy_house_from_runtime(
    runtime_reference: AstrologyRuntimeReference,
    *,
    planet_code: str,
    tradition: str,
) -> int | None:
    """Retourne la maison de joie depuis les regles accidentelles runtime."""
    for rule in runtime_reference.dignity_reference.accidental_rules:
        if rule.system_code != tradition:
            continue
        if rule.dignity_type_code != "planetary_joy":
            continue
        if rule.planet_code != planet_code:
            continue
        for condition in rule.conditions:
            if condition.key == "house_code":
                return int(condition.value)
    return None


def _condition_int(match: Any | None, key: str) -> int | None:
    """Extrait une valeur entiere depuis l'etiquette technique d'un match."""
    if match is None:
        return None
    for item in str(getattr(match, "condition", "")).split(";"):
        name, separator, raw_value = item.partition("=")
        if separator and name == key:
            return int(raw_value)
    return None


def _optional_bool(value: object) -> bool | None:
    """Preserve l'absence d'un fait booleen au lieu de fabriquer un faux."""
    return value if isinstance(value, bool) else None
