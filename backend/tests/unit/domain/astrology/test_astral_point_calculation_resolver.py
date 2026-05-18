"""Tests du resolver de calcul des points astraux."""

from __future__ import annotations

from dataclasses import replace

import pytest

from app.domain.astrology.astral_point_calculation_resolver import (
    AstralPointCalculationResolver,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference


def _point(code: str):
    """Retourne un point de fixture par code."""
    return next(point for point in complete_reference().astral_points.items if point.code == code)


def test_resolver_returns_engine_instruction_for_direct_point() -> None:
    """Une variante directe conserve sa clé moteur typée."""
    instruction = AstralPointCalculationResolver().resolve(_point("north_node"))

    assert instruction.point_code == "north_node"
    assert instruction.variant_code == "true"
    assert instruction.engine_key == "SE_TRUE_NODE"
    assert not instruction.is_derived


def test_resolver_returns_derived_instruction_for_opposite_node() -> None:
    """Un point opposé dépend du point source et d'un offset de 180 degrés."""
    instruction = AstralPointCalculationResolver().resolve(_point("south_node"))

    assert instruction.point_code == "south_node"
    assert instruction.derived_from_point_code == "north_node"
    assert instruction.derived_from_variant_code == "true"
    assert instruction.longitude_offset_deg == 180.0


def test_resolver_rejects_unknown_variant() -> None:
    """Aucune variante inconnue ne déclenche un fallback silencieux."""
    with pytest.raises(ValueError, match="unknown astral point variant"):
        AstralPointCalculationResolver().resolve(_point("north_node"), "legacy")


def test_resolver_rejects_direct_variant_without_engine_key() -> None:
    """Une variante directe sans clé DB échoue au lieu d'inférer un fallback local."""
    point = _point("north_node")
    broken_variant = replace(point.variants[0], engine_key=None)
    broken_point = replace(point, variants=(broken_variant,))

    with pytest.raises(ValueError, match="has no engine key"):
        AstralPointCalculationResolver().resolve(broken_point)
