# Tests de preuve du mode astronomique de production CS-250.
"""Verifie le contrat de preuve SwissEph et la trace d'ephémérides."""

from __future__ import annotations

from app.domain.astrology.runtime.astronomical_proof import (
    CS253_GATE_MARKER,
    PRODUCTION_ASTRONOMY_MODE,
    PRODUCTION_TOLERANCE,
    SENSITIVE_GOLDEN_CASES,
    build_astronomical_proof_manifest,
    build_ephemeris_trace,
    build_public_temporal_gate,
    manifest_to_dict,
)


def test_production_astronomy_mode_is_swisseph() -> None:
    """Le manifest de preuve qualifie uniquement le mode SwissEph."""
    manifest = build_astronomical_proof_manifest(cs250_status="ready-to-review")

    assert manifest.mode == PRODUCTION_ASTRONOMY_MODE
    assert manifest.mode == "swisseph"
    assert manifest.authorized_public_temporal is False
    assert manifest.cs253_gate.marker == CS253_GATE_MARKER


def test_ephemeris_trace_contains_reproducibility_metadata() -> None:
    """La trace expose version et source reproductible sans chemin brut obligatoire."""
    trace = build_ephemeris_trace()

    assert trace.mode == "swisseph"
    assert trace.swisseph_version
    assert trace.path_version or trace.reproducibility_note
    assert trace.reproducibility_note in {
        "external-path-bootstrap",
        "pyswisseph-moshier-integrated-no-external-path",
    }


def test_tolerance_policy_is_single_canonical_owner() -> None:
    """Tous les cas sensibles reutilisent la meme politique de tolerance."""
    assert PRODUCTION_TOLERANCE.name == "swisseph-sensitive-v1"
    assert PRODUCTION_TOLERANCE.longitude_degrees == 0.01
    assert PRODUCTION_TOLERANCE.house_angle_degrees == 0.02
    assert PRODUCTION_TOLERANCE.ayanamsa_degrees == 0.01
    assert all(case.tolerance is PRODUCTION_TOLERANCE for case in SENSITIVE_GOLDEN_CASES)


def test_cs253_gate_blocks_public_temporal_until_cs250_done() -> None:
    """CS-253 reste bloque tant que la story de preuve n'est pas done."""
    gate = build_public_temporal_gate(cs250_status="ready-to-review")

    assert gate.cs253_gate_state == "blocked"
    assert gate.authorized_public_temporal is False
    assert "CS-250" in gate.reason


def test_manifest_contract_shape_contains_required_fields() -> None:
    """Le manifest serialise les champs requis par la story."""
    payload = manifest_to_dict(build_astronomical_proof_manifest(cs250_status="ready-to-review"))

    assert payload["mode"] == "swisseph"
    assert payload["authorized_public_temporal"] is False
    assert payload["tolerance_policy"]["name"] == "swisseph-sensitive-v1"  # type: ignore[index]
    assert payload["ephemeris_trace"]["swisseph_version"]  # type: ignore[index]
    assert payload["cs253_gate"]["cs253_gate_state"] == "blocked"  # type: ignore[index]
    assert len(payload["golden_cases"]) == 8  # type: ignore[arg-type]
