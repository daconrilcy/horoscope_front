# Tests du manifest interne transit_chart_v1.
"""Verifie le contrat CS-279 sans ouvrir de surface publique."""

from __future__ import annotations

import ast
from pathlib import Path

from app.domain.astrology.runtime.transit_chart_manifest import (
    TRANSIT_CHART_PUBLIC_EXPOSURE_STATUS,
    TransitManifestClassification,
    build_transit_chart_manifest,
    transit_chart_manifest_to_dict,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
MANIFEST_PATH = REPO_ROOT / "app/domain/astrology/runtime/transit_chart_manifest.py"


def test_internal_manifest_exists_for_transit_chart_v1() -> None:
    """Le manifest declare une famille transit unique et non publique."""
    manifest = build_transit_chart_manifest()

    assert manifest.family_code == "transit_chart_v1"
    assert manifest.classification is TransitManifestClassification.INTERNAL_NON_PUBLIC
    assert manifest.public_exposure_status == TRANSIT_CHART_PUBLIC_EXPOSURE_STATUS
    assert manifest.owner == "backend-domain:astrology-runtime-temporal"


def test_manifest_declares_required_internal_inputs_and_outputs() -> None:
    """Les inputs et outputs internes restent explicites et bornes."""
    manifest = build_transit_chart_manifest()

    input_keys = {field.key for field in manifest.inputs}
    output_keys = {field.key for field in manifest.outputs}

    assert {
        "natal_chart_reference",
        "transit_target",
        "timezone",
        "location_policy",
        "proof_reference",
    } <= input_keys
    assert {
        "transiting_chart_objects",
        "transit_to_natal_relationships",
        "diagnostic_trace_keys",
        "blocked_public_status",
    } <= output_keys
    assert all("public" not in field.value_type.lower() for field in manifest.inputs)


def test_manifest_lists_cs250_proof_and_cs252_doctrine_prerequisites() -> None:
    """Les gates preuve et doctrine sont cites sans raccourci runtime."""
    manifest = build_transit_chart_manifest()

    proof_payload = " ".join(
        f"{item.story_id} {item.owner} {item.requirement} {item.evidence_ref}"
        for item in manifest.proof_prerequisites
    )
    doctrine_payload = " ".join(
        f"{item.story_id} {item.owner} {item.requirement} {item.evidence_ref}"
        for item in manifest.doctrine_prerequisites
    )

    assert "CS-250" in proof_payload
    assert "astronomical_proof" in proof_payload
    assert "swisseph" in proof_payload.lower()
    assert "CS-252" in doctrine_payload
    assert "astrology_doctrine_governance" in doctrine_payload
    assert "doctrine" in doctrine_payload
    assert "school policy" in doctrine_payload


def test_trace_requirements_are_redacted_and_do_not_create_replay_storage() -> None:
    """La trace reste diagnostique et separee de tout stockage replay."""
    manifest = build_transit_chart_manifest()
    trace_by_key = {field.key: field for field in manifest.trace_requirements}
    trace_payload = " ".join(
        f"{field.key} {field.value_type} {field.policy}" for field in manifest.trace_requirements
    )

    assert {
        "run_id",
        "graph_code",
        "graph_version",
        "node_status",
        "redacted_input_keys",
        "redacted_output_keys",
    } <= set(trace_by_key)
    assert trace_by_key["graph_code"].value_type == "transit_chart_v1"
    assert "redacted" in trace_payload
    assert "does not create replay storage" in trace_payload


def test_follow_up_runtime_stories_are_identified_without_implementation() -> None:
    """Les prochaines stories sont nommees sans livrer le runner ou l'API."""
    manifest = build_transit_chart_manifest()
    follow_up_keys = {story.key for story in manifest.follow_up_runtime_stories}

    assert follow_up_keys == {
        "internal_graph_manifest",
        "calculation_runner_integration",
        "projection_contract",
        "public_api_gate",
    }
    assert all(story.gate for story in manifest.follow_up_runtime_stories)


def test_manifest_serializes_stable_json_shape() -> None:
    """La preuve JSON expose les champs attendus en snake_case."""
    payload = transit_chart_manifest_to_dict(build_transit_chart_manifest())

    assert set(payload) == {
        "family_code",
        "contract_version",
        "classification",
        "public_exposure_status",
        "owner",
        "inputs",
        "outputs",
        "proof_prerequisites",
        "doctrine_prerequisites",
        "trace_requirements",
        "follow_up_runtime_stories",
    }
    assert payload["family_code"] == "transit_chart_v1"
    assert payload["classification"] == "internal-non-public"
    assert payload["public_exposure_status"] == TRANSIT_CHART_PUBLIC_EXPOSURE_STATUS


def test_manifest_ast_guard_keeps_api_frontend_and_storage_out() -> None:
    """AST guard: le manifest n'importe ni API, ni frontend, ni stockage."""
    tree = ast.parse(MANIFEST_PATH.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert not any(module.startswith("app.api") for module in imported_modules)
    assert not any(module.startswith("app.services") for module in imported_modules)
    assert not any(module.startswith("app.infra") for module in imported_modules)
    assert not any("frontend" in module for module in imported_modules)
