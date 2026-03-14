from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from app.prediction.schemas import NatalChart, PlanetState, StepAstroState
from app.prediction.transit_signal_builder import TransitSignalBuilder


@pytest.fixture
def mock_context():
    ctx = MagicMock()

    work_cat = MagicMock()
    work_cat.code = "work"
    work_cat.is_enabled = True

    ctx.prediction_context.categories = [work_cat]

    # Planet weight
    p_weight = MagicMock()
    p_weight.planet_code = "Sun"
    p_weight.category_code = "work"
    p_weight.weight = 1.0
    ctx.prediction_context.planet_category_weights = [p_weight]

    # House weight
    h_weight = MagicMock()
    h_weight.category_code = "work"
    h_weight.house_number = 10
    h_weight.weight = 1.0
    ctx.prediction_context.house_category_weights = [h_weight]

    # Planet profile
    sun_profile = MagicMock()
    sun_profile.weight_intraday = 1.0
    sun_profile.typical_polarity = "positive"
    sun_profile.orb_active_deg = 4.0
    ctx.prediction_context.planet_profiles = {"Sun": sun_profile}

    # Aspect profile
    conj_profile = MagicMock()
    conj_profile.intensity_weight = 1.0
    conj_profile.default_valence = "positive"
    conj_profile.orb_multiplier = 1.0
    conj_profile.phase_sensitive = True
    ctx.prediction_context.aspect_profiles = {"conjunction": conj_profile}
    ctx.ruleset_context.parameters = {}

    exact_type = MagicMock()
    exact_type.base_weight = 1.0
    exact_type.priority = 90
    ctx.ruleset_context.event_types = {
        "aspect_exact_to_luminary": exact_type,
        "aspect_exact_to_personal": exact_type,
        "aspect_exact_to_angle": exact_type,
    }

    return ctx


def test_transit_signal_curve(mock_context):
    builder = TransitSignalBuilder()

    natal = NatalChart(
        planet_positions={"Sun": 100.0},
        planet_houses={"Sun": 10},
        house_sign_rulers={},
        natal_aspects=[],
    )

    # Create a sequence of transit Sun moving towards natal Sun
    steps = []
    base_time = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)
    for i in range(-5, 6):
        # 1 degree per step approx
        lon = 100.0 + i * 1.0
        steps.append(
            StepAstroState(
                ut_jd=0.0,
                local_time=base_time + timedelta(hours=i),
                ascendant_deg=0.0,
                mc_deg=0.0,
                house_cusps=[],
                house_system_effective="placidus",
                planets={
                    "Sun": PlanetState(
                        code="Sun",
                        longitude=lon,
                        speed_lon=1.0,
                        is_retrograde=False,
                        sign_code=3,
                        natal_house_transited=10,
                    )
                },
            )
        )

    timeline = builder.build_timeline(steps, natal, mock_context)

    work_scores = [timeline["work"][s.local_time] for s in steps]

    # Score should peak at i=0 (lon=100.0)
    max_score = max(work_scores)
    assert work_scores[5] == max_score  # Middle step is index 5

    # Curve should be bell-like (parabolic decay)
    assert work_scores[0] < work_scores[5]
    assert work_scores[10] < work_scores[5]
    assert work_scores[2] > 0


def test_applying_vs_separating(mock_context):
    builder = TransitSignalBuilder()
    natal = NatalChart(
        planet_positions={"Sun": 100.0},
        planet_houses={"Sun": 10},
        house_sign_rulers={},
        natal_aspects=[],
    )

    # Step 1: 2 deg orb, applying
    # Step 2: 1 deg orb, applying
    # Step 3: 2 deg orb, separating

    steps = [
        StepAstroState(
            ut_jd=0.0,
            local_time=datetime(2026, 3, 11, 10, tzinfo=UTC),
            ascendant_deg=0.0,
            mc_deg=0.0,
            house_cusps=[],
            house_system_effective="",
            planets={"Sun": PlanetState("Sun", 98.0, 1.0, False, 3, 10)},
        ),
        StepAstroState(
            ut_jd=0.0,
            local_time=datetime(2026, 3, 11, 11, tzinfo=UTC),
            ascendant_deg=0.0,
            mc_deg=0.0,
            house_cusps=[],
            house_system_effective="",
            planets={"Sun": PlanetState("Sun", 99.0, 1.0, False, 3, 10)},
        ),
        StepAstroState(
            ut_jd=0.0,
            local_time=datetime(2026, 3, 11, 12, tzinfo=UTC),
            ascendant_deg=0.0,
            mc_deg=0.0,
            house_cusps=[],
            house_system_effective="",
            planets={"Sun": PlanetState("Sun", 102.0, 1.0, False, 3, 10)},
        ),
    ]

    timeline = builder.build_timeline(steps, natal, mock_context)
    scores = [timeline["work"][s.local_time] for s in steps]

    assert scores[1] > scores[0]
    # scores[0] and scores[2] have same orb (2.0) but diff phase
    assert scores[0] > scores[2]  # 1.0 vs 0.9


def test_transit_signal_exists_without_exact_step(mock_context):
    builder = TransitSignalBuilder()
    natal = NatalChart(
        planet_positions={"Sun": 100.0},
        planet_houses={"Sun": 10},
        house_sign_rulers={},
        natal_aspects=[],
    )
    steps = [
        StepAstroState(
            ut_jd=0.0,
            local_time=datetime(2026, 3, 11, 12, tzinfo=UTC),
            ascendant_deg=0.0,
            mc_deg=0.0,
            house_cusps=[],
            house_system_effective="placidus",
            planets={"Sun": PlanetState("Sun", 102.0, 1.0, False, 3, 10)},
        )
    ]

    timeline = builder.build_timeline(steps, natal, mock_context)

    assert timeline["work"][steps[0].local_time] > 0.0


def test_transit_signal_respects_primary_secondary_routing(mock_context):
    builder = TransitSignalBuilder()

    primary_house = MagicMock()
    primary_house.category_code = "work"
    primary_house.house_number = 10
    primary_house.weight = 1.0
    primary_house.routing_role = "primary"

    secondary_house = MagicMock()
    secondary_house.category_code = "work"
    secondary_house.house_number = 6
    secondary_house.weight = 1.0
    secondary_house.routing_role = "secondary"
    mock_context.prediction_context.house_category_weights = [primary_house, secondary_house]

    natal_primary = NatalChart(
        planet_positions={"Sun": 100.0},
        planet_houses={"Sun": 10},
        house_sign_rulers={},
        natal_aspects=[],
    )
    natal_secondary = NatalChart(
        planet_positions={"Sun": 100.0},
        planet_houses={"Sun": 6},
        house_sign_rulers={},
        natal_aspects=[],
    )
    step = StepAstroState(
        ut_jd=0.0,
        local_time=datetime(2026, 3, 11, 12, tzinfo=UTC),
        ascendant_deg=0.0,
        mc_deg=0.0,
        house_cusps=[],
        house_system_effective="placidus",
        planets={"Sun": PlanetState("Sun", 100.0, 1.0, False, 3, 10)},
    )

    primary_timeline = builder.build_timeline([step], natal_primary, mock_context)
    secondary_timeline = builder.build_timeline([step], natal_secondary, mock_context)

    assert primary_timeline["work"][step.local_time] > secondary_timeline["work"][step.local_time]


def test_transit_signal_uses_event_detector_orb_profiles(mock_context):
    builder = TransitSignalBuilder()

    sun_profile = mock_context.prediction_context.planet_profiles["Sun"]
    sun_profile.orb_active_deg = 4.0
    conj_profile = mock_context.prediction_context.aspect_profiles["conjunction"]
    conj_profile.orb_multiplier = 0.5

    natal = NatalChart(
        planet_positions={"Sun": 100.0},
        planet_houses={"Sun": 10},
        house_sign_rulers={},
        natal_aspects=[],
    )
    near_step = StepAstroState(
        ut_jd=0.0,
        local_time=datetime(2026, 3, 11, 12, tzinfo=UTC),
        ascendant_deg=0.0,
        mc_deg=0.0,
        house_cusps=[],
        house_system_effective="placidus",
        planets={"Sun": PlanetState("Sun", 101.0, 1.0, False, 3, 10)},
    )
    far_step = StepAstroState(
        ut_jd=0.0,
        local_time=datetime(2026, 3, 11, 13, tzinfo=UTC),
        ascendant_deg=0.0,
        mc_deg=0.0,
        house_cusps=[],
        house_system_effective="placidus",
        planets={"Sun": PlanetState("Sun", 103.0, 1.0, False, 3, 10)},
    )

    timeline = builder.build_timeline([near_step, far_step], natal, mock_context)

    assert timeline["work"][near_step.local_time] > 0.0
    assert timeline["work"][far_step.local_time] == 0.0
