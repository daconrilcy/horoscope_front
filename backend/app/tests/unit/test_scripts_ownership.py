# Garde d'ownership des scripts racine.
"""Verifie que les scripts ponctuels de story ne reviennent pas en racine."""

from __future__ import annotations

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = BACKEND_ROOT.parent


def test_route_removal_audit_validator_is_not_root_script() -> None:
    """Le validateur ponctuel de suppression des routes reste absent de `scripts/`."""
    forbidden_name = "validate_route_removal_audit" + ".py"
    forbidden_script = REPO_ROOT / "scripts" / forbidden_name

    assert not forbidden_script.exists()
