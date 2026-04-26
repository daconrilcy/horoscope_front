#!/usr/bin/env python3
"""Valide le package, les plans et les preuves de refactorisation CONDAMAD.

Le validateur utilise uniquement la bibliotheque standard et applique les
garde-fous structurants du skill `condamad-refactor-surgeon`.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ALLOWED_REFACTOR_TYPES = {
    "extract-function",
    "extract-class",
    "move-function",
    "move-class",
    "rename-symbol",
    "inline-function",
    "split-module",
    "merge-duplicate-logic",
    "simplify-conditional",
    "replace-primitive-with-value-object",
    "separate-query-from-modifier",
    "introduce-parameter-object",
    "remove-dead-code",
    "consolidate-imports",
    "isolate-side-effect",
    "strengthen-boundary",
}

REQUIRED_FILES = [
    "SKILL.md",
    "workflow.md",
    "agents/openai.yaml",
    "references/refactor-taxonomy.md",
    "references/refactor-contract.md",
    "references/behavior-preservation-contract.md",
    "references/no-legacy-dry-contract.md",
    "references/validation-contract.md",
    "references/diff-review-contract.md",
    "templates/refactor-plan.md",
    "templates/refactor-evidence.md",
    "scripts/condamad_refactor_validate.py",
    "scripts/condamad_refactor_collect_evidence.py",
    "scripts/condamad_refactor_scan.py",
    "scripts/self_tests/condamad_refactor_validate_selftest.py",
]

PLAN_SECTIONS = [
    "Refactor Type",
    "Primary Domain",
    "Current State Evidence",
    "Target State",
    "Behavior Invariants",
    "Scope Boundary",
    "No Legacy / DRY Constraints",
    "Validation Plan",
    "Diff Review Plan",
]

EVIDENCE_SECTIONS = [
    "Refactor Summary",
    "Behavior Invariants Evidence",
    "Validation Evidence",
    "Git Evidence Snapshot",
    "Residual Risks",
]

PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\bTBD\b|\bTODO\b|placeholder", re.I)
FORBIDDEN_ARTIFACT_RE = re.compile(r"__pycache__|\.pyc$|\.pyo$", re.I)
FORBIDDEN_LEGACY_ALLOW_RE = re.compile(
    r"\b(?:allow|permit|keep|create|add|use|introduce|preserve)\b"
    r".{0,80}\b(?:shim|fallback|alias|re-export|compatibility wrapper|legacy path)\b",
    re.I | re.S,
)
NEGATED_LEGACY_RE = re.compile(
    r"\b(?:do not|don't|must not|never|no)\b"
    r".{0,80}\b(?:shim|fallback|alias|re-export|compatibility wrapper|legacy path)\b",
    re.I | re.S,
)
CONCRETE_SCOPE_RE = re.compile(
    r"`[^`\n]+[/\\][^`\n]+`|`[A-Za-z_][\w.:-]+`|^\s*-\s*[A-Za-z_][\w.:-]+\s*$",
    re.MULTILINE,
)
TEST_OR_STATIC_RE = re.compile(
    r"\b(?:pytest|unittest|vitest|npm\s+test|pnpm\s+test|ruff\s+check|mypy|tsc|eslint)\b",
    re.I,
)
NEGATIVE_SCAN_RE = re.compile(
    r"\b(?:condamad_refactor_scan\.py|rg\b|grep\b).*(?:--fail-on-hit|legacy|shim|fallback|alias|re-export|__pycache__|\\.pyc|\\.pyo)",
    re.I | re.S,
)


def read_text(path: Path) -> str:
    """Lit un fichier texte avec tolerance aux caracteres invalides."""
    return path.read_text(encoding="utf-8", errors="replace")


def section_bounds(text: str) -> dict[str, tuple[int, int]]:
    """Retourne les bornes des sections Markdown de niveau 2."""
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE))
    bounds: dict[str, tuple[int, int]] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        bounds[normalize_heading(match.group(1))] = (start, end)
    return bounds


def normalize_heading(value: str) -> str:
    """Normalise un titre Markdown pour comparaison."""
    return re.sub(r"\s+", " ", value.strip()).casefold()


def get_section(text: str, title: str) -> str:
    """Extrait le contenu d'une section de niveau 2."""
    bounds = section_bounds(text).get(normalize_heading(title))
    if bounds is None:
        return ""
    return text[bounds[0] : bounds[1]].strip()


def has_required_sections(text: str, sections: list[str]) -> list[str]:
    """Liste les sections Markdown manquantes."""
    headings = section_bounds(text)
    return [
        section
        for section in sections
        if normalize_heading(section) not in headings
    ]


def yaml_value(text: str, key: str) -> str | None:
    """Extrait une valeur YAML simple depuis un texte."""
    match = re.search(rf"^\s*{re.escape(key)}:\s*(.+?)\s*$", text, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip().strip('"').strip("'")


def iter_packaged_artifacts(root: Path) -> list[str]:
    """Liste les artefacts caches interdits dans le package."""
    findings: list[str] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root).as_posix()
        if FORBIDDEN_ARTIFACT_RE.search(rel):
            findings.append(rel)
    return findings


def validate_skill_root(root: Path) -> list[str]:
    """Valide la structure et les contrats du package de skill."""
    errors: list[str] = []
    if not root.is_dir():
        return [f"Skill root not found: {root}"]
    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(f"Missing required file: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"Required file is empty: {rel}")

    if (root / "scripts/tests").exists():
        errors.append("Forbidden self-test directory exists: scripts/tests")
    if not (root / "scripts/self_tests").is_dir():
        errors.append("Missing required directory: scripts/self_tests")

    for artifact in iter_packaged_artifacts(root):
        errors.append(f"Forbidden packaged artifact: {artifact}")

    skill_path = root / "SKILL.md"
    if skill_path.is_file():
        skill_text = read_text(skill_path)
        if not re.search(r"^---\s*\n.*?\n---", skill_text, re.S):
            errors.append("SKILL.md missing frontmatter")
        if yaml_value(skill_text, "name") != "condamad-refactor-surgeon":
            errors.append("SKILL.md frontmatter name must be condamad-refactor-surgeon")
        for phrase in [
            "bounded",
            "mono-domain",
            "behavior-preserving",
            "No Legacy",
            "DRY",
        ]:
            if phrase.casefold() not in skill_text.casefold():
                errors.append(f"SKILL.md missing doctrine phrase: {phrase}")

    openai_path = root / "agents/openai.yaml"
    if openai_path.is_file():
        openai_text = read_text(openai_path)
        if not re.search(r"allow_implicit_invocation:\s*false\b", openai_text, re.I):
            errors.append("agents/openai.yaml must set allow_implicit_invocation: false")
        if "$condamad-refactor-surgeon" not in openai_text:
            errors.append("agents/openai.yaml default prompt must reference $condamad-refactor-surgeon")

    taxonomy = root / "references/refactor-taxonomy.md"
    if taxonomy.is_file():
        taxonomy_text = read_text(taxonomy)
        missing_types = [
            refactor_type
            for refactor_type in sorted(ALLOWED_REFACTOR_TYPES)
            if f"`{refactor_type}`" not in taxonomy_text
        ]
        for refactor_type in missing_types:
            errors.append(f"Taxonomy missing allowed type: {refactor_type}")

    required_phrase_files = {
        "workflow.md": [
            "Stop Conditions",
            "behavior-preserving",
            "no new behavior",
            "destructive git commands",
            "dependency updates",
            "migrations",
        ],
        "references/behavior-preservation-contract.md": [
            "no new behavior",
            "behavior-preserving",
        ],
        "references/no-legacy-dry-contract.md": [
            "compatibility wrappers",
            "shims",
            "aliases",
            "re-exports",
            "silent fallbacks",
            "legacy paths",
        ],
        "references/validation-contract.md": [
            "Targeted Tests",
            "Static Checks",
            "Negative Legacy Scans",
            "Diff Review",
            "formatters",
            "generators",
            "dependency updates",
            "migrations",
            "destructive git commands",
        ],
        "templates/refactor-plan.md": [
            "Current State Evidence",
            "Target State",
            "Behavior Invariants",
            "Negative Legacy Scans",
            "Diff Review",
        ],
        "templates/refactor-evidence.md": [
            "Targeted Tests",
            "Static Checks",
            "Negative Legacy Scans",
            "Diff Review",
            "CONDAMAD:REFACTOR-EVIDENCE:START",
            "CONDAMAD:REFACTOR-EVIDENCE:END",
        ],
    }
    for rel, phrases in required_phrase_files.items():
        path = root / rel
        if not path.is_file():
            continue
        content = read_text(path)
        for phrase in phrases:
            if phrase.casefold() not in content.casefold():
                errors.append(f"{rel} missing required phrase: {phrase}")
    return errors


def extract_refactor_type(section: str) -> str:
    """Extrait le type de refactor depuis sa section."""
    match = re.search(r"`([^`]+)`", section)
    if match:
        return match.group(1).strip()
    return section.strip().splitlines()[0].strip() if section.strip() else ""


def validate_primary_domain(section: str) -> list[str]:
    """Valide qu'un seul domaine primaire est declare."""
    domains = re.findall(r"^\s*-\s*Domain:\s*(\S.+?)\s*$", section, re.MULTILINE)
    if len(domains) != 1:
        return [f"Primary Domain must declare exactly one '- Domain:' entry, found {len(domains)}"]
    if PLACEHOLDER_RE.search(domains[0]):
        return ["Primary Domain contains a placeholder"]
    return []


def concrete_section(section: str, name: str) -> list[str]:
    """Valide qu'une section contient une preuve non placeholder."""
    if not section:
        return [f"Missing required section: {name}"]
    stripped = re.sub(r"```.*?```", "", section, flags=re.S).strip()
    if not stripped or PLACEHOLDER_RE.search(stripped):
        return [f"{name} must not contain placeholders only"]
    return []


def validate_scope_boundary(section: str) -> list[str]:
    """Valide que le perimetre du refactor est exploitable avant edition."""
    errors = concrete_section(section, "Scope Boundary")
    if errors:
        return errors
    if "In scope:" not in section:
        errors.append("Scope Boundary missing marker: In scope:")
    if "Out of scope:" not in section:
        errors.append("Scope Boundary missing marker: Out of scope:")
    in_scope_match = re.search(
        r"In scope:\s*(?P<body>.*?)(?:\n\s*Out of scope:|\Z)",
        section,
        re.I | re.S,
    )
    in_scope = in_scope_match.group("body") if in_scope_match else ""
    if not CONCRETE_SCOPE_RE.search(in_scope) or PLACEHOLDER_RE.search(in_scope):
        errors.append("Scope Boundary must list at least one concrete in-scope path or symbol")
    return errors


def allows_forbidden_legacy(section: str) -> bool:
    """Detecte les autorisations legacy sans penaliser les interdictions claires."""
    return bool(FORBIDDEN_LEGACY_ALLOW_RE.search(section)) and not bool(
        NEGATED_LEGACY_RE.search(section)
    )


def validate_plan(path: Path) -> list[str]:
    """Valide un plan de refactorisation avant edition."""
    if not path.is_file():
        return [f"Plan not found: {path}"]
    text = read_text(path)
    errors = [f"Plan missing section: {section}" for section in has_required_sections(text, PLAN_SECTIONS)]
    refactor_type = extract_refactor_type(get_section(text, "Refactor Type"))
    if refactor_type not in ALLOWED_REFACTOR_TYPES:
        errors.append(f"Invalid Refactor Type: {refactor_type or '<empty>'}")
    errors.extend(validate_primary_domain(get_section(text, "Primary Domain")))
    for section in ["Current State Evidence", "Target State", "Behavior Invariants"]:
        errors.extend(concrete_section(get_section(text, section), section))
    errors.extend(validate_scope_boundary(get_section(text, "Scope Boundary")))
    no_legacy = get_section(text, "No Legacy / DRY Constraints")
    if allows_forbidden_legacy(no_legacy):
        errors.append("Plan appears to allow forbidden legacy compatibility behavior")
    validation = get_section(text, "Validation Plan")
    if not TEST_OR_STATIC_RE.search(validation):
        errors.append("Validation Plan must include at least one test or static command")
    if not NEGATIVE_SCAN_RE.search(validation):
        errors.append("Validation Plan must include at least one negative scan command")
    diff_review = get_section(text, "Diff Review Plan")
    if not re.search(r"git diff --check|git diff --stat|git diff --name-status", validation + "\n" + diff_review):
        errors.append("Plan must include diff review commands")
    return errors


def validate_evidence(path: Path) -> list[str]:
    """Valide les preuves finales d'une refactorisation."""
    if not path.is_file():
        return [f"Evidence not found: {path}"]
    text = read_text(path)
    errors = [
        f"Evidence missing section: {section}"
        for section in has_required_sections(text, EVIDENCE_SECTIONS)
    ]
    validation = get_section(text, "Validation Evidence")
    if not TEST_OR_STATIC_RE.search(validation):
        errors.append("Evidence must include at least one test or static command")
    if not NEGATIVE_SCAN_RE.search(validation):
        errors.append("Evidence must include at least one negative scan command")
    if "git diff --check" not in validation:
        errors.append("Evidence must include git diff --check")
    if "CONDAMAD:REFACTOR-EVIDENCE:START" not in text or "CONDAMAD:REFACTOR-EVIDENCE:END" not in text:
        errors.append("Evidence must include idempotent evidence markers")
    if re.search(r"\b(manual review|looks good|covered by tests)\b", text, re.I):
        errors.append("Evidence contains weak validation wording")
    return errors


def main() -> int:
    """Execute la validation depuis la ligne de commande."""
    parser = argparse.ArgumentParser(description="Validate CONDAMAD refactor assets.")
    parser.add_argument("--skill-root", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()

    if not any([args.skill_root, args.plan, args.evidence]):
        parser.error("provide at least one of --skill-root, --plan, --evidence")

    errors: list[str] = []
    if args.skill_root:
        errors.extend(validate_skill_root(args.skill_root.expanduser().resolve()))
    if args.plan:
        errors.extend(validate_plan(args.plan.expanduser().resolve()))
    if args.evidence:
        errors.extend(validate_evidence(args.evidence.expanduser().resolve()))

    if errors:
        print("CONDAMAD refactor validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CONDAMAD refactor validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
