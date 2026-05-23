"""Tests des payloads runtime des etoiles fixes."""

from __future__ import annotations

import pytest

from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectCapabilities,
    ChartObjectPayloads,
    ChartObjectRuntimeData,
    ChartObjectSourceRuntimeData,
    ChartObjectSourceType,
    ChartObjectType,
    FixedStarConjunctionRuntimePayload,
    FixedStarRuntimePayload,
)


def test_fixed_star_payload_contract_has_no_narrative_fields() -> None:
    """Le payload d'etoile fixe reste documentaire et typé."""
    payload = FixedStarRuntimePayload(
        catalog_code="regulus",
        display_name="Regulus",
        reference_system="tropical_catalog",
        source_code="runtime_reference",
        constellation_code="leo",
        magnitude=1.35,
        reference_epoch="J2000",
        categories=("royal",),
    )

    assert payload.catalog_code == "regulus"
    assert set(FixedStarRuntimePayload.__dataclass_fields__) == {
        "catalog_code",
        "display_name",
        "reference_system",
        "source_code",
        "constellation_code",
        "magnitude",
        "reference_epoch",
        "categories",
    }
    assert "narrative" not in FixedStarRuntimePayload.__dataclass_fields__


def test_chart_object_payloads_fixed_star_conjunctions_default_empty_tuple() -> None:
    """Les contacts fixed star sont absents par defaut."""
    payloads = ChartObjectPayloads()

    assert payloads.fixed_star_conjunctions == ()


def test_fixed_star_conjunction_payload_is_calculatory() -> None:
    """Le contact runtime expose seulement les valeurs calculees."""
    payload = FixedStarConjunctionRuntimePayload(
        fixed_star_code="regulus",
        fixed_star_display_name="Regulus",
        target_code="mars",
        target_display_name="Mars",
        fixed_star_longitude_deg=150.0,
        target_longitude_deg=150.42,
        orb_deg=0.42,
        max_orb_deg=1.0,
        rule_code="default_fixed_star_conjunction",
        source="fixed_star_conjunction_calculator",
    )

    assert payload.orb_deg == 0.42
    assert set(FixedStarConjunctionRuntimePayload.__dataclass_fields__) == {
        "fixed_star_code",
        "fixed_star_display_name",
        "target_code",
        "target_display_name",
        "fixed_star_longitude_deg",
        "target_longitude_deg",
        "orb_deg",
        "max_orb_deg",
        "rule_code",
        "source",
    }


def test_non_target_rejects_fixed_star_conjunction_payload() -> None:
    """Un objet non eligible ne peut pas porter un contact calcule."""
    with pytest.raises(ValueError, match="fixed star conjunction capability"):
        ChartObjectRuntimeData(
            code="north_node",
            object_type=ChartObjectType.ASTRAL_POINT,
            display_name="North Node",
            longitude=150.0,
            latitude=None,
            zodiac_position=None,
            source=ChartObjectSourceRuntimeData(
                source_type=ChartObjectSourceType.EPHEMERIS,
                source_key="north_node",
            ),
            capabilities=ChartObjectCapabilities(),
            classifications=("astral_point",),
            payloads=ChartObjectPayloads(
                fixed_star_conjunctions=(
                    FixedStarConjunctionRuntimePayload(
                        fixed_star_code="regulus",
                        fixed_star_display_name="Regulus",
                        target_code="north_node",
                        target_display_name="North Node",
                        fixed_star_longitude_deg=150.0,
                        target_longitude_deg=150.0,
                        orb_deg=0.0,
                        max_orb_deg=1.0,
                        rule_code="default_fixed_star_conjunction",
                        source="fixed_star_conjunction_calculator",
                    ),
                )
            ),
        )
