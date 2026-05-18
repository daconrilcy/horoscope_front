"""Tests du branchement des points astraux dans le résultat natal."""

from __future__ import annotations

from dataclasses import replace

from app.domain.astrology.natal_calculation import build_natal_result, opposite_longitude
from app.domain.astrology.natal_preparation import BirthInput
from app.domain.astrology.runtime.runtime_reference import (
    AstralPointReferenceSet,
    AstralPointRuntime,
    AstralPointVariantRuntime,
)
from tests.factories.astrology_runtime_reference_factory import complete_reference


def test_natal_result_contains_configured_astral_points() -> None:
    """Le résultat natal expose `astral_points[]` normalisé sans champs plats."""
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

    by_code = {point.code: point for point in result.astral_points}
    assert set(by_code) == {"north_node", "south_node"}
    assert by_code["north_node"].variant_code == "true"
    assert by_code["north_node"].sign
    assert 0.0 <= by_code["north_node"].degree_in_sign < 30.0
    assert by_code["north_node"].house is not None
    assert by_code["north_node"].calculation_source == "simplified:SE_TRUE_NODE"
    assert "astral_points" in result.model_dump()
    assert "points" not in result.model_dump()
    assert not hasattr(result, "true_node")
    assert not hasattr(result, "mean_node")
    assert not hasattr(result, "lilith")


def test_opposite_longitude_normalizes_zodiac_degrees() -> None:
    """L'utilitaire canonique calcule l'opposition sans sortir du zodiaque."""
    assert opposite_longitude(123.45) == 303.45
    assert opposite_longitude(270.0) == 90.0


def test_natal_result_derives_lunar_perigee_from_lunar_apogee() -> None:
    """Le résultat natal applique l'opposition apogée/périgée lunaire à 180 degrés."""
    reference = complete_reference()
    reference = replace(
        reference,
        astral_points=AstralPointReferenceSet(
            (
                AstralPointRuntime(
                    code="lunar_apogee",
                    display_name="Lunar Apogee",
                    family_code="lunar_apsides",
                    astronomical_type="lunar_orbit",
                    is_physical_body=False,
                    default_variant_code="mean",
                    variants=(
                        AstralPointVariantRuntime(
                            variant_code="mean",
                            display_name="Mean Lunar Apogee",
                            calculation_mode="mean_apogee",
                            engine_key="SE_MEAN_APOG",
                            is_default=True,
                        ),
                    ),
                    aliases=(),
                ),
                AstralPointRuntime(
                    code="lunar_perigee",
                    display_name="Lunar Perigee",
                    family_code="lunar_apsides",
                    astronomical_type="lunar_orbit",
                    is_physical_body=False,
                    default_variant_code="mean",
                    variants=(
                        AstralPointVariantRuntime(
                            variant_code="mean",
                            display_name="Mean Lunar Perigee",
                            calculation_mode="mean_perigee",
                            engine_key=None,
                            is_default=True,
                        ),
                    ),
                    aliases=(),
                ),
            )
        ),
    )

    result = build_natal_result(
        birth_input=BirthInput(
            birth_date="1990-06-15",
            birth_time="10:30",
            birth_place="Paris",
            birth_timezone="Europe/Paris",
        ),
        runtime_reference=reference,
        ruleset_version="test",
        house_system="equal",
    )

    by_code = {point.code: point for point in result.astral_points}
    expected = opposite_longitude(by_code["lunar_apogee"].longitude)
    assert by_code["lunar_perigee"].longitude == expected
    assert by_code["lunar_perigee"].calculation_source == "derived:lunar_apogee/mean+180"
