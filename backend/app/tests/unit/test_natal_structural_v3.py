from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.prediction.natal_sensitivity import NatalSensitivityCalculator
from app.prediction.schemas import AstroEvent, NatalChart


@pytest.fixture
def mock_context():
    ctx = MagicMock()
    ctx.ruleset_context.parameters = {
        "v3_b_weight_occ": 0.4,
        "v3_b_weight_rul": 0.3,
        "v3_b_weight_ang": 0.2,
        "v3_b_weight_asp": 0.1,
    }
    
    work_cat = MagicMock()
    work_cat.code = "work"
    work_cat.is_enabled = True
    
    ctx.prediction_context.categories = [work_cat]
    ctx.prediction_context.house_category_weights = []
    ctx.prediction_context.planet_profiles = {}
    ctx.prediction_context.planet_category_weights = []
    ctx.prediction_context.sign_rulerships = {}
    
    return ctx

def test_compute_v3_bounds_and_centering(mock_context):
    calculator = NatalSensitivityCalculator()
    natal = NatalChart(
        planet_positions={},
        planet_houses={},
        house_sign_rulers={},
        natal_aspects=[]
    )
    
    results = calculator.compute_v3(natal, mock_context)
    
    assert "work" in results
    out = results["work"]
    # No factors present -> total score should be 1.0 (baseline)
    assert out.total_score == 1.0
    assert len(out.components) == 4
    for c in out.components:
        assert c.contribution == 0.0

def test_compute_v3_with_factors(mock_context):
    calculator = NatalSensitivityCalculator()
    
    # Mock significators for work
    p_weight = MagicMock()
    p_weight.planet_code = "Sun"
    p_weight.category_code = "work"
    p_weight.weight = 1.0
    mock_context.prediction_context.planet_category_weights = [p_weight]
    
    # Mock aspects
    aspect = AstroEvent(
        event_type="natal_aspect",
        ut_time=0.0,
        local_time=datetime.now(UTC),
        body="Sun",
        target="Moon",
        aspect="conjunction",
        orb_deg=0.0,
        priority=50,
        base_weight=1.0,
        metadata={"is_natal": True}
    )
    
    natal = NatalChart(
        planet_positions={"Sun": 10.0, "Moon": 10.0},
        planet_houses={"Sun": 1, "Moon": 1},
        house_sign_rulers={},
        natal_aspects=[aspect]
    )
    
    results = calculator.compute_v3(natal, mock_context)
    out = results["work"]
    
    # Aspects factor should be > 0
    aspect_comp = next(c for c in out.components if c.factor == "aspects")
    assert aspect_comp.contribution > 0
    assert out.total_score > 1.0

def test_compute_v3_clipping(mock_context):
    calculator = NatalSensitivityCalculator()
    
    # Force a very high contribution
    mock_natal = MagicMock()
    mock_natal.natal_aspects = []
    mock_natal.planet_houses = {}
    
    # We'll mock the internal methods instead
    calculator._compute_occ = MagicMock(return_value=100.0)
    
    results = calculator.compute_v3(mock_natal, mock_context)
    assert results["work"].total_score == 1.5 # Clipped at max
