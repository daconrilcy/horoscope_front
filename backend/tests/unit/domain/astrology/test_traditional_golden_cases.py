"""Tests golden des contrats traditionnels hellenistiques et medievaux."""

from __future__ import annotations

from pathlib import Path

from tests.unit.domain.astrology.fixtures.golden_snapshot import load_snapshot
from tests.unit.domain.astrology.fixtures.traditional_golden_cases import (
    golden_cases,
    snapshot_payload,
    story_evidence_path,
)


def _case(case_id: str) -> dict[str, object]:
    """Retourne une entree de snapshot par identifiant de cas."""
    return next(item for item in golden_cases() if item["case_id"] == case_id)


def test_g1_g2_lock_chart_sect_and_sun_horizon_contracts() -> None:
    """G1/G2 verrouillent la secte chart-level et les champs horizon."""
    g1 = _case("G1")["observed_summary"]
    g2 = _case("G2")["observed_summary"]

    assert g1 == {
        "calculation_basis": "sun_house_horizon_rule",
        "chart_sect": "day",
        "reference_system": "traditional",
        "sun_above_horizon": True,
        "sun_horizon_position": "above_horizon",
    }
    assert g2 == {
        "calculation_basis": "sun_house_horizon_rule",
        "chart_sect": "night",
        "reference_system": "traditional",
        "sun_above_horizon": False,
        "sun_horizon_position": "below_horizon",
    }


def test_g3_to_g6_lock_planet_sect_conditions_and_out_of_sect() -> None:
    """G3-G6 couvrent en-secte et hors-secte pour planetes diurnes/nocturnes."""
    assert _case("G3")["observed_summary"]["sect_condition"]["planet_sect_condition"] == "in_sect"
    assert _case("G3")["observed_summary"]["sect_condition"]["intrinsic_sect"] == "diurnal"
    assert _case("G4")["observed_summary"]["sect_condition"]["planet_sect_condition"] == "in_sect"
    assert _case("G4")["observed_summary"]["sect_condition"]["intrinsic_sect"] == "nocturnal"

    g5 = _case("G5")["observed_summary"]
    g6 = _case("G6")["observed_summary"]
    assert g5["sect_condition"]["planet_sect_condition"] == "out_of_sect"
    assert "out_of_sect" in g5["condition_codes"]
    assert g6["sect_condition"]["planet_sect_condition"] == "out_of_sect"
    assert "out_of_sect" in g6["condition_codes"]


def test_g7_g8_lock_hayz_complete_versus_in_sect_only() -> None:
    """G7 prouve hayz complet et G8 prouve qu'en-secte seul ne suffit pas."""
    assert "hayz" in _case("G7")["observed_summary"]["condition_codes"]

    g8 = _case("G8")["observed_summary"]
    assert g8["sect_condition"]["sect_condition"]["is_in_sect"] is True
    assert "hayz" not in g8["condition_codes"]


def test_g9_locks_planetary_rejoicing_profile_contribution() -> None:
    """G9 verrouille la joie planetaire via les dignites accidentelles."""
    observed = _case("G9")["observed_summary"]

    assert {"code": "planetary_joy", "score": 3, "source": "planetary_joy_house"} in observed[
        "accidental_breakdown"
    ]
    assert any(item["code"] == "planetary_joy" for item in observed["profile_breakdown"])
    assert observed["accidental_score"] >= 3


def test_g10_locks_runtime_backed_mercury_classification() -> None:
    """G10 verifie Mercure commun sans mapping local dans le test."""
    mercury = _case("G10")["observed_summary"]["sect_condition"]

    assert mercury["planet_code"] == "mercury"
    assert mercury["intrinsic_sect"] == "common"
    assert mercury["planet_sect_condition"] == "variable_by_condition"
    assert mercury["is_in_sect"] is False
    assert mercury["is_out_of_sect"] is False


def test_g11_locks_essential_dignity_and_scores() -> None:
    """G11 verrouille une dignite essentielle et ses axes de scoring."""
    observed = _case("G11")["observed_summary"]

    assert {"code": "domicile", "score": 5, "source": "essential_rule"} in observed[
        "essential_breakdown"
    ]
    assert observed["essential_score"] == 5
    assert observed["functional_strength_score"] > 0
    assert observed["expression_quality_score"] > 0
    assert observed["intensity_score"] > 0


def test_g12_locks_integrated_pipeline_and_public_json_projection() -> None:
    """G12 verrouille NatalResult, surfaces aval et projection JSON publique."""
    observed = _case("G12")["observed_summary"]

    assert observed["engine"] == "simplified"
    assert observed["dignity_sect"]["chart_sect"] in {"day", "night"}
    assert observed["first_planet_sect_condition"]["planet_code"] == observed["first_planet"]
    assert observed["condition_profile_planets"]
    assert observed["condition_signal_planets"]
    assert observed["dominant_planets"]["top_planet"] is not None
    assert observed["json_projection"]["sect"] == observed["dignity_sect"]
    assert (
        observed["json_projection"]["first_planet_sect_condition"]
        == observed["first_planet_sect_condition"]
    )
    assert observed["json_projection"]["dominant_planets"]["planet_codes"]


def test_g12_adapter_fixture_locks_downstream_surfaces() -> None:
    """G12 inclut une surface aval deterministe pour l'adaptateur."""
    observed = _case("G12")["observed_summary"]["deterministic_downstream"]

    assert observed["condition_profiles"] == ["mars", "sun"]
    assert observed["dominance"]["chart_ruler"] == "mars"
    assert observed["interpretation_adapter"]["signals"]
    assert observed["interpretation_adapter"]["dominant_topics"]


def test_curated_snapshot_matches_persistent_evidence() -> None:
    """Le snapshot persistant reste identique aux sorties runtime curates."""
    expected = load_snapshot(Path(story_evidence_path))

    assert snapshot_payload() == expected
