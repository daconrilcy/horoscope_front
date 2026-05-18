"""Tests du resolver de calcul des points astraux."""

from __future__ import annotations

from dataclasses import replace

import pytest

from app.domain.astrology.astral_point_calculation_resolver import (
    AstralPointCalculationResolver,
)
from app.domain.astrology.runtime.runtime_reference import (
    AstralPointRuntime,
    AstralPointVariantRuntime,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference


def _point(code: str):
    """Retourne un point de fixture par code."""
    return next(point for point in complete_reference().astral_points.items if point.code == code)


def _runtime_point(
    *,
    code: str,
    variant_code: str,
    calculation_mode: str,
    engine_key: str | None = None,
) -> AstralPointRuntime:
    """Construit un point runtime minimal pour les variantes hors fixture globale."""
    return AstralPointRuntime(
        code=code,
        display_name=code,
        family_code="test",
        astronomical_type="test",
        is_physical_body=False,
        default_variant_code=variant_code,
        variants=(
            AstralPointVariantRuntime(
                variant_code=variant_code,
                display_name=variant_code,
                calculation_mode=calculation_mode,
                engine_key=engine_key,
                is_default=True,
            ),
        ),
        aliases=(),
    )


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


def test_resolver_returns_derived_instruction_for_lunar_perigee() -> None:
    """Le périgée lunaire dépend de l'apogée lunaire et d'un offset de 180 degrés."""
    point = _runtime_point(
        code="lunar_perigee",
        variant_code="mean",
        calculation_mode="mean_perigee",
    )

    instruction = AstralPointCalculationResolver().resolve(point)

    assert instruction.point_code == "lunar_perigee"
    assert instruction.derived_from_point_code == "lunar_apogee"
    assert instruction.derived_from_variant_code == "mean"
    assert instruction.longitude_offset_deg == 180.0


@pytest.mark.parametrize(
    ("point_code", "variant_code", "calculation_mode", "engine_key"),
    (
        ("north_node", "mean", "mean", "SE_MEAN_NODE"),
        ("north_node", "true", "true", "SE_TRUE_NODE"),
        ("lunar_apogee", "mean", "mean_apogee", "SE_MEAN_APOG"),
        ("lunar_apogee", "true", "osculating_apogee", "SE_OSCU_APOG"),
        ("black_moon_lilith", "mean", "mean_apogee", "SE_MEAN_APOG"),
        ("black_moon_lilith", "true", "osculating_apogee", "SE_OSCU_APOG"),
    ),
)
def test_resolver_maps_direct_variants_to_expected_engine_sources(
    point_code: str,
    variant_code: str,
    calculation_mode: str,
    engine_key: str,
) -> None:
    """Les variantes directes restent branchées sur la source SwissEph attendue."""
    instruction = AstralPointCalculationResolver().resolve(
        _runtime_point(
            code=point_code,
            variant_code=variant_code,
            calculation_mode=calculation_mode,
            engine_key=engine_key,
        )
    )

    assert instruction.point_code == point_code
    assert instruction.variant_code == variant_code
    assert instruction.engine_key == engine_key
    assert instruction.calculation_mode == calculation_mode
    assert not instruction.is_derived


@pytest.mark.parametrize(
    ("point_code", "variant_code", "calculation_mode", "source_code", "source_variant"),
    (
        ("south_node", "mean", "mean_opposition", "north_node", "mean"),
        ("south_node", "true", "true_opposition", "north_node", "true"),
        ("lunar_perigee", "mean", "mean_perigee", "lunar_apogee", "mean"),
        ("lunar_perigee", "true", "osculating_perigee", "lunar_apogee", "true"),
    ),
)
def test_resolver_maps_derived_variants_to_expected_oppositions(
    point_code: str,
    variant_code: str,
    calculation_mode: str,
    source_code: str,
    source_variant: str,
) -> None:
    """Les points dérivés restent opposés à leur source canonique."""
    instruction = AstralPointCalculationResolver().resolve(
        _runtime_point(
            code=point_code,
            variant_code=variant_code,
            calculation_mode=calculation_mode,
        )
    )

    assert instruction.point_code == point_code
    assert instruction.variant_code == variant_code
    assert instruction.engine_key is None
    assert instruction.derived_from_point_code == source_code
    assert instruction.derived_from_variant_code == source_variant
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
