# Garde d'architecture pour l'inventaire natal legacy CS-426.
"""Verifie que l'inventaire CS-426 reste complet et exploitable par les stories destructives."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
APP_ROOT = REPO_ROOT / "backend/app"
STORY_ROOT = REPO_ROOT / "_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang"
EVIDENCE_ROOT = STORY_ROOT / "evidence"
MAP_PATH = EVIDENCE_ROOT / "legacy-generation-map.md"
CLASSIFICATION_PATH = EVIDENCE_ROOT / "legacy-surface-classification.md"
INITIAL_SCANS_PATH = EVIDENCE_ROOT / "initial-scans.txt"
CS440_ROOT = REPO_ROOT / "_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards"
CS440_AUDIT_PATH = CS440_ROOT / "evidence/legacy-natal-zero-hit-audit.md"
CS440_REPORT_PATH = REPO_ROOT / "_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md"
FRONTEND_SRC_ROOT = REPO_ROOT / "frontend/src"
REGRESSION_GUARDRAILS_PATH = REPO_ROOT / "_condamad/stories/regression-guardrails.md"
TEST_ROOTS = (
    REPO_ROOT / "backend/tests",
    REPO_ROOT / "backend/app/tests",
    REPO_ROOT / "frontend/src/tests",
)

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
    "backend/app/api/v1/routers/public/users.py",
    "backend/app/api/v1/routers/internal/llm/qa.py",
    "backend/app/services/api_contracts/public/natal_interpretation.py",
    "backend/app/services/api_contracts/internal/llm/qa.py",
    "backend/app/services/llm_generation/natal/interpretation_service.py",
    "backend/app/domain/llm/runtime/gateway.py",
    "backend/app/domain/llm/runtime/adapter.py",
    "backend/app/domain/llm/prompting/catalog.py",
    "backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py",
    "backend/scripts/debug_api_natal_call.py",
    "backend/scripts/debug_natal_internal_error.py",
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
ZERO_HIT_RUNTIME_TOKENS = {
    "natal_interpretation_short",
    "natal_long_free",
    "shouldRefreshShortAfterBasicUpgrade",
    "forceRefresh",
    "use_case_level",
}
AUTHORIZED_RUNTIME_TOKEN_OWNERS = {
    Path("backend/app/api/v1/routers/public/natal_interpretation.py"): {
        "natal_interpretation_short",
    },
    Path("backend/app/api/v1/routers/internal/llm/qa.py"): {
        "use_case_level",
    },
    Path("backend/app/domain/llm/runtime/adapter.py"): {
        "natal_interpretation_short",
        "natal_long_free",
    },
    Path("backend/app/services/api_contracts/internal/llm/qa.py"): {
        "use_case_level",
    },
    Path("backend/app/services/llm_generation/admin_prompts.py"): {
        "natal_long_free",
    },
    Path("backend/app/services/llm_generation/natal/interpretation_service.py"): {
        "natal_interpretation_short",
        "natal_long_free",
    },
}
REMOVED_PROMPT_SOURCE_PATHS = {
    Path("backend/app/ops/llm/bootstrap/seed_29_prompts.py"),
    Path("backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py"),
    Path("backend/scripts/seed_29_prompts.py"),
    Path("backend/scripts/seed_30_8_v3_prompts.py"),
    Path("backend/scripts/seed_30_2_astroresponse_v2.py"),
    Path("backend/scripts/seed_30_3_gpt5_prompts.py"),
    Path("backend/scripts/seed_28_4.py"),
    Path("backend/scripts/seed_natal_short.py"),
    Path("backend/scripts/update_all_prompts_59_5.py"),
}
AUTHORIZED_RUNTIME_REASONS = {
    "readonly historical projection",
    "deleted-key rejection guard",
    "admin-only prompt metadata",
    "admin-only internal QA",
    "historical persisted-row read compatibility",
}
AUTHORIZED_TEST_TOKEN_FILES = {
    Path("backend/app/tests/integration/test_admin_actions_api.py"),
    Path("backend/app/tests/integration/test_admin_llm_natal_prompts.py"),
    Path("backend/app/tests/integration/test_contract_api.py"),
    Path("backend/app/tests/integration/test_gateway_gpt5_params.py"),
    Path("backend/app/tests/integration/test_llm_qa_router.py"),
    Path("backend/app/tests/integration/test_migration_20260422_0073_cleanup_llm_legacy.py"),
    Path("backend/app/tests/integration/test_natal_chart_long_entitlement.py"),
    Path("backend/app/tests/integration/test_natal_free_short_variant.py"),
    Path("backend/app/tests/integration/test_natal_interpretation_endpoint.py"),
    Path("backend/app/tests/integration/test_natal_interpretations_history.py"),
    Path("backend/app/tests/unit/test_ai_engine_adapter.py"),
    Path("backend/app/tests/unit/test_gateway_input_validation_payload.py"),
    Path("backend/app/tests/unit/test_gateway_modes.py"),
    Path("backend/app/tests/unit/test_natal_interpretation_service_v2.py"),
    Path("backend/app/tests/unit/test_seed_29_prompt_contract.py"),
    Path("backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py"),
    Path("backend/tests/architecture/test_llm_legacy_extinction.py"),
    Path("backend/tests/architecture/test_theme_astral_prompt_contract_guard.py"),
    Path("backend/tests/evaluation/__init__.py"),
    Path("backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py"),
    Path("backend/tests/integration/test_admin_llm_catalog.py"),
    Path("backend/tests/integration/test_llm_release.py"),
    Path("backend/tests/integration/test_natal_basic_complete_v3_runtime.py"),
    Path("backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py"),
    Path("backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py"),
    Path("backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py"),
    Path("backend/tests/integration/test_theme_natal_public_api_product_actions.py"),
    Path("backend/tests/integration/test_theme_natal_public_reads.py"),
    Path("backend/tests/llm_orchestration/test_assembly_resolution.py"),
    Path("backend/tests/llm_orchestration/test_llm_legacy_extinction.py"),
    Path("backend/tests/llm_orchestration/test_prompt_governance_registry.py"),
    Path("backend/tests/llm_orchestration/test_runtime_convergence.py"),
    Path("backend/tests/unit/test_natal_interpretation_stored_payload.py"),
    Path("frontend/src/tests/natalPublicDomGuard.test.tsx"),
}
FORBIDDEN_LEGACY_FIXTURE_NAMES = {
    "natal_interpretation",
    "natal_interpretation_short",
    "natal_long_free",
}


def _read(path: Path) -> str:
    """Charge un artefact d'evidence avec un chemin stable depuis la racine du depot."""

    return path.read_text(encoding="utf-8")


def _iter_source_files(*roots: Path) -> list[Path]:
    """Enumere les sources utiles sans dependre du dossier courant de pytest."""

    ignored_parts = {"__pycache__", ".pytest_cache", ".ruff_cache", "node_modules", "target"}
    files: list[Path] = []
    for root in roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if ignored_parts.intersection(path.parts):
                continue
            if path.suffix.lower() not in {".py", ".ts", ".tsx"}:
                continue
            files.append(path)
    return files


def _iter_test_paths() -> list[Path]:
    """Enumere les fichiers de test et fixtures textuelles qui peuvent porter du legacy."""

    ignored_parts = {"__pycache__", ".pytest_cache", ".ruff_cache", "node_modules", "target"}
    supported_suffixes = {".py", ".ts", ".tsx", ".yaml", ".yml", ".json"}
    files: list[Path] = []
    for root in TEST_ROOTS:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if ignored_parts.intersection(path.parts):
                continue
            if path.suffix.lower() not in supported_suffixes:
                continue
            files.append(path)
    return files


def _token_hits(paths: list[Path], tokens: set[str]) -> list[tuple[Path, str]]:
    """Retourne les hits exacts des anciens symboles pour les guards zero-hit."""

    hits: list[tuple[Path, str]] = []
    for path in paths:
        content = _read(path)
        for token in tokens:
            if token in content:
                hits.append((path.relative_to(REPO_ROOT), token))
    return hits


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


def test_legacy_natal_runtime_hits_are_explicitly_authorized() -> None:
    """Tout ancien symbole runtime natal doit etre readonly, admin-only ou garde d'extinction."""

    source_files = [
        path
        for path in _iter_source_files(APP_ROOT, FRONTEND_SRC_ROOT)
        if "tests" not in path.relative_to(REPO_ROOT).parts
    ]
    unauthorized_hits = []

    for relative_path, token in _token_hits(source_files, ZERO_HIT_RUNTIME_TOKENS):
        allowed_tokens = AUTHORIZED_RUNTIME_TOKEN_OWNERS.get(relative_path, set())
        if token not in allowed_tokens:
            unauthorized_hits.append((str(relative_path), token))

    assert unauthorized_hits == []


def test_legacy_natal_prompt_source_files_are_physically_removed() -> None:
    """Les anciens seeds prompts nataux ne doivent plus rester executables."""

    assert [
        path.as_posix() for path in REMOVED_PROMPT_SOURCE_PATHS if (REPO_ROOT / path).exists()
    ] == []


def test_legacy_natal_test_hits_are_explicitly_authorized() -> None:
    """Les tests ne peuvent garder un ancien symbole que dans un fichier classe CS-440."""

    unauthorized_hits = []
    for relative_path, token in _token_hits(_iter_test_paths(), ZERO_HIT_RUNTIME_TOKENS):
        if relative_path not in AUTHORIZED_TEST_TOKEN_FILES:
            unauthorized_hits.append((str(relative_path), token))

    assert unauthorized_hits == []


def test_legacy_natal_nominal_fixture_directories_are_removed() -> None:
    """Les anciens noms de fixtures d'evaluation natale ne restent pas actifs."""

    remaining_legacy_fixture_paths = []
    for root in TEST_ROOTS:
        for path in root.rglob("*"):
            if path.name in FORBIDDEN_LEGACY_FIXTURE_NAMES:
                remaining_legacy_fixture_paths.append(str(path.relative_to(REPO_ROOT)))

    assert remaining_legacy_fixture_paths == []


def test_legacy_natal_zero_hit_closure_is_persisted() -> None:
    """L'audit, le rapport final et le registre durable portent la fermeture CS-440."""

    audit = _read(CS440_AUDIT_PATH)
    report = _read(CS440_REPORT_PATH)
    registry = _read(REGRESSION_GUARDRAILS_PATH)

    for token in ZERO_HIT_RUNTIME_TOKENS | {"variant_code"}:
        assert f"`{token}`" in audit
        assert f"`{token}`" in report
    for reason in AUTHORIZED_RUNTIME_REASONS:
        assert reason in audit
    for path in AUTHORIZED_TEST_TOKEN_FILES:
        assert path.as_posix() in audit
    assert "RG-174" in registry
    assert "Legacy natal deleted: zero public/runtime hit" in registry
