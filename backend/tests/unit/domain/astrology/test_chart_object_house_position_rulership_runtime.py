"""Tests des payloads house position et rulership des objets runtime."""

from __future__ import annotations

from dataclasses import replace

import pytest

from app.domain.astrology.builders.chart_object_house_runtime_enricher import (
    RulershipChartObjectSelector,
    RulershipPayloadEnricher,
)
from app.domain.astrology.builders.chart_object_runtime_builder import (
    build_chart_object_runtime_data,
)
from app.domain.astrology.house_ruler_resolver import HouseRulerResult
from app.domain.astrology.natal_calculation import NatalAstralPointPosition, PlanetPosition
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectCapabilities,
    ChartObjectPayloads,
    ChartObjectRuntimeData,
    ChartObjectSourceRuntimeData,
    ChartObjectSourceType,
    ChartObjectType,
    RulershipRuntimePayload,
    validate_rulership_payloads,
)
from app.domain.astrology.runtime.house_runtime_data import HouseRuntimeData

SIGN_RULERS = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}


def _objects() -> tuple[ChartObjectRuntimeData, ...]:
    """Construit des objets runtime avec maisons et signes exploitables."""
    return build_chart_object_runtime_data(
        planet_positions=(
            PlanetPosition(
                planet_code="sun",
                longitude=130.0,
                sign_code="leo",
                house_number=10,
            ),
            PlanetPosition(
                planet_code="mars",
                longitude=15.0,
                sign_code="aries",
                house_number=1,
            ),
            PlanetPosition(
                planet_code="venus",
                longitude=45.0,
                sign_code="taurus",
                house_number=2,
            ),
            PlanetPosition(
                planet_code="saturn",
                longitude=285.0,
                sign_code="capricorn",
                house_number=10,
            ),
        ),
        astral_points=(
            NatalAstralPointPosition(
                code="north_node",
                variant_code="true",
                longitude=75.0,
                sign="gemini",
                degree_in_sign=15.0,
                house=3,
                calculation_source="simplified:SE_TRUE_NODE",
                is_physical_body=False,
            ),
        ),
        houses=tuple(
            HouseRuntimeData(number=number, cusp_longitude=float((number - 1) * 30))
            for number in range(1, 13)
        ),
    )


def _house_rulers() -> tuple[HouseRulerResult, ...]:
    """Construit des maitrises resolues par maison pour la projection."""
    return tuple(
        HouseRulerResult(
            house_number=house_number,
            cusp_sign=sign_code,
            ruler_planet=ruler_code,
            ruler_planet_sign=ruler_code,
            ruler_planet_house=house_number,
        )
        for house_number, (sign_code, ruler_code) in enumerate(SIGN_RULERS.items(), start=1)
    )


def _enriched_by_code() -> dict[str, ChartObjectRuntimeData]:
    """Retourne les objets enrichis indexes par code."""
    enriched = RulershipPayloadEnricher().enrich(_objects(), _house_rulers(), SIGN_RULERS)
    validate_rulership_payloads(enriched)
    return {item.code: item for item in enriched}


def test_house_position_payload_exposes_complete_runtime_shape() -> None:
    """La position en maison expose numero, modalite, cuspide et source."""
    by_code = _enriched_by_code()

    house_position = by_code["mars"].payloads.house_position

    assert house_position is not None
    assert house_position.house_number == 1
    assert house_position.house_modality == "angular"
    assert house_position.house_cusp_code == "house_1_cusp"
    assert house_position.source == "houses.runtime"


def test_house_position_modality_uses_canonical_house_runtime_helper() -> None:
    """Les modalites suivent la classification canonique des maisons."""
    by_code = _enriched_by_code()

    assert by_code["mars"].payloads.house_position is not None
    assert by_code["mars"].payloads.house_position.house_modality == "angular"
    assert by_code["venus"].payloads.house_position is not None
    assert by_code["venus"].payloads.house_position.house_modality == "succedent"
    assert by_code["north_node"].payloads.house_position is not None
    assert by_code["north_node"].payloads.house_position.house_modality == "cadent"


def test_rulership_payload_validates_calculatory_shape() -> None:
    """Le payload de maitrise refuse les flags incoherents."""
    with pytest.raises(ValueError, match="house ruler flag"):
        RulershipRuntimePayload(
            rules_houses=(),
            is_house_ruler=True,
            is_ascendant_ruler=False,
            is_midheaven_ruler=False,
            source="house_rulers.sign_rulerships",
        )


def test_chart_object_payload_shape_declares_rulership_without_free_dict() -> None:
    """Le contrat expose un payload type et une capacite dediee."""
    assert "rulership" in ChartObjectPayloads.__dataclass_fields__
    assert "supports_rulership" in ChartObjectCapabilities.__dataclass_fields__


def test_planets_and_luminaries_project_rules_houses() -> None:
    """Les corps qui gouvernent des maisons exposent les maisons gouvernees."""
    by_code = _enriched_by_code()

    assert by_code["mars"].payloads.rulership is not None
    assert by_code["mars"].payloads.rulership.rules_houses == (1, 8)
    assert by_code["venus"].payloads.rulership is not None
    assert by_code["venus"].payloads.rulership.rules_houses == (2, 7)
    assert by_code["sun"].payloads.rulership is not None
    assert by_code["sun"].payloads.rulership.rules_houses == (5,)


def test_angular_ruler_flags_target_ascendant_and_midheaven_houses() -> None:
    """Les flags ASC/MC sont derives des maisons gouvernees."""
    by_code = _enriched_by_code()

    assert by_code["mars"].payloads.rulership is not None
    assert by_code["mars"].payloads.rulership.is_ascendant_ruler is True
    assert by_code["mars"].payloads.rulership.is_midheaven_ruler is False
    assert by_code["saturn"].payloads.rulership is not None
    assert by_code["saturn"].payloads.rulership.is_midheaven_ruler is True


def test_dispositor_comes_from_canonical_sign_rulerships() -> None:
    """Le dispositor vient du mapping signe vers maitre fourni au runtime."""
    by_code = _enriched_by_code()

    assert by_code["sun"].payloads.rulership is not None
    assert by_code["sun"].payloads.rulership.dispositor_code == "sun"
    assert by_code["venus"].payloads.rulership is not None
    assert by_code["venus"].payloads.rulership.dispositor_code == "venus"


def test_missing_sign_keeps_dispositor_none_without_fallback() -> None:
    """Un objet sans signe ne recoit pas de dispositor invente."""
    objects = tuple(
        replace(item, zodiac_position=None) if item.code == "mars" else item for item in _objects()
    )
    by_code = {
        item.code: item
        for item in RulershipPayloadEnricher().enrich(objects, _house_rulers(), SIGN_RULERS)
    }

    assert by_code["mars"].payloads.rulership is not None
    assert by_code["mars"].payloads.rulership.dispositor_code is None


def test_non_eligible_objects_do_not_receive_rulership_payloads() -> None:
    """Les points, angles et cuspides restent sans payload rulership."""
    by_code = _enriched_by_code()

    assert by_code["north_node"].capabilities.supports_rulership is False
    assert by_code["north_node"].payloads.rulership is None
    assert by_code["asc"].payloads.rulership is None
    assert by_code["house_1_cusp"].payloads.rulership is None


def test_rulership_payload_rejects_non_capable_object() -> None:
    """Un payload rulership sans capacite dediee echoue explicitement."""
    with pytest.raises(ValueError, match="rulership capability"):
        ChartObjectRuntimeData(
            code="north_node",
            object_type=ChartObjectType.ASTRAL_POINT,
            display_name="North Node",
            longitude=None,
            latitude=None,
            zodiac_position=None,
            source=ChartObjectSourceRuntimeData(
                source_type=ChartObjectSourceType.DERIVED,
                source_key="derived",
            ),
            capabilities=ChartObjectCapabilities(),
            classifications=("astral_point",),
            payloads=ChartObjectPayloads(
                rulership=RulershipRuntimePayload(
                    rules_houses=(1,),
                    is_house_ruler=True,
                    is_ascendant_ruler=True,
                    is_midheaven_ruler=False,
                    source="house_rulers.sign_rulerships",
                ),
            ),
        )


def test_selector_uses_capability_not_object_type() -> None:
    """La selection rulership suit la capacite runtime declaree."""
    selected = RulershipChartObjectSelector().choose(_objects())

    assert {item.code for item in selected} == {"sun", "mars", "venus", "saturn"}
