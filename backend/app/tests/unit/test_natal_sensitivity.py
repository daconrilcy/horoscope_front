from types import SimpleNamespace

import pytest

from app.prediction.natal_sensitivity import NatalSensitivityCalculator
from app.prediction.schemas import NatalChart


def _category(code: str, is_enabled: bool = True) -> SimpleNamespace:
    return SimpleNamespace(code=code, is_enabled=is_enabled)


def _house_weight(category_code: str, house_number: int, weight: float = 1.0) -> SimpleNamespace:
    return SimpleNamespace(category_code=category_code, house_number=house_number, weight=weight)


def _planet_weight(category_code: str, planet_code: str, weight: float) -> SimpleNamespace:
    return SimpleNamespace(category_code=category_code, planet_code=planet_code, weight=weight)


def _planet_profile(weight_day_climate: float) -> SimpleNamespace:
    return SimpleNamespace(weight_day_climate=weight_day_climate)


@pytest.fixture
def mock_ctx() -> SimpleNamespace:
    prediction_context = SimpleNamespace(
        categories=(
            _category("WORK"),
            _category("LOVE"),
            _category("DISABLED", is_enabled=False),
        ),
        house_category_weights=(
            _house_weight("WORK", 6),
            _house_weight("WORK", 10),
            _house_weight("LOVE", 5),
            _house_weight("LOVE", 7),
        ),
        planet_category_weights=(
            _planet_weight("WORK", "sun", 0.5),
            _planet_weight("LOVE", "venus", 0.8),
        ),
        planet_profiles={
            "sun": _planet_profile(1.0),
            "moon": _planet_profile(0.8),
            "venus": _planet_profile(1.0),
            "saturn": _planet_profile(0.7),
        },
        sign_rulerships={
            "aries": "mars",
            "taurus": "venus",
            "gemini": "mercury",
            "cancer": "moon",
            "leo": "sun",
            "virgo": "mercury",
            "libra": "venus",
            "scorpio": "mars",
            "sagittarius": "jupiter",
            "capricorn": "saturn",
            "aquarius": "saturn",
            "pisces": "jupiter",
        },
    )
    ruleset_context = SimpleNamespace(
        parameters={
            "ns_weight_occ": 0.1,
            "ns_weight_rul": 0.1,
            "ns_weight_ang": 0.1,
            "ns_weight_dom": 0.0,
        }
    )
    return SimpleNamespace(
        prediction_context=prediction_context,
        ruleset_context=ruleset_context,
    )


def test_all_active_categories_present(mock_ctx: SimpleNamespace) -> None:
    calculator = NatalSensitivityCalculator()
    natal = NatalChart(planet_positions={}, planet_houses={}, house_sign_rulers={})

    results = calculator.compute(natal, mock_ctx)

    assert "WORK" in results
    assert "LOVE" in results
    assert "DISABLED" not in results


def test_bounds_always_respected(mock_ctx: SimpleNamespace) -> None:
    calculator = NatalSensitivityCalculator()
    mock_ctx.ruleset_context.parameters.update(
        {
            "ns_weight_occ": 5.0,
            "ns_weight_rul": 5.0,
            "ns_weight_ang": 5.0,
        }
    )
    natal = NatalChart(
        planet_positions={},
        planet_houses={"sun": 10, "moon": 6, "venus": 7, "saturn": 1},
        house_sign_rulers={10: "capricorn", 7: "libra"},
    )

    results = calculator.compute(natal, mock_ctx)

    assert all(calculator.NS_MIN <= value <= calculator.NS_MAX for value in results.values())


def test_no_occupation_neutral(mock_ctx: SimpleNamespace) -> None:
    calculator = NatalSensitivityCalculator()
    natal = NatalChart(
        planet_positions={},
        planet_houses={"sun": 2, "moon": 3},
        house_sign_rulers={},
    )

    results = calculator.compute(natal, mock_ctx)

    assert results["WORK"] == 1.0
    assert results["LOVE"] == 1.0


def test_strong_occupation_above_1(mock_ctx: SimpleNamespace) -> None:
    calculator = NatalSensitivityCalculator()
    natal = NatalChart(
        planet_positions={},
        planet_houses={"sun": 10, "moon": 6},
        house_sign_rulers={},
    )

    results = calculator.compute(natal, mock_ctx)

    assert results["WORK"] == pytest.approx(1.23)


def test_angular_ruler_raises_ns_from_sign_rulerships(mock_ctx: SimpleNamespace) -> None:
    calculator = NatalSensitivityCalculator()
    natal = NatalChart(
        planet_positions={},
        planet_houses={"saturn": 1},
        house_sign_rulers={10: "capricorn"},
    )

    results = calculator.compute(natal, mock_ctx)

    assert results["WORK"] == pytest.approx(1.1)


def test_angular_planet_raises_ns(mock_ctx: SimpleNamespace) -> None:
    calculator = NatalSensitivityCalculator()
    natal = NatalChart(
        planet_positions={},
        planet_houses={"sun": 1},
        house_sign_rulers={},
    )

    results = calculator.compute(natal, mock_ctx)

    assert results["WORK"] == pytest.approx(1.05)


def test_ns_capped_at_1_25(mock_ctx: SimpleNamespace) -> None:
    calculator = NatalSensitivityCalculator()
    mock_ctx.ruleset_context.parameters["ns_weight_occ"] = 10.0
    natal = NatalChart(
        planet_positions={},
        planet_houses={"sun": 10},
        house_sign_rulers={},
    )

    results = calculator.compute(natal, mock_ctx)

    assert results["WORK"] == 1.25


def test_ns_floored_at_0_75(mock_ctx: SimpleNamespace) -> None:
    calculator = NatalSensitivityCalculator()
    mock_ctx.ruleset_context.parameters["ns_weight_occ"] = -10.0
    natal = NatalChart(
        planet_positions={},
        planet_houses={"sun": 10},
        house_sign_rulers={},
    )

    results = calculator.compute(natal, mock_ctx)

    assert results["WORK"] == 0.75


def test_dom_zero_no_exception(mock_ctx: SimpleNamespace) -> None:
    calculator = NatalSensitivityCalculator()
    mock_ctx.ruleset_context.parameters["ns_weight_dom"] = 0.0
    natal = NatalChart(planet_positions={}, planet_houses={}, house_sign_rulers={})

    results = calculator.compute(natal, mock_ctx)

    assert results["WORK"] == 1.0
