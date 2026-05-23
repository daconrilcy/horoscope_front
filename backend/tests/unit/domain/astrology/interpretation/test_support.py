"""Helpers de tests pour l'input interpretatif chart-object."""

from __future__ import annotations

from app.domain.astrology.builders.chart_object_runtime_builder import (
    build_house_position_payload,
)
from app.domain.astrology.planetary_conditions.contracts import (
    ConditionConfidence,
    PlanetaryMotionDirection,
    PlanetarySpeedState,
    PlanetVisibilityKey,
)
from app.domain.astrology.runtime.chart_object_runtime_data import (
    ChartObjectCapabilities,
    ChartObjectMotionPayload,
    ChartObjectPayloads,
    ChartObjectRuntimeData,
    ChartObjectSourceRuntimeData,
    ChartObjectSourceType,
    ChartObjectType,
    ChartObjectVisibilityPayload,
    DignityBreakdownItem,
    DignityRuntimePayload,
    DominanceBreakdownItem,
    DominanceRuntimePayload,
    FixedStarConjunctionRuntimePayload,
    RulershipRuntimePayload,
    ZodiacPositionRuntimeData,
)


def interpretable_chart_object(
    code: str = "mars",
    *,
    supports_interpretation: bool = True,
    zodiac_position: ZodiacPositionRuntimeData | None = None,
    with_payloads: bool = True,
) -> ChartObjectRuntimeData:
    """Construit un objet runtime minimal coherent pour les tests."""
    payloads = _payloads(code) if with_payloads else ChartObjectPayloads()
    return ChartObjectRuntimeData(
        code=code,
        object_type=ChartObjectType.PLANET,
        display_name=code.title(),
        longitude=15.0,
        latitude=None,
        zodiac_position=zodiac_position
        if zodiac_position is not None
        else ZodiacPositionRuntimeData(sign_code="aries", degree_in_sign=15.0),
        source=ChartObjectSourceRuntimeData(
            source_type=ChartObjectSourceType.EPHEMERIS,
            source_key=code,
        ),
        capabilities=ChartObjectCapabilities(
            supports_interpretation=supports_interpretation,
            supports_dignities=with_payloads,
            supports_dominance=with_payloads,
            supports_house_position=with_payloads,
            supports_motion=with_payloads,
            supports_visibility=with_payloads,
            supports_rulership=with_payloads,
            supports_fixed_star_conjunction=with_payloads,
        ),
        classifications=("planet",),
        payloads=payloads,
    )


def _payloads(code: str) -> ChartObjectPayloads:
    """Assemble tous les payloads utiles sans recalcul."""
    return ChartObjectPayloads(
        motion=ChartObjectMotionPayload(
            speed_longitude=0.6,
            is_retrograde=False,
            direction=PlanetaryMotionDirection.DIRECT,
            is_direct=True,
            is_stationary=False,
            speed_state=PlanetarySpeedState.NORMAL,
            absolute_speed_longitude=0.6,
            normalized_speed_ratio=1.0,
            source="fixture.motion",
        ),
        visibility=ChartObjectVisibilityPayload(
            visibility_key=PlanetVisibilityKey.VISIBLE,
            is_visible=True,
            confidence=ConditionConfidence.HIGH,
            reason="fixture",
            source="fixture.visibility",
        ),
        dignity=DignityRuntimePayload(
            essential_score=2.0,
            accidental_score=1.0,
            total_score=3.0,
            source="fixture.dignity",
            essential_breakdown=(DignityBreakdownItem("domicile", 2.0, "fixture.dignity"),),
            condition_codes=("in_sect",),
        ),
        dominance=DominanceRuntimePayload(
            contribution_score=0.82,
            source="fixture.dominance",
            rank=1,
            contribution_breakdown=(
                DominanceBreakdownItem(
                    factor_code="angularity",
                    raw_value=1.0,
                    normalized_value=1.0,
                    weight=0.5,
                    weighted_score=0.5,
                ),
            ),
            factors=("angularity",),
        ),
        house_position=build_house_position_payload(house_number=1),
        rulership=RulershipRuntimePayload(
            rules_houses=(1,),
            is_house_ruler=True,
            is_ascendant_ruler=True,
            is_midheaven_ruler=False,
            source="fixture.rulership",
            dispositor_code="mars",
            rules_signs=("aries",),
            rulership_sources=("traditional",),
        ),
        fixed_star_conjunctions=(
            FixedStarConjunctionRuntimePayload(
                fixed_star_code="regulus",
                fixed_star_display_name="Regulus",
                target_code=code,
                target_display_name=code.title(),
                fixed_star_longitude_deg=150.0,
                target_longitude_deg=150.4,
                orb_deg=0.4,
                max_orb_deg=1.0,
                rule_code="fixed_star_orb",
                source="fixture.fixed_star",
            ),
        ),
    )
