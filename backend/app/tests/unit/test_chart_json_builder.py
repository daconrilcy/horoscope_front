"""Tests de projection JSON publique du theme natal."""

from unittest.mock import MagicMock

import pytest

from app.domain.astrology.advanced_conditions.contracts import (
    AdvancedPlanetaryCondition,
    PlanetConditionAxisImpact,
)
from app.domain.astrology.condition.contracts import (
    PlanetConditionBreakdownItem,
    PlanetConditionExplanationFact,
    PlanetConditionProfile,
    PlanetConditionSignal,
    PlanetConditionSignalSet,
)
from app.domain.astrology.dignities.contracts import (
    AccidentalDignityMatch,
    EssentialDignityMatch,
    PlanetDignityResult,
)
from app.domain.astrology.dominance.contracts import (
    DominantPlanetsResult,
    PlanetDominanceFactor,
    PlanetDominanceResult,
)
from app.domain.astrology.house_ruler_resolver import HouseRulerResult
from app.domain.astrology.interpretation.house_strength_contracts import (
    HouseStrengthLevel,
    HouseStrengthReason,
)
from app.domain.astrology.interpretation_adapters.contracts import (
    InterpretationAdapterResult,
    InterpretationSignal,
    InterpretationThemeActivation,
)
from app.domain.astrology.natal_calculation import AspectResult
from app.domain.astrology.runtime.house_runtime_data import (
    HouseAxisRuntimeData,
    HouseOccupantRuntimeData,
    HouseRulerRuntimeData,
    HouseStrengthRuntimeData,
)
from app.services.chart.json_builder import (
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
    houses[0].ruler = HouseRulerRuntimeData(planet="saturn", sign="aries", house=9)
    houses[9].ruler = HouseRulerRuntimeData(planet="venus", sign="taurus", house=10)

    result.houses = houses
    result.house_rulers = [
        HouseRulerResult(
            house_number=1,
            cusp_sign="capricorn",
            ruler_planet="saturn",
            ruler_planet_sign="aries",
            ruler_planet_house=9,
        ),
        HouseRulerResult(
            house_number=10,
            cusp_sign="libra",
            ruler_planet="venus",
            ruler_planet_sign="taurus",
            ruler_planet_house=10,
        ),
    ]

    # Aspects
    a1 = AspectResult(
        aspect_code="trine",
        planet_a="sun",
        planet_b="moon",
        angle=120.3,
        orb=0.3,
        orb_used=0.3,
        orb_max=6.0,
        family="major",
        is_major=True,
        is_minor=False,
        default_valence="positive",
        interpretive_valence="harmonious",
        energy_type="harmonious_flow",
    )

    result.aspects = [a1]
    result.dignities = [
        PlanetDignityResult(
            planet_code="sun",
            score_profile="traditional_standard",
            tradition="traditional",
            reference_version="v1.2",
            sect="day",
            essential_score=5,
            accidental_score=4,
            total_score=9,
            functional_strength_score=1.9,
            expression_quality_score=1.5,
            intensity_score=1.5,
            essential_breakdown=(
                EssentialDignityMatch(
                    dignity_type_code="domicile",
                    score_value=5,
                    source="essential_rule",
                    reason="sun in taurus: domicile",
                    sign_code="taurus",
                    degree_start=0,
                    degree_end=30,
                ),
            ),
            accidental_breakdown=(
                AccidentalDignityMatch(
                    dignity_type_code="angular_house",
                    score_value=4,
                    source="house_modality",
                    reason="sun matches angular_house: house_codes=(1, 4, 7, 10)",
                    condition="house_codes=(1, 4, 7, 10)",
                ),
            ),
        )
    ]
    result.condition_profiles = [
        PlanetConditionProfile(
            planet_code="sun",
            score_profile="traditional_standard",
            tradition="traditional",
            reference_version="v1.2",
            sect="day",
            functional_strength=1.9,
            visibility=1.0,
            stability=0.5,
            intensity=1.5,
            coherence=0.4,
            support=0.7,
            constraint=0.3,
            ranking_score=5.7,
            condition_level="strong",
            breakdown=(
                PlanetConditionBreakdownItem(
                    dignity_family="essential",
                    dignity_type_code="domicile",
                    source="essential_rule",
                    reason="sun in taurus: domicile",
                    score_value=5,
                    functional_strength=1.0,
                    visibility=0.5,
                    stability=0.4,
                    intensity=0.6,
                    coherence=0.3,
                    support=0.6,
                    constraint=0.1,
                ),
                PlanetConditionBreakdownItem(
                    dignity_family="accidental",
                    dignity_type_code="angular_house",
                    source="house_modality",
                    reason="sun matches angular_house: house_codes=(1, 4, 7, 10)",
                    score_value=4,
                    functional_strength=0.9,
                    visibility=0.5,
                    stability=0.1,
                    intensity=0.9,
                    coherence=0.1,
                    support=0.1,
                    constraint=0.2,
                ),
            ),
            explanation_facts=(
                PlanetConditionExplanationFact("essential_match_count", "1"),
                PlanetConditionExplanationFact("accidental_match_count", "1"),
                PlanetConditionExplanationFact("ranking_score", "5.7"),
            ),
        )
    ]
    result.condition_signals = [
        PlanetConditionSignalSet(
            planet_code="sun",
            score_profile="traditional_standard",
            tradition="traditional",
            reference_version="v1.2",
            signals=(
                PlanetConditionSignal(
                    code="visibility_high",
                    label="Visibility high",
                    axis="visibility",
                    level="high",
                    level_min=0.5,
                    level_max=100.0,
                    axis_value=1.0,
                    interpretation_use="surface_condition_axis",
                    priority_weight=30.0,
                    prompt_hint="visibility_emphasized",
                ),
            ),
        )
    ]
    result.advanced_conditions = [
        AdvancedPlanetaryCondition(
            condition_code="hayz",
            condition_type_code="hayz",
            source_planet_code="sun",
            target_planet_code=None,
            score_profile="traditional_advanced_v1",
            reference_version="v1",
            score_impact=1.5,
            ranking_weight=1.1,
            axes_impact=PlanetConditionAxisImpact(
                functional_strength_delta=0.3,
                visibility_delta=0.2,
                stability_delta=0.4,
                intensity_delta=0.1,
                coherence_delta=0.3,
                support_delta=0.2,
                constraint_delta=0.0,
            ),
            reason="sun matches accidental dignity hayz.",
        )
    ]
    result.dominant_planets = DominantPlanetsResult(
        score_profile_code="natal_standard_v1",
        tradition_code="modern",
        reference_version_code="v1",
        planets=(
            PlanetDominanceResult(
                planet_code="sun",
                total_score=0.75,
                rank=1,
                dominance_level="high",
                factors=(
                    PlanetDominanceFactor(
                        factor_code="chart_ruler",
                        raw_value=1.0,
                        normalized_value=1.0,
                        weight=1.4,
                        weighted_score=1.4,
                        reason="sun rules the Ascendant sign.",
                    ),
                ),
                explanation_facts=("sun rules the Ascendant sign.",),
            ),
        ),
        top_planet_code="sun",
        chart_ruler_code="sun",
        most_elevated_planet_code="sun",
    )
    result.interpretation_adapter = InterpretationAdapterResult(
        signals=(
            InterpretationSignal(
                signal_code="dominant_mars_signature",
                theme_code="drive_assertion_action",
                source_type="dominant_planet",
                source_code="mars",
                priority="critical",
                priority_rank=10,
                weight=1.0,
                semantic_category="planetary_signature",
                theme_category="behavioral",
                explanation_fact="dominant_planet:mars:rank=1:level=dominant",
            ),
        ),
        activated_themes=(
            InterpretationThemeActivation(
                theme_code="drive_assertion_action",
                theme_category="behavioral",
                activation_score=1.0,
                priority="critical",
                priority_rank=10,
                contributing_signals=("dominant_mars_signature",),
            ),
        ),
        dominant_topics=("drive_assertion_action",),
        dominant_axes=("behavioral",),
        tension_patterns=(),
        support_patterns=(),
        critical_patterns=("dominant_mars_signature",),
        narrative_priorities=("dominant_mars_signature", "drive_assertion_action"),
    )

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
    assert sun["sign_label"] == "taurus"
    assert sun["longitude"] == 35.4
    assert sun["longitude_in_sign"] == pytest.approx(5.4)
    assert sun["house"] == 10
    assert sun["is_retrograde"] is False

    # Houses
    assert len(chart["houses"]) == 12
    h1 = next(h for h in chart["houses"] if h["number"] == 1)
    assert h1["sign"] == "capricorn"
    assert h1["cusp_sign_label"] == "capricorn"
    assert chart["house_rulers"] == [
        {
            "house_number": 1,
            "cusp_sign": "capricorn",
            "cusp_sign_label": "capricorn",
            "ruler_planet": "saturn",
            "ruler_planet_sign": "aries",
            "ruler_planet_sign_label": "aries",
            "ruler_planet_house": 9,
        },
        {
            "house_number": 10,
            "cusp_sign": "libra",
            "cusp_sign_label": "libra",
            "ruler_planet": "venus",
            "ruler_planet_sign": "taurus",
            "ruler_planet_sign_label": "taurus",
            "ruler_planet_house": 10,
        },
    ]

    # Aspects
    assert len(chart["aspects"]) == 1
    assert chart["aspects"][0]["type"] == "trine"
    assert chart["aspects"][0]["aspect_code"] == "trine"
    assert chart["aspects"][0]["planet_a"] == "sun"
    assert chart["aspects"][0]["orb"] == 0.3
    assert chart["aspects"][0]["orb_used"] == 0.3
    assert chart["aspects"][0]["orb_max"] == 6.0
    assert chart["aspects"][0]["family"] == "major"
    assert chart["aspects"][0]["strength_level"] == "dominant"
    assert chart["aspects"][0]["normalized_strength"] == 1.0
    assert chart["aspects"][0]["is_exact"] is True
    assert chart["aspects"][0]["is_tight"] is True
    assert chart["aspects"][0]["interpretive_valence"] == "harmonious"
    assert chart["aspects"][0]["energy_type"] == "harmonious_flow"
    assert chart["aspects"][0]["applying"] is None
    assert chart["meta"]["aspects_applying_available"] is False
    assert chart["dignities"]["score_profile"] == "traditional_standard"
    assert chart["dignities"]["planets"]["sun"]["total_score"] == 9
    assert chart["dignities"]["planets"]["sun"]["essential_breakdown"][0]["type"] == "domicile"
    assert (
        chart["dignities"]["planets"]["sun"]["essential_breakdown"][0]["reason"]
        == "sun in taurus: domicile"
    )
    assert chart["planet_condition_profiles"]["score_profile"] == "traditional_standard"
    condition_sun = chart["planet_condition_profiles"]["planets"]["sun"]
    assert condition_sun["planet_code"] == "sun"
    assert condition_sun["score_profile"] == "traditional_standard"
    assert condition_sun["tradition"] == "traditional"
    assert condition_sun["reference_version"] == "v1.2"
    assert condition_sun["sect"] == "day"
    assert condition_sun["visibility"] == 1.0
    assert condition_sun["ranking_score"] == 5.7
    assert condition_sun["condition_level"] == "strong"
    assert condition_sun["breakdown"][0]["dignity_type_code"] == "domicile"
    assert condition_sun["breakdown"][1]["dignity_type_code"] == "angular_house"
    assert sum(item["visibility"] for item in condition_sun["breakdown"]) == pytest.approx(
        condition_sun["visibility"]
    )
    assert sum(item["stability"] for item in condition_sun["breakdown"]) == pytest.approx(
        condition_sun["stability"]
    )
    assert sum(item["coherence"] for item in condition_sun["breakdown"]) == pytest.approx(
        condition_sun["coherence"]
    )
    assert sum(item["support"] for item in condition_sun["breakdown"]) == pytest.approx(
        condition_sun["support"]
    )
    assert sum(item["constraint"] for item in condition_sun["breakdown"]) == pytest.approx(
        condition_sun["constraint"]
    )
    assert condition_sun["explanation_facts"][0] == {
        "fact_type": "essential_match_count",
        "value": "1",
    }
    assert condition_sun["explanation_facts"][1] == {
        "fact_type": "accidental_match_count",
        "value": "1",
    }
    assert chart["planet_condition_signals"]["score_profile"] == "traditional_standard"
    signal_sun = chart["planet_condition_signals"]["planets"]["sun"]
    assert signal_sun["planet_code"] == "sun"
    assert signal_sun["signals"] == [
        {
            "code": "visibility_high",
            "label": "Visibility high",
            "axis": "visibility",
            "level": "high",
            "level_min": 0.5,
            "level_max": 100.0,
            "axis_value": 1.0,
            "interpretation_use": "surface_condition_axis",
            "priority_weight": 30.0,
            "prompt_hint": "visibility_emphasized",
        }
    ]
    assert chart["dominant_planets"]["score_profile"] == "natal_standard_v1"
    assert chart["advanced_conditions"] == [
        {
            "condition_code": "hayz",
            "condition_type_code": "hayz",
            "source_planet_code": "sun",
            "target_planet_code": None,
            "score_profile": "traditional_advanced_v1",
            "reference_version": "v1",
            "score_impact": 1.5,
            "ranking_weight": 1.1,
            "axes_impact": {
                "functional_strength": 0.3,
                "visibility": 0.2,
                "stability": 0.4,
                "intensity": 0.1,
                "coherence": 0.3,
                "support": 0.2,
                "constraint": 0.0,
            },
            "reason": "sun matches accidental dignity hayz.",
        }
    ]
    assert chart["dominant_planets"]["chart_ruler"] == "sun"
    assert chart["dominant_planets"]["most_elevated_planet"] == "sun"
    assert chart["dominant_planets"]["top_planet"] == "sun"
    dominance_sun = chart["dominant_planets"]["planets"][0]
    assert dominance_sun["planet"] == "sun"
    assert dominance_sun["rank"] == 1
    assert dominance_sun["total_score"] == 0.75
    assert dominance_sun["dominance_level"] == "high"
    assert dominance_sun["factors"][0] == {
        "factor": "chart_ruler",
        "raw_value": 1.0,
        "normalized_value": 1.0,
        "weight": 1.4,
        "weighted_score": 1.4,
        "reason": "sun rules the Ascendant sign.",
    }
    assert dominance_sun["explanation_facts"] == ["sun rules the Ascendant sign."]
    assert chart["interpretation_adapter"]["signals"] == [
        {
            "signal": "dominant_mars_signature",
            "theme": "drive_assertion_action",
            "source_type": "dominant_planet",
            "source_code": "mars",
            "priority": "critical",
            "priority_rank": 10,
            "weight": 1.0,
            "semantic_category": "planetary_signature",
            "theme_category": "behavioral",
            "explanation_fact": "dominant_planet:mars:rank=1:level=dominant",
        }
    ]
    assert chart["interpretation_adapter"]["activated_themes"] == [
        {
            "theme": "drive_assertion_action",
            "theme_category": "behavioral",
            "activation_score": 1.0,
            "priority": "critical",
            "priority_rank": 10,
            "contributing_signals": ["dominant_mars_signature"],
        }
    ]
    assert chart["interpretation_adapter"]["critical_patterns"] == ["dominant_mars_signature"]

    # Angles
    assert chart["angles"]["ASC"]["sign"] == "capricorn"
    assert chart["angles"]["ASC"]["sign_label"] == "capricorn"
    assert chart["angles"]["MC"]["sign"] == "libra"
    assert chart["angles"]["DSC"]["sign"] == "cancer"
    assert chart["angles"]["IC"]["sign"] == "aries"


def test_build_chart_json_projects_rich_runtime_house(mock_natal_result, mock_birth_profile):
    rich_house = mock_natal_result.houses[0]
    rich_house.number = 1
    rich_house.cusp_longitude = 12.4
    rich_house.cusp_sign = "aries"
    rich_house.contained_signs = ["aries", "taurus"]
    rich_house.intercepted_signs = []
    rich_house.ruler = HouseRulerRuntimeData(planet="mars", sign="virgo", house=6)
    rich_house.occupants = [
        HouseOccupantRuntimeData(
            planet="sun",
            sign="aries",
            longitude=12.4,
            is_dominant=True,
        )
    ]
    rich_house.axis = HouseAxisRuntimeData(opposite_house=7, theme="self_relationship")
    rich_house.strength = HouseStrengthRuntimeData.from_parts(
        normalized_score=0.81,
        reasons=(HouseStrengthReason.ANGULAR_HOUSE,),
    )

    chart = build_chart_json(mock_natal_result, mock_birth_profile)
    house = next(item for item in chart["houses"] if item["number"] == 1)

    assert house == {
        "number": 1,
        "cusp_longitude": 12.4,
        "cusp_sign": "aries",
        "cusp_sign_label": "aries",
        "sign": "aries",
        "contained_signs": ["aries", "taurus"],
        "intercepted_signs": [],
        "ruler": {"planet": "mars", "sign": "virgo", "house": 6},
        "occupants": [
            {
                "planet": "sun",
                "sign": "aries",
                "longitude": 12.4,
                "is_dominant": True,
            }
        ],
        "axis": {"opposite_house": 7, "theme": "self_relationship"},
        "strength": {
            "score": 0.81,
            "level": HouseStrengthLevel.DOMINANT.value,
            "dominant": True,
            "reasons": ["angular_house"],
        },
    }


def test_house_rulers_legacy_payload_projects_canonical_runtime_ruler(
    mock_natal_result, mock_birth_profile
):
    mock_natal_result.houses[0].ruler = HouseRulerRuntimeData(planet="mars", sign="virgo", house=6)
    mock_natal_result.house_rulers[0] = HouseRulerResult(
        house_number=1,
        cusp_sign="capricorn",
        ruler_planet="saturn",
        ruler_planet_sign="aries",
        ruler_planet_house=9,
    )

    chart = build_chart_json(mock_natal_result, mock_birth_profile)

    assert chart["house_rulers"][0] == {
        "house_number": 1,
        "cusp_sign": "capricorn",
        "cusp_sign_label": "capricorn",
        "ruler_planet": "mars",
        "ruler_planet_sign": "virgo",
        "ruler_planet_sign_label": "virgo",
        "ruler_planet_house": 6,
    }


def test_house_rulers_legacy_payload_stays_consistent_with_runtime_houses(
    mock_natal_result, mock_birth_profile
):
    chart = build_chart_json(mock_natal_result, mock_birth_profile)
    houses_by_number = {house["number"]: house for house in chart["houses"]}

    for legacy_ruler in chart["house_rulers"]:
        house = houses_by_number[legacy_ruler["house_number"]]
        assert legacy_ruler["house_number"] == house["number"]
        assert legacy_ruler["cusp_sign"] == house["cusp_sign"]
        assert legacy_ruler["ruler_planet"] == house["ruler"]["planet"]
        assert legacy_ruler["ruler_planet_sign"] == house["ruler"]["sign"]
        assert legacy_ruler["ruler_planet_house"] == house["ruler"]["house"]


def test_house_rulers_legacy_payload_ignores_stale_result_when_runtime_ruler_missing(
    mock_natal_result, mock_birth_profile
):
    mock_natal_result.house_rulers.append(
        HouseRulerResult(
            house_number=2,
            cusp_sign="aquarius",
            ruler_planet="saturn",
            ruler_planet_sign="aries",
            ruler_planet_house=9,
        )
    )

    chart = build_chart_json(mock_natal_result, mock_birth_profile)
    expected_count = sum(1 for house in chart["houses"] if house["ruler"] is not None)

    assert len(chart["house_rulers"]) == expected_count
    assert all(legacy_ruler["house_number"] != 2 for legacy_ruler in chart["house_rulers"])


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
    assert chart["house_rulers"] == []

    # Angles should be None
    assert chart["angles"]["ASC"] is None
    assert chart["angles"]["MC"] is None
    assert chart["dominant_planets"] is None
    assert chart["interpretation_adapter"] is None


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
    assert chart["dominant_planets"] is None


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
        "house_rulers": [
            {
                "house_number": 1,
                "cusp_sign": "capricorn",
                "ruler_planet": "saturn",
                "ruler_planet_sign": "aries",
                "ruler_planet_house": 9,
            }
        ],
    }

    evidence = build_evidence_catalog(chart_json)

    # SUN, MOON, ASC, MC should be first (priority 0)
    assert evidence[0].startswith(("SUN_", "MOON_", "ASC_", "MC_"))

    # ASPECTS should be after H (priority 2)
    h_indexes = [i for i, x in enumerate(evidence) if "_H" in x and not x.startswith("HOUSE_")]
    aspect_indexes = [i for i, x in enumerate(evidence) if "ASPECT_" in x]
    assert min(aspect_indexes) > max(h_indexes)

    # HOUSE_1_IN_CAPRICORN should be last (priority 3)
    assert "HOUSE_1_IN_CAPRICORN" in evidence
    assert "HOUSE_1_RULER_SATURN" in evidence
    assert "HOUSE_1_RULER_SATURN_H9" in evidence
    assert "HOUSE_1_RULER_SATURN_ARIES" in evidence


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
    from app.services.chart.json_builder import _longitude_in_sign, _longitude_to_sign

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


def test_build_chart_json_uses_resolved_sign_labels(mock_natal_result, mock_birth_profile):
    """Le JSON public conserve les codes et ajoute les libellés localisés."""
    from app.services.reference_data.astrology_translation_resolver import AstrologyLabels

    labels = AstrologyLabels(
        effective_language_code="en",
        sign_labels={
            "aries": "Aries",
            "taurus": "Taurus",
            "capricorn": "Capricorn",
            "libra": "Libra",
            "cancer": "Cancer",
        },
    )

    chart = build_chart_json(mock_natal_result, mock_birth_profile, labels=labels)

    assert chart["planets"][0]["sign"] == "taurus"
    assert chart["planets"][0]["sign_label"] == "Taurus"
    assert chart["houses"][0]["cusp_sign"] == "capricorn"
    assert chart["houses"][0]["cusp_sign_label"] == "Capricorn"
    assert chart["house_rulers"][0]["ruler_planet_sign"] == "aries"
    assert chart["house_rulers"][0]["ruler_planet_sign_label"] == "Aries"
    assert chart["angles"]["ASC"]["sign"] == "capricorn"
    assert chart["angles"]["ASC"]["sign_label"] == "Capricorn"


def test_evidence_catalog_uses_chart_sign_labels() -> None:
    """Le catalogue d'évidence lit les libellés depuis le payload enrichi."""
    from app.services.chart.json_builder import build_enriched_evidence_catalog

    chart_json = {
        "planets": [
            {
                "code": "sun",
                "sign": "taurus",
                "sign_label": "Taurus",
                "house": 10,
                "is_retrograde": False,
            }
        ],
        "aspects": [],
        "angles": {"ASC": {"sign": "aries", "sign_label": "Aries"}},
        "houses": [{"number": 1, "cusp_sign": "capricorn", "cusp_sign_label": "Capricorn"}],
        "house_rulers": [
            {
                "house_number": 1,
                "cusp_sign": "capricorn",
                "cusp_sign_label": "Capricorn",
                "ruler_planet": "saturn",
                "ruler_planet_sign": "aries",
                "ruler_planet_sign_label": "Aries",
                "ruler_planet_house": 9,
            }
        ],
    }

    catalog = build_enriched_evidence_catalog(chart_json)

    assert "sun en Taurus" in catalog["SUN_TAURUS"]
    assert "Ascendant en Aries" in catalog["ASC_ARIES"]
    assert "Maison 1 en Capricorn" in catalog["HOUSE_1_IN_CAPRICORN"]
    assert "Maître de Maison 1 en Aries" in catalog["HOUSE_1_RULER_SATURN_ARIES"]
