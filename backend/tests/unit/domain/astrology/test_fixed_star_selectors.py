"""Tests des selectors runtime d'etoiles fixes."""

from __future__ import annotations

import pytest

from app.domain.astrology.fixed_stars.fixed_star_selectors import (
    FixedStarChartObjectSelector,
    FixedStarConjunctionTargetSelector,
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


def _object(
    code: str,
    *,
    longitude: float | None,
    payloads: ChartObjectPayloads | None = None,
    capabilities: ChartObjectCapabilities | None = None,
    object_type: ChartObjectType = ChartObjectType.PLANET,
) -> ChartObjectRuntimeData:
    """Construit un objet runtime minimal pour les selectors."""
    return ChartObjectRuntimeData(
        code=code,
        object_type=object_type,
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


def _fixed_star(code: str = "regulus", longitude: float | None = 150.0) -> ChartObjectRuntimeData:
    """Construit une etoile fixe runtime minimale."""
    return _object(
        code,
        longitude=longitude,
        object_type=ChartObjectType.FIXED_STAR,
        payloads=ChartObjectPayloads(
            fixed_star=FixedStarRuntimePayload(
                catalog_code=code,
                display_name=code.title(),
                reference_system="tropical_catalog",
                source_code="runtime_reference",
            )
        ),
    )


def test_fixed_star_selector_uses_payload() -> None:
    """Le selector retient uniquement les objets avec payload fixed star."""
    selected = FixedStarChartObjectSelector().select(
        (
            _fixed_star(),
            _object("mars", longitude=150.0),
        )
    )

    assert tuple(item.code for item in selected) == ("regulus",)


def test_missing_star_longitude_raises_explicit_error() -> None:
    """Une etoile fixe sans longitude echoue a la selection."""
    with pytest.raises(ValueError, match="fixed star regulus requires longitude"):
        FixedStarChartObjectSelector().select((_fixed_star(longitude=None),))


def test_target_selector_uses_fixed_star_conjunction_capability() -> None:
    """Le selector cible est pilote par capacite, pas par famille nominale."""
    selected = FixedStarConjunctionTargetSelector().select(
        (
            _object(
                "mars",
                longitude=150.0,
                capabilities=ChartObjectCapabilities(supports_fixed_star_conjunction=True),
            ),
            _fixed_star(),
        )
    )

    assert tuple(item.code for item in selected) == ("mars",)


def test_target_selector_excludes_fixed_star_payloads_even_if_capable() -> None:
    """Une etoile fixe ne devient pas cible CS-222 par capacite accidentelle."""
    accidental_target_star = _object(
        "regulus",
        longitude=150.0,
        object_type=ChartObjectType.FIXED_STAR,
        capabilities=ChartObjectCapabilities(supports_fixed_star_conjunction=True),
        payloads=ChartObjectPayloads(
            fixed_star=FixedStarRuntimePayload(
                catalog_code="regulus",
                display_name="Regulus",
                reference_system="tropical_catalog",
                source_code="runtime_reference",
            )
        ),
    )

    selected = FixedStarConjunctionTargetSelector().select(
        (
            accidental_target_star,
            _object(
                "mars",
                longitude=150.0,
                capabilities=ChartObjectCapabilities(supports_fixed_star_conjunction=True),
            ),
        )
    )

    assert tuple(item.code for item in selected) == ("mars",)


def test_missing_target_longitude_raises_explicit_error() -> None:
    """Une cible eligible sans longitude echoue a la selection."""
    with pytest.raises(
        ValueError,
        match="fixed star conjunction target mars requires longitude",
    ):
        FixedStarConjunctionTargetSelector().select(
            (
                _object(
                    "mars",
                    longitude=None,
                    capabilities=ChartObjectCapabilities(supports_fixed_star_conjunction=True),
                ),
            )
        )
