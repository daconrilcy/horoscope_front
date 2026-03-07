import pytest
from unittest.mock import MagicMock

from app.prediction.natal_sensitivity import NatalSensitivityCalculator
from app.prediction.schemas import NatalChart


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    
    # Categories
    cat_work = MagicMock(code="WORK", is_enabled=True)
    cat_love = MagicMock(code="LOVE", is_enabled=True)
    cat_disabled = MagicMock(code="DISABLED", is_enabled=False)
    ctx.prediction_context.categories = [cat_work, cat_love, cat_disabled]
    
    # House category weights
    # WORK: house 6 and 10
    # LOVE: house 5 and 7
    ctx.prediction_context.house_category_weights = [
        MagicMock(category_code="WORK", house_number=6, weight=1.0),
        MagicMock(category_code="WORK", house_number=10, weight=1.0),
        MagicMock(category_code="LOVE", house_number=5, weight=1.0),
        MagicMock(category_code="LOVE", house_number=7, weight=1.0),
    ]
    
    # Planet category weights (for Ang)
    ctx.prediction_context.planet_category_weights = [
        MagicMock(category_code="WORK", planet_code="Sun", weight=0.5),
        MagicMock(category_code="LOVE", planet_code="Venus", weight=0.8),
    ]
    
    # Planet profiles (for Occ)
    ctx.prediction_context.planet_profiles = {
        "Sun": MagicMock(weight_day_climate=1.0),
        "Moon": MagicMock(weight_day_climate=0.8),
        "Venus": MagicMock(weight_day_climate=1.0),
    }
    
    # Parameters
    ctx.ruleset_context.parameters = {
        "ns_weight_occ": 0.1,
        "ns_weight_rul": 0.1,
        "ns_weight_ang": 0.1,
        "ns_weight_dom": 0.0
    }
    
    return ctx

def test_all_active_categories_present(mock_ctx):
    calculator = NatalSensitivityCalculator()
    natal = NatalChart({}, {}, {})
    results = calculator.compute(natal, mock_ctx)
    
    assert "WORK" in results
    assert "LOVE" in results
    assert "DISABLED" not in results

def test_no_occupation_neutral(mock_ctx):
    calculator = NatalSensitivityCalculator()
    # Planètes dans des maisons non liées (ex: 2, 3, 8, 9, 11, 12)
    natal = NatalChart(
        planet_positions={},
        planet_houses={"Sun": 2, "Moon": 3},
        house_sign_rulers={}
    )
    results = calculator.compute(natal, mock_ctx)
    
    # WORK et LOVE devraient être à 1.0 (poids neutre) car pas d'occupation, rulership ou angularité
    assert results["WORK"] == 1.0
    assert results["LOVE"] == 1.0

def test_strong_occupation_above_1(mock_ctx):
    calculator = NatalSensitivityCalculator()
    # Sun (weight 1.0) in house 10 (WORK) - House 10 is ANGULAR
    # Moon (weight 0.8) in house 6 (WORK)
    natal = NatalChart(
        planet_positions={},
        planet_houses={"Sun": 10, "Moon": 6},
        house_sign_rulers={}
    )
    results = calculator.compute(natal, mock_ctx)
    
    # Occ(WORK) = weight_sun + weight_moon = 1.0 + 0.8 = 1.8
    # Ang(WORK) = weight_sun_for_work = 0.5 (Sun is in house 10 which is angular)
    # NS(WORK) = 1.0 + w_occ * 1.8 + w_ang * 0.5 = 1.0 + 0.1 * 1.8 + 0.1 * 0.5 = 1.0 + 0.18 + 0.05 = 1.23
    assert results["WORK"] == pytest.approx(1.23)

def test_angular_ruler_raises_ns(mock_ctx):
    calculator = NatalSensitivityCalculator()
    # Ruler of house 10 (WORK) is Saturn. Saturn is in house 1 (angular).
    natal = NatalChart(
        planet_positions={},
        planet_houses={"Saturn": 1},
        house_sign_rulers={10: "Saturn"}
    )
    results = calculator.compute(natal, mock_ctx)
    
    # NS(WORK) = 1.0 + w_rul * 1.0 = 1.1
    assert results["WORK"] == pytest.approx(1.1)

def test_angular_planet_raises_ns(mock_ctx):
    calculator = NatalSensitivityCalculator()
    # Sun in house 1 (angular). Sun has weight 0.5 for WORK.
    natal = NatalChart(
        planet_positions={},
        planet_houses={"Sun": 1},
        house_sign_rulers={}
    )
    results = calculator.compute(natal, mock_ctx)
    
    # NS(WORK) = 1.0 + w_ang * 0.5 = 1.05
    assert results["WORK"] == pytest.approx(1.05)

def test_ns_capped_at_1_25(mock_ctx):
    calculator = NatalSensitivityCalculator()
    # Extreme case to exceed 1.25
    mock_ctx.ruleset_context.parameters["ns_weight_occ"] = 10.0
    natal = NatalChart(
        planet_positions={},
        planet_houses={"Sun": 10},
        house_sign_rulers={}
    )
    results = calculator.compute(natal, mock_ctx)
    
    assert results["WORK"] == 1.25

def test_ns_floored_at_0_75(mock_ctx):
    calculator = NatalSensitivityCalculator()
    # If parameters were negative (theoretically)
    mock_ctx.ruleset_context.parameters["ns_weight_occ"] = -10.0
    natal = NatalChart(
        planet_positions={},
        planet_houses={"Sun": 10},
        house_sign_rulers={}
    )
    results = calculator.compute(natal, mock_ctx)
    
    assert results["WORK"] == 0.75

def test_dom_zero_no_exception(mock_ctx):
    calculator = NatalSensitivityCalculator()
    mock_ctx.ruleset_context.parameters["ns_weight_dom"] = 0.0
    natal = NatalChart({}, {}, {})
    # Should not raise exception
    results = calculator.compute(natal, mock_ctx)
    assert results["WORK"] == 1.0
