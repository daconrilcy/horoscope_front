# Tests du contrat de selection de la premiere technique temporelle.
"""Verifie la decision CS-253 sans ouvrir de runtime public."""

from app.domain.astrology.runtime.temporal_technique_selection import (
    DEPENDENCY_STORY_IDS,
    SELECTED_TEMPORAL_FAMILY_CODE,
    TemporalCandidateStatus,
    TemporalPublicProjectionStatus,
    TemporalTechniqueSelectionStatus,
    build_first_temporal_technique_selection,
    temporal_selection_to_dict,
)

REJECTED_TEMPORAL_FAMILIES = {
    "synastry_chart_v1",
    "solar_return_v1",
    "lunar_return_v1",
    "progressed_chart_v1",
    "composite_chart_v1",
    "profection_v1",
    "forecasting_v1",
}


def test_transit_chart_is_the_single_selected_temporal_family() -> None:
    """La selection ouvre uniquement le chemin transit en contrat interne."""
    selection = build_first_temporal_technique_selection(cs250_status="ready-to-review")

    assert selection.selected_family_code == SELECTED_TEMPORAL_FAMILY_CODE
    assert selection.selected_family_code == "transit_chart_v1"
    assert selection.selection_status is TemporalTechniqueSelectionStatus.SELECTED_BLOCKED_BY_CS250
    assert selection.decision_owner == "backend-domain:astrology-runtime-temporal"
    assert {candidate.family_code for candidate in selection.rejected_candidates} == (
        REJECTED_TEMPORAL_FAMILIES
    )
    assert all(
        candidate.status is TemporalCandidateStatus.CLOSED
        for candidate in selection.rejected_candidates
    )


def test_rejected_candidates_keep_explicit_non_selection_reasons() -> None:
    """Chaque famille non retenue garde une raison lisible et durable."""
    selection = build_first_temporal_technique_selection(cs250_status="ready-to-review")

    assert all(candidate.reason for candidate in selection.rejected_candidates)
    assert "multi-chart" in _reason(selection, "synastry_chart_v1")
    assert "return-specific" in _reason(selection, "solar_return_v1")
    assert "progression method" in _reason(selection, "progressed_chart_v1")
    assert "doctrine school" in _reason(selection, "profection_v1")
    assert "forecasting primitive" in _reason(selection, "forecasting_v1")


def test_required_inputs_graph_contracts_and_relationships_are_declared() -> None:
    """Le contrat declare inputs, graphe, objets et relations requis."""
    selection = build_first_temporal_technique_selection(cs250_status="ready-to-review")
    input_keys = {item.key for item in selection.required_inputs}
    object_keys = {item.key for item in selection.required_chart_objects}
    relationship_keys = {item.key for item in selection.required_relationships}

    assert {
        "natal_chart_input",
        "target_date_or_date_range",
        "timezone_policy",
        "location_policy",
        "calculation_mode_proof",
    } <= input_keys
    assert selection.required_graph_code == "transit_chart_v1"
    assert set(selection.dependency_story_ids) == set(DEPENDENCY_STORY_IDS)
    assert {"CS-246", "CS-247", "CS-248", "CS-250"} <= set(selection.dependency_story_ids)
    assert {"natal_chart_objects", "transiting_chart_objects", "transit_houses"} <= object_keys
    assert {
        "transit_object_to_natal_object",
        "transit_to_natal_aspect",
        "house_transit_relationship",
    } <= relationship_keys


def test_cs250_gate_keeps_selection_non_public_before_done() -> None:
    """CS-250 bloque toute projection publique du chemin transit."""
    selection = build_first_temporal_technique_selection(cs250_status="ready-to-review")

    assert selection.selection_status is TemporalTechniqueSelectionStatus.SELECTED_BLOCKED_BY_CS250
    assert selection.public_projection_status is TemporalPublicProjectionStatus.BLOCKED_BY_CS250
    assert selection.cs250_gate_state == "blocked"
    assert "No public API" in " ".join(selection.end_criteria)


def test_cs250_done_marks_selection_ready_without_public_surface() -> None:
    """CS-250 done ferme le gate de preuve sans ajouter de surface publique."""
    selection = build_first_temporal_technique_selection(cs250_status="done")

    assert selection.selection_status is TemporalTechniqueSelectionStatus.SELECTED_READY_AFTER_CS250
    assert selection.public_projection_status is TemporalPublicProjectionStatus.READY_AFTER_CS250
    assert selection.cs250_gate_state == "proof-closed"


def test_written_risk_acceptance_remains_non_public() -> None:
    """Une risk acceptance n'autorise qu'une experimentation non publique."""
    selection = build_first_temporal_technique_selection(
        cs250_status="ready-to-review",
        risk_acceptance_non_public=True,
    )

    assert (
        selection.selection_status
        is TemporalTechniqueSelectionStatus.SELECTED_RISK_ACCEPTED_NON_PUBLIC
    )
    assert (
        selection.public_projection_status
        is TemporalPublicProjectionStatus.NON_PUBLIC_RISK_ACCEPTED
    )
    assert selection.cs250_gate_state == "risk-accepted-non-public"


def test_selection_snapshot_serializes_snake_case_json_values() -> None:
    """La preuve JSON expose des valeurs stables sans enums Python."""
    payload = temporal_selection_to_dict(
        build_first_temporal_technique_selection(cs250_status="ready-to-review")
    )

    assert payload["selected_family_code"] == "transit_chart_v1"
    assert payload["selection_status"] == "selected-blocked-by-cs250"
    assert payload["public_projection_status"] == "blocked-by-cs250"
    assert len(payload["rejected_candidates"]) == 7  # type: ignore[arg-type]
    assert all(
        candidate["status"] == "closed"
        for candidate in payload["rejected_candidates"]  # type: ignore[index]
    )


def _reason(selection: object, family_code: str) -> str:
    """Retourne la raison de fermeture d'une famille candidate."""
    for candidate in selection.rejected_candidates:  # type: ignore[attr-defined]
        if candidate.family_code == family_code:
            return candidate.reason
    raise AssertionError(f"Candidate {family_code} not found")
