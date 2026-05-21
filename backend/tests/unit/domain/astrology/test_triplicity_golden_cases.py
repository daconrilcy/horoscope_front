"""Cas golden CS-205 pour la triplicite essentielle dependante de la secte."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.domain.astrology.dignities.contracts import PlanetDignityResult
from app.domain.astrology.runtime.runtime_reference import (
    AstrologyRuntimeReference,
    TriplicityRulerReferenceData,
)
from tests.unit.domain.astrology.fixtures.golden_snapshot import (
    load_snapshot,
    normalize_golden_value,
)
from tests.unit.domain.astrology.fixtures.traditional_golden_cases import (
    dignity_results_with_reference,
    planet,
)
from tests.unit.domain.astrology.fixtures.triplicity_seed_cases import (
    seed_backed_triplicity_reference,
)

PROJECT_ROOT = Path(__file__).resolve().parents[5]
STORY_EVIDENCE_PATH = (
    PROJECT_ROOT / "_condamad/stories/CS-205-sect-aware-triplicity-golden-cases/evidence/"
    "triplicity-golden-after.json"
)
TRIPLICITY_ELEMENT = "fire"
TRIPLICITY_SIGN = "leo"


def test_runtime_assignments_expose_day_night_and_participating_roles() -> None:
    """Le runtime seed-backed expose les roles attendus sans table locale."""
    reference = seed_backed_triplicity_reference()

    roles = {
        ruler.role_code
        for ruler in reference.dignity_reference.triplicity_rulers
        if ruler.element_code == TRIPLICITY_ELEMENT
    }
    sects = {
        ruler.sect_code
        for ruler in reference.dignity_reference.triplicity_rulers
        if ruler.element_code == TRIPLICITY_ELEMENT
    }

    assert {"primary", "participating"}.issubset(roles)
    assert {"day", "night", "all"}.issubset(sects)


def test_day_chart_uses_day_triplicity_ruler() -> None:
    """G1 verrouille le maitre de triplicite diurne issu du runtime."""
    g1 = _case("G1_day_triplicity")

    assert g1["chart_sect"] == "day"
    assert g1["expected_triplicity_role"] == "primary"
    assert g1["observed"]["active_triplicity"] is True
    assert _triplicity_snapshot_item(g1)["score"] == 3


def test_night_chart_uses_night_triplicity_ruler() -> None:
    """G2 verrouille le maitre de triplicite nocturne issu du runtime."""
    g2 = _case("G2_night_triplicity")

    assert g2["chart_sect"] == "night"
    assert g2["expected_triplicity_role"] == "primary"
    assert g2["observed"]["active_triplicity"] is True
    assert g2["observed"]["essential_score"] == 3


def test_same_element_can_select_different_triplicity_ruler_by_sect() -> None:
    """G3 prouve que la meme triplicite feu change de maitre par secte."""
    g3 = _case("G3_same_element_different_sect")

    assert g3["element"] == TRIPLICITY_ELEMENT
    assert g3["day"]["planet_code"] != g3["night"]["planet_code"]
    assert g3["day"]["observed"]["active_triplicity"] is True
    assert g3["night"]["observed"]["active_triplicity"] is True


def test_participating_triplicity_ruler_behavior() -> None:
    """G4 documente et verrouille le participant si le profil le score."""
    g4 = _case("G4_participating_triplicity")

    assert g4["expected_triplicity_role"] == "participating"
    assert g4["participant_supported"] is True
    assert g4["participant_applied"] is True
    assert g4["observed"]["active_triplicity"] is True
    assert g4["observed"]["essential_score"] == 3


def test_non_ruler_does_not_receive_triplicity() -> None:
    """G5 prouve qu'une planete non maitresse active ne recoit pas la triplicite."""
    g5 = _case("G5_non_ruler_no_triplicity")

    assert g5["observed"]["active_triplicity"] is False
    assert not any(
        item["type_code"] == "triplicity" for item in g5["observed"]["essential_breakdown"]
    )


def test_scoring_service_uses_chart_sect_for_triplicity_selection() -> None:
    """G6 verrouille l'integration via PlanetDignityScoringService."""
    g6 = _case("G6_scoring_service_integration")

    assert g6["service_path"] == "PlanetDignityScoringService"
    assert g6["chart_sect_source"] == "ChartSectResult.chart_sect"
    assert g6["day"]["planet_code"] != g6["night"]["planet_code"]
    assert g6["day"]["observed"]["active_triplicity"] is True
    assert g6["night"]["observed"]["active_triplicity"] is True


def test_curated_triplicity_snapshot_matches_persistent_evidence() -> None:
    """Le snapshot CS-205 persistant reste identique aux sorties curates."""
    expected = load_snapshot(STORY_EVIDENCE_PATH)

    assert snapshot_payload() == expected


def make_day_triplicity_case() -> dict[str, Any]:
    """Construit G1 depuis le maitre diurne declare dans le runtime."""
    reference = seed_backed_triplicity_reference()
    ruler = _triplicity_ruler(reference, sect_code="day")
    return _triplicity_case(
        "G1_day_triplicity",
        reference,
        chart_sect="day",
        ruler=ruler,
    )


def make_night_triplicity_case() -> dict[str, Any]:
    """Construit G2 depuis le maitre nocturne declare dans le runtime."""
    reference = seed_backed_triplicity_reference()
    ruler = _triplicity_ruler(reference, sect_code="night")
    return _triplicity_case(
        "G2_night_triplicity",
        reference,
        chart_sect="night",
        ruler=ruler,
    )


def make_same_element_case() -> dict[str, Any]:
    """Construit G3 en comparant les deux sectes pour le meme element runtime."""
    day = make_day_triplicity_case()
    night = make_night_triplicity_case()
    return normalize_golden_value(
        {
            "case_id": "G3_same_element_different_sect",
            "element": TRIPLICITY_ELEMENT,
            "sign": TRIPLICITY_SIGN,
            "day": _compact_case(day),
            "night": _compact_case(night),
            "runtime_note": "day and night rulers are distinct in seed-backed runtime",
        }
    )


def make_participating_triplicity_case_if_supported() -> dict[str, Any]:
    """Construit G4 depuis le role participant declare dans le runtime."""
    reference = seed_backed_triplicity_reference()
    ruler = _triplicity_ruler(reference, sect_code="all")
    case = _triplicity_case(
        "G4_participating_triplicity",
        reference,
        chart_sect="day",
        ruler=ruler,
    )
    return normalize_golden_value(
        {
            **case,
            "participant_supported": True,
            "participant_applied": case["observed"]["active_triplicity"],
            "participant_note": (
                "runtime role `all` is consumed by the essential calculator and "
                "the active profile scores triplicity"
            ),
        }
    )


def make_non_triplicity_ruler_case() -> dict[str, Any]:
    """Construit G5 avec le maitre nocturne dans un theme diurne."""
    reference = seed_backed_triplicity_reference()
    inactive_ruler = _triplicity_ruler(reference, sect_code="night")
    return _triplicity_case(
        "G5_non_ruler_no_triplicity",
        reference,
        chart_sect="day",
        ruler=inactive_ruler,
    )


def make_scoring_service_integration_case() -> dict[str, Any]:
    """Construit G6 avec le service canonique sur les deux sectes."""
    day = make_day_triplicity_case()
    night = make_night_triplicity_case()
    return normalize_golden_value(
        {
            "case_id": "G6_scoring_service_integration",
            "service_path": "PlanetDignityScoringService",
            "chart_sect_source": "ChartSectResult.chart_sect",
            "day": _compact_case(day),
            "night": _compact_case(night),
        }
    )


def snapshot_payload() -> dict[str, Any]:
    """Produit le snapshot complet attendu par la story CS-205."""
    cases = [
        make_day_triplicity_case(),
        make_night_triplicity_case(),
        make_same_element_case(),
        make_participating_triplicity_case_if_supported(),
        make_non_triplicity_ruler_case(),
        make_scoring_service_integration_case(),
    ]
    return {
        "snapshot": "CS-205 sect-aware triplicity golden cases",
        "runtime_source": "AstrologyRuntimeReference.dignity_reference.triplicity_rulers",
        "chart_sect_source": "ChartSectResult.chart_sect",
        "float_policy": "round floats to 6 decimals",
        "volatile_fields_excluded": [
            "database ids",
            "timestamps",
            "full natal payload",
            "localized labels",
        ],
        "case_count": len(cases),
        "cases": cases,
    }


def _case(case_id: str) -> dict[str, Any]:
    """Retourne une entree de snapshot par identifiant de cas."""
    return next(item for item in snapshot_payload()["cases"] if item["case_id"] == case_id)


def _triplicity_case(
    case_id: str,
    reference: AstrologyRuntimeReference,
    *,
    chart_sect: str,
    ruler: TriplicityRulerReferenceData,
) -> dict[str, Any]:
    """Calcule un cas de triplicite depuis un ruler runtime explicite."""
    result = _result_for(reference, chart_sect=chart_sect, planet_code=ruler.planet_code)
    active_triplicity = _triplicity_match(result)
    return normalize_golden_value(
        {
            "case_id": case_id,
            "chart_sect": chart_sect,
            "element": ruler.element_code,
            "sign": TRIPLICITY_SIGN,
            "planet_code": ruler.planet_code,
            "expected_triplicity_role": ruler.role_code,
            "runtime_assignment": {
                "element_code": ruler.element_code,
                "sect_code": ruler.sect_code,
                "planet_code": ruler.planet_code,
                "role_code": ruler.role_code,
                "system_code": ruler.system_code,
            },
            "observed": {
                "active_triplicity": active_triplicity is not None,
                "essential_score": result.essential_score,
                "essential_breakdown": _essential_breakdown(result),
            },
        }
    )


def _result_for(
    reference: AstrologyRuntimeReference,
    *,
    chart_sect: str,
    planet_code: str,
) -> PlanetDignityResult:
    """Retourne le resultat de scoring canonique pour une planete cible."""
    sun_house = 10 if chart_sect == "day" else 2
    case_planets = (
        planet("sun", 120.0, "leo", sun_house),
        planet(planet_code, 125.0, TRIPLICITY_SIGN, sun_house),
    )
    results = dignity_results_with_reference(case_planets, reference)
    result = next(item for item in results if item.planet_code == planet_code)
    assert result.chart_sect.chart_sect == chart_sect
    return result


def _triplicity_ruler(
    reference: AstrologyRuntimeReference,
    *,
    sect_code: str,
) -> TriplicityRulerReferenceData:
    """Lit le ruler de triplicite depuis les assignments runtime."""
    matches = [
        ruler
        for ruler in reference.dignity_reference.triplicity_rulers
        if ruler.element_code == TRIPLICITY_ELEMENT and ruler.sect_code == sect_code
    ]
    assert len(matches) == 1
    return matches[0]


def _triplicity_match(result: PlanetDignityResult) -> dict[str, Any] | None:
    """Retourne le match de triplicite observe si present."""
    for match in result.essential_breakdown:
        if match.dignity_type_code == "triplicity":
            return normalize_golden_value(
                {
                    "type_code": match.dignity_type_code,
                    "score": match.score_value,
                    "source": match.source,
                    "reason": match.reason,
                    "sign_code": match.sign_code,
                }
            )
    return None


def _essential_breakdown(result: PlanetDignityResult) -> list[dict[str, Any]]:
    """Compacte le breakdown essentiel pour le snapshot CS-205."""
    return normalize_golden_value(
        [
            {
                "type_code": match.dignity_type_code,
                "score": match.score_value,
                "source": match.source,
                "reason": match.reason,
                "sign_code": match.sign_code,
            }
            for match in result.essential_breakdown
        ]
    )


def _compact_case(case: dict[str, Any]) -> dict[str, Any]:
    """Reduit un cas complet aux champs utiles pour les comparaisons croisees."""
    return {
        "chart_sect": case["chart_sect"],
        "planet_code": case["planet_code"],
        "expected_triplicity_role": case["expected_triplicity_role"],
        "observed": case["observed"],
    }


def _triplicity_snapshot_item(case: dict[str, Any]) -> dict[str, Any]:
    """Retourne l'item triplicite dans un cas snapshot."""
    return next(
        item
        for item in case["observed"]["essential_breakdown"]
        if item["type_code"] == "triplicity"
    )
