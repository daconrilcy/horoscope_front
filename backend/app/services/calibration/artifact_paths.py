"""Chemins canoniques des artefacts generes de calibration."""

from __future__ import annotations

from pathlib import Path

from app.services.calibration.runtime import resolve_project_root

CALIBRATION_ARTIFACTS_DIR = Path("docs/calibration")
PERCENTILE_REPORT_FILENAME = "percentile_report.json"


def resolve_calibration_artifact_path(filename: str) -> Path:
    """Retourne le chemin absolu canonique pour un artefact calibration."""
    return resolve_project_root() / CALIBRATION_ARTIFACTS_DIR / filename


def resolve_percentile_report_path() -> Path:
    """Retourne le chemin canonique du rapport percentile de calibration."""
    return resolve_calibration_artifact_path(PERCENTILE_REPORT_FILENAME)
