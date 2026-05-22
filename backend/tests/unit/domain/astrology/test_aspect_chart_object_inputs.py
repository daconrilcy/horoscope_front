"""Tests de la frontiere chart_objects du moteur d'aspects natal."""

from __future__ import annotations

from math import inf, nan

import pytest

from app.domain.astrology.calculators.aspect_inputs import (
    AspectBodyProjector,
    AspectChartObjectSelector,
)
from app.domain.astrology.calculators.aspects import calculate_major_aspects
from app.domain.astrology.runtime.aspect_calculation_contracts import (
    AspectDefinitionRuntimeData,
)
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectCapabilities,
    ChartObjectPayloads,
    ChartObjectRuntimeData,
    ChartObjectSourceRuntimeData,
    ChartObjectSourceType,
    ChartObjectType,
)
from tests.factories.celestial_catalog_factory import make_celestial_catalog


def _chart_object(
    code: str,
    *,
    longitude: float | None,
    supports_aspects: bool,
    object_type: ChartObjectType = ChartObjectType.PLANET,
) -> ChartObjectRuntimeData:
    """Construit un objet runtime minimal pour les entrees d'aspects."""
    return ChartObjectRuntimeData(
        code=code,
        object_type=object_type,
        display_name=code.replace("_", " ").title(),
        longitude=longitude,
        latitude=None,
        zodiac_position=None,
        source=ChartObjectSourceRuntimeData(
            source_type=ChartObjectSourceType.EPHEMERIS,
            source_key=code,
        ),
        capabilities=ChartObjectCapabilities(supports_aspects=supports_aspects),
        classifications=(object_type.value,),
        payloads=ChartObjectPayloads(),
    )


def _square_definition() -> AspectDefinitionRuntimeData:
    """Retourne une definition d'aspect majeure stable pour les tests."""
    return AspectDefinitionRuntimeData(
        code="square",
        angle=90.0,
        family="major",
        default_orb_deg=8.0,
        is_enabled=True,
        is_major=True,
        is_minor=False,
        default_valence="negative",
        interpretive_valence="dynamic_challenging",
        energy_type="friction_activation",
        system_code="modern",
    )


def test_selector_filters_only_aspect_capable_objects() -> None:
    """Le selector se limite a `supports_aspects=True`."""
    selected = AspectChartObjectSelector().select(
        (
            _chart_object("sun", longitude=10.0, supports_aspects=True),
            _chart_object("house_1_cusp", longitude=None, supports_aspects=False),
            _chart_object("moon", longitude=100.0, supports_aspects=True),
        )
    )

    assert tuple(item.code for item in selected) == ("sun", "moon")


def test_selector_ignores_non_aspectable_object_without_longitude() -> None:
    """Un objet non aspectable incomplet ne pollue pas le moteur d'aspects."""
    selected = AspectChartObjectSelector().select(
        (_chart_object("house_1_cusp", longitude=None, supports_aspects=False),)
    )

    assert selected == ()


def test_selector_rejects_aspectable_object_without_longitude() -> None:
    """Un objet aspectable incomplet echoue explicitement."""
    with pytest.raises(ValueError, match="aspectable chart object sun requires longitude"):
        AspectChartObjectSelector().select(
            (_chart_object("sun", longitude=None, supports_aspects=True),)
        )


def test_selector_rejects_duplicate_aspectable_codes() -> None:
    """Deux objets aspectables de meme code creent une ambiguite bloquante."""
    with pytest.raises(ValueError, match="duplicate aspectable chart object code: sun"):
        AspectChartObjectSelector().select(
            (
                _chart_object("sun", longitude=10.0, supports_aspects=True),
                _chart_object("SUN", longitude=20.0, supports_aspects=True),
            )
        )


def test_projector_maps_chart_objects_to_aspect_bodies() -> None:
    """La projection unique conserve le code, le type et la longitude."""
    catalog = make_celestial_catalog()
    projected = AspectBodyProjector(catalog).project_many(
        (
            _chart_object("sun", longitude=10.0, supports_aspects=True),
            _chart_object(
                "asc",
                longitude=100.0,
                supports_aspects=True,
                object_type=ChartObjectType.ANGLE,
            ),
        )
    )

    assert [(item.code, item.body_type, item.longitude) for item in projected] == [
        ("sun", "luminary", 10.0),
        ("asc", "angle", 100.0),
    ]


@pytest.mark.parametrize("longitude", [nan, inf, -inf])
def test_projector_rejects_non_finite_longitude(longitude: float) -> None:
    """La projection refuse les longitudes non finies au lieu de les cacher."""
    with pytest.raises(ValueError, match="longitude must be finite"):
        AspectBodyProjector(make_celestial_catalog()).project(
            _chart_object("sun", longitude=longitude, supports_aspects=True)
        )


def test_projector_rejects_non_numeric_longitude() -> None:
    """La projection conserve l'exigence historique d'une longitude numerique."""
    chart_object = _chart_object("sun", longitude=10.0, supports_aspects=True)
    broken = chart_object.__class__(
        code=chart_object.code,
        object_type=chart_object.object_type,
        display_name=chart_object.display_name,
        longitude="bad",  # type: ignore[arg-type]
        latitude=chart_object.latitude,
        zodiac_position=chart_object.zodiac_position,
        source=chart_object.source,
        capabilities=chart_object.capabilities,
        classifications=chart_object.classifications,
        payloads=chart_object.payloads,
    )

    with pytest.raises(ValueError, match="longitude must be numeric"):
        AspectBodyProjector(make_celestial_catalog()).project(broken)


def test_calculation_consumes_projected_chart_objects_with_angle() -> None:
    """Le calcul geometrique accepte un angle aspectable projete."""
    catalog = make_celestial_catalog()
    chart_objects = AspectChartObjectSelector().select(
        (
            _chart_object("sun", longitude=10.0, supports_aspects=True),
            _chart_object("moon", longitude=100.0, supports_aspects=True),
            _chart_object("mars", longitude=280.0, supports_aspects=True),
            _chart_object(
                "asc",
                longitude=190.0,
                supports_aspects=True,
                object_type=ChartObjectType.ANGLE,
            ),
        )
    )
    positions = list(AspectBodyProjector(catalog).project_many(chart_objects))

    aspects = calculate_major_aspects(
        positions,
        [_square_definition()],
        orb_rules=[],
        system_inheritance={"modern": None},
    )

    pairs = {(aspect["planet_a"], aspect["planet_b"]) for aspect in aspects}
    assert ("moon", "sun") in pairs
    assert ("mars", "sun") in pairs
    assert ("asc", "moon") in pairs
