# Tests d'architecture ciblant les contrats structurels d'aspects.
"""Verifie l'absence d'aliases interpretatifs dans les surfaces structurelles."""

from __future__ import annotations

from dataclasses import fields

from app.domain.astrology.runtime.aspect_calculation_contracts import (
    AspectCalculationResult,
    AspectStructuralDefinitionRuntimeData,
)
from app.domain.astrology.runtime.aspect_modifiers import (
    AspectModifierRuntimeData,
    AspectStructuralModifierRuntimeData,
)
from app.domain.astrology.runtime.aspect_runtime_data import (
    AspectRuntimeData,
    AspectStructuralRuntimeData,
)

FORBIDDEN_STRUCTURAL_FIELDS = frozenset(
    {
        "default_valence",
        "interpretive_valence",
        "energy_type",
        "interpretive_weight",
        "interpretation",
    }
)


def test_aspect_runtime_facades_do_not_expose_interpretive_aliases() -> None:
    """AST guard: les facades structurelles ne portent plus d'alias legacy."""
    for contract in (AspectRuntimeData, AspectStructuralRuntimeData):
        contract_fields = {field.name for field in fields(contract)}

        assert contract_fields.isdisjoint(FORBIDDEN_STRUCTURAL_FIELDS)


def test_aspect_calculation_result_stays_structural() -> None:
    """Le resultat de calcul d'aspect reste limite aux faits geometriques."""
    result_fields = {field.name for field in fields(AspectCalculationResult)}

    assert result_fields == {
        "aspect_code",
        "planet_a",
        "planet_b",
        "angle",
        "orb",
        "orb_used",
        "orb_max",
        "family",
        "is_major",
        "is_minor",
        "chart_a",
        "chart_b",
    }
    assert result_fields.isdisjoint(FORBIDDEN_STRUCTURAL_FIELDS)


def test_structural_definition_does_not_require_interpretive_profile_fields() -> None:
    """La definition structurelle reste separee du profil interpretatif."""
    definition_fields = {field.name for field in fields(AspectStructuralDefinitionRuntimeData)}

    assert definition_fields.isdisjoint(FORBIDDEN_STRUCTURAL_FIELDS)


def test_aspect_modifiers_do_not_carry_interpretive_weight() -> None:
    """Les modifiers structurels restent separes des poids interpretatifs."""
    for contract in (AspectModifierRuntimeData, AspectStructuralModifierRuntimeData):
        modifier_fields = {field.name for field in fields(contract)}

        assert modifier_fields.isdisjoint(FORBIDDEN_STRUCTURAL_FIELDS)
