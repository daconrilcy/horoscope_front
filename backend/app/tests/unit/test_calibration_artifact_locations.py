# Garde des emplacements canoniques des artefacts calibration.
"""Verifie qu'un seul chemin actif existe pour les artefacts calibration."""

from __future__ import annotations

import ast
from pathlib import Path

from app.services.calibration import artifact_paths
from app.services.calibration.generate_review_grid import _default_output_path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
REPO_ROOT = BACKEND_ROOT.parent
FORBIDDEN_BACKEND_DOCS_CALIBRATION = BACKEND_ROOT / "docs" / "calibration"
CANONICAL_RELATIVE_DIR = Path("docs/calibration")


def _string_literals(path: Path) -> set[str]:
    """Extrait les chaines litterales Python pour detecter les chemins interdits."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


def test_calibration_artifacts_use_docs_calibration_as_canonical_path() -> None:
    """Le chemin canonique documente doit rester `docs/calibration`."""
    assert artifact_paths.CALIBRATION_ARTIFACTS_DIR == CANONICAL_RELATIVE_DIR
    assert artifact_paths.resolve_percentile_report_path() == (
        REPO_ROOT / CANONICAL_RELATIVE_DIR / "percentile_report.json"
    )


def test_review_grid_default_output_uses_canonical_path() -> None:
    """La grille de revue doit produire ses sorties dans le dossier canonique."""
    output = _default_output_path("md", __import__("datetime").date(2026, 5, 4))

    assert output == REPO_ROOT / CANONICAL_RELATIVE_DIR / "review-grid-2026-05-04.md"


def test_backend_docs_calibration_is_not_an_active_artifact_location() -> None:
    """L'ancien dossier backend/docs/calibration ne doit pas redevenir actif."""
    assert not FORBIDDEN_BACKEND_DOCS_CALIBRATION.exists()


def test_calibration_producers_do_not_reference_backend_docs_calibration() -> None:
    """Les producteurs ne doivent plus contenir de chemin de sortie concurrent."""
    producer_files = [
        BACKEND_ROOT / "app" / "scheduled_tasks" / "compute_calibration_percentiles.py",
        BACKEND_ROOT / "app" / "services" / "calibration" / "generate_review_grid.py",
        BACKEND_ROOT / "app" / "services" / "calibration" / "artifact_paths.py",
    ]
    offenders = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in producer_files
        if "backend/docs/calibration" in _string_literals(path)
    ]

    assert offenders == []
