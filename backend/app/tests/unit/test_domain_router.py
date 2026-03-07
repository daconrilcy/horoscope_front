from datetime import datetime
from types import SimpleNamespace

import pytest

from app.prediction.domain_router import DomainRouter
from app.prediction.schemas import AstroEvent


def _category(code: str, is_enabled: bool = True) -> SimpleNamespace:
    return SimpleNamespace(code=code, is_enabled=is_enabled)

def _house_weight(category_code: str, house_number: int, weight: float) -> SimpleNamespace:
    return SimpleNamespace(category_code=category_code, house_number=house_number, weight=weight)

def _planet_weight(category_code: str, planet_code: str, weight: float) -> SimpleNamespace:
    return SimpleNamespace(category_code=category_code, planet_code=planet_code, weight=weight)

@pytest.fixture
def mock_ctx() -> SimpleNamespace:
    prediction_context = SimpleNamespace(
        categories=(
            _category("WORK"),
            _category("LOVE"),
            _category("DISABLED", is_enabled=False),
        ),
        house_category_weights=(
            _house_weight("WORK", 10, 1.0),
            _house_weight("WORK", 6, 0.5),
            _house_weight("LOVE", 7, 1.0),
            _house_weight("LOVE", 5, 0.5),
        ),
        planet_category_weights=(
            _planet_weight("WORK", "Sun", 1.0),
            _planet_weight("LOVE", "Venus", 1.0),
            _planet_weight("WORK", "Mars", 0.5),
        )
    )
    return SimpleNamespace(prediction_context=prediction_context)

def test_house_vector_sum_1(mock_ctx):
    router = DomainRouter()
    event = AstroEvent(
        event_type="exact", ut_time=0, local_time=datetime.now(),
        body="Sun", target="Mars", aspect="conjunction", orb_deg=0,
        priority=50, base_weight=1.0,
        metadata={"natal_house_target": 10, "natal_house_transited": 6}
    )
    
    vector = router._build_house_vector(event)
    assert vector == {10: 0.70, 6: 0.30}
    assert sum(vector.values()) == pytest.approx(1.0)

def test_single_house_weight_1(mock_ctx):
    router = DomainRouter()
    # Case h_natal == h_transit
    event = AstroEvent(
        event_type="exact", ut_time=0, local_time=datetime.now(),
        body="Sun", target="Sun", aspect="conjunction", orb_deg=0,
        priority=50, base_weight=1.0,
        metadata={"natal_house_target": 10, "natal_house_transited": 10}
    )
    vector = router._build_house_vector(event)
    assert vector == {10: 1.0}

def test_planet_blend_in_range(mock_ctx):
    router = DomainRouter()
    active_cats = ["WORK", "LOVE"]
    planet_to_cat = router._build_planet_index(mock_ctx)

    # Sun has 1.0 for WORK, 0.0 for LOVE
    blend = router._compute_planet_blend("Sun", planet_to_cat, active_cats)

    # WORK: 0.5 + 0.5 * 1.0 = 1.0
    # LOVE: 0.5 + 0.5 * 0.0 = 0.5
    assert blend["WORK"] == 1.0
    assert blend["LOVE"] == 0.5

    # Verify all are in [0.5, 1.0]
    for val in blend.values():
        assert 0.5 <= val <= 1.0

def test_all_categories_covered(mock_ctx):
    router = DomainRouter()
    event = AstroEvent(
        event_type="exact", ut_time=0, local_time=datetime.now(),
        body="Sun", target="Mars", aspect="conjunction", orb_deg=0,
        priority=50, base_weight=1.0,
        metadata={"natal_house_target": 10, "natal_house_transited": 6}
    )
    
    results = router.route(event, mock_ctx)
    assert "WORK" in results
    assert "LOVE" in results
    assert "DISABLED" not in results

def test_no_target_no_exception(mock_ctx):
    router = DomainRouter()
    # AC5 - event without target (e.g. planetary hour)
    event = AstroEvent(
        event_type="planetary_hour_change", ut_time=0, local_time=datetime.now(),
        body="Sun", target=None, aspect=None, orb_deg=0,
        priority=50, base_weight=1.0,
        metadata={} # No natal house info
    )
    
    # Should only use planet blend
    # Sun blend: WORK=1.0, LOVE=0.5
    results = router.route(event, mock_ctx)
    assert results["WORK"] == 1.0
    assert results["LOVE"] == 0.5

def test_planet_blend_never_cancels(mock_ctx):
    router = DomainRouter()
    active_cats = ["WORK", "LOVE"]
    planet_to_cat = router._build_planet_index(mock_ctx)

    # Case with no weights for a planet
    blend = router._compute_planet_blend("Neptune", planet_to_cat, active_cats)
    assert all(val >= 0.5 for val in blend.values())


def test_planet_blend_none_planet_code(mock_ctx):
    """L1 régression : planet_code=None → plancher 0.5 (cohérent avec planète inconnue)."""
    router = DomainRouter()
    active_cats = ["WORK", "LOVE"]
    planet_to_cat = router._build_planet_index(mock_ctx)

    blend = router._compute_planet_blend(None, planet_to_cat, active_cats)
    assert blend["WORK"] == 0.5
    assert blend["LOVE"] == 0.5

def test_full_calculation_ac4(mock_ctx):
    router = DomainRouter()
    # h_target=10 (WORK: 1.0), h_transit=6 (WORK: 0.5)
    # house_projection[WORK] = 0.7*1.0 + 0.3*0.5 = 0.7 + 0.15 = 0.85
    # house_projection[LOVE] = 0.7*0.0 + 0.3*0.0 = 0.0
    
    # body="Mars" (WORK: 0.5, LOVE: 0.0)
    # planet_blend[WORK] = 0.5 + 0.5*0.5 = 0.75
    # planet_blend[LOVE] = 0.5 + 0.5*0.0 = 0.5
    
    # D(e, WORK) = 0.85 * 0.75 = 0.6375
    # D(e, LOVE) = 0.0 * 0.5 = 0.0
    
    event = AstroEvent(
        event_type="exact", ut_time=0, local_time=datetime.now(),
        body="Mars", target="Saturn", aspect="square", orb_deg=0,
        priority=50, base_weight=1.0,
        metadata={"natal_house_target": 10, "natal_house_transited": 6}
    )
    
    results = router.route(event, mock_ctx)
    assert results["WORK"] == pytest.approx(0.6375)
    assert results["LOVE"] == 0.0
