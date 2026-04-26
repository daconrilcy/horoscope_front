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
    value = re.sub(r"^\d+\.\s*", "", value.strip())
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
    if any(re.search(pattern, evidence) for pattern in COMMAND_PATTERNS):
        return True
    if TEST_PATH_RE.search(evidence):
        return True
    return bool(MANUAL_CHECK_RE.search(evidence))


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
    if not re.search(r"^Status:\s*ready-for-dev\s*$", text, re.I | re.M):
        errors.append("Story must contain 'Status: ready-for-dev'")
    for missing in has_required_sections(text):
        errors.append(f"Missing required section: {missing}")
    errors.extend(validate_current_state_evidence(text))
    errors.extend(validate_domain_boundary(text))
    errors.extend(validate_acceptance_criteria(text))
    errors.extend(validate_tasks(text))
    errors.extend(validate_no_legacy(text))
    errors.extend(validate_dev_agent_instructions(text))
    errors.extend(validate_expected_files(text))
    errors.extend(validate_dependency_policy_section(text))
    errors.extend(validate_validation_plan(text))
    errors.extend(validate_dependency_policy(text))
    errors.extend(validate_vague_terms(text))
    return errors


def main() -> int:
    """Execute la validation depuis la ligne de commande."""
    parser = argparse.ArgumentParser(description="Validate a CONDAMAD story file.")
    parser.add_argument(
        "story", type=Path, help="Path to a CONDAMAD story markdown file."
    )
    args = parser.parse_args()

    errors = validate_story(args.story.expanduser().resolve())
    if errors:
        print("CONDAMAD story validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CONDAMAD story validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
