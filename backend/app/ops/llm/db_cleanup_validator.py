from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REGISTRY_RELATIVE_PATH = Path("backend/docs/llm-db-cleanup-registry.json")
REQUIRED_OBJECT_IDS = frozenset(
    {
        "table:llm_use_case_configs",
        "table:llm_prompt_versions",
        "table:llm_output_schemas",
        "table:llm_personas",
        "table:llm_assembly_configs",
        "table:llm_execution_profiles",
        "table:llm_release_snapshots",
        "table:llm_active_releases",
        "table:llm_call_logs",
        "table:llm_replay_snapshots",
        "table:llm_canonical_consumption_aggregates",
        "table:llm_sample_payloads",
        "column:llm_use_case_configs.fallback_use_case_key",
        "column:llm_prompt_versions.model",
        "column:llm_prompt_versions.temperature",
        "column:llm_prompt_versions.max_output_tokens",
        "column:llm_prompt_versions.fallback_use_case_key",
        "column:llm_prompt_versions.reasoning_effort",
        "column:llm_prompt_versions.verbosity",
        "column:llm_assembly_configs.fallback_use_case",
        "column:llm_call_logs.use_case",
        "index:llm_call_logs.ix_llm_call_logs_use_case_timestamp",
    }
)


@dataclass(frozen=True)
class LlmDbCleanupViolation:
    code: str
    message: str
    detail: str | None = None

    def as_user_string(self) -> str:
        if self.detail:
            return f"[llm-db-cleanup:{self.code}] {self.message} | {self.detail}"
        return f"[llm-db-cleanup:{self.code}] {self.message}"


def load_cleanup_registry(registry_path: Path) -> dict[str, Any]:
    return json.loads(registry_path.read_text(encoding="utf-8"))


def validate_registry_structure(
    registry: dict[str, Any], *, root_path: Path
) -> list[LlmDbCleanupViolation]:
    violations: list[LlmDbCleanupViolation] = []
    version = str(registry.get("version", "")).strip()
    if not version:
        violations.append(
            LlmDbCleanupViolation(
                code="REGISTRY_VERSION",
                message="Le registre de cleanup DB LLM doit porter une version explicite.",
            )
        )

    objects = registry.get("objects")
    if not isinstance(objects, list) or not objects:
        return [
            LlmDbCleanupViolation(
                code="REGISTRY_OBJECTS",
                message="Le registre de cleanup DB LLM doit contenir une liste non vide d objets.",
            )
        ]

    object_ids: list[str] = []
    for obj in objects:
        if not isinstance(obj, dict):
            violations.append(
                LlmDbCleanupViolation(
                    code="REGISTRY_OBJECT_FORMAT",
                    message="Chaque entree objet doit etre un dictionnaire JSON.",
                )
            )
            continue
        object_id = str(obj.get("object_id", "")).strip()
        if not object_id:
            violations.append(
                LlmDbCleanupViolation(
                    code="REGISTRY_OBJECT_ID",
                    message="Chaque objet doit definir un object_id stable.",
                )
            )
            continue
        object_ids.append(object_id)
        usage_status = obj.get("usage_status")
        decision = obj.get("decision")
        if usage_status not in {"nominal", "legacy", "unused", "unknown"}:
            violations.append(
                LlmDbCleanupViolation(
                    code="REGISTRY_USAGE_STATUS",
                    message=f"usage_status invalide pour {object_id}.",
                    detail=f"got={usage_status!r}",
                )
            )
        if decision not in {"keep", "migrate", "freeze", "archive", "drop"}:
            violations.append(
                LlmDbCleanupViolation(
                    code="REGISTRY_DECISION",
                    message=f"decision invalide pour {object_id}.",
                    detail=f"got={decision!r}",
                )
            )
        if usage_status == "unknown" and decision == "drop":
            violations.append(
                LlmDbCleanupViolation(
                    code="UNKNOWN_DROP",
                    message=(
                        f"Un objet classe unknown ne peut pas etre en decision drop: {object_id}."
                    ),
                )
            )

    duplicates = sorted({object_id for object_id in object_ids if object_ids.count(object_id) > 1})
    if duplicates:
        violations.append(
            LlmDbCleanupViolation(
                code="REGISTRY_DUPLICATE_OBJECTS",
                message="Le registre contient des object_id dupliques.",
                detail=", ".join(duplicates),
            )
        )

    missing_required = sorted(REQUIRED_OBJECT_IDS - set(object_ids))
    if missing_required:
        violations.append(
            LlmDbCleanupViolation(
                code="REGISTRY_REQUIRED_OBJECTS",
                message="Le registre ne couvre pas tout le perimetre minimum impose.",
                detail=", ".join(missing_required),
            )
        )

    governance_doc = registry.get("governance_doc")
    if not isinstance(governance_doc, str) or not governance_doc.strip():
        violations.append(
            LlmDbCleanupViolation(
                code="REGISTRY_GOVERNANCE_DOC",
                message="Le registre doit pointer vers une documentation de gouvernance.",
            )
        )
    else:
        if not (root_path / governance_doc).exists():
            violations.append(
                LlmDbCleanupViolation(
                    code="REGISTRY_GOVERNANCE_DOC",
                    message="La documentation de gouvernance referencee est introuvable.",
                    detail=governance_doc,
                )
            )

    compatibility_rules = registry.get("compatibility_rules")
    if not isinstance(compatibility_rules, list) or not compatibility_rules:
        violations.append(
            LlmDbCleanupViolation(
                code="REGISTRY_COMPAT_RULES",
                message="Le registre doit definir des regles de compatibilite explicites.",
            )
        )
    else:
        violations.extend(validate_compatibility_rules_structure(compatibility_rules))

    return violations


def validate_compatibility_rules_structure(
    compatibility_rules: list[dict[str, Any]],
) -> list[LlmDbCleanupViolation]:
    violations: list[LlmDbCleanupViolation] = []
    for rule in compatibility_rules:
        rule_id = str(rule.get("rule_id", "")).strip()
        pattern = str(rule.get("pattern", "")).strip()
        allowed_paths = list(rule.get("allowed_paths", []))
        if not rule_id or not pattern or not allowed_paths:
            violations.append(
                LlmDbCleanupViolation(
                    code="INVALID_COMPAT_RULE",
                    message=(
                        "Chaque regle de compatibilite doit definir "
                        "rule_id, pattern et allowed_paths."
                    ),
                    detail=rule_id or pattern or "unknown_rule",
                )
            )
            continue
        for allowed_path in allowed_paths:
            normalized = str(allowed_path).replace("\\", "/")
            if normalized.endswith("/"):
                violations.append(
                    LlmDbCleanupViolation(
                        code="BROAD_COMPAT_ALLOWLIST",
                        message=(
                            "Les allowlists de compatibilite doivent "
                            "cibler des fichiers explicites,"
                            " pas des repertoires entiers."
                        ),
                        detail=f"rule={rule_id} path={normalized}",
                    )
                )
    return violations


def discover_llm_tables(models_root: Path) -> set[str]:
    table_names: set[str] = set()
    pattern = re.compile(r'__tablename__\s*=\s*"([^"]+)"')
    for path in models_root.rglob("*.py"):
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for match in pattern.findall(content):
            if match.startswith("llm_"):
                table_names.add(match)
    return table_names


def discover_governed_llm_tables(registry: dict[str, Any], *, models_root: Path) -> set[str]:
    governed = discover_llm_tables(models_root)
    for obj in registry.get("objects", []):
        if not isinstance(obj, dict):
            continue
        if obj.get("kind") != "table":
            continue
        table_name = str(obj.get("table", "")).strip()
        if table_name.startswith("llm_"):
            governed.add(table_name)
    return governed


def validate_discovered_tables(
    registry: dict[str, Any], *, models_root: Path
) -> list[LlmDbCleanupViolation]:
    discovered = discover_llm_tables(models_root)
    registered_ids = {
        str(obj["object_id"])
        for obj in registry.get("objects", [])
        if isinstance(obj, dict) and "object_id" in obj
    }
    missing_tables = sorted(
        f"table:{table_name}"
        for table_name in discovered
        if f"table:{table_name}" not in registered_ids
    )
    if not missing_tables:
        return []
    return [
        LlmDbCleanupViolation(
            code="UNREGISTERED_LLM_TABLE",
            message=(
                "Des tables LLM presentes dans les modeles ne sont pas classees dans le registre."
            ),
            detail=", ".join(missing_tables),
        )
    ]


def discover_reviewable_llm_migrations(
    migrations_root: Path, *, known_tables: set[str]
) -> set[str]:
    reviewable: set[str] = set()
    for path in migrations_root.glob("*.py"):
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if any(table_name in content for table_name in known_tables):
            reviewable.add(path.name)
    return reviewable


def validate_reviewed_migrations(
    registry: dict[str, Any], *, migrations_root: Path, known_tables: set[str]
) -> list[LlmDbCleanupViolation]:
    reviewable = discover_reviewable_llm_migrations(migrations_root, known_tables=known_tables)
    reviewed = set(registry.get("reviewed_migrations", []))
    violations: list[LlmDbCleanupViolation] = []
    missing = sorted(reviewable - reviewed)
    extra = sorted(reviewed - reviewable)
    if missing:
        violations.append(
            LlmDbCleanupViolation(
                code="UNREVIEWED_LLM_MIGRATION",
                message="Des migrations LLM detectees ne sont pas referencees dans le registre.",
                detail=", ".join(missing),
            )
        )
    if extra:
        violations.append(
            LlmDbCleanupViolation(
                code="STALE_REVIEWED_MIGRATION",
                message=(
                    "Le registre reference des migrations LLM non detectees dans le repo courant."
                ),
                detail=", ".join(extra),
            )
        )
    return violations


def scan_python_sources_for_legacy_patterns(
    *, root_path: Path, compatibility_rules: list[dict[str, Any]]
) -> list[LlmDbCleanupViolation]:
    violations: list[LlmDbCleanupViolation] = []
    search_roots = [root_path / "backend" / "app", root_path / "backend" / "scripts"]
    python_files: list[Path] = []
    for search_root in search_roots:
        if not search_root.exists():
            continue
        python_files.extend(
            path
            for path in search_root.rglob("*.py")
            if "__pycache__" not in path.parts
            and "tests" not in path.parts
            and path.name != "db_cleanup_validator.py"
        )

    for rule in compatibility_rules:
        rule_id = str(rule.get("rule_id", "")).strip()
        pattern = str(rule.get("pattern", "")).strip()
        allowed_paths = tuple(
            str(item).replace("\\", "/") for item in rule.get("allowed_paths", [])
        )
        regex = re.compile(pattern)
        for path in python_files:
            relative_path = path.relative_to(root_path).as_posix()
            content = path.read_text(encoding="utf-8")
            if not regex.search(content):
                continue
            if any(relative_path.startswith(prefix) for prefix in allowed_paths):
                continue
            violations.append(
                LlmDbCleanupViolation(
                    code="LEGACY_ACCESS_OUTSIDE_ALLOWLIST",
                    message="Usage legacy detecte hors perimetre explicitement borne.",
                    detail=f"rule={rule_id} path={relative_path}",
                )
            )
    return violations


class LlmDbCleanupValidator:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.registry_path = root_path / REGISTRY_RELATIVE_PATH

    def validate_all(self) -> list[LlmDbCleanupViolation]:
        registry = load_cleanup_registry(self.registry_path)
        models_root = self.root_path / "backend" / "app" / "infra" / "db" / "models"
        migrations_root = self.root_path / "backend" / "migrations" / "versions"
        known_tables = discover_governed_llm_tables(registry, models_root=models_root)

        violations: list[LlmDbCleanupViolation] = []
        violations.extend(validate_registry_structure(registry, root_path=self.root_path))
        violations.extend(validate_discovered_tables(registry, models_root=models_root))
        violations.extend(
            validate_reviewed_migrations(
                registry,
                migrations_root=migrations_root,
                known_tables=known_tables,
            )
        )
        violations.extend(
            scan_python_sources_for_legacy_patterns(
                root_path=self.root_path,
                compatibility_rules=list(registry.get("compatibility_rules", [])),
            )
        )
        return violations


def llm_db_cleanup_registry_version(root_path: Path | None = None) -> str:
    base_path = root_path or Path(__file__).resolve().parents[4]
    registry = load_cleanup_registry(base_path / REGISTRY_RELATIVE_PATH)
    return str(registry.get("version", "unknown"))
