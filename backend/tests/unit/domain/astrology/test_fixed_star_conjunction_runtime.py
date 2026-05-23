"""Tests du calcul runtime des conjonctions d'etoiles fixes."""

from __future__ import annotations

import pytest

from app.domain.astrology.fixed_stars.contracts import (
    DEFAULT_FIXED_STAR_CONJUNCTION_MAX_ORB_DEG,
    FixedStarConjunctionRulesRuntimeData,
)
from app.domain.astrology.fixed_stars.fixed_star_conjunction_calculator import (
    FixedStarConjunctionCalculator,
)
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectCapabilities,
    ChartObjectPayloads,
    ChartObjectRuntimeData,
    ChartObjectSourceRuntimeData,
    ChartObjectSourceType,
    ChartObjectType,
    FixedStarRuntimePayload,
)


def _chart_object(
    code: str,
    longitude: float,
    *,
    payloads: ChartObjectPayloads | None = None,
    capabilities: ChartObjectCapabilities | None = None,
) -> ChartObjectRuntimeData:
    """Construit un objet runtime minimal pour le calculateur."""
    return ChartObjectRuntimeData(
        code=code,
        object_type=ChartObjectType.PLANET,
        display_name=code.title(),
        longitude=longitude,
        latitude=None,
        zodiac_position=None,
        source=ChartObjectSourceRuntimeData(
            source_type=ChartObjectSourceType.EPHEMERIS,
            source_key=code,
        ),
        capabilities=capabilities or ChartObjectCapabilities(),
        classifications=("test",),
        payloads=payloads or ChartObjectPayloads(),
    )


def _star(longitude: float, *, categories: tuple[str, ...] = ()) -> ChartObjectRuntimeData:
    """Construit une etoile fixe runtime."""
    return _chart_object(
        "regulus",
        longitude,
        payloads=ChartObjectPayloads(
            fixed_star=FixedStarRuntimePayload(
                catalog_code="regulus",
                display_name="Regulus",
                reference_system="tropical_catalog",
                source_code="runtime_reference",
                categories=categories,
            )
        ),
    )


def _target(longitude: float) -> ChartObjectRuntimeData:
    """Construit une cible eligible aux contacts fixed star."""
    return _chart_object(
        "mars",
        longitude,
        capabilities=ChartObjectCapabilities(supports_fixed_star_conjunction=True),
    )


def test_exact_conjunction_has_zero_orb() -> None:
    """Une conjonction exacte produit un orbe nul."""
    contacts = FixedStarConjunctionCalculator().calculate((_star(150.0), _target(150.0)))

    assert len(contacts) == 1
    assert contacts[0].orb_deg == 0.0


def test_within_orb_uses_rule() -> None:
    """Un contact dans l'orbe applique la regle centralisee."""
    rules = FixedStarConjunctionRulesRuntimeData(orb_by_star_code=(("regulus", 0.5),))
    contacts = FixedStarConjunctionCalculator(rules).calculate((_star(150.0), _target(150.42)))

    assert len(contacts) == 1
    assert contacts[0].orb_deg == 0.42
    assert contacts[0].max_orb_deg == 0.5
    assert contacts[0].rule_code == "fixed_star:regulus"


def test_outside_orb_returns_no_payload() -> None:
    """Un contact hors orbe ne produit rien."""
    contacts = FixedStarConjunctionCalculator().calculate((_star(150.0), _target(152.0)))

    assert contacts == ()


def test_rules_support_category_overrides() -> None:
    """Les orbes viennent du contrat de regles dedie."""
    rules = FixedStarConjunctionRulesRuntimeData(orb_by_category=(("royal", 2.0),))
    contacts = FixedStarConjunctionCalculator(rules).calculate(
        (_star(150.0, categories=("royal",)), _target(151.5))
    )

    assert contacts[0].max_orb_deg == 2.0
    assert contacts[0].rule_code == "fixed_star_category:royal"


def test_angular_distance_wraps_zodiac_edge() -> None:
    """La distance angulaire est normalisee au bord zodiacal."""
    contacts = FixedStarConjunctionCalculator().calculate((_star(359.8), _target(0.1)))

    assert contacts[0].orb_deg == pytest.approx(0.3)
    assert contacts[0].max_orb_deg == DEFAULT_FIXED_STAR_CONJUNCTION_MAX_ORB_DEG


def test_reference_consistency_uses_runtime_longitudes_as_exposed() -> None:
    """Les longitudes du catalogue sont consommees telles qu'exposees runtime."""
    contact = FixedStarConjunctionCalculator().calculate((_star(150.0), _target(150.5)))[0]

    assert contact.fixed_star_longitude_deg == 150.0
    assert contact.target_longitude_deg == 150.5
