"""Cas golden traditionnels construits depuis les services runtime.

Les helpers exposent des faits de fixture explicites pour G1-G12, puis laissent
les calculateurs canoniques produire les contrats observes.
"""

from __future__ import annotations

from typing import Any

from app.domain.astrology.advanced_conditions.advanced_condition_engine import (
    AdvancedConditionEngine,
)
from app.domain.astrology.condition.planet_condition_profile_service import (
    PlanetConditionProfileService,
)
from app.domain.astrology.condition.planet_condition_signal_builder import (
    PlanetConditionSignalBuilder,
)
from app.domain.astrology.dignities.contracts import PlanetDignityInput, PlanetDignityResult
from app.domain.astrology.dignities.planet_dignity_scoring_service import (
    PlanetDignityScoringService,
)
from app.domain.astrology.dignities.sect_calculator import SectCalculator
from app.domain.astrology.dominance.planet_dominance_engine import PlanetDominanceEngine
from app.domain.astrology.house_ruler_resolver import HouseRulerResult
from app.domain.astrology.interpretation_adapters import InterpretationAdapterEngine
from app.domain.astrology.natal_calculation import AspectResult, PlanetPosition, build_natal_result
from app.domain.astrology.natal_preparation import BirthInput
from app.domain.astrology.runtime.house_runtime_data import (
    HouseOccupantRuntimeData,
    HouseRuntimeData,
)
from app.domain.astrology.runtime.runtime_reference import AstrologyRuntimeReference
from app.services.chart.json_builder import build_chart_json
from app.services.user_profile.birth_profile_service import UserBirthProfileData
from tests.factories.astrology_runtime_reference_factory import (
    complete_reference_with_planet_sect_rules,
)
from tests.unit.domain.astrology.fixtures.golden_snapshot import normalize_golden_value

story_evidence_path = (
    "_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-after.json"
)


def planet(
    planet_code: str,
    longitude: float,
    sign_code: str,
    house_number: int,
    *,
    speed_longitude: float | None = 0.1,
    is_retrograde: bool | None = False,
) -> PlanetDignityInput:
    """Construit une position de dignite explicite pour un cas golden."""
    return PlanetDignityInput(
        planet_code=planet_code,
        longitude=longitude,
        sign_code=sign_code,
        house_number=house_number,
        speed_longitude=speed_longitude,
        is_retrograde=is_retrograde,
    )


def traditional_reference() -> AstrologyRuntimeReference:
    """Ajoute les regles runtime explicites de secte planetaire aux fixtures."""
    return complete_reference_with_planet_sect_rules()


def observed_chart_sect(sun_house_number: int) -> dict[str, Any]:
    """Calcule la secte chart-level depuis le calculateur canonique."""
    result = SectCalculator().calculate(
        (planet("sun", 120.0, "leo", sun_house_number),),
        traditional_reference().dignity_reference,
    )
    return normalize_golden_value(result)


def dignity_results(planets: tuple[PlanetDignityInput, ...]) -> tuple[PlanetDignityResult, ...]:
    """Calcule les dignites avec le service canonique de scoring."""
    return PlanetDignityScoringService().calculate(planets, traditional_reference())


def dignity_by_code(
    planets: tuple[PlanetDignityInput, ...],
    planet_code: str,
) -> PlanetDignityResult:
    """Retourne le resultat de dignite observe pour une planete de fixture."""
    return next(result for result in dignity_results(planets) if result.planet_code == planet_code)


def advanced_case(
    case_planets: tuple[PlanetDignityInput, ...],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Calcule conditions avancees et profils enrichis pour les positions donnees."""
    reference = traditional_reference()
    dignities = dignity_results(case_planets)
    profiles = PlanetConditionProfileService().calculate(dignities, reference)
    positions = tuple(
        PlanetPosition(
            planet_code=item.planet_code,
            longitude=item.longitude,
            sign_code=item.sign_code,
            house_number=item.house_number,
            speed_longitude=item.speed_longitude,
            is_retrograde=item.is_retrograde,
        )
        for item in case_planets
    )
    return AdvancedConditionEngine().calculate(
        runtime_reference=reference,
        planet_positions=positions,
        aspects=(),
        dignities=dignities,
        condition_profiles=profiles,
    )


def integrated_pipeline_summary() -> dict[str, Any]:
    """Execute le pipeline natal simplifie et retourne les champs contractuels."""
    birth_input = BirthInput(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
    )
    result = build_natal_result(
        birth_input,
        traditional_reference(),
        ruleset_version="1.0.0",
        engine="simplified",
        birth_lat=48.8566,
        birth_lon=2.3522,
    )
    birth_profile = UserBirthProfileData(
        birth_date="1990-06-15",
        birth_time="10:30",
        birth_place="Paris",
        birth_timezone="Europe/Paris",
        birth_lat=48.8566,
        birth_lon=2.3522,
    )
    chart_json = build_chart_json(result, birth_profile)
    first_planet = result.dignities[0].planet_code
    return normalize_golden_value(
        {
            "engine": result.engine,
            "dignity_sect": result.dignity_sect,
            "first_planet": first_planet,
            "first_planet_sect_condition": result.dignities[0].sect_condition,
            "advanced_condition_codes": [
                item.condition_code for item in result.advanced_conditions
            ],
            "condition_profile_planets": [
                item.planet_code for item in result.condition_profiles[:3]
            ],
            "condition_signal_planets": [item.planet_code for item in result.condition_signals[:3]],
            "dominant_planets": {
                "top_planet": result.dominant_planets.top_planet_code
                if result.dominant_planets is not None
                else None,
                "chart_ruler": result.dominant_planets.chart_ruler_code
                if result.dominant_planets is not None
                else None,
            },
            "interpretation_adapter": {
                "signals": [item.signal_code for item in result.interpretation_adapter.signals]
                if result.interpretation_adapter is not None
                else [],
                "critical_patterns": list(result.interpretation_adapter.critical_patterns)
                if result.interpretation_adapter is not None
                else [],
            },
            "json_projection": {
                "sect": chart_json["dignities"]["sect"],
                "first_planet_sect_condition": chart_json["dignities"]["planets"][first_planet][
                    "sect_condition"
                ],
                "advanced_conditions": [
                    item["condition_code"] for item in chart_json["advanced_conditions"]
                ],
                "dominant_planets": {
                    "top_planet": chart_json["dominant_planets"]["top_planet"],
                    "chart_ruler": chart_json["dominant_planets"]["chart_ruler"],
                    "most_elevated_planet": chart_json["dominant_planets"]["most_elevated_planet"],
                    "planet_codes": [
                        item["planet"] for item in chart_json["dominant_planets"]["planets"]
                    ],
                },
                "interpretation_adapter": {
                    "signals": [
                        item["signal"] for item in chart_json["interpretation_adapter"]["signals"]
                    ],
                    "critical_patterns": chart_json["interpretation_adapter"]["critical_patterns"],
                },
            },
            "deterministic_downstream": adapter_fixture_summary(),
        }
    )


def adapter_fixture_summary() -> dict[str, Any]:
    """Construit une surface aval stable pour dominance et adaptateur."""
    reference = traditional_reference()
    case_planets = (
        planet("sun", 120.0, "leo", 10),
        planet("mars", 15.0, "aries", 1),
    )
    dignities = dignity_results(case_planets)
    profiles = PlanetConditionProfileService().calculate(dignities, reference)
    positions = (
        PlanetPosition(planet_code="sun", longitude=120.0, sign_code="leo", house_number=10),
        PlanetPosition(planet_code="mars", longitude=15.0, sign_code="aries", house_number=1),
    )
    houses = (
        HouseRuntimeData(
            number=1,
            cusp_longitude=0.0,
            occupants=[HouseOccupantRuntimeData("mars", "aries", 15.0)],
        ),
        HouseRuntimeData(
            number=10,
            cusp_longitude=90.0,
            occupants=[HouseOccupantRuntimeData("sun", "leo", 120.0)],
        ),
    )
    house_rulers = (
        HouseRulerResult(
            house_number=1,
            cusp_sign="aries",
            ruler_planet="mars",
            ruler_planet_sign="aries",
            ruler_planet_house=1,
        ),
        HouseRulerResult(
            house_number=10,
            cusp_sign="cancer",
            ruler_planet="moon",
            ruler_planet_sign="cancer",
            ruler_planet_house=10,
        ),
    )
    aspects = (
        AspectResult(
            aspect_code="conjunction",
            planet_a="sun",
            planet_b="mars",
            angle=0.0,
            orb=1.0,
            orb_used=1.0,
            orb_max=8.0,
            family="major",
            is_major=True,
            is_minor=False,
            default_valence="contextual",
            interpretive_valence="fusion",
            energy_type="fusion",
        ),
    )
    advanced_conditions, profiles = AdvancedConditionEngine().calculate(
        runtime_reference=reference,
        planet_positions=positions,
        aspects=aspects,
        dignities=dignities,
        condition_profiles=profiles,
    )
    signals = PlanetConditionSignalBuilder().build(profiles, reference)
    dominance = PlanetDominanceEngine().calculate(
        runtime_reference=reference,
        planet_positions=positions,
        houses=houses,
        house_rulers=house_rulers,
        condition_profiles=profiles,
        advanced_conditions=advanced_conditions,
        aspects=aspects,
    )
    adapter = InterpretationAdapterEngine().calculate(
        runtime_reference=reference,
        planet_positions=positions,
        aspects=aspects,
        dignities=dignities,
        condition_profiles=profiles,
        condition_signals=signals,
        advanced_conditions=advanced_conditions,
        dominant_planets=dominance,
    )
    return normalize_golden_value(
        {
            "condition_profiles": [item.planet_code for item in profiles],
            "condition_signals": {
                item.planet_code: [signal.code for signal in item.signals] for item in signals
            },
            "dominance": {
                "top_planet": dominance.top_planet_code,
                "chart_ruler": dominance.chart_ruler_code,
                "planets": [item.planet_code for item in dominance.planets],
            },
            "interpretation_adapter": {
                "signals": [item.signal_code for item in adapter.signals],
                "dominant_topics": list(adapter.dominant_topics),
                "critical_patterns": list(adapter.critical_patterns),
            },
        }
    )


def golden_cases() -> list[dict[str, Any]]:
    """Retourne les sorties curates G1-G12 sous forme comparable."""
    day_diurnal = (planet("sun", 120.0, "leo", 10),)
    night_nocturnal = (
        planet("sun", 120.0, "leo", 2),
        planet("moon", 95.0, "cancer", 3),
    )
    night_diurnal = (
        planet("sun", 120.0, "leo", 2),
        planet("jupiter", 120.0, "leo", 11),
    )
    day_nocturnal = (
        planet("sun", 120.0, "leo", 10),
        planet("moon", 95.0, "cancer", 3),
    )
    hayz_complete = (planet("sun", 120.0, "leo", 10),)
    hayz_incomplete = (planet("sun", 35.0, "taurus", 10),)
    joy_case = (
        planet("sun", 120.0, "leo", 10),
        planet("moon", 95.0, "cancer", 3),
    )
    mercury_case = (
        planet("sun", 120.0, "leo", 10),
        planet("mercury", 80.0, "gemini", 1),
    )
    essential_case = (planet("sun", 120.0, "leo", 10),)

    g7_conditions, g7_profiles = advanced_case(hayz_complete)
    g8_conditions, g8_profiles = advanced_case(hayz_incomplete)
    g9_result = dignity_by_code(joy_case, "moon")
    g9_profiles = PlanetConditionProfileService().calculate(
        dignity_results(joy_case), traditional_reference()
    )
    g11_result = dignity_by_code(essential_case, "sun")

    return [
        _case("G1", "synthetic_domain", ("dignities.sect",), "day chart", observed_chart_sect(10)),
        _case("G2", "synthetic_domain", ("dignities.sect",), "night chart", observed_chart_sect(2)),
        _case(
            "G3",
            "synthetic_domain",
            ("dignities.planets[*].sect_condition",),
            "diurnal planet in day chart",
            _sect_condition_summary(dignity_by_code(day_diurnal, "sun")),
        ),
        _case(
            "G4",
            "synthetic_domain",
            ("dignities.planets[*].sect_condition",),
            "nocturnal planet in night chart",
            _sect_condition_summary(dignity_by_code(night_nocturnal, "moon")),
        ),
        _case(
            "G5",
            "synthetic_domain",
            ("sect_condition", "advanced_conditions.out_of_sect"),
            "diurnal planet out of sect in night chart",
            _advanced_summary(night_diurnal, "jupiter"),
        ),
        _case(
            "G6",
            "synthetic_domain",
            ("sect_condition", "advanced_conditions.out_of_sect"),
            "nocturnal planet out of sect in day chart",
            _advanced_summary(day_nocturnal, "moon"),
        ),
        _case(
            "G7",
            "synthetic_domain",
            ("advanced_conditions.hayz",),
            "complete hayz",
            {
                "condition_codes": [item.condition_code for item in g7_conditions],
                "profile_breakdown": _profile_breakdown(g7_profiles, "sun"),
                "condition_signals": _signal_codes(g7_profiles, "sun"),
            },
        ),
        _case(
            "G8",
            "synthetic_domain",
            ("sect_condition", "advanced_conditions.hayz"),
            "in-sect without non-sect hayz factors",
            {
                "sect_condition": _sect_condition_summary(dignity_by_code(hayz_incomplete, "sun")),
                "condition_codes": [item.condition_code for item in g8_conditions],
                "profile_breakdown": _profile_breakdown(g8_profiles, "sun"),
                "condition_signals": _signal_codes(g8_profiles, "sun"),
            },
        ),
        _case(
            "G9",
            "synthetic_domain",
            ("dignities.accidental_breakdown", "planet_condition_profiles"),
            "planetary rejoicing",
            {
                "accidental_breakdown": _breakdown_codes(g9_result.accidental_breakdown),
                "accidental_score": g9_result.accidental_score,
                "profile_breakdown": _profile_breakdown(g9_profiles, "moon"),
            },
        ),
        _case(
            "G10",
            "synthetic_domain",
            ("dignities.planets[*].sect_condition",),
            "runtime-backed Mercury classification",
            _sect_condition_summary(dignity_by_code(mercury_case, "mercury")),
        ),
        _case(
            "G11",
            "synthetic_domain",
            ("dignities.essential_breakdown",),
            "essential dignity stability",
            {
                "essential_breakdown": _breakdown_codes(g11_result.essential_breakdown),
                "essential_score": g11_result.essential_score,
                "functional_strength_score": g11_result.functional_strength_score,
                "expression_quality_score": g11_result.expression_quality_score,
                "intensity_score": g11_result.intensity_score,
            },
        ),
        _case(
            "G12",
            "integrated_natal",
            (
                "NatalResult",
                "planet_condition_profiles",
                "planet_condition_signals",
                "dominant_planets",
                "interpretation_adapter",
                "json_builder",
            ),
            "full pipeline and public JSON projection",
            integrated_pipeline_summary(),
        ),
    ]


def _case(
    case_id: str,
    fixture_type: str,
    targeted_contracts: tuple[str, ...],
    expected_summary: str,
    observed_summary: dict[str, Any],
) -> dict[str, Any]:
    """Construit une entree de snapshot golden compacte."""
    return normalize_golden_value(
        {
            "case_id": case_id,
            "fixture_type": fixture_type,
            "targeted_contracts": targeted_contracts,
            "expected_summary": expected_summary,
            "observed_summary": observed_summary,
            "assertions": sorted(targeted_contracts),
        }
    )


def _sect_condition_summary(result: PlanetDignityResult) -> dict[str, Any]:
    """Retourne la condition de secte et les scores utiles d'une planete."""
    return normalize_golden_value(
        {
            "planet_code": result.planet_code,
            "chart_sect": result.chart_sect,
            "sect_condition": result.sect_condition,
            "essential_score": result.essential_score,
            "accidental_score": result.accidental_score,
            "total_score": result.total_score,
        }
    )


def _advanced_summary(
    case_planets: tuple[PlanetDignityInput, ...],
    planet_code: str,
) -> dict[str, Any]:
    """Retourne les conditions avancees observees pour une planete."""
    conditions, _profiles = advanced_case(case_planets)
    result = dignity_by_code(case_planets, planet_code)
    return normalize_golden_value(
        {
            "sect_condition": result.sect_condition,
            "condition_codes": [
                item.condition_code for item in conditions if item.source_planet_code == planet_code
            ],
        }
    )


def _breakdown_codes(items: tuple[Any, ...]) -> list[dict[str, Any]]:
    """Compacte les breakdowns de dignite en codes, sources et scores."""
    return normalize_golden_value(
        [
            {
                "code": item.dignity_type_code,
                "score": item.score_value,
                "source": item.source,
            }
            for item in items
        ]
    )


def _profile_breakdown(profiles: tuple[Any, ...], planet_code: str) -> list[dict[str, Any]]:
    """Retourne les contributions conditionnelles observees pour une planete."""
    profile = next(item for item in profiles if item.planet_code == planet_code)
    return normalize_golden_value(
        [
            {
                "family": item.dignity_family,
                "code": item.dignity_type_code,
                "source": item.source,
                "score": item.score_value,
            }
            for item in profile.breakdown
        ]
    )


def _signal_codes(profiles: tuple[Any, ...], planet_code: str) -> list[str]:
    """Retourne les signaux conditionnels gouvernes pour une planete."""
    signal_sets = PlanetConditionSignalBuilder().build(profiles, traditional_reference())
    signal_set = next(item for item in signal_sets if item.planet_code == planet_code)
    return sorted(signal.code for signal in signal_set.signals)


def snapshot_payload() -> dict[str, Any]:
    """Produit le snapshot complet attendu par la story CS-200."""
    cases = golden_cases()
    return {
        "snapshot": "CS-200 traditional golden cases",
        "float_policy": "round floats to 6 decimals",
        "volatile_fields_excluded": [
            "database ids",
            "timestamps",
            "full ephemeris traces",
            "localized labels unrelated to contracts",
        ],
        "case_count": len(cases),
        "cases": cases,
    }
