from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.prediction.intraday_activation_builder import IntradayActivationBuilder
from app.prediction.schemas import NatalChart, PlanetState, StepAstroState


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
    
    # Profiles
    moon_profile = MagicMock(weight_intraday=1.0, typical_polarity="positive")
    ctx.prediction_context.planet_profiles = {"Moon": moon_profile}
    
    conj_profile = MagicMock(intensity_weight=1.0, default_valence="positive")
    ctx.prediction_context.aspect_profiles = {"conjunction": conj_profile}
    
    return ctx

def test_intraday_activation_moon_aspect(mock_context):
    builder = IntradayActivationBuilder()
    
    # Natal Sun in 10th house
    natal = NatalChart(
        planet_positions={"Sun": 100.0},
        planet_houses={"Sun": 10},
        house_sign_rulers={},
        natal_aspects=[]
    )
    
    # Moon exact conjunction to Natal Sun
    steps = [
        StepAstroState(
            ut_jd=0.0,
            local_time=datetime(2026, 3, 11, 12, 0, tzinfo=UTC),
            ascendant_deg=0.0, mc_deg=0.0, house_cusps=[], house_system_effective="",
            planets={"Moon": PlanetState("Moon", 100.0, 1.0, False, 3, 10)}
        )
    ]
    
    timeline = builder.build_timeline(steps, natal, mock_context)
    
    score = timeline["work"][steps[0].local_time]
    assert score > 0
    # 0.5 (moon base) * 1.0 (w_aspect) * 1.0 (f_orb) * 1.0 (pol) + 0.1 (house boost) = 0.6
    assert score == pytest.approx(0.6)

def test_intraday_activation_asc_ingress(mock_context):
    builder = IntradayActivationBuilder()
    natal = NatalChart(
        planet_positions={},
        planet_houses={},
        house_sign_rulers={},
        natal_aspects=[],
    )
    
    # Step 1: Asc at 29 deg Aries (sign 0)
    # Step 2: Asc at 1 deg Taurus (sign 1)
    steps = [
        StepAstroState(
            ut_jd=0.0, local_time=datetime(2026, 3, 11, 10, 0, tzinfo=UTC),
            ascendant_deg=29.0, mc_deg=29.0, house_cusps=[], house_system_effective="",
            planets={}
        ),
        StepAstroState(
            ut_jd=0.0, local_time=datetime(2026, 3, 11, 10, 15, tzinfo=UTC),
            ascendant_deg=31.0, mc_deg=29.0, house_cusps=[], house_system_effective="",
            planets={}
        )
    ]
    
    timeline = builder.build_timeline(steps, natal, mock_context)
    
    score1 = timeline["work"][steps[0].local_time]
    score2 = timeline["work"][steps[1].local_time]
    
    assert score1 == 0.0
    assert score2 == 0.05 # Sign change boost (W_ANGLE_INGRESS)

def test_intraday_activation_mc_ingress(mock_context):
    builder = IntradayActivationBuilder()
    natal = NatalChart(
        planet_positions={},
        planet_houses={},
        house_sign_rulers={},
        natal_aspects=[],
    )
    
    steps = [
        StepAstroState(
            ut_jd=0.0, local_time=datetime(2026, 3, 11, 10, 0, tzinfo=UTC),
            ascendant_deg=0.0, mc_deg=29.0, house_cusps=[], house_system_effective="",
            planets={}
        ),
        StepAstroState(
            ut_jd=0.0, local_time=datetime(2026, 3, 11, 10, 15, tzinfo=UTC),
            ascendant_deg=0.0, mc_deg=31.0, house_cusps=[], house_system_effective="",
            planets={}
        )
    ]
    
    timeline = builder.build_timeline(steps, natal, mock_context)
    
    score1 = timeline["work"][steps[0].local_time]
    score2 = timeline["work"][steps[1].local_time]
    
    assert score1 == 0.0
    assert score2 == 0.05 # MC Sign change boost
