# Tests d'architecture documentant les surfaces runtime natales.
"""Verifie que l'inventaire CS-224 reste explicite et complet."""

from __future__ import annotations

from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent
DOC_PATH = REPO_ROOT / "docs/architecture/astrology-runtime-surfaces.md"

REQUIRED_SURFACES = (
    "chart_objects",
    "planet_positions",
    "astral_points",
    "houses",
    "angles",
    "aspects",
    "dignity_results",
    "dominance_result",
    "advanced_conditions",
    "fixed_star_conjunctions",
)
REQUIRED_STATUSES = (
    "canonical",
    "compatibility projection",
    "public API projection",
    "chart-level result",
    "legacy",
)
REQUIRED_COLUMNS = (
    "Surface",
    "Statut",
    "Source cible",
    "Autorisee dans calculateurs",
    "Owner",
    "Allowlist reason",
    "Commentaire",
)


def test_runtime_surface_documentation_exists() -> None:
    """La documentation d'architecture CS-224 est presente."""
    assert DOC_PATH.exists()


def test_runtime_surface_documentation_lists_required_surfaces() -> None:
    """Chaque surface de transition est classee dans l'inventaire."""
    content = DOC_PATH.read_text(encoding="utf-8")

    for surface in REQUIRED_SURFACES:
        assert f"`{surface}`" in content


def test_runtime_surface_documentation_declares_statuses_and_columns() -> None:
    """Le tableau garde les champs necessaires a la gouvernance."""
    content = DOC_PATH.read_text(encoding="utf-8")

    for status in REQUIRED_STATUSES:
        assert status in content
    for column in REQUIRED_COLUMNS:
        assert column in content
    assert "`chart_objects` | canonical" in content
    assert "`planet_positions` | compatibility projection" in content
    assert "`aspects` | chart-level result" in content
