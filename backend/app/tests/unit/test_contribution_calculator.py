from datetime import datetime
from types import SimpleNamespace

import pytest

from app.prediction.contribution_calculator import ContributionCalculator
from app.prediction.schemas import AstroEvent


@pytest.fixture
def mock_ctx():
    # Setup profiles
    planet_profiles = {
        "Sun": SimpleNamespace(code="Sun", weight_intraday=1.2, typical_polarity="positive"),
        "Moon": SimpleNamespace(code="Moon", weight_intraday=1.1, typical_polarity="positive"),
        "Mars": SimpleNamespace(code="Mars", weight_intraday=1.0, typical_polarity="negative"),
        "Saturn": SimpleNamespace(code="Saturn", weight_intraday=0.8, typical_polarity="negative"),
    }

    aspect_profiles = {
        "conjunction": SimpleNamespace(
            code="conjunction", intensity_weight=1.00, default_valence="contextual"
        ),
        "opposition": SimpleNamespace(
            code="opposition", intensity_weight=0.90, default_valence="negative"
        ),
        "square": SimpleNamespace(code="square", intensity_weight=0.85, default_valence="negative"),
        "trine": SimpleNamespace(code="trine", intensity_weight=0.80, default_valence="positive"),
        "sextile": SimpleNamespace(
            code="sextile", intensity_weight=0.65, default_valence="positive"
        ),
    }

    event_types = {
        "aspect_transit": SimpleNamespace(code="aspect_transit", base_weight=1.0),
    }

    prediction_context = SimpleNamespace(
        planet_profiles=planet_profiles,
        aspect_profiles=aspect_profiles,
    )

    ruleset_context = SimpleNamespace(
        event_types=event_types,
        parameters={
            "orb_max_conjunction": 10.0,
            "orb_max_trine": 8.0,
            "orb_max_square": 7.0,
        },
    )

    return SimpleNamespace(prediction_context=prediction_context, ruleset_context=ruleset_context)


def test_out_of_orb_all_zero(mock_ctx):
    calculator = ContributionCalculator()
    event = AstroEvent(
        event_type="aspect_transit",
        ut_time=0,
        local_time=datetime.now(),
        body="Sun",
        target="Moon",
        aspect="conjunction",
        orb_deg=11.0,  # > 10.0 → out of orb
        priority=50,
        base_weight=1.0,
        metadata={},
    )

    d_map = {"WORK": 1.0, "LOVE": 0.5}
    ns_map = {"WORK": 1.0, "LOVE": 1.0}

    results = calculator.compute(event, ns_map, d_map, mock_ctx)
    assert results == {"WORK": 0.0, "LOVE": 0.0}


def test_exact_orb_max_f_orb(mock_ctx):
    calculator = ContributionCalculator()
    event = AstroEvent(
        event_type="aspect_transit",
        ut_time=0,
        local_time=datetime.now(),
        body="Sun",
        target="Moon",
        aspect="conjunction",
        orb_deg=0.0,
        priority=50,
        base_weight=1.0,
        metadata={},
    )

    # f_orb = 1.0 - (0/10)^2 = 1.0
    f_orb = calculator._f_orb(event, mock_ctx)
    assert f_orb == 1.0


def test_f_phase_applying():
    calculator = ContributionCalculator()
    event = AstroEvent(
        event_type="aspect_transit",
        ut_time=0,
        local_time=datetime.now(),
        body="Sun",
        target="Moon",
        aspect="conjunction",
        orb_deg=1.0,
        priority=50,
        base_weight=1.0,
        metadata={"phase": "applying"},
    )
    assert calculator._f_phase(event) == 1.05


def test_f_phase_exact():
    calculator = ContributionCalculator()
    event = AstroEvent(
        event_type="aspect_transit",
        ut_time=0,
        local_time=datetime.now(),
        body="Sun",
        target="Moon",
        aspect="conjunction",
        orb_deg=0.0,
        priority=50,
        base_weight=1.0,
        metadata={"phase": "exact"},
    )
    assert calculator._f_phase(event) == 1.15


def test_f_phase_separating():
    calculator = ContributionCalculator()
    event = AstroEvent(
        event_type="aspect_transit",
        ut_time=0,
        local_time=datetime.now(),
        body="Sun",
        target="Moon",
        aspect="conjunction",
        orb_deg=1.0,
        priority=50,
        base_weight=1.0,
        metadata={"phase": "separating"},
    )
    assert calculator._f_phase(event) == 0.95


def test_f_target_angle_1_30():
    calculator = ContributionCalculator()
    assert calculator._f_target("Asc") == 1.30
    assert calculator._f_target("MC") == 1.30
    assert calculator._f_target("Sun") == 1.20
    assert calculator._f_target("Mercury") == 1.10
    assert calculator._f_target("Jupiter") == 1.00
    assert calculator._f_target("Uranus") == 0.90


def test_saturn_conjunction_mc_negative(mock_ctx):
    calculator = ContributionCalculator()
    # Saturn (weight_intraday=0.8, polarity=negative)
    # Conjunction (valence=contextual → planet polarity → -0.5)
    # MC (target=angle → f_target=1.30)
    # Phase exact → f_phase=1.15, orb=0 → f_orb=1.0
    # base = 1.0 (w_event) * 0.8 * 1.0 * 1.0 * 1.15 * 1.30 = 1.196
    # Final = 1.196 * 1.0 (NS) * 1.0 (D) * -0.5 (Pol) = -0.598

    event = AstroEvent(
        event_type="aspect_transit",
        ut_time=0,
        local_time=datetime.now(),
        body="Saturn",
        target="MC",
        aspect="conjunction",
        orb_deg=0.0,
        priority=50,
        base_weight=1.0,
        metadata={"phase": "exact"},
    )

    d_map = {"WORK": 1.0}
    ns_map = {"WORK": 1.0}

    results = calculator.compute(event, ns_map, d_map, mock_ctx)
    assert results["WORK"] == pytest.approx(-0.598)


def test_moon_trine_sun_positive(mock_ctx):
    calculator = ContributionCalculator()
    # Moon (weight_intraday=1.1), Trine (valence=positive → 1.0, intensity=0.8)
    # Sun (target=luminary → f_target=1.20), applying → f_phase=1.05
    # orb=1.0, orb_max=8.0 → f_orb = 1 - (1/8)^2 = 0.984375
    # base = 1.0 * 1.1 * 0.8 * 0.984375 * 1.05 * 1.20 = 1.11525 → clamped to 1.0

    event = AstroEvent(
        event_type="aspect_transit",
        ut_time=0,
        local_time=datetime.now(),
        body="Moon",
        target="Sun",
        aspect="trine",
        orb_deg=1.0,
        priority=50,
        base_weight=1.0,
        metadata={"phase": "applying"},
    )

    d_map = {"LOVE": 1.0}
    ns_map = {"LOVE": 1.0}

    results = calculator.compute(event, ns_map, d_map, mock_ctx)
    assert results["LOVE"] == 1.0


def test_mars_square_mercury_negative(mock_ctx):
    calculator = ContributionCalculator()
    # Mars (weight_intraday=1.0), Square (valence=negative → -1.0, intensity=0.85)
    # Mercury (target=personal → f_target=1.10), separating → f_phase=0.95, orb=0 → f_orb=1.0
    # base = 1.0 * 1.0 * 0.85 * 1.0 * 0.95 * 1.10 = 0.88825
    # Final = 0.88825 * 1.2 (NS) * 0.5 (D) * -1.0 (Pol) = -0.53295

    event = AstroEvent(
        event_type="aspect_transit",
        ut_time=0,
        local_time=datetime.now(),
        body="Mars",
        target="Mercury",
        aspect="square",
        orb_deg=0.0,
        priority=50,
        base_weight=1.0,
        metadata={"phase": "separating"},
    )

    d_map = {"WORK": 0.5}
    ns_map = {"WORK": 1.2}

    results = calculator.compute(event, ns_map, d_map, mock_ctx)
    assert results["WORK"] == pytest.approx(-0.53295)


def test_clamped_to_plus_minus_1(mock_ctx):
    calculator = ContributionCalculator()
    # base_weight=10.0 forces a very large raw contribution → must be clamped
    event = AstroEvent(
        event_type="aspect_transit",
        ut_time=0,
        local_time=datetime.now(),
        body="Sun",
        target="Asc",
        aspect="conjunction",
        orb_deg=0.0,
        priority=50,
        base_weight=10.0,
        metadata={"phase": "exact"},
    )

    d_map = {"WORK": 1.0}
    ns_map = {"WORK": 1.25}

    results = calculator.compute(event, ns_map, d_map, mock_ctx)
    assert results["WORK"] == 1.0

    # Negative extreme
    mock_ctx.prediction_context.aspect_profiles["conjunction"].default_valence = "negative"
    results = calculator.compute(event, ns_map, d_map, mock_ctx)
    assert results["WORK"] == -1.0


def test_orb_max_from_metadata(mock_ctx):
    calculator = ContributionCalculator()
    # orb_max=5.0 in metadata takes priority over ruleset parameters
    # f_orb = 1 - (3/5)^2 = 1 - 0.36 = 0.64
    event = AstroEvent(
        event_type="aspect_transit",
        ut_time=0,
        local_time=datetime.now(),
        body="Sun",
        target="Moon",
        aspect="conjunction",
        orb_deg=3.0,
        priority=50,
        base_weight=1.0,
        metadata={"orb_max": 5.0},
    )

    f_orb = calculator._f_orb(event, mock_ctx)
    assert f_orb == pytest.approx(0.64)


def test_unknown_aspect_pol_returns_zero(mock_ctx):
    calculator = ContributionCalculator()
    event = AstroEvent(
        event_type="aspect_transit",
        ut_time=0,
        local_time=datetime.now(),
        body="Sun",
        target="Moon",
        aspect="unknown_aspect",
        orb_deg=1.0,
        priority=50,
        base_weight=1.0,
        metadata={},
    )
    assert calculator._pol(event, "WORK", mock_ctx) == 0.0


def test_non_aspect_event_does_not_require_orb_max(mock_ctx, caplog):
    calculator = ContributionCalculator()
    event = AstroEvent(
        event_type="planetary_hour_change",
        ut_time=0,
        local_time=datetime.now(),
        body="Sun",
        target=None,
        aspect=None,
        orb_deg=0.0,
        priority=50,
        base_weight=1.0,
        metadata={"hour_number": 1},
    )

    with caplog.at_level("WARNING"):
        result = calculator.compute(event, {"WORK": 1.0}, {"WORK": 1.0}, mock_ctx)

    assert calculator._f_orb(event, mock_ctx) == 1.0
    assert result["WORK"] == 0.0
    assert "orb_max not found" not in caplog.text
