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
    ctx.prediction_context.house_profiles = {}
    ctx.prediction_context.planet_profiles = {}
    ctx.prediction_context.planet_category_weights = []
    ctx.prediction_context.sign_rulerships = {}
    ctx.prediction_context.aspect_profiles = {}

    return ctx


def test_compute_v3_bounds_and_centering(mock_context):
    calculator = NatalSensitivityCalculator()
    natal = NatalChart(
        planet_positions={}, planet_houses={}, house_sign_rulers={}, natal_aspects=[]
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
        metadata={"is_natal": True},
    )

    natal = NatalChart(
        planet_positions={"Sun": 10.0, "Moon": 10.0},
        planet_houses={"Sun": 1, "Moon": 1},
        house_sign_rulers={},
        natal_aspects=[aspect],
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
    assert results["work"].total_score == 1.5  # Clipped at max


def test_compute_v3_can_drop_below_center_for_weak_theme(mock_context):
    calculator = NatalSensitivityCalculator()

    house_weight = MagicMock()
    house_weight.category_code = "work"
    house_weight.house_number = 10
    house_weight.weight = 1.0
    house_weight.routing_role = "primary"
    mock_context.prediction_context.house_category_weights = [house_weight]
    mock_context.prediction_context.house_profiles = {
        6: MagicMock(house_kind="cadent"),
        10: MagicMock(house_kind="angular"),
    }
    mock_context.prediction_context.sign_rulerships = {"capricorn": "Saturn"}

    planet_weight = MagicMock()
    planet_weight.planet_code = "Saturn"
    planet_weight.category_code = "work"
    planet_weight.weight = 1.0
    planet_weight.influence_role = "primary"
    mock_context.prediction_context.planet_category_weights = [planet_weight]
    mock_context.prediction_context.planet_profiles = {
        "Saturn": MagicMock(
            class_code="social",
            speed_class="slow",
            speed_rank=7,
            weight_day_climate=0.5,
        )
    }

    natal = NatalChart(
        planet_positions={"Saturn": 10.0},
        planet_houses={"Saturn": 6},
        house_sign_rulers={10: "capricorn"},
        natal_aspects=[],
    )

    results = calculator.compute_v3(natal, mock_context)

    assert results["work"].total_score < 1.0
    rulership_component = next(c for c in results["work"].components if c.factor == "rulership")
    angularity_component = next(c for c in results["work"].components if c.factor == "angularity")
    assert rulership_component.contribution < 0.0
    assert angularity_component.contribution < 0.0


def test_compute_v3_respects_house_weights_and_roles(mock_context):
    calculator = NatalSensitivityCalculator()

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
    mock_context.prediction_context.planet_profiles = {
        "Sun": MagicMock(
            class_code="luminary",
            speed_class="fast",
            speed_rank=1,
            weight_day_climate=1.0,
        )
    }

    natal_primary = NatalChart(
        planet_positions={"Sun": 10.0},
        planet_houses={"Sun": 10},
        house_sign_rulers={},
        natal_aspects=[],
    )
    natal_secondary = NatalChart(
        planet_positions={"Sun": 10.0},
        planet_houses={"Sun": 6},
        house_sign_rulers={},
        natal_aspects=[],
    )

    results_primary = calculator.compute_v3(natal_primary, mock_context)
    results_secondary = calculator.compute_v3(natal_secondary, mock_context)

    occ_primary = next(c for c in results_primary["work"].components if c.factor == "occupation")
    occ_secondary = next(
        c for c in results_secondary["work"].components if c.factor == "occupation"
    )

    assert occ_primary.contribution > occ_secondary.contribution


def test_compute_v3_occupation_ignores_slow_planets(mock_context):
    calculator = NatalSensitivityCalculator()

    house_weight = MagicMock()
    house_weight.category_code = "work"
    house_weight.house_number = 10
    house_weight.weight = 1.0
    house_weight.routing_role = "primary"
    mock_context.prediction_context.house_category_weights = [house_weight]
    mock_context.prediction_context.planet_profiles = {
        "Saturn": MagicMock(
            class_code="social",
            speed_class="slow",
            speed_rank=7,
            weight_day_climate=1.0,
        ),
        "Mercury": MagicMock(
            class_code="personal",
            speed_class="fast",
            speed_rank=3,
            weight_day_climate=1.0,
        ),
    }

    natal_slow_only = NatalChart(
        planet_positions={"Saturn": 10.0},
        planet_houses={"Saturn": 10},
        house_sign_rulers={},
        natal_aspects=[],
    )
    natal_fast = NatalChart(
        planet_positions={"Mercury": 10.0},
        planet_houses={"Mercury": 10},
        house_sign_rulers={},
        natal_aspects=[],
    )

    results_slow_only = calculator.compute_v3(natal_slow_only, mock_context)
    results_fast = calculator.compute_v3(natal_fast, mock_context)

    occ_slow = next(c for c in results_slow_only["work"].components if c.factor == "occupation")
    occ_fast = next(c for c in results_fast["work"].components if c.factor == "occupation")

    assert occ_slow.contribution == 0.0
    assert occ_fast.contribution > 0.0


def test_compute_v3_aspects_can_lower_structural_score(mock_context):
    calculator = NatalSensitivityCalculator()
    mock_context.ruleset_context.parameters.update(
        {
            "v3_b_weight_occ": 0.0,
            "v3_b_weight_rul": 0.0,
            "v3_b_weight_ang": 0.0,
            "v3_b_weight_asp": 0.4,
        }
    )

    planet_weight = MagicMock()
    planet_weight.planet_code = "Sun"
    planet_weight.category_code = "work"
    planet_weight.weight = 1.0
    planet_weight.influence_role = "primary"
    mock_context.prediction_context.planet_category_weights = [planet_weight]
    mock_context.prediction_context.aspect_profiles = {
        "square": MagicMock(
            intensity_weight=1.0,
            default_valence="negative",
            orb_multiplier=1.0,
        )
    }

    hard_aspect = AstroEvent(
        event_type="natal_aspect",
        ut_time=0.0,
        local_time=datetime(1970, 1, 1, tzinfo=UTC),
        body="Sun",
        target="Moon",
        aspect="square",
        orb_deg=0.0,
        priority=50,
        base_weight=1.0,
        metadata={"is_natal": True},
    )
    natal = NatalChart(
        planet_positions={"Sun": 10.0, "Moon": 100.0},
        planet_houses={"Sun": 10, "Moon": 4},
        house_sign_rulers={},
        natal_aspects=[hard_aspect],
    )

    results = calculator.compute_v3(natal, mock_context)

    aspect_comp = next(c for c in results["work"].components if c.factor == "aspects")
    assert aspect_comp.contribution < 0.0
    assert results["work"].total_score < 1.0
