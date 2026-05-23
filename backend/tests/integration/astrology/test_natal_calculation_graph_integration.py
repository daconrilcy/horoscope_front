# Tests d'integration du graphe natal CS-228.
"""Valide que le theme natal complet reste compatible apres migration graphe."""

from __future__ import annotations

from app.domain.astrology.natal_calculation import NatalResult, build_natal_result
from app.domain.astrology.natal_preparation import BirthInput
from tests.factories.astrology_runtime_reference_factory import complete_reference


def test_build_natal_result_returns_complete_natal_result_from_graph() -> None:
    """Le graphe produit les surfaces runtime et projections historiques attendues."""
    result = build_natal_result(
        birth_input=BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        ),
        runtime_reference=complete_reference(),
        ruleset_version="test",
        house_system="equal",
    )

    assert isinstance(result, NatalResult)
    assert result.chart_objects
    assert result.houses
    assert result.aspects
    assert result.planet_positions
    assert result.dignities
    assert result.dominant_planets is not None
    assert result.chart_balance is not None
