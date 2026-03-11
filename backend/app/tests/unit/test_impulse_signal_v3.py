from datetime import UTC, datetime

import pytest

from app.infra.db.repositories.prediction_schemas import (
    AspectProfileData,
    CategoryData,
    EventTypeData,
    HouseCategoryWeightData,
    PlanetCategoryWeightData,
    PlanetProfileData,
    PredictionContext,
    RulesetContext,
    RulesetData,
)
from app.prediction.context_loader import LoadedPredictionContext
from app.prediction.impulse_signal_builder import ImpulseSignalBuilder
from app.prediction.schemas import AstroEvent, SamplePoint


def _loaded_context() -> LoadedPredictionContext:
    sun_profile = PlanetProfileData(
        planet_id=1,
        code="sun",
        name="Sun",
        class_code="luminary",
        speed_rank=1,
        speed_class="fast",
        weight_intraday=1.0,
        weight_day_climate=1.0,
        typical_polarity="positive",
        orb_active_deg=5.0,
        orb_peak_deg=1.5,
        keywords=("sun",),
    )
    prediction_context = PredictionContext(
        categories=(CategoryData(1, "work", "Work", "Work", 1, True),),
        planet_profiles={"Sun": sun_profile, "sun": sun_profile},
        house_profiles={},
        planet_category_weights=(
            PlanetCategoryWeightData(1, "Sun", 1, "work", 1.0, "primary"),
        ),
        house_category_weights=(
            HouseCategoryWeightData(10, 10, 1, "work", 1.0, "primary"),
        ),
        sign_rulerships={},
        aspect_profiles={
            "conjunction": AspectProfileData(
                aspect_id=1,
                code="conjunction",
                intensity_weight=1.0,
                default_valence="positive",
                orb_multiplier=1.0,
                phase_sensitive=True,
            ),
        },
        astro_points={},
        point_category_weights=(),
    )
    ruleset_context = RulesetContext(
        ruleset=RulesetData(
            id=1,
            version="1.0.0",
            reference_version_id=1,
            zodiac_type="tropical",
            coordinate_mode="geocentric",
            house_system="whole_sign",
            time_step_minutes=15,
            is_locked=True,
        ),
        parameters={},
        event_types={
            "aspect_exact_to_angle": EventTypeData(
                id=1,
                code="aspect_exact_to_angle",
                name="Exact angle",
                event_group="aspect",
                priority=90,
                base_weight=1.0,
            ),
            "moon_sign_ingress": EventTypeData(
                id=2,
                code="moon_sign_ingress",
                name="Moon ingress",
                event_group="ingress",
                priority=60,
                base_weight=0.6,
            ),
        },
    )
    return LoadedPredictionContext(
        prediction_context=prediction_context,
        ruleset_context=ruleset_context,
        calibrations={"work": None},
        is_provisional_calibration=True,
        calibration_label="provisional",
    )


def test_impulse_signal_requires_existing_support_regime() -> None:
    builder = ImpulseSignalBuilder()
    ctx = _loaded_context()
    sample = SamplePoint(ut_time=0.0, local_time=datetime(2026, 3, 11, 12, 0, tzinfo=UTC))
    event = AstroEvent(
        event_type="aspect_exact_to_angle",
        ut_time=0.0,
        local_time=sample.local_time,
        body="Sun",
        target="Asc",
        aspect="conjunction",
        orb_deg=0.0,
        priority=90,
        base_weight=1.0,
        metadata={"phase": "exact", "natal_house_target": 10, "natal_house_transited": 10},
    )

    timeline = builder.build_timeline(
        [event],
        [sample],
        {"work": 1.4},
        ctx,
        support_timelines={"work": {sample.local_time: 0.0}},
    )

    assert timeline["work"][sample.local_time] == 0.0


def test_impulse_signal_accents_existing_regime_without_using_baseline() -> None:
    builder = ImpulseSignalBuilder()
    ctx = _loaded_context()
    sample = SamplePoint(ut_time=0.0, local_time=datetime(2026, 3, 11, 12, 0, tzinfo=UTC))
    event = AstroEvent(
        event_type="aspect_exact_to_angle",
        ut_time=0.0,
        local_time=sample.local_time,
        body="Sun",
        target="Asc",
        aspect="conjunction",
        orb_deg=0.0,
        priority=90,
        base_weight=1.0,
        metadata={"phase": "exact", "natal_house_target": 10, "natal_house_transited": 10},
    )
    support = {"work": {sample.local_time: 0.6}}

    low_baseline_timeline = builder.build_timeline(
        [event],
        [sample],
        {"work": 0.75},
        ctx,
        support_timelines=support,
    )
    high_baseline_timeline = builder.build_timeline(
        [event],
        [sample],
        {"work": 1.5},
        ctx,
        support_timelines=support,
    )

    assert low_baseline_timeline["work"][sample.local_time] == pytest.approx(0.5)
    assert high_baseline_timeline["work"][sample.local_time] == pytest.approx(0.5)


def test_impulse_signal_exposes_diagnostics_and_total_capping() -> None:
    builder = ImpulseSignalBuilder()
    ctx = _loaded_context()
    sample = SamplePoint(ut_time=0.0, local_time=datetime(2026, 3, 11, 12, 0, tzinfo=UTC))
    events = [
        AstroEvent(
            event_type="aspect_exact_to_angle",
            ut_time=0.0,
            local_time=sample.local_time,
            body="Sun",
            target="Asc",
            aspect="conjunction",
            orb_deg=0.0,
            priority=90,
            base_weight=1.0,
            metadata={"phase": "exact", "natal_house_target": 10, "natal_house_transited": 10},
        ),
        AstroEvent(
            event_type="aspect_exact_to_angle",
            ut_time=0.0,
            local_time=sample.local_time,
            body="Sun",
            target="Asc",
            aspect="conjunction",
            orb_deg=0.0,
            priority=90,
            base_weight=1.0,
            metadata={"phase": "exact", "natal_house_target": 10, "natal_house_transited": 10},
        ),
        AstroEvent(
            event_type="moon_sign_ingress",
            ut_time=0.0,
            local_time=sample.local_time,
            body="Moon",
            target=None,
            aspect=None,
            orb_deg=0.0,
            priority=60,
            base_weight=0.6,
            metadata={"from_sign": 1, "to_sign": 2, "natal_house_target": 10},
        ),
    ]

    result = builder.build(
        events,
        [sample],
        {"work": 1.2},
        ctx,
        support_timelines={"work": {sample.local_time: 1.0}},
    )

    assert result.timeline["work"][sample.local_time] == pytest.approx(1.0)
    assert result.diagnostics["performance"]["impulse_event_count"] == 3
    assert result.diagnostics["themes"]["work"]["top_contributors"]
