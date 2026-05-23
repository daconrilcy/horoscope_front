"""Tests de l'enricher des conjonctions d'etoiles fixes."""

from __future__ import annotations

import pytest

from app.domain.astrology.fixed_stars.fixed_star_enricher import FixedStarConjunctionEnricher
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectCapabilities,
    ChartObjectPayloads,
    ChartObjectRuntimeData,
    ChartObjectSourceRuntimeData,
    ChartObjectSourceType,
    ChartObjectType,
    FixedStarConjunctionRuntimePayload,
)


def _target(code: str = "mars") -> ChartObjectRuntimeData:
    """Construit une cible enrichissable."""
    return ChartObjectRuntimeData(
        code=code,
        object_type=ChartObjectType.PLANET,
        display_name=code.title(),
        longitude=150.0,
        latitude=None,
        zodiac_position=None,
        source=ChartObjectSourceRuntimeData(
            source_type=ChartObjectSourceType.EPHEMERIS,
            source_key=code,
        ),
        capabilities=ChartObjectCapabilities(supports_fixed_star_conjunction=True),
        classifications=("planet",),
        payloads=ChartObjectPayloads(),
    )


def _contact(target_code: str = "mars") -> FixedStarConjunctionRuntimePayload:
    """Construit un contact calcule minimal."""
    return FixedStarConjunctionRuntimePayload(
        fixed_star_code="regulus",
        fixed_star_display_name="Regulus",
        target_code=target_code,
        target_display_name=target_code.title(),
        fixed_star_longitude_deg=150.0,
        target_longitude_deg=150.0,
        orb_deg=0.0,
        max_orb_deg=1.0,
        rule_code="default_fixed_star_conjunction",
        source="fixed_star_conjunction_calculator",
    )


def test_immutable_enrichment_preserves_other_payloads() -> None:
    """L'enricher retourne une nouvelle cible avec les contacts rattaches."""
    target = _target()
    enriched = FixedStarConjunctionEnricher().enrich((target,), (_contact(),))

    assert enriched[0] is not target
    assert target.payloads.fixed_star_conjunctions == ()
    assert enriched[0].payloads.fixed_star_conjunctions == (_contact(),)


def test_unknown_target_raises_explicit_error() -> None:
    """Un contact vers une cible inconnue est refuse."""
    with pytest.raises(ValueError, match="unknown fixed star conjunction target"):
        FixedStarConjunctionEnricher().enrich((_target(),), (_contact("venus"),))
