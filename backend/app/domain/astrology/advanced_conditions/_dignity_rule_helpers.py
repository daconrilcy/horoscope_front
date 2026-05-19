"""Aides internes pour lire les regles accidentelles runtime."""

from __future__ import annotations

from collections.abc import Iterable

from app.domain.astrology.dignities.contracts import PlanetDignityResult
from app.domain.astrology.runtime.runtime_reference import (
    AccidentalDignityRuleReferenceData,
    AstrologyRuntimeReference,
    DignityConditionValue,
)


def dignity_by_planet(
    dignities: Iterable[PlanetDignityResult],
) -> dict[str, PlanetDignityResult]:
    """Indexe les resultats de dignite par planete."""
    return {item.planet_code: item for item in dignities}


def accidental_matches(
    dignity: PlanetDignityResult | None,
    codes: frozenset[str],
) -> tuple[str, ...]:
    """Retourne les codes accidentels deja detectes pour une planete."""
    if dignity is None:
        return ()
    return tuple(
        match.dignity_type_code
        for match in dignity.accidental_breakdown
        if match.dignity_type_code in codes
    )


def accidental_rules(
    runtime_reference: AstrologyRuntimeReference,
    codes: frozenset[str],
) -> tuple[AccidentalDignityRuleReferenceData, ...]:
    """Filtre les regles accidentelles runtime par type de dignite."""
    return tuple(
        rule
        for rule in runtime_reference.dignity_reference.accidental_rules
        if rule.dignity_type_code in codes
    )


def condition_value(
    rule: AccidentalDignityRuleReferenceData,
    key: str,
) -> str | int | float | tuple[str | int | float, ...] | None:
    """Lit une valeur de condition normalisee par cle."""
    for condition in rule.conditions:
        if isinstance(condition, DignityConditionValue) and condition.key == key:
            return condition.value
    return None
