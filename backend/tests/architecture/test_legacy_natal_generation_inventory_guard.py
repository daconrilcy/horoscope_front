# Garde d'architecture pour l'inventaire natal legacy CS-426.
"""Verifie que l'inventaire CS-426 reste complet et exploitable par les stories destructives."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
STORY_ROOT = REPO_ROOT / "_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang"
EVIDENCE_ROOT = STORY_ROOT / "evidence"
MAP_PATH = EVIDENCE_ROOT / "legacy-generation-map.md"
CLASSIFICATION_PATH = EVIDENCE_ROOT / "legacy-surface-classification.md"
INITIAL_SCANS_PATH = EVIDENCE_ROOT / "initial-scans.txt"

ALLOWED_CLASSIFICATIONS = {"delete", "replace", "readonly", "keep", "needs-decision"}
REQUIRED_MAP_COLUMNS = {
    "surface",
    "symbol",
    "trigger",
    "generation mode",
    "legacy primitive",
    "classification",
    "evidence",
}
REQUIRED_CLASSIFICATION_COLUMNS = {
    "surface",
    "classification",
    "rationale",
    "owner",
    "expected decision",
    "next story input",
}
REQUIRED_SURFACE_TOKENS = {
    "backend/app/api/v1/routers/public/natal_interpretation.py",
    "backend/app/services/llm_generation/natal/interpretation_service.py",
    "backend/app/domain/llm/runtime/gateway.py",
    "backend/app/domain/llm/prompting/catalog.py",
    "backend/app/ops/llm/bootstrap/seed_29_prompts.py",
    "backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py",
    "backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py",
    "backend/scripts/seed_natal_short.py",
    "backend/scripts/diagnose_natal_interpretation_duplicates.py",
    "frontend/src/features/natal-chart/NatalInterpretation.tsx",
    "frontend/src/api/natal-chart/index.ts",
    "_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md",
    "_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md",
    "_story_briefs/cs-425-invalider-regenerer-lectures-basic-natal-degradees.md",
}
REQUIRED_LEGACY_TOKENS = {
    "natal_interpretation_short",
    "natal_long_free",
    "natal_interpretation",
    "basic_natal_prompt_payload",
    "use_case_level",
    "variant_code",
    "forceRefresh",
    "PROMPT_FALLBACK_CONFIGS",
    "fallback_default",
    "AstroResponse_v3",
    "EXIGENCE PREMIUM",
    "UserNatalInterpretationModel",
    "chart_id",
    "answer_type",
    "was_fallback",
}
REQUIRED_EXPOSURE_TOKENS = {"public", "admin-only", "test-only", "bootstrap", "historical"}


def _read(path: Path) -> str:
    """Charge un artefact d'evidence avec un chemin stable depuis la racine du depot."""

    return path.read_text(encoding="utf-8")


def _table_rows(markdown: str) -> list[dict[str, str]]:
    """Extrait les lignes de table Markdown simples sous forme de dictionnaires."""

    rows = [line.strip() for line in markdown.splitlines() if line.startswith("|")]
    tables: list[dict[str, str]] = []
    current_header: list[str] | None = None
    for line in rows:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        if current_header is None:
            current_header = [cell.lower() for cell in cells]
            continue
        if len(cells) == len(current_header):
            tables.append(dict(zip(current_header, cells, strict=True)))
    return tables


def test_inventory_artifacts_exist() -> None:
    """Les trois artefacts persistants requis par CS-426 existent."""

    assert MAP_PATH.exists()
    assert CLASSIFICATION_PATH.exists()
    assert INITIAL_SCANS_PATH.exists()


def test_generation_map_has_required_shape_and_allowed_classifications() -> None:
    """La cartographie expose les colonnes contractuelles et les statuts autorises."""

    rows = _table_rows(_read(MAP_PATH))

    assert rows
    assert REQUIRED_MAP_COLUMNS.issubset(rows[0])
    assert {row["classification"] for row in rows}.issubset(ALLOWED_CLASSIFICATIONS)
    content = _read(MAP_PATH)
    for token in REQUIRED_EXPOSURE_TOKENS:
        assert token in content


def test_generation_map_covers_legacy_sources_and_primitives() -> None:
    """Les surfaces et primitives nommees par le brief restent inventoriees."""

    content = _read(MAP_PATH)

    for token in REQUIRED_SURFACE_TOKENS | REQUIRED_LEGACY_TOKENS:
        assert token in content


def test_classification_artifact_has_required_shape_and_decisions() -> None:
    """La classification porte les proprietaires et decisions attendues."""

    rows = _table_rows(_read(CLASSIFICATION_PATH))

    assert rows
    assert REQUIRED_CLASSIFICATION_COLUMNS.issubset(rows[0])
    assert {row["classification"] for row in rows}.issubset(ALLOWED_CLASSIFICATIONS)

    needs_decision_rows = [row for row in rows if row["classification"] == "needs-decision"]
    assert needs_decision_rows
    for row in needs_decision_rows:
        assert row["owner"]
        assert row["expected decision"]
        assert "decide" in row["expected decision"].lower()


def test_readonly_rows_are_explicitly_non_generative() -> None:
    """Chaque ligne readonly indique pourquoi elle ne produit pas de sortie LLM."""

    map_rows = _table_rows(_read(MAP_PATH))
    classification_rows = _table_rows(_read(CLASSIFICATION_PATH))
    readonly_text = "\n".join(
        row.get("notes", "") + " " + row.get("rationale", "")
        for row in [*map_rows, *classification_rows]
        if row.get("classification") == "readonly"
    ).lower()

    assert "non-generative" in readonly_text


def test_initial_scans_preserve_required_validation_commands() -> None:
    """Les scans initiaux VC1 a VC6 sont conserves comme baseline."""

    content = _read(INITIAL_SCANS_PATH)

    for validation_id in ("VC1", "VC2", "VC3", "VC4", "VC5", "VC6"):
        assert f"## {validation_id}" in content
    for token in REQUIRED_LEGACY_TOKENS:
        assert token in content
    assert "git status --short -- _condamad/run-state.json" in content
    assert "_condamad/run-state.json is out of scope" in content
