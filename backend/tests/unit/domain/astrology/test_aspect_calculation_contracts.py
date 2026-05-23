"""Tests des contrats de calcul structurel des aspects CS-230."""

from __future__ import annotations

from dataclasses import fields

from app.domain.astrology.runtime.aspect_calculation_contracts import AspectCalculationResult


def test_aspect_calculation_result_excludes_interpretive_fields() -> None:
    """Le resultat de calcul d'aspect ne porte plus de champs interpretatifs."""
    field_names = {field.name for field in fields(AspectCalculationResult)}

    assert field_names.isdisjoint(
        {
            "default_valence",
            "interpretive_valence",
            "energy_type",
            "interpretive_weight",
        }
    )


def test_aspect_calculation_result_serializes_structural_payload_only() -> None:
    """La projection du resultat de calcul reste limitee aux faits structurels."""
    payload = AspectCalculationResult(
        aspect_code="trine",
        planet_a="moon",
        planet_b="sun",
        angle=120.0,
        orb=0.2,
        orb_used=0.2,
        orb_max=6.0,
        family="major",
        is_major=True,
        is_minor=False,
    ).as_dict()

    assert payload == {
        "aspect_code": "trine",
        "planet_a": "moon",
        "planet_b": "sun",
        "angle": 120.0,
        "orb": 0.2,
        "orb_used": 0.2,
        "orb_max": 6.0,
        "family": "major",
        "is_major": True,
        "is_minor": False,
    }
