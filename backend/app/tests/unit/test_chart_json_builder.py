from unittest.mock import MagicMock

import pytest

from app.services.chart_json_builder import (
    EVIDENCE_ID_PATTERN,
    build_chart_json,
    build_evidence_catalog,
)
from app.services.user_profile.birth_profile_service import UserBirthProfileData


@pytest.fixture
def mock_birth_profile():
    return UserBirthProfileData(
        birth_date="1985-04-15",
        birth_time="14:30",
        birth_place="Paris, France",
        birth_timezone="Europe/Paris",
        birth_lat=48.8566,
        birth_lon=2.3522,
    )


@pytest.fixture
def mock_natal_result():
    # Mocking NatalResult
    result = MagicMock()
    result.engine = "swisseph"
    result.reference_version = "v1.2"
    result.ruleset_version = "1.0.0"
    result.zodiac = MagicMock()
    result.zodiac.value = "tropical"
    result.house_system = MagicMock()
    result.house_system.value = "placidus"
    result.prepared_input.birth_timezone = "Europe/Paris"

    # Planet Positions
    p1 = MagicMock()
    p1.planet_code = "sun"
    p1.sign_code = "taurus"
    p1.longitude = 35.4
    p1.house_number = 10
    p1.is_retrograde = False
    p1.speed_longitude = 0.98

    p2 = MagicMock()
    p2.planet_code = "mercury"
    p2.sign_code = "aries"
    p2.longitude = 15.2
    p2.house_number = 9
    p2.is_retrograde = True
    p2.speed_longitude = -0.5

    result.planet_positions = [p1, p2]

    # Houses
    houses = []
    # Simplified: 1=Capricorn (284.5), 10=Libra (194.2), 7=Cancer (104.5), 4=Aries (14.2)
    cusps = {1: 284.5, 10: 194.2, 7: 104.5, 4: 14.2}
    for i in range(1, 13):
        h = MagicMock()
        h.number = i
        h.cusp_longitude = cusps.get(i, (i - 1) * 30.0 % 360.0)
        houses.append(h)

    result.houses = houses

    # Aspects
    a1 = MagicMock()
    a1.aspect_code = "trine"
    a1.planet_a = "sun"
    a1.planet_b = "moon"
    a1.angle = 120.3
    a1.orb_used = 0.3

    result.aspects = [a1]

    return result


def test_build_chart_json_full(mock_natal_result, mock_birth_profile):
    chart = build_chart_json(mock_natal_result, mock_birth_profile)

    # Meta
    assert chart["meta"]["chart_json_version"] == "1"
    assert chart["meta"]["birth_date"] == "1985-04-15"
    assert chart["meta"]["birth_time"] == "14:30"
    assert chart["meta"]["degraded_mode"] is None
    assert chart["meta"]["engine"] == "swisseph"

    # Planets
    assert len(chart["planets"]) == 2
    sun = next(p for p in chart["planets"] if p["code"] == "sun")
    assert sun["sign"] == "taurus"
    assert sun["longitude"] == 35.4
    assert sun["longitude_in_sign"] == pytest.approx(5.4)
    assert sun["house"] == 10
    assert sun["is_retrograde"] is False

    # Houses
    assert len(chart["houses"]) == 12
    h1 = next(h for h in chart["houses"] if h["number"] == 1)
    assert h1["sign"] == "capricorn"

    # Aspects
    assert len(chart["aspects"]) == 1
    assert chart["aspects"][0]["type"] == "trine"
    assert chart["aspects"][0]["planet_a"] == "sun"
    assert chart["aspects"][0]["orb"] == 0.3
    assert chart["aspects"][0]["applying"] is None
    assert chart["meta"]["aspects_applying_available"] is False

    # Angles
    assert chart["angles"]["ASC"]["sign"] == "capricorn"
    assert chart["angles"]["MC"]["sign"] == "libra"
    assert chart["angles"]["DSC"]["sign"] == "cancer"
    assert chart["angles"]["IC"]["sign"] == "aries"


def test_build_chart_json_no_time(mock_natal_result, mock_birth_profile):
    mock_birth_profile.birth_time = None
    chart = build_chart_json(mock_natal_result, mock_birth_profile)

    assert chart["meta"]["degraded_mode"] == "no_time"
    assert chart["meta"]["birth_time"] is None

    # Planets should have house as None
    for p in chart["planets"]:
        assert p["house"] is None

    # Houses should be empty
    assert len(chart["houses"]) == 0

    # Angles should be None
    assert chart["angles"]["ASC"] is None
    assert chart["angles"]["MC"] is None


def test_build_chart_json_no_location(mock_natal_result, mock_birth_profile):
    mock_birth_profile.birth_lat = None
    chart = build_chart_json(mock_natal_result, mock_birth_profile)

    assert chart["meta"]["degraded_mode"] == "no_location"
    assert chart["meta"]["birth_place"] is None

    # In no_location but with time, we might still have houses if the engine calculates them,
    # but AC2 says angles should be null.
    assert chart["angles"]["ASC"] is None


def test_build_chart_json_no_location_no_time(mock_natal_result, mock_birth_profile):
    mock_birth_profile.birth_time = None
    mock_birth_profile.birth_lat = None
    chart = build_chart_json(mock_natal_result, mock_birth_profile)

    assert chart["meta"]["degraded_mode"] == "no_location_no_time"
    assert chart["meta"]["birth_time"] is None
    assert chart["meta"]["birth_place"] is None
    assert len(chart["houses"]) == 0
    assert chart["angles"]["ASC"] is None


def test_build_evidence_catalog_priority():
    chart_json = {
        "planets": [
            {"code": "sun", "sign": "taurus", "house": 10, "is_retrograde": False},
            {"code": "mercury", "sign": "aries", "house": 9, "is_retrograde": True},
            {"code": "moon", "sign": "cancer", "house": 2},
        ],
        "aspects": [{"type": "trine", "planet_a": "sun", "planet_b": "moon", "orb": 0.3}],
        "angles": {"ASC": {"sign": "capricorn"}, "MC": {"sign": "libra"}},
        "houses": [{"number": 1, "sign": "capricorn"}],
    }

    evidence = build_evidence_catalog(chart_json)

    # SUN, MOON, ASC, MC should be first (priority 0)
    assert evidence[0].startswith(("SUN_", "MOON_", "ASC_", "MC_"))

    # ASPECTS should be after H (priority 2)
    h_indexes = [i for i, x in enumerate(evidence) if "_H" in x]
    aspect_indexes = [i for i, x in enumerate(evidence) if "ASPECT_" in x]
    assert min(aspect_indexes) > max(h_indexes)

    # HOUSE_1_IN_CAPRICORN should be last (priority 3)
    assert evidence[-1] == "HOUSE_1_IN_CAPRICORN"


def test_evidence_catalog_pattern():
    chart_json = {
        "planets": [{"code": "sun", "sign": "taurus", "house": 10}],
        "aspects": [{"type": "conjunction", "planet_a": "venus", "planet_b": "mars", "orb": 1.2}],
        "angles": {"ASC": {"sign": "aries"}},
        "houses": [],
    }
    evidence = build_evidence_catalog(chart_json)
    for eid in evidence:
        assert EVIDENCE_ID_PATTERN.match(eid), f"Invalid ID: {eid}"


def test_longitude_conversions():
    from app.services.chart_json_builder import _longitude_in_sign, _longitude_to_sign

    assert _longitude_to_sign(0) == "aries"
    assert _longitude_to_sign(35.4) == "taurus"
    assert _longitude_in_sign(35.4) == pytest.approx(5.4)
    assert _longitude_to_sign(359.9) == "pisces"


def test_build_chart_json_handles_none_speed_and_orb_used(mock_natal_result, mock_birth_profile):
    mock_natal_result.planet_positions[0].speed_longitude = None
    mock_natal_result.aspects[0].orb_used = None
    mock_natal_result.aspects[0].orb = 1.25

    chart = build_chart_json(mock_natal_result, mock_birth_profile)

    assert chart["planets"][0]["speed"] is None
    assert chart["aspects"][0]["orb"] == pytest.approx(1.25)
