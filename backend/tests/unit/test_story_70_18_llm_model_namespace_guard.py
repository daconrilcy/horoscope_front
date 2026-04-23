# Garde-fou AC11 pour le namespace canonique des modèles DB LLM.
"""Vérifie que les modèles DB LLM ne régressent pas vers les chemins legacy."""

from __future__ import annotations

import re
from pathlib import Path

from app.infra.db.models.llm.llm_observability import LlmCallLogModel

BACKEND_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = BACKEND_ROOT / "app" / "infra" / "db" / "models"
LLM_MODEL_ROOT = MODEL_ROOT / "llm"
SCAN_ROOTS = (
    BACKEND_ROOT / "app",
    BACKEND_ROOT / "migrations",
    BACKEND_ROOT / "scripts",
    BACKEND_ROOT / "tests",
)
CANONICAL_LLM_MODEL_FILES = (
    "llm_assembly.py",
    "llm_audit.py",
    "llm_canonical_consumption.py",
    "llm_canonical_perimeter.py",
    "llm_compatibility.py",
    "llm_constraints.py",
    "llm_execution_profile.py",
    "llm_field_lengths.py",
    "llm_indexes.py",
    "llm_json_validators.py",
    "llm_observability.py",
    "llm_output_schema.py",
    "llm_persona.py",
    "llm_prompt.py",
    "llm_release.py",
    "llm_sample_payload.py",
)
LEGACY_ROOT_IMPORT_PATTERNS = (
    "from app.infra.db.models import Llm",
    "from app.infra.db.models import PromptAssembly",
    "from app.infra.db.models import PromptStatus",
    "from app.infra.db.models import PersonaTone",
    "from app.infra.db.models import PersonaVerbosity",
    "from app.infra.db.models import ReleaseStatus",
    "app.infra.db.models.llm_",
)
LEGACY_MULTILINE_ROOT_IMPORT_RE = re.compile(
    r"from app\.infra\.db\.models import \((?P<body>.*?)\)",
    re.DOTALL,
)
LEGACY_BARREL_EXPORT_MARKERS = (
    "Llm",
    "PromptAssembly",
    "PromptStatus",
    "PersonaTone",
    "PersonaVerbosity",
    "ReleaseStatus",
)


def iter_python_files() -> list[Path]:
    """Retourne les fichiers Python suivis par le garde-fou sans caches temporaires."""
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            parts = set(path.parts)
            if {"__pycache__", ".pytest_cache", ".ruff_cache", ".tmp-pytest"} & parts:
                continue
            files.append(path)
    return files


def test_llm_db_models_live_only_in_canonical_namespace() -> None:
    """Garantit que les fichiers modèles LLM ne restent pas au niveau racine DB."""
    legacy_files = sorted(path.name for path in MODEL_ROOT.glob("llm_*.py"))
    assert legacy_files == []

    canonical_files = sorted(path.name for path in LLM_MODEL_ROOT.glob("llm_*.py"))
    assert canonical_files == sorted(CANONICAL_LLM_MODEL_FILES)


def test_llm_db_model_imports_do_not_use_legacy_namespace() -> None:
    """Empêche les imports LLM via le barrel racine ou les anciens modules plats."""
    offenders: list[str] = []
    for path in iter_python_files():
        if path == Path(__file__):
            continue
        content = path.read_text(encoding="utf-8")
        for pattern in LEGACY_ROOT_IMPORT_PATTERNS:
            if pattern in content:
                offenders.append(f"{path.relative_to(BACKEND_ROOT)} contient {pattern!r}")
        for match in LEGACY_MULTILINE_ROOT_IMPORT_RE.finditer(content):
            if any(marker in match.group("body") for marker in LEGACY_BARREL_EXPORT_MARKERS):
                offenders.append(
                    f"{path.relative_to(BACKEND_ROOT)} importe un symbole LLM via le barrel racine"
                )

    assert offenders == []


def test_root_model_barrel_does_not_reexport_llm_symbols() -> None:
    """Vérifie que le barrel DB racine ne sert pas de shim legacy LLM."""
    content = (MODEL_ROOT / "__init__.py").read_text(encoding="utf-8")
    offenders = [marker for marker in LEGACY_BARREL_EXPORT_MARKERS if marker in content]
    assert offenders == []


def test_alembic_env_imports_canonical_llm_package_for_metadata() -> None:
    """Garantit qu Alembic charge la metadata LLM sans réexport barrel racine."""
    content = (BACKEND_ROOT / "migrations" / "env.py").read_text(encoding="utf-8")

    assert "from app.infra.db.models import llm as _llm_models" in content


def test_llm_call_log_model_does_not_keep_python_provider_alias() -> None:
    """Interdit le retour de l alias applicatif `provider` sur le log LLM."""
    assert "provider" not in LlmCallLogModel.__dict__
    assert "provider_compat" in LlmCallLogModel.__dict__


def test_each_canonical_llm_model_file_is_used_by_backend_code() -> None:
    """Vérifie que chaque fichier déplacé est référencé par un import canonique."""
    scanned_files = iter_python_files()
    missing: list[str] = []
    for filename in CANONICAL_LLM_MODEL_FILES:
        stem = filename.removesuffix(".py")
        canonical_import = f"app.infra.db.models.llm.{stem}"
        is_used = any(
            canonical_import in path.read_text(encoding="utf-8")
            for path in scanned_files
            if path != LLM_MODEL_ROOT / filename
        )
        if not is_used:
            missing.append(canonical_import)

    assert missing == []
