from datetime import UTC, date, datetime

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
from app.prediction.intraday_activation_builder import IntradayActivationBuilder
from app.prediction.schemas import AstroEvent, NatalChart, PlanetState, StepAstroState
from app.prediction.temporal_sampler import DayGrid


def _loaded_context() -> LoadedPredictionContext:
    moon_profile = PlanetProfileData(
        planet_id=1,
        code="moon",
        name="Moon",
        class_code="luminary",
        speed_rank=1,
        speed_class="fast",
        weight_intraday=1.0,
        weight_day_climate=1.0,
        typical_polarity="positive",
        orb_active_deg=5.0,
        orb_peak_deg=1.5,
        keywords=("moon",),
    )
    sun_profile = PlanetProfileData(
        planet_id=2,
        code="sun",
        name="Sun",
        class_code="luminary",
        speed_rank=2,
        speed_class="fast",
        weight_intraday=1.0,
        weight_day_climate=1.0,
        typical_polarity="positive",
        orb_active_deg=5.0,
        orb_peak_deg=1.5,
        keywords=("sun",),
    )
    venus_profile = PlanetProfileData(
        planet_id=3,
        code="venus",
        name="Venus",
        class_code="personal",
        speed_rank=3,
        speed_class="fast",
        weight_intraday=1.0,
        weight_day_climate=1.0,
        typical_polarity="positive",
        orb_active_deg=4.0,
        orb_peak_deg=1.5,
        keywords=("venus",),
    )
    prediction_context = PredictionContext(
        categories=(
            CategoryData(1, "work", "Work", "Work", 1, True),
            CategoryData(2, "love", "Love", "Love", 2, True),
        ),
        planet_profiles={
            "Moon": moon_profile,
            "moon": moon_profile,
            "Sun": sun_profile,
            "sun": sun_profile,
            "Venus": venus_profile,
            "venus": venus_profile,
        },
        house_profiles={},
        planet_category_weights=(
            PlanetCategoryWeightData(1, "Moon", 1, "work", 1.0, "primary"),
            PlanetCategoryWeightData(2, "Sun", 1, "work", 1.0, "primary"),
            PlanetCategoryWeightData(2, "Venus", 2, "love", 1.0, "primary"),
        ),
        house_category_weights=(
            HouseCategoryWeightData(10, 10, 1, "work", 1.0, "primary"),
            HouseCategoryWeightData(7, 7, 2, "love", 1.0, "primary"),
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
            )
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
            "aspect_exact_to_luminary": EventTypeData(
                id=1,
                code="aspect_exact_to_luminary",
                name="Exact luminary",
                event_group="aspect",
                priority=90,
                base_weight=1.0,
            ),
            "aspect_exact_to_angle": EventTypeData(
                id=2,
                code="aspect_exact_to_angle",
                name="Exact angle",
                event_group="aspect",
                priority=90,
                base_weight=1.0,
            ),
            "aspect_exact_to_personal": EventTypeData(
                id=3,
                code="aspect_exact_to_personal",
                name="Exact personal",
                event_group="aspect",
                priority=90,
                base_weight=1.0,
            ),
            "asc_sign_change": EventTypeData(
                id=4,
                code="asc_sign_change",
                name="Asc sign change",
                event_group="ingress",
                priority=50,
                base_weight=1.0,
            ),
            "planetary_hour_change": EventTypeData(
                id=5,
                code="planetary_hour_change",
                name="Planetary hour change",
                event_group="timing",
                priority=20,
                base_weight=0.8,
            ),
            "moon_sign_ingress": EventTypeData(
                id=6,
                code="moon_sign_ingress",
                name="Moon ingress",
                event_group="ingress",
                priority=40,
                base_weight=0.6,
            ),
        },
    )
    return LoadedPredictionContext(
        prediction_context=prediction_context,
        ruleset_context=ruleset_context,
        calibrations={"work": None, "love": None},
        is_provisional_calibration=True,
        calibration_label="provisional",
    )


def _step(
    when: datetime,
    *,
    moon_longitude: float | None = None,
    moon_house: int = 10,
    ascendant_deg: float = 0.0,
    mc_deg: float = 0.0,
    ut_jd: float = 2461110.5,
) -> StepAstroState:
    planets = {}
    if moon_longitude is not None:
        planets["Moon"] = PlanetState(
            code="Moon",
            longitude=moon_longitude,
            speed_lon=1.0,
            is_retrograde=False,
            sign_code=int(moon_longitude // 30),
            natal_house_transited=moon_house,
        )
    return StepAstroState(
        ut_jd=ut_jd,
        local_time=when,
        ascendant_deg=ascendant_deg,
        mc_deg=mc_deg,
        house_cusps=[],
        house_system_effective="placidus",
        planets=planets,
    )


def test_intraday_activation_uses_event_engine_rules_for_moon_aspects() -> None:
    builder = IntradayActivationBuilder()
    ctx = _loaded_context()
    natal = NatalChart(
        planet_positions={"Sun": 100.0},
        planet_houses={"Sun": 10},
        house_sign_rulers={},
        natal_aspects=[],
    )
    step = _step(datetime(2026, 3, 11, 12, 0, tzinfo=UTC), moon_longitude=100.0)

    result = builder.build([step], natal, ctx)

    score = result.timeline["work"][step.local_time]
    assert score == pytest.approx(1.38)
    assert result.diagnostics["themes"]["work"]["top_contributors"][0]["type"] == "moon_aspect"


def test_intraday_activation_routes_mc_ingress_by_weighted_houses() -> None:
    builder = IntradayActivationBuilder()
    ctx = _loaded_context()
    natal = NatalChart(
        planet_positions={},
        planet_houses={},
        house_sign_rulers={},
        natal_aspects=[],
    )
    steps = [
        _step(datetime(2026, 3, 11, 10, 0, tzinfo=UTC), mc_deg=29.0, ut_jd=2461111.90),
        _step(datetime(2026, 3, 11, 10, 15, tzinfo=UTC), mc_deg=31.0, ut_jd=2461111.91),
    ]

    result = builder.build(steps, natal, ctx)

    assert result.timeline["work"][steps[1].local_time] == pytest.approx(0.05)
    assert result.timeline["love"][steps[1].local_time] == 0.0


def test_intraday_activation_secondary_modulators_do_not_create_unrelated_relief() -> None:
    builder = IntradayActivationBuilder()
    ctx = _loaded_context()
    natal = NatalChart(
        planet_positions={},
        planet_houses={},
        house_sign_rulers={},
        natal_aspects=[],
    )
    step = _step(datetime(2026, 3, 11, 6, 0, tzinfo=UTC), ut_jd=2461111.75)
    detected_events = [
        AstroEvent(
            event_type="planetary_hour_change",
            ut_time=step.ut_jd,
            local_time=step.local_time,
            body="Mercury",
            target=None,
            aspect=None,
            orb_deg=0.0,
            priority=20,
            base_weight=0.8,
            metadata={"hour_number": 1},
        )
    ]

    result = builder.build([step], natal, ctx, detected_events=detected_events)

    assert result.timeline["work"][step.local_time] == 0.0
    assert result.timeline["love"][step.local_time] == 0.0


def test_intraday_activation_accounts_for_planetary_hours_when_day_grid_available() -> None:
    builder = IntradayActivationBuilder()
    ctx = _loaded_context()
    natal = NatalChart(
        planet_positions={},
        planet_houses={},
        house_sign_rulers={},
        natal_aspects=[],
    )
    step = _step(datetime(2026, 3, 11, 6, 0, tzinfo=UTC))
    day_grid = DayGrid(
        samples=[step],
        ut_start=2461111.75,
        ut_end=2461112.75,
        sunrise_ut=2461111.75,
        sunset_ut=2461112.25,
        local_date=date(2026, 3, 11),
        timezone="UTC",
    )

    # Wednesday planetary day starts with Mercury, then Moon, then Saturn, then Jupiter,
    # then Mars, then Sun at the sixth planetary hour.
    result = builder.build([step], natal, ctx, day_grid=day_grid)

    assert result.timeline["work"][step.local_time] > 0.0
    assert result.diagnostics["performance"]["secondary_event_count"] >= 1
