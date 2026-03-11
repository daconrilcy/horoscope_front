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
    ctx.prediction_context.planet_profiles = {"Sun": sun_profile}
    
    # Aspect profile
    conj_profile = MagicMock()
    conj_profile.intensity_weight = 1.0
    conj_profile.default_valence = "positive"
    ctx.prediction_context.aspect_profiles = {"conjunction": conj_profile}
    
    return ctx

def test_transit_signal_curve(mock_context):
    builder = TransitSignalBuilder()
    
    natal = NatalChart(
        planet_positions={"Sun": 100.0},
        planet_houses={"Sun": 10},
        house_sign_rulers={},
        natal_aspects=[]
    )
    
    # Create a sequence of transit Sun moving towards natal Sun
    steps = []
    base_time = datetime(2026, 3, 11, 12, 0, tzinfo=UTC)
    for i in range(-5, 6):
        # 1 degree per step approx
        lon = 100.0 + i * 1.0
        steps.append(StepAstroState(
            ut_jd=0.0,
            local_time=base_time + timedelta(hours=i),
            ascendant_deg=0.0,
            mc_deg=0.0,
            house_cusps=[],
            house_system_effective="placidus",
            planets={"Sun": PlanetState(
                code="Sun", longitude=lon, speed_lon=1.0, 
                is_retrograde=False, sign_code=3, natal_house_transited=10
            )}
        ))
    
    timeline = builder.build_timeline(steps, natal, mock_context)
    
    work_scores = [timeline["work"][s.local_time] for s in steps]
    
    # Score should peak at i=0 (lon=100.0)
    max_score = max(work_scores)
    assert work_scores[5] == max_score # Middle step is index 5
    
    # Curve should be bell-like (parabolic decay)
    assert work_scores[0] < work_scores[5]
    assert work_scores[10] < work_scores[5]
    assert work_scores[0] > 0 # Still within orb (5 deg < 8 deg)

def test_applying_vs_separating(mock_context):
    builder = TransitSignalBuilder()
    natal = NatalChart(
        planet_positions={"Sun": 100.0},
        planet_houses={"Sun": 10},
        house_sign_rulers={},
        natal_aspects=[]
    )
    
    # Step 1: 2 deg orb, applying
    # Step 2: 1 deg orb, applying
    # Step 3: 2 deg orb, separating
    
    steps = [
        StepAstroState(
            ut_jd=0.0, local_time=datetime(2026, 3, 11, 10, tzinfo=UTC),
            ascendant_deg=0.0, mc_deg=0.0, house_cusps=[], house_system_effective="", 
            planets={"Sun": PlanetState("Sun", 98.0, 1.0, False, 3, 10)}
        ),
        StepAstroState(
            ut_jd=0.0, local_time=datetime(2026, 3, 11, 11, tzinfo=UTC),
            ascendant_deg=0.0, mc_deg=0.0, house_cusps=[], house_system_effective="", 
            planets={"Sun": PlanetState("Sun", 99.0, 1.0, False, 3, 10)}
        ),
        StepAstroState(
            ut_jd=0.0, local_time=datetime(2026, 3, 11, 12, tzinfo=UTC),
            ascendant_deg=0.0, mc_deg=0.0, house_cusps=[], house_system_effective="", 
            planets={"Sun": PlanetState("Sun", 102.0, 1.0, False, 3, 10)}
        ),
    ]
    
    timeline = builder.build_timeline(steps, natal, mock_context)
    scores = [timeline["work"][s.local_time] for s in steps]
    
    assert scores[1] > scores[0]
    # scores[0] and scores[2] have same orb (2.0) but diff phase
    assert scores[0] > scores[2] # 1.0 vs 0.9
