#!/usr/bin/env python3
"""Valide le contrat d'une story CONDAMAD Story Writer.

Le validateur refuse les stories trop interpretables: sections manquantes,
criteres d'acceptation sans preuve, taches non reliees aux AC, domaine multiple
ou formulations vagues.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REQUIRED_SECTIONS = [
    "Objective",
    "Trigger / Source",
    "Domain Boundary",
    "Operation Contract",
    "Required Contracts",
    "Current State Evidence",
    "Target State",
    "Acceptance Criteria",
    "Implementation Tasks",
    "Mandatory Reuse / DRY Constraints",
    "No Legacy / Forbidden Paths",
    "Files to Inspect First",
    "Expected Files to Modify",
    "Dependency Policy",
    "Validation Plan",
    "Regression Risks",
    "Dev Agent Instructions",
    "References",
]

REMOVAL_REQUIRED_SECTIONS = [
    "Removal Classification Rules",
    "Removal Audit Format",
    "Canonical Ownership",
    "Delete-Only Rule",
    "External Usage Blocker",
    "Reintroduction Guard",
    "Generated Contract Check",
]

SUPPORTED_ARCHETYPES = {
    "api-route-removal",
    "api-contract-change",
    "api-error-contract-centralization",
    "route-architecture-convergence",
    "api-adapter-boundary-convergence",
    "legacy-facade-removal",
    "field-contract-removal",
    "namespace-convergence",
    "ownership-routing-refactor",
    "module-move",
    "large-file-split",
    "dead-code-removal",
    "frontend-route-removal",
    "runtime-contract-preservation",
    "batch-migration",
    "architecture-guard-hardening",
    "registry-catalog-refactor",
    "test-guard-hardening",
    "service-boundary-refactor",
    "custom",
}

ALLOWED_STORY_STATUSES = {
    "ready-to-dev",
    "ready-to-review",
    "done",
}

STORY_TITLE_RE = re.compile(r"^# Story\s+CS-\d{3}\s+\S+:\s+\S", re.M)

KNOWN_CONTRACTS = (
    "Runtime Source of Truth",
    "Baseline Snapshot",
    "Ownership Routing",
    "Allowlist Exception",
    "Contract Shape",
    "Batch Migration",
    "Reintroduction Guard",
    "Persistent Evidence",
)

ARCHETYPE_REQUIRED_CONTRACTS = {
    "api-route-removal": {
        "Runtime Source of Truth",
        "Baseline Snapshot",
        "Contract Shape",
        "Reintroduction Guard",
        "Persistent Evidence",
    },
    "api-contract-change": {
        "Runtime Source of Truth",
        "Baseline Snapshot",
        "Contract Shape",
        "Reintroduction Guard",
        "Persistent Evidence",
    },
    "api-error-contract-centralization": {
        "Runtime Source of Truth",
        "Ownership Routing",
        "Allowlist Exception",
        "Contract Shape",
        "Reintroduction Guard",
    },
    "route-architecture-convergence": {
        "Runtime Source of Truth",
        "Baseline Snapshot",
        "Ownership Routing",
        "Allowlist Exception",
        "Reintroduction Guard",
        "Persistent Evidence",
    },
    "api-adapter-boundary-convergence": {
        "Runtime Source of Truth",
        "Baseline Snapshot",
        "Ownership Routing",
        "Allowlist Exception",
        "Reintroduction Guard",
    },
    "legacy-facade-removal": {
        "Runtime Source of Truth",
        "Baseline Snapshot",
        "Ownership Routing",
        "Reintroduction Guard",
        "Persistent Evidence",
    },
    "field-contract-removal": {
        "Baseline Snapshot",
        "Contract Shape",
        "Reintroduction Guard",
        "Persistent Evidence",
    },
    "namespace-convergence": {
        "Baseline Snapshot",
        "Ownership Routing",
        "Batch Migration",
        "Reintroduction Guard",
        "Persistent Evidence",
    },
    "ownership-routing-refactor": {
        "Baseline Snapshot",
        "Ownership Routing",
        "Allowlist Exception",
        "Reintroduction Guard",
    },
    "module-move": {
        "Baseline Snapshot",
        "Ownership Routing",
        "Reintroduction Guard",
    },
    "large-file-split": {
        "Baseline Snapshot",
        "Ownership Routing",
        "Reintroduction Guard",
    },
    "dead-code-removal": {
        "Baseline Snapshot",
        "Reintroduction Guard",
        "Persistent Evidence",
    },
    "frontend-route-removal": {
        "Baseline Snapshot",
        "Contract Shape",
        "Reintroduction Guard",
        "Persistent Evidence",
    },
    "runtime-contract-preservation": {
        "Runtime Source of Truth",
        "Baseline Snapshot",
        "Contract Shape",
        "Persistent Evidence",
    },
    "batch-migration": {
        "Baseline Snapshot",
        "Batch Migration",
        "Reintroduction Guard",
        "Persistent Evidence",
    },
    "architecture-guard-hardening": {
        "Runtime Source of Truth",
        "Allowlist Exception",
        "Reintroduction Guard",
    },
    "registry-catalog-refactor": {
        "Baseline Snapshot",
        "Ownership Routing",
        "Batch Migration",
        "Persistent Evidence",
    },
    "test-guard-hardening": {
        "Runtime Source of Truth",
        "Allowlist Exception",
        "Reintroduction Guard",
    },
    "service-boundary-refactor": {
        "Baseline Snapshot",
        "Ownership Routing",
        "Reintroduction Guard",
    },
}

CONTRACT_SHAPE_ARCHETYPES = {
    archetype
    for archetype, contracts in ARCHETYPE_REQUIRED_CONTRACTS.items()
    if "Contract Shape" in contracts
}

BATCH_MIGRATION_ARCHETYPES = {
    archetype
    for archetype, contracts in ARCHETYPE_REQUIRED_CONTRACTS.items()
    if "Batch Migration" in contracts
}

CONTRACT_SECTION_TITLES = {
    "Runtime Source of Truth": "Runtime Source of Truth",
    "Baseline Snapshot": "Baseline / Before-After Rule",
    "Ownership Routing": "Ownership Routing Rule",
    "Allowlist Exception": "Allowlist / Exception Register",
    "Contract Shape": "Contract Shape",
    "Batch Migration": "Batch Migration Plan",
    "Reintroduction Guard": "Reintroduction Guard",
    "Persistent Evidence": "Persistent Evidence Artifacts",
}

REMOVAL_ARCHETYPES = {
    "api-route-removal",
    "legacy-facade-removal",
    "field-contract-removal",
    "dead-code-removal",
    "frontend-route-removal",
}

REMOVAL_STRONG_TRIGGERS = [
    "remove",
    "delete",
    "removal",
    "deletion",
    "supprimer",
    "suppression",
    "éliminer",
    "eliminer",
    "retirer",
]

REMOVAL_WEAK_TRIGGERS = [
    "legacy",
    "historical",
    "façade",
    "facade",
    "compat",
]

REMOVAL_TARGET_RE = re.compile(
    r"\b(route|endpoint|field|module|file|type|ui|screen|path|surface)s?\b",
    re.I,
)

GENERATED_CONTRACT_ARCHETYPES = {
    "api-route-removal",
    "legacy-facade-removal",
    "field-contract-removal",
    "frontend-route-removal",
}

ALLOWED_CLASSIFICATIONS = {
    "canonical-active",
    "external-active",
    "historical-facade",
    "dead",
    "needs-user-decision",
}

REQUIRED_REMOVAL_DECISIONS = {
    "keep",
    "delete",
    "replace-consumer",
    "needs-user-decision",
}

EVIDENCE_PROFILES = {
    "route_removed",
    "python_module_removed",
    "frontend_route_removed",
    "no_legacy_contract",
    "field_removed",
    "namespace_converged",
    "runtime_openapi_contract",
    "openapi_before_after_snapshot",
    "route_absence_runtime",
    "python_import_absence",
    "ast_architecture_guard",
    "repo_wide_negative_scan",
    "targeted_forbidden_symbol_scan",
    "allowlist_register_validated",
    "json_contract_shape",
    "api_error_shape_contract",
    "frontend_typecheck_no_orphan",
    "baseline_before_after_diff",
    "batch_migration_mapping",
    "reintroduction_guard",
    "external_usage_blocker",
}

RUNTIME_EVIDENCE_PROFILES = {
    "runtime_openapi_contract",
    "openapi_before_after_snapshot",
    "route_absence_runtime",
    "ast_architecture_guard",
    "json_contract_shape",
    "api_error_shape_contract",
}

RUNTIME_CONTRACT_TERMS_RE = re.compile(
    r"\b(route|routes|router|openapi|http|api|endpoint|config|settings|db|database|"
    r"schema|generated contract|generated client|manifest|runtime)\b",
    re.I,
)

RUNTIME_COMMAND_RE = re.compile(
    r"app\.openapi\(|app\.routes|from\s+backend\.app\.main\s+import\s+app|"
    r"TestClient|route table|loaded config|settings\.|inspect\(|MetaData|alembic|"
    r"generated manifest|AST guard",
    re.I,
)

BASELINE_OPERATION_TYPES = {"move", "split", "converge", "migrate"}

OWNERSHIP_ARCHETYPE_TERMS = (
    "boundary",
    "namespace",
    "service",
    "api",
    "adapter",
    "core",
    "domain",
    "infra",
    "ownership",
)

ALLOWLIST_TRIGGER_RE = re.compile(
    r"\b(allowlist|exception|allowed exception|except|sauf)\b", re.I
)

CONTRACT_SHAPE_CHANGE_RE = re.compile(
    r"\b(remove field|field removal|change response|response shape change|"
    r"drop detail|contract shape change|payload shape change)\b",
    re.I,
)

PERSISTENT_EVIDENCE_TRIGGER_RE = re.compile(
    r"\b(audit|snapshot|baseline|openapi diff|diff snapshot|migration mapping|"
    r"allowlist register|exception register)\b",
    re.I,
)

VAGUE_TERMS = [
    "improve",
    "cleanup",
    "refactor everything",
    "as needed",
    "where relevant",
    "etc.",
]

VAGUE_CHECK_SECTIONS = [
    "Objective",
    "Target State",
    "Acceptance Criteria",
    "Implementation Tasks",
]

VAGUE_NEGATIVE_CONTEXT_RE = re.compile(
    r"\b(?:do not|no|forbidden|out of scope|non-goal|non-goals|unrelated)\s+"
    r"(?:\w+\s+){0,4}?(?:improve|cleanup|refactor everything|as needed|where relevant|etc\.)\b",
    re.I,
)

COMMAND_PATTERNS = [
    r"\bpytest\b",
    r"\bpython\b",
    r"\bruff\b",
    r"\brg\b",
    r"\bnpm\b",
    r"\bpnpm\b",
    r"\bvitest\b",
    r"\beslint\b",
    r"\btsc\b",
]

WEAK_EVIDENCE_PATTERNS = [
    r"^\s*review manually\.?\s*$",
    r"^\s*check it works\.?\s*$",
    r"^\s*covered by tests\.?\s*$",
]

TEST_PATH_RE = re.compile(
    r"(?:^|[\s`])(?:[\w./-]*tests?[\w./-]*|[\w./-]*test[\w./-]*)"
    r"\.(?:py|ts|tsx|js|jsx)(?:[\s`]|$)",
    re.I,
)

MANUAL_CHECK_RE = re.compile(
    r"\bManual check:\s+.+\b(?:expected|verify|verifies|confirm|confirms)\b.+",
    re.I,
)

KNOWN_PATH_EXTENSIONS = {
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".py",
    ".scss",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

BACKTICK_VALUE_RE = re.compile(r"`([^`\n<>]+)`")


@dataclass(frozen=True)
class MarkdownTable:
    """Represente une table markdown simple."""

    headers: list[str]
    rows: list[list[str]]


def read_text(path: Path) -> str:
    """Lit une story markdown en preservant les caracteres invalides."""
    return path.read_text(encoding="utf-8", errors="replace")


def normalize(value: str) -> str:
    """Normalise une chaine pour les comparaisons de titres."""
    value = re.sub(r"^\d+[a-z]?\.\s*", "", value.strip(), flags=re.I)
    value = re.sub(r"\s+", " ", value)
    return value.casefold()


def split_row(line: str) -> list[str]:
    """Decoupe une ligne de table markdown en cellules nettoyees."""
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(line: str) -> bool:
    """Indique si la ligne est un separateur de table markdown."""
    cells = split_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def parse_tables(text: str) -> list[MarkdownTable]:
    """Extrait les tables markdown simples d'un texte."""
    lines = text.splitlines()
    tables: list[MarkdownTable] = []
    index = 0
    while index + 1 < len(lines):
        if "|" not in lines[index] or not is_separator(lines[index + 1]):
            index += 1
            continue
        headers = split_row(lines[index])
        rows: list[list[str]] = []
        index += 2
        while index < len(lines) and "|" in lines[index]:
            rows.append(split_row(lines[index]))
            index += 1
        tables.append(MarkdownTable(headers=headers, rows=rows))
    return tables


def section_bounds(text: str) -> dict[str, tuple[int, int]]:
    """Retourne les bornes des sections markdown par titre normalise."""
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.M))
    bounds: dict[str, tuple[int, int]] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        bounds[normalize(match.group(1))] = (start, end)
    return bounds


def get_section(text: str, title: str) -> str:
    """Extrait une section par titre logique."""
    bounds = section_bounds(text).get(normalize(title))
    if bounds is None:
        return ""
    return text[bounds[0] : bounds[1]].strip()


def has_required_sections(text: str) -> list[str]:
    """Verifie la presence des sections obligatoires."""
    headings = section_bounds(text)
    return [
        section for section in REQUIRED_SECTIONS if normalize(section) not in headings
    ]


def find_ac_table(text: str) -> MarkdownTable | None:
    """Retourne la table AC si elle contient les colonnes minimales."""
    for table in parse_tables(text):
        headers = [normalize(header) for header in table.headers]
        has_ac = "ac" in headers
        has_requirement = "requirement" in headers
        has_evidence = any(
            header in {"validation evidence required", "verification", "evidence"}
            for header in headers
        )
        if has_ac and has_requirement and has_evidence:
            return table
    return None


def ac_table_columns(table: MarkdownTable) -> tuple[int, int, int]:
    """Retourne les index AC, requirement et evidence d'une table AC."""
    headers = [normalize(header) for header in table.headers]
    ac_index = headers.index("ac")
    requirement_index = headers.index("requirement")
    evidence_index = next(
        position
        for position, header in enumerate(headers)
        if header in {"validation evidence required", "verification", "evidence"}
    )
    return ac_index, requirement_index, evidence_index


def acceptance_criteria_ids(text: str) -> set[str]:
    """Extrait les identifiants AC declares dans la table des AC."""
    section = get_section(text, "Acceptance Criteria")
    table = find_ac_table(section)
    if table is None:
        return set()
    ac_index, _, _ = ac_table_columns(table)
    return {
        row[ac_index].strip()
        for row in table.rows
        if len(row) > ac_index and re.fullmatch(r"AC\d+", row[ac_index].strip())
    }


def has_concrete_ac_evidence(evidence: str) -> bool:
    """Verifie qu'une preuve d'AC est executable ou structuree."""
    if not evidence or evidence in {"...", "<...>", "test / guard / grep / command"}:
        return False
    if any(re.fullmatch(pattern, evidence, re.I) for pattern in WEAK_EVIDENCE_PATTERNS):
        return False
    profile_match = re.search(r"Evidence profile:\s*`?([A-Za-z0-9_-]+)`?", evidence)
    has_known_profile = bool(
        profile_match and profile_match.group(1) in EVIDENCE_PROFILES
    )
    has_command = any(re.search(pattern, evidence) for pattern in COMMAND_PATTERNS)
    has_test_path = bool(TEST_PATH_RE.search(evidence))
    has_manual_check = bool(MANUAL_CHECK_RE.search(evidence))

    if has_known_profile:
        return has_command or has_test_path or has_manual_check
    return has_command or has_test_path or has_manual_check


def evidence_profile_names(evidence: str) -> set[str]:
    """Extrait les profils de preuve cites dans une cellule d'evidence."""
    return {
        match.group(1)
        for match in re.finditer(r"Evidence profile:\s*`?([A-Za-z0-9_-]+)`?", evidence)
    }


def has_runtime_evidence(evidence: str) -> bool:
    """Indique si une preuve interroge une source runtime deterministe."""
    has_runtime_command = bool(RUNTIME_COMMAND_RE.search(evidence))
    has_runtime_test = bool(TEST_PATH_RE.search(evidence)) and bool(
        re.search(r"\b(pytest|npm|pnpm|vitest|tsc)\b", evidence, re.I)
    )
    return has_runtime_command or has_runtime_test


def validate_acceptance_criteria(text: str) -> list[str]:
    """Valide les AC et leurs preuves."""
    errors: list[str] = []
    section = get_section(text, "Acceptance Criteria")
    table = find_ac_table(section)
    if table is None:
        return [
            "Acceptance Criteria table must include AC, Requirement, and evidence columns"
        ]

    ac_index, requirement_index, evidence_index = ac_table_columns(table)

    expected_number = 1
    seen: list[str] = []
    for row in table.rows:
        if len(row) <= max(ac_index, requirement_index, evidence_index):
            errors.append("Acceptance Criteria table has an incomplete row")
            continue
        ac_id = row[ac_index].strip()
        requirement = row[requirement_index].strip()
        evidence = row[evidence_index].strip()
        if not re.fullmatch(r"AC\d+", ac_id):
            errors.append(f"Invalid AC id: {ac_id or '<empty>'}")
            continue
        if ac_id != f"AC{expected_number}":
            errors.append(
                f"AC ids must be sequential: expected AC{expected_number}, got {ac_id}"
            )
        if not requirement or requirement in {"...", "<...>"}:
            errors.append(f"{ac_id} has empty requirement")
        if not has_concrete_ac_evidence(evidence):
            errors.append(f"{ac_id} has no concrete validation evidence")
        if RUNTIME_CONTRACT_TERMS_RE.search(requirement) and not has_runtime_evidence(
            evidence
        ):
            errors.append(
                f"{ac_id} touches a runtime contract and must include runtime evidence"
            )
        seen.append(ac_id)
        expected_number += 1

    if not seen:
        errors.append("Acceptance Criteria table has no AC rows")
    return errors


def validate_tasks(text: str) -> list[str]:
    """Verifie que chaque tache de premier niveau reference un AC."""
    errors: list[str] = []
    section = get_section(text, "Implementation Tasks")
    existing_ac_ids = acceptance_criteria_ids(text)
    task_lines = [
        line.strip()
        for line in section.splitlines()
        if re.match(r"^-\s+\[[ xX]\]\s+Task\b", line.strip())
    ]
    if not task_lines:
        return ["Implementation Tasks must contain at least one '- [ ] Task' item"]
    for line in task_lines:
        match = re.search(r"\(AC:\s*(AC\d+(?:\s*,\s*AC\d+)*)\)", line)
        if not match:
            errors.append(f"Task missing AC reference: {line}")
            continue
        referenced_ac_ids = {
            ac_id.strip() for ac_id in match.group(1).split(",") if ac_id.strip()
        }
        unknown_ac_ids = sorted(referenced_ac_ids - existing_ac_ids)
        for ac_id in unknown_ac_ids:
            errors.append(f"Task references unknown AC: {ac_id} in {line}")
    return errors


def validate_current_state_evidence(text: str) -> list[str]:
    """Verifie que l'etat actuel est appuye par preuve ou hypothese explicite."""
    section = get_section(text, "Current State Evidence")
    has_evidence = re.search(
        r"^\s*-\s*Evidence\s+\d+:\s+`?[^`\n]+`?\s+-\s+\S+", section, re.M
    )
    has_unavailable_evidence = (
        "Repository evidence: not available" in section
        and "Assumption risk:" in section
    )
    if has_evidence or has_unavailable_evidence:
        return []
    return [
        "Current State Evidence must include at least one evidence item or an explicit repository evidence assumption risk"
    ]


def validate_domain_boundary(text: str) -> list[str]:
    """Controle le domaine unique et les non-goals."""
    errors: list[str] = []
    section = get_section(text, "Domain Boundary")
    domain_count = len(re.findall(r"^\s*-\s*Domain:\s*\S+", section, re.M))
    if domain_count != 1:
        errors.append(
            f"Domain Boundary must contain exactly one '- Domain:' entry, found {domain_count}"
        )
    for marker in ["In scope:", "Out of scope:", "Explicit non-goals:"]:
        if marker not in section:
            errors.append(f"Domain Boundary missing marker: {marker}")
    non_goals_match = re.search(
        r"Explicit non-goals:\s*\n(?P<body>(?:\s+-\s+.+\n?)+)",
        section,
        re.I,
    )
    if not non_goals_match or "..." in non_goals_match.group("body"):
        errors.append("Domain Boundary must include concrete explicit non-goals")
    return errors


def marker_value(section: str, marker: str) -> str:
    """Retourne la valeur d'un marker de liste markdown."""
    match = re.search(
        rf"^\s*-\s*{re.escape(marker)}:\s*(?P<value>.+?)\s*$",
        section,
        re.I | re.M,
    )
    return match.group("value").strip() if match else ""


def validate_operation_contract(text: str) -> list[str]:
    """Valide le contrat operationnel et l'archetype primaire."""
    errors: list[str] = []
    section = get_section(text, "Operation Contract")
    if not section:
        return ["Operation Contract section is empty"]

    required_markers = [
        "Operation type",
        "Primary archetype",
        "Archetype reason",
        "Behavior change allowed",
        "Deletion allowed",
        "Replacement allowed",
        "User decision required if",
    ]
    for marker in required_markers:
        value = marker_value(section, marker)
        if not value or value in {"...", "<condition>", "<why this archetype applies>"}:
            errors.append(f"Operation Contract missing concrete marker: {marker}")

    operation_type = marker_value(section, "Operation type").casefold()
    if operation_type and operation_type not in {
        "create",
        "update",
        "move",
        "remove",
        "split",
        "converge",
        "guard",
        "migrate",
    }:
        errors.append(f"Unsupported Operation type: {operation_type}")

    archetype = marker_value(section, "Primary archetype").casefold()
    if archetype and archetype not in SUPPORTED_ARCHETYPES:
        errors.append(f"Unsupported Primary archetype: {archetype}")
    if archetype == "custom" and "Additional validation rules:" not in section:
        errors.append(
            "Custom archetype must include 'Additional validation rules:' in Operation Contract"
        )

    for marker in ["Deletion allowed", "Replacement allowed"]:
        value = marker_value(section, marker).casefold()
        if value and value not in {"yes", "no"}:
            errors.append(f"Operation Contract marker must be yes or no: {marker}")

    behavior_change = marker_value(section, "Behavior change allowed").casefold()
    if behavior_change and behavior_change not in {"no", "constrained", "yes"}:
        errors.append(
            "Operation Contract marker must be no, constrained, or yes: Behavior change allowed"
        )
    if behavior_change in {"constrained", "yes"}:
        constraints = block_after_marker(
            section,
            "Behavior change constraints:",
            [
                "Deletion allowed:",
                "Replacement allowed:",
                "User decision required if:",
            ],
        )
        if not re.search(r"^\s*-\s+\S", constraints, re.M):
            errors.append(
                "Operation Contract must include concrete Behavior change constraints when behavior change is constrained or yes"
            )

    errors.extend(validate_operation_contract_contradictions(text))

    if is_removal_story(text):
        deletion_allowed = marker_value(section, "Deletion allowed").casefold()
        if deletion_allowed != "yes":
            errors.append("Removal story must set 'Deletion allowed: yes'")
        if archetype not in REMOVAL_ARCHETYPES:
            errors.append(
                "Removal story must use a removal Primary archetype from story-archetypes.md"
            )

    return errors


def validate_operation_contract_contradictions(text: str) -> list[str]:
    """Detecte les contradictions entre operation, suppression et contrat."""
    errors: list[str] = []
    section = get_section(text, "Operation Contract")
    operation_type = marker_value(section, "Operation type").casefold()
    behavior_change = marker_value(section, "Behavior change allowed").casefold()
    deletion_allowed = marker_value(section, "Deletion allowed").casefold()
    replacement_allowed = marker_value(section, "Replacement allowed").casefold()
    lowered_text = text.casefold()

    if operation_type == "remove" and deletion_allowed == "no":
        errors.append("Operation Contract contradiction: remove requires deletion")
    if behavior_change == "no" and CONTRACT_SHAPE_CHANGE_RE.search(lowered_text):
        errors.append(
            "Operation Contract contradiction: behavior change is forbidden but contract shape removal/change is described"
        )
    if (
        replacement_allowed == "yes"
        and "items classified as removable must be deleted, not repointed"
        in lowered_text
    ):
        errors.append(
            "Operation Contract contradiction: Replacement allowed is yes while Delete-Only Rule requires deletion"
        )
    return errors


def required_contracts_from_story(text: str) -> dict[str, str]:
    """Retourne les contrats declares dans la story avec leur statut yes/no."""
    section = get_section(text, "Required Contracts")
    table = find_table_with_columns(section, ["Contract", "Required", "Reason"])
    if table is None:
        return {}
    headers = [normalize(header) for header in table.headers]
    contract_index = headers.index("contract")
    required_index = headers.index("required")
    return {
        row[contract_index].strip(): row[required_index].strip().casefold()
        for row in table.rows
        if len(row) > max(contract_index, required_index)
    }


def validate_required_contracts(text: str) -> list[str]:
    """Verifie que les contrats requis par l'archetype sont persistés."""
    section = get_section(text, "Required Contracts")
    if not section:
        return ["Required Contracts section is empty"]
    table = find_table_with_columns(section, ["Contract", "Required", "Reason"])
    if table is None:
        return ["Required Contracts must include Contract, Required, and Reason table"]

    errors: list[str] = []
    headers = [normalize(header) for header in table.headers]
    contract_index = headers.index("contract")
    required_index = headers.index("required")
    reason_index = headers.index("reason")
    declared: dict[str, str] = {}
    seen_contracts: set[str] = set()
    for row in table.rows:
        if len(row) <= max(contract_index, required_index, reason_index):
            errors.append("Required Contracts table has an incomplete row")
            continue
        contract = row[contract_index].strip()
        required = row[required_index].strip().casefold()
        reason = row[reason_index].strip()
        if contract in seen_contracts:
            errors.append(f"Required Contracts duplicate contract row: {contract}")
        seen_contracts.add(contract)
        if contract not in KNOWN_CONTRACTS:
            errors.append(f"Required Contracts unknown contract: {contract}")
        declared[contract] = required
        if required not in {"yes", "no"}:
            errors.append(f"Required Contracts marker must be yes or no: {contract}")
        if not reason or reason in {"...", "<...>"}:
            errors.append(f"Required Contracts row missing concrete reason: {contract}")

    for contract in KNOWN_CONTRACTS:
        if contract not in declared:
            errors.append(
                f"Required Contracts must list every known contract: {contract}"
            )

    archetype = marker_value(
        get_section(text, "Operation Contract"), "Primary archetype"
    ).casefold()
    if archetype == "custom":
        return errors
    for contract in sorted(ARCHETYPE_REQUIRED_CONTRACTS.get(archetype, set())):
        if declared.get(contract) != "yes":
            errors.append(
                f"Required Contracts must mark archetype contract as yes: {contract}"
            )
    errors.extend(validate_required_contract_section_alignment(text, declared))
    return errors


def validate_required_contract_section_alignment(
    text: str, declared: dict[str, str]
) -> list[str]:
    """Controle l'alignement yes/no des contrats avec leurs sections."""
    errors: list[str] = []
    for contract in KNOWN_CONTRACTS:
        required = declared.get(contract, "")
        section_title = CONTRACT_SECTION_TITLES[contract]
        section = get_section(text, section_title)
        if required == "yes":
            if not section:
                errors.append(
                    f"Required contract marked yes but section is missing: {contract}"
                )
                continue
            if is_not_applicable_section(section):
                errors.append(
                    f"Required contract marked yes but section is not applicable: {contract}"
                )
            if contract == "Reintroduction Guard" and not has_executable_guard_evidence(
                section
            ):
                errors.append(
                    "Required contract marked yes but Reintroduction Guard lacks executable evidence"
                )
        elif required == "no":
            if not section:
                errors.append(
                    f"Required contract marked no must include not applicable section: {contract}"
                )
                continue
            if not is_not_applicable_section(section):
                errors.append(
                    f"Required contract marked no but section is active: {contract}"
                )
            if not re.search(r"^\s*-\s*Reason:\s*\S.+$", section, re.I | re.M):
                errors.append(
                    f"Required contract marked no must include not applicable Reason: {contract}"
                )
    return errors


def is_not_applicable_section(section: str) -> bool:
    """Indique si une section est explicitement non applicable."""
    return bool(re.search(r"\bnot applicable\b", section, re.I))


def is_removal_story(text: str) -> bool:
    """Detecte si une story doit appliquer le contrat Removal."""
    operation = get_section(text, "Operation Contract")
    operation_type = marker_value(operation, "Operation type").casefold()
    archetype = marker_value(operation, "Primary archetype").casefold()
    if operation_type == "remove" or archetype in REMOVAL_ARCHETYPES:
        return True

    first_heading = re.search(r"^#\s+(.+)$", text, re.M)
    signal_parts = [
        first_heading.group(1) if first_heading else "",
        get_section(text, "Objective"),
        get_section(text, "Trigger / Source"),
        get_section(text, "Acceptance Criteria"),
    ]
    signal_text = "\n".join(signal_parts).casefold()
    has_strong_removal = any(
        contains_trigger(signal_text, trigger) for trigger in REMOVAL_STRONG_TRIGGERS
    )
    return has_strong_removal or has_weak_removal_signal(signal_text)


def contains_trigger(text: str, trigger: str) -> bool:
    """Detecte un trigger comme terme distinct, pas comme sous-chaine."""
    return bool(re.search(rf"(?<![\w-]){re.escape(trigger)}(?![\w-])", text, re.I))


def has_weak_removal_signal(text: str) -> bool:
    """Detecte legacy/compat avec une cible removal dans le meme segment."""
    segments = re.split(r"[\n.;:]+", text)
    return any(
        any(contains_trigger(segment, trigger) for trigger in REMOVAL_WEAK_TRIGGERS)
        and bool(REMOVAL_TARGET_RE.search(segment))
        for segment in segments
    )


def validate_removal_contract(text: str) -> list[str]:
    """Valide les sections specialisees des stories de suppression."""
    if not is_removal_story(text):
        return []

    errors: list[str] = []
    for section in REMOVAL_REQUIRED_SECTIONS:
        if not get_section(text, section):
            errors.append(f"Removal story missing required section: {section}")

    errors.extend(validate_removal_classification_rules(text))
    errors.extend(validate_removal_audit_format(text))
    errors.extend(validate_canonical_ownership(text))
    errors.extend(validate_delete_only_rule(text))
    errors.extend(validate_external_usage_blocker(text))
    errors.extend(validate_reintroduction_guard(text))
    errors.extend(validate_generated_contract_check(text))
    return errors


def validate_removal_classification_rules(text: str) -> list[str]:
    """Controle les classifications deterministes obligatoires."""
    section = get_section(text, "Removal Classification Rules")
    if not section:
        return []
    errors: list[str] = []
    for value in ALLOWED_CLASSIFICATIONS:
        if f"`{value}`" not in section and value not in section:
            errors.append(
                f"Removal Classification Rules missing classification: {value}"
            )
    if "not applicable" in section.casefold():
        errors.append(
            "Removal story cannot mark Removal Classification Rules not applicable"
        )
    return errors


def validate_removal_audit_format(text: str) -> list[str]:
    """Controle le format d'audit removal impose par la story."""
    section = get_section(text, "Removal Audit Format")
    if not section:
        return []
    if "not applicable" in section.casefold():
        return ["Removal story cannot mark Removal Audit Format not applicable"]
    errors: list[str] = []
    required_columns = [
        "Item",
        "Type",
        "Classification",
        "Consumers",
        "Canonical replacement",
        "Decision",
        "Proof",
        "Risk",
    ]
    table = find_table_with_columns(section, required_columns)
    if table is None:
        errors.append("Removal Audit Format must include the required audit table")
    for decision in REQUIRED_REMOVAL_DECISIONS:
        if f"`{decision}`" not in section and decision not in section:
            errors.append(f"Removal Audit Format missing allowed decision: {decision}")
    if (
        "route-consumption-audit.md" not in section
        and "audit" not in section.casefold()
    ):
        errors.append("Removal Audit Format must require a persisted audit artifact")
    return errors


def find_table_with_columns(
    text: str, required_columns: list[str]
) -> MarkdownTable | None:
    """Retourne une table markdown contenant toutes les colonnes requises."""
    required = {normalize(column) for column in required_columns}
    for table in parse_tables(text):
        headers = {normalize(header) for header in table.headers}
        if required.issubset(headers):
            return table
    return None


def validate_canonical_ownership(text: str) -> list[str]:
    """Controle la table de proprietaires canoniques."""
    section = get_section(text, "Canonical Ownership")
    if not section:
        return []
    if "not applicable" in section.casefold():
        return ["Removal story cannot mark Canonical Ownership not applicable"]
    if (
        find_table_with_columns(
            section, ["Responsibility", "Canonical owner", "Non-canonical surfaces"]
        )
        is None
    ):
        return ["Canonical Ownership must include the required ownership table"]
    return []


def validate_delete_only_rule(text: str) -> list[str]:
    """Controle que la suppression ne peut pas etre remplacee par un detour."""
    section = get_section(text, "Delete-Only Rule")
    if not section:
        return []
    lowered = section.casefold()
    if "not applicable" in lowered:
        return ["Removal story cannot mark Delete-Only Rule not applicable"]
    required_fragments = ["deleted, not repointed", "wrapper", "alias", "re-export"]
    return [
        f"Delete-Only Rule missing forbidden route: {fragment}"
        for fragment in required_fragments
        if fragment not in lowered
    ]


def validate_external_usage_blocker(text: str) -> list[str]:
    """Controle le blocker pour usage externe actif."""
    section = get_section(text, "External Usage Blocker")
    if not section:
        return []
    lowered = section.casefold()
    if "not applicable" in lowered:
        return ["Removal story cannot mark External Usage Blocker not applicable"]
    required = ["external-active", "must not be deleted", "user decision"]
    return [
        f"External Usage Blocker missing requirement: {fragment}"
        for fragment in required
        if fragment not in lowered
    ]


def validate_reintroduction_guard(text: str) -> list[str]:
    """Controle le garde-fou de reintroduction."""
    section = get_section(text, "Reintroduction Guard")
    if not section:
        return []
    lowered = section.casefold()
    if "not applicable" in lowered:
        return ["Removal story cannot mark Reintroduction Guard not applicable"]
    if "architecture guard" not in lowered or "reintroduced" not in lowered:
        return [
            "Reintroduction Guard must require an architecture guard against reintroduction"
        ]
    deterministic_sources = [
        "registered router prefixes",
        "importable python modules",
        "frontend route table",
        "generated openapi paths",
        "forbidden symbols",
    ]
    if not any(source in lowered for source in deterministic_sources):
        return ["Reintroduction Guard must name at least one deterministic source"]
    if not has_executable_guard_evidence(section):
        return [
            "Reintroduction Guard must include a concrete command, test path, or reintroduction_guard evidence profile with command/test"
        ]
    return []


def has_executable_guard_evidence(section: str) -> bool:
    """Indique si un guard est prouve par une commande, un test ou un profil executable."""
    has_command = any(re.search(pattern, section) for pattern in COMMAND_PATTERNS)
    has_test_path = bool(TEST_PATH_RE.search(section))
    has_guard_profile = "Evidence profile: `reintroduction_guard`" in section or (
        "Evidence profile: reintroduction_guard" in section
    )
    has_forbidden_symbol = bool(BACKTICK_VALUE_RE.search(section))
    if has_guard_profile:
        return (has_command or has_test_path) and has_forbidden_symbol
    return (
        has_command or has_test_path or has_runtime_evidence(section)
    ) and has_forbidden_symbol


def validate_generated_contract_check(text: str) -> list[str]:
    """Controle les preuves de contrats generes pour les surfaces API."""
    section = get_section(text, "Generated Contract Check")
    if not section:
        return []
    archetype = marker_value(
        get_section(text, "Operation Contract"), "Primary archetype"
    ).casefold()
    lowered = section.casefold()
    if "not applicable" in lowered:
        if archetype in GENERATED_CONTRACT_ARCHETYPES:
            return [
                "Generated Contract Check cannot be not applicable for API/frontend/field removal stories"
            ]
        if "reason:" not in lowered and "justification:" not in lowered:
            return ["Generated Contract Check not applicable must include a reason"]
        return []
    if "openapi" not in lowered and "generated" not in lowered:
        return [
            "Generated Contract Check must require OpenAPI or generated artifact absence"
        ]
    return []


def validate_runtime_source_of_truth(text: str) -> list[str]:
    """Exige une source runtime quand la story touche un contrat runtime."""
    section = get_section(text, "Runtime Source of Truth")
    required_contracts = required_contracts_from_story(text)
    story_requires_runtime = (
        bool(
            RUNTIME_CONTRACT_TERMS_RE.search(
                "\n".join(
                    [
                        get_section(text, "Operation Contract"),
                        get_section(text, "Target State"),
                        get_section(text, "Acceptance Criteria"),
                        get_section(text, "Validation Plan"),
                    ]
                )
            )
        )
        or required_contracts.get("Runtime Source of Truth") == "yes"
    )
    if not story_requires_runtime:
        return []
    if not section:
        return ["Runtime contract story missing section: Runtime Source of Truth"]
    lowered = section.casefold()
    if "not applicable" in lowered:
        return ["Runtime Source of Truth cannot be not applicable for runtime stories"]
    errors: list[str] = []
    for marker in [
        "Primary source of truth:",
        "Secondary evidence:",
        "Static scans alone are not sufficient",
    ]:
        if marker.casefold() not in lowered:
            errors.append(f"Runtime Source of Truth missing marker: {marker}")
    if not RUNTIME_COMMAND_RE.search(section):
        errors.append(
            "Runtime Source of Truth must name a runtime artifact such as app.openapi(), app.routes, AST guard, loaded config, DB schema, or generated manifest"
        )
    return errors


def validate_baseline_rule(text: str) -> list[str]:
    """Exige un baseline before/after pour les operations a risque."""
    operation = get_section(text, "Operation Contract")
    operation_type = marker_value(operation, "Operation type").casefold()
    behavior_change = marker_value(operation, "Behavior change allowed").casefold()
    required_contracts = required_contracts_from_story(text)
    if (
        operation_type not in BASELINE_OPERATION_TYPES
        and behavior_change != "no"
        and required_contracts.get("Baseline Snapshot") != "yes"
    ):
        return []
    section = get_section(text, "Baseline / Before-After Rule")
    if not section:
        return [
            "Baseline-triggering story missing section: Baseline / Before-After Rule"
        ]
    lowered = section.casefold()
    if "not applicable" in lowered:
        return ["Baseline / Before-After Rule cannot be not applicable for this story"]
    errors: list[str] = []
    for marker in [
        "Baseline artifact before implementation:",
        "Comparison after implementation:",
        "Expected invariant:",
    ]:
        if marker.casefold() not in lowered:
            errors.append(f"Baseline / Before-After Rule missing marker: {marker}")
    if not (
        any(is_concrete_path(value) for value in BACKTICK_VALUE_RE.findall(section))
        or any(re.search(pattern, section) for pattern in COMMAND_PATTERNS)
    ):
        errors.append(
            "Baseline / Before-After Rule must include a concrete artifact path or command"
        )
    return errors


def validate_ownership_routing_rule(text: str) -> list[str]:
    """Exige la table d'ownership pour boundary/refactor/convergence."""
    operation = get_section(text, "Operation Contract")
    archetype = marker_value(operation, "Primary archetype").casefold()
    required_contracts = required_contracts_from_story(text)
    if required_contracts:
        requires_ownership = required_contracts.get("Ownership Routing") == "yes"
    else:
        requires_ownership = any(
            term in archetype for term in OWNERSHIP_ARCHETYPE_TERMS
        )
    if not requires_ownership:
        return []
    section = get_section(text, "Ownership Routing Rule")
    if not section:
        return ["Ownership story missing section: Ownership Routing Rule"]
    if "not applicable" in section.casefold():
        return ["Ownership Routing Rule cannot be not applicable for this archetype"]
    if (
        find_table_with_columns(
            section,
            ["Responsibility type", "Canonical owner", "Forbidden destination"],
        )
        is None
    ):
        return ["Ownership Routing Rule must include the responsibility routing table"]
    return []


def validate_contract_shape(text: str) -> list[str]:
    """Exige la forme exacte des contrats API/DTO/types quand active."""
    archetype = marker_value(
        get_section(text, "Operation Contract"), "Primary archetype"
    ).casefold()
    required_contracts = required_contracts_from_story(text)
    requires_shape = (
        archetype in CONTRACT_SHAPE_ARCHETYPES
        or required_contracts.get("Contract Shape") == "yes"
    )
    if not requires_shape:
        return []

    section = get_section(text, "Contract Shape")
    if not section:
        return ["Contract Shape story missing section: Contract Shape"]
    if "not applicable" in section.casefold():
        return ["Contract Shape cannot be not applicable for this archetype"]

    errors: list[str] = []
    for marker in [
        "Contract type:",
        "Fields:",
        "Required fields:",
        "Optional fields:",
        "Status codes:",
        "Serialization names:",
        "Frontend type impact:",
        "Generated contract impact:",
    ]:
        value = block_after_marker(
            section,
            marker,
            [
                "Contract type:",
                "Fields:",
                "Required fields:",
                "Optional fields:",
                "Status codes:",
                "Serialization names:",
                "Frontend type impact:",
                "Generated contract impact:",
            ],
        )
        if marker.casefold() not in section.casefold() or not re.search(
            r"^\s*-\s+\S", value, re.M
        ):
            errors.append(f"Contract Shape missing concrete marker: {marker}")
    return errors


def validate_batch_migration_plan(text: str) -> list[str]:
    """Exige un plan de migration par lots quand le contrat est active."""
    archetype = marker_value(
        get_section(text, "Operation Contract"), "Primary archetype"
    ).casefold()
    required_contracts = required_contracts_from_story(text)
    requires_batch = (
        archetype in BATCH_MIGRATION_ARCHETYPES
        or required_contracts.get("Batch Migration") == "yes"
    )
    if not requires_batch:
        return []

    section = get_section(text, "Batch Migration Plan")
    if not section:
        return ["Batch migration story missing section: Batch Migration Plan"]
    if "not applicable" in section.casefold():
        return ["Batch Migration Plan cannot be not applicable for this archetype"]

    table = find_table_with_columns(
        section,
        [
            "Batch",
            "Old surface",
            "Canonical surface",
            "Consumers changed",
            "Tests adapted",
            "No-shim proof",
            "Blocker condition",
        ],
    )
    if table is None:
        return [
            "Batch Migration Plan must include Batch, Old surface, Canonical surface, Consumers changed, Tests adapted, No-shim proof, and Blocker condition"
        ]
    if not table.rows:
        return ["Batch Migration Plan must include at least one batch row"]
    return []


def validate_allowlist_exception_register(text: str) -> list[str]:
    """Valide les exceptions explicites et refuse les allowlists larges."""
    required_contracts = required_contracts_from_story(text)
    trigger_text = "\n".join(
        [
            get_section(text, "Objective"),
            get_section(text, "Trigger / Source"),
            get_section(text, "Operation Contract"),
            get_section(text, "Acceptance Criteria"),
            get_section(text, "Validation Plan"),
            get_section(text, "No Legacy / Forbidden Paths"),
        ]
    )
    trigger_text = re.sub(
        r"\b(?:no|not applicable|none|without)\s+[\w\s/-]{0,40}?(?:allowlist|exception|exception register)\b",
        "",
        trigger_text,
        flags=re.I,
    )
    if (
        not ALLOWLIST_TRIGGER_RE.search(trigger_text)
        and required_contracts.get("Allowlist Exception") != "yes"
    ):
        return []
    section = get_section(text, "Allowlist / Exception Register")
    if not section:
        return ["Allowlist story missing section: Allowlist / Exception Register"]
    if "not applicable" in section.casefold():
        return [
            "Allowlist / Exception Register cannot be not applicable when exceptions are mentioned"
        ]

    table = find_table_with_columns(
        section,
        ["File", "Symbol / Route / Import", "Reason", "Expiry or permanence decision"],
    )
    if table is None:
        return [
            "Allowlist / Exception Register must include File, Symbol / Route / Import, Reason, and Expiry or permanence decision"
        ]

    errors: list[str] = []
    headers = [normalize(header) for header in table.headers]
    file_index = headers.index(normalize("File"))
    symbol_index = headers.index(normalize("Symbol / Route / Import"))
    expiry_index = headers.index(normalize("Expiry or permanence decision"))
    for row in table.rows:
        if len(row) <= max(file_index, symbol_index, expiry_index):
            errors.append("Allowlist / Exception Register has an incomplete row")
            continue
        file_value = row[file_index].strip()
        symbol_value = row[symbol_index].strip()
        expiry_value = row[expiry_index].strip()
        combined = f"{file_value} {symbol_value} {expiry_value}"
        if "*" in combined:
            errors.append("Allowlist / Exception Register must not use wildcards")
        if re.search(r"[/\\]\*\*|\*\*|folder|directory|dossier", combined, re.I):
            errors.append(
                "Allowlist / Exception Register must not use folder-wide exceptions"
            )
        if not expiry_value or expiry_value in {"-", "n/a", "none"}:
            errors.append(
                "Allowlist / Exception Register row has empty expiry/permanence decision"
            )
        if re.search(
            r"\btemporary\b|\btemporaire\b", expiry_value, re.I
        ) and not re.search(
            r"\d{4}-\d{2}-\d{2}|until|when|condition|issue|ticket|permanent",
            expiry_value,
            re.I,
        ):
            errors.append(
                "Allowlist / Exception Register temporary exception needs date or exit condition"
            )
    return errors


def validate_no_legacy_reintroduction_guard(text: str) -> list[str]:
    """Exige un garde-fou quand des symboles No Legacy precis sont interdits."""
    section = get_section(text, "No Legacy / Forbidden Paths")
    if not section:
        return []
    backticked_values = [
        value for value in BACKTICK_VALUE_RE.findall(section) if value.strip()
    ]
    if not backticked_values:
        return []
    guard_section = get_section(text, "Reintroduction Guard")
    combined = "\n".join(
        [
            guard_section,
            get_section(text, "Acceptance Criteria"),
            get_section(text, "Validation Plan"),
        ]
    )
    if has_executable_guard_evidence(combined):
        return []
    if "not applicable" in guard_section.casefold() and re.search(
        r"reason:|justification:", guard_section, re.I
    ):
        return []
    return [
        "No Legacy / Forbidden Paths lists specific symbols and must activate or justify a Reintroduction Guard"
    ]


def validate_persistent_evidence_artifacts(text: str) -> list[str]:
    """Exige un artefact persistant pour audits, snapshots et baselines."""
    required_contracts = required_contracts_from_story(text)
    baseline_section = get_section(text, "Baseline / Before-After Rule")
    removal_audit_section = get_section(text, "Removal Audit Format")
    explicit_persistent_trigger = bool(
        baseline_section and "not applicable" not in baseline_section.casefold()
    ) or bool(
        removal_audit_section
        and "not applicable" not in removal_audit_section.casefold()
    )
    trigger_text = text.replace(get_section(text, "Persistent Evidence Artifacts"), "")
    explicit_persistent_trigger = explicit_persistent_trigger or bool(
        re.search(
            r"\b(openapi diff|diff snapshot|migration mapping|allowlist register|exception register)\b",
            trigger_text,
            re.I,
        )
    )
    if (
        not explicit_persistent_trigger
        and required_contracts.get("Persistent Evidence") != "yes"
    ):
        return []
    section = get_section(text, "Persistent Evidence Artifacts")
    if not section:
        return [
            "Persistent evidence story missing section: Persistent Evidence Artifacts"
        ]
    if "not applicable" in section.casefold():
        return [
            "Persistent Evidence Artifacts cannot be not applicable when audit/snapshot/baseline/diff evidence is mentioned"
        ]
    table = find_table_with_columns(section, ["Artifact", "Path", "Purpose"])
    if table is None:
        return [
            "Persistent Evidence Artifacts must include Artifact, Path, and Purpose table"
        ]
    path_index = [normalize(header) for header in table.headers].index("path")
    has_concrete_artifact = any(
        len(row) > path_index
        and any(
            is_concrete_path(value)
            for value in BACKTICK_VALUE_RE.findall(row[path_index])
        )
        for row in table.rows
    )
    if not has_concrete_artifact:
        return [
            "Persistent Evidence Artifacts must include at least one concrete artifact path"
        ]
    return []


def validate_expected_files(text: str) -> list[str]:
    """Verifie la presence des listes de fichiers cibles."""
    errors: list[str] = []
    inspect_section = get_section(text, "Files to Inspect First")
    expected_section = get_section(text, "Expected Files to Modify")
    if not has_concrete_path_or_assumption(inspect_section):
        errors.append(
            "Files to Inspect First must list at least one concrete path or explicit assumption risk"
        )
    markers = ["Likely files:", "Likely tests:", "Files not expected to change:"]
    for marker in markers:
        if marker not in expected_section:
            errors.append(f"Expected Files to Modify missing marker: {marker}")
            continue
        block = block_after_marker(expected_section, marker, markers)
        if not has_concrete_path_or_assumption(block):
            errors.append(
                f"Expected Files to Modify block must contain a concrete path or explicit assumption risk: {marker}"
            )
    return errors


def block_after_marker(text: str, marker: str, all_markers: list[str]) -> str:
    """Extrait le contenu suivant un marker jusqu'au marker suivant."""
    start = text.find(marker)
    if start < 0:
        return ""
    start += len(marker)
    end_candidates = [
        position
        for other in all_markers
        if other != marker and (position := text.find(other, start)) >= 0
    ]
    end = min(end_candidates) if end_candidates else len(text)
    return text[start:end].strip()


def has_concrete_path_or_assumption(block: str) -> bool:
    """Verifie un chemin concret ou une hypothese explicite."""
    has_path = any(
        is_concrete_path(value) for value in BACKTICK_VALUE_RE.findall(block)
    )
    has_assumption = re.search(
        r"unknown until repo inspection", block, re.I
    ) and re.search(r"assumption risk", block, re.I)
    return has_path or bool(has_assumption)


def is_concrete_path(value: str) -> bool:
    """Indique si une valeur entre backticks ressemble a un chemin de repo."""
    normalized = value.strip()
    if not normalized or normalized in {".", ".."}:
        return False
    has_separator = "/" in normalized or "\\" in normalized
    has_known_extension = any(
        normalized.casefold().endswith(extension) for extension in KNOWN_PATH_EXTENSIONS
    )
    return has_separator or has_known_extension


def validate_dependency_policy_section(text: str) -> list[str]:
    """Verifie la section dediee aux dependances."""
    section = get_section(text, "Dependency Policy")
    if not section:
        return ["Dependency Policy section is empty"]
    match = re.search(
        r"^\s*-\s*New dependencies:\s*(?P<value>.+?)\s*$", section, re.I | re.M
    )
    if match is None:
        return ["Dependency Policy must include 'New dependencies:'"]
    value = match.group("value").strip()
    if re.fullmatch(r"none\.?", value, re.I):
        return []

    has_named_dependency = bool(
        re.search(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value)
    ) and not re.search(r"<[^>]+>|\.\.\.", value)
    has_explicit_justification = bool(
        re.search(r"^\s*-\s*Justification:\s*\S.+$", section, re.I | re.M)
    )
    if not has_named_dependency:
        return ["Dependency Policy must name each allowed dependency"]
    if not has_explicit_justification:
        return [
            "Dependency Policy must include an explicit 'Justification:' line for dependency changes"
        ]
    return []


def validate_validation_plan(text: str) -> list[str]:
    """Verifie qu'au moins une commande de validation est presente."""
    section = get_section(text, "Validation Plan")
    if any(re.search(pattern, section) for pattern in COMMAND_PATTERNS):
        return []
    return ["Validation Plan must include at least one concrete command"]


def validate_no_legacy(text: str) -> list[str]:
    """Verifie les contraintes No Legacy minimales."""
    section = get_section(text, "No Legacy / Forbidden Paths")
    if not section:
        return ["No Legacy / Forbidden Paths section is empty"]
    required_words = ["compatibility", "legacy", "fallback"]
    missing = [word for word in required_words if word not in section.casefold()]
    return [f"No Legacy section missing concept: {word}" for word in missing]


def validate_dev_agent_instructions(text: str) -> list[str]:
    """Verifie les garde-fous anti-derive pour l'agent de dev."""
    section = get_section(text, "Dev Agent Instructions")
    required_fragments = [
        "Implement only this story",
        "Do not broaden the domain",
        "Do not introduce new dependencies",
        "Do not mark a task complete without validation evidence",
        "If an AC cannot be satisfied",
        "Do not preserve legacy behavior",
    ]
    return [
        f"Dev Agent Instructions missing guardrail: {fragment}"
        for fragment in required_fragments
        if fragment not in section
    ]


def validate_dependency_policy(text: str) -> list[str]:
    """Detecte les autorisations de dependances sans justification."""
    errors: list[str] = []
    dependency_mentions = re.findall(r"\bnew dependenc(?:y|ies)\b", text, re.I)
    if dependency_mentions and not re.search(
        r"\bjustification\b|\bexplicitly listed\b", text, re.I
    ):
        errors.append(
            "New dependency mentions require explicit justification or explicit listing"
        )
    return errors


def validate_vague_terms(text: str) -> list[str]:
    """Signale les termes vagues interdits."""
    errors: list[str] = []
    for section_name in VAGUE_CHECK_SECTIONS:
        section = get_section(text, section_name)
        for line in section.splitlines():
            if VAGUE_NEGATIVE_CONTEXT_RE.search(line):
                continue
            for term in VAGUE_TERMS:
                if re.search(rf"(?<![\w-]){re.escape(term)}(?![\w-])", line, re.I):
                    errors.append(f"Vague term is forbidden in {section_name}: {term}")
    return errors


def validate_story(path: Path) -> list[str]:
    """Retourne les erreurs detectees dans une story CONDAMAD."""
    errors: list[str] = []
    if not path.is_file():
        return [f"Story not found: {path}"]
    text = read_text(path)
    if STORY_TITLE_RE.search(text) is None:
        errors.append(
            "Story title must include a sequential number: # Story CS-### <story-key>: <title>"
        )
    status_match = re.search(r"^Status:\s*(?P<status>\S+)\s*$", text, re.I | re.M)
    if status_match is None:
        errors.append(
            "Story must contain a valid Status line: ready-to-dev, ready-to-review, or done"
        )
    elif status_match.group("status").casefold() not in ALLOWED_STORY_STATUSES:
        errors.append(
            "Story status must be one of: ready-to-dev, ready-to-review, done"
        )
    for missing in has_required_sections(text):
        errors.append(f"Missing required section: {missing}")
    errors.extend(validate_current_state_evidence(text))
    errors.extend(validate_domain_boundary(text))
    errors.extend(validate_operation_contract(text))
    errors.extend(validate_required_contracts(text))
    errors.extend(validate_runtime_source_of_truth(text))
    errors.extend(validate_baseline_rule(text))
    errors.extend(validate_ownership_routing_rule(text))
    errors.extend(validate_contract_shape(text))
    errors.extend(validate_batch_migration_plan(text))
    errors.extend(validate_allowlist_exception_register(text))
    errors.extend(validate_acceptance_criteria(text))
    errors.extend(validate_tasks(text))
    errors.extend(validate_removal_contract(text))
    errors.extend(validate_no_legacy(text))
    errors.extend(validate_no_legacy_reintroduction_guard(text))
    errors.extend(validate_persistent_evidence_artifacts(text))
    errors.extend(validate_dev_agent_instructions(text))
    errors.extend(validate_expected_files(text))
    errors.extend(validate_dependency_policy_section(text))
    errors.extend(validate_validation_plan(text))
    errors.extend(validate_dependency_policy(text))
    errors.extend(validate_vague_terms(text))
    return errors


def explain_contracts(path: Path) -> int:
    """Affiche le diagnostic des contrats requis et declares."""
    if not path.is_file():
        print(f"Story not found: {path}")
        return 1
    text = read_text(path)
    operation = get_section(text, "Operation Contract")
    archetype = marker_value(operation, "Primary archetype").casefold() or "<missing>"
    required = sorted(ARCHETYPE_REQUIRED_CONTRACTS.get(archetype, set()))
    declared = required_contracts_from_story(text)
    present_yes = sorted(
        contract for contract, value in declared.items() if value == "yes"
    )
    present_no = sorted(
        contract for contract, value in declared.items() if value == "no"
    )
    missing = sorted(
        contract for contract in required if declared.get(contract) != "yes"
    )

    print("CONDAMAD story contract explanation")
    print(f"- Primary archetype: {archetype}")
    print("- Archetype required contracts:")
    for contract in required:
        print(f"  - {contract}")
    if not required:
        print("  - <none or custom>")
    print("- Story contracts marked yes:")
    for contract in present_yes:
        print(f"  - {contract}")
    if not present_yes:
        print("  - <none>")
    print("- Story contracts marked no:")
    for contract in present_no:
        print(f"  - {contract}")
    if not present_no:
        print("  - <none>")
    print("- Missing required contracts:")
    for contract in missing:
        print(f"  - {contract}")
    if not missing:
        print("  - <none>")
    return 1 if missing else 0


def main() -> int:
    """Execute la validation depuis la ligne de commande."""
    parser = argparse.ArgumentParser(description="Validate a CONDAMAD story file.")
    parser.add_argument(
        "--explain-contracts",
        action="store_true",
        help="Print archetype contract requirements and story contract coverage.",
    )
    parser.add_argument(
        "story", type=Path, help="Path to a CONDAMAD story markdown file."
    )
    args = parser.parse_args()

    story_path = args.story.expanduser().resolve()
    if args.explain_contracts:
        return explain_contracts(story_path)

    errors = validate_story(story_path)
    if errors:
        print("CONDAMAD story validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CONDAMAD story validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
