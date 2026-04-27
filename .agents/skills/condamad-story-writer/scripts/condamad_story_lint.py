#!/usr/bin/env python3
"""Linte une story CONDAMAD au-dela du contrat bloquant.

Ce lint garde la story lisible pour Codex: pas de marqueurs de gabarit, pas de
lignes demesurees et pas de sections vides.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from condamad_story_validate import (
    REQUIRED_SECTIONS,
    RUNTIME_CONTRACT_TERMS_RE,
    ac_table_columns,
    find_ac_table,
    get_section,
    has_runtime_evidence,
    marker_value,
    read_text,
    validate_story,
)

MAX_LINE_LENGTH = 180
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\.\.\.")
COMPOUND_AC_RE = re.compile(r"\b(and|et)\b|,\s+\w+", re.I)
VAGUE_OPTIONAL_RE = re.compile(
    r"\b(if needed|where relevant|as applicable|si necessaire|si nécessaire)\b",
    re.I,
)


def lint_story(path: Path) -> list[str]:
    """Retourne les erreurs de lint detectees dans la story."""
    errors = validate_story(path)
    if errors:
        return errors

    text = read_text(path)
    for index, line in enumerate(text.splitlines(), start=1):
        if len(line) > MAX_LINE_LENGTH:
            errors.append(f"Line {index} exceeds {MAX_LINE_LENGTH} characters")
    if PLACEHOLDER_RE.search(text):
        errors.append("Story still contains template placeholders")
    for section in REQUIRED_SECTIONS:
        if not get_section(text, section).strip():
            errors.append(f"Section is empty: {section}")
    return errors


def lint_warnings(path: Path) -> list[str]:
    """Retourne les avertissements non bloquants anti-flou."""
    text = read_text(path)
    warnings: list[str] = []
    warnings.extend(warn_compound_acceptance_criteria(text))
    warnings.extend(warn_runtime_evidence_only_rg(text))
    warnings.extend(warn_vague_optional_language(text))
    warnings.extend(warn_removal_ambiguity(text))
    warnings.extend(warn_allowlist_without_expiry(text))
    warnings.extend(warn_temporary_without_exit_condition(text))
    warnings.extend(warn_validation_plan_path_drift(text))
    warnings.extend(warn_generic_scans(text))
    warnings.extend(warn_behavior_no_contract_change(text))
    warnings.extend(warn_keep_in_no_legacy(text))
    return warnings


def warn_compound_acceptance_criteria(text: str) -> list[str]:
    """Signale les AC qui semblent contenir plusieurs invariants."""
    table = find_ac_table(get_section(text, "Acceptance Criteria"))
    if table is None:
        return []
    ac_index, requirement_index, _ = ac_table_columns(table)
    warnings: list[str] = []
    for row in table.rows:
        if len(row) <= max(ac_index, requirement_index):
            continue
        ac_id = row[ac_index].strip()
        requirement = row[requirement_index].strip()
        if COMPOUND_AC_RE.search(requirement):
            warnings.append(f"{ac_id} is possibly compound; keep one invariant per AC")
    return warnings


def warn_runtime_evidence_only_rg(text: str) -> list[str]:
    """Signale une preuve runtime limitee a rg."""
    table = find_ac_table(get_section(text, "Acceptance Criteria"))
    if table is None:
        return []
    ac_index, requirement_index, evidence_index = ac_table_columns(table)
    warnings: list[str] = []
    for row in table.rows:
        if len(row) <= max(ac_index, requirement_index, evidence_index):
            continue
        requirement = row[requirement_index]
        evidence = row[evidence_index]
        if (
            RUNTIME_CONTRACT_TERMS_RE.search(requirement)
            and re.search(r"\brg\b", evidence)
            and not has_runtime_evidence(evidence)
        ):
            warnings.append(
                f"{row[ac_index].strip()} uses rg-only evidence for route/API/runtime behavior"
            )
    return warnings


def warn_vague_optional_language(text: str) -> list[str]:
    """Signale les formulations optionnelles qui diluent le contrat."""
    return (
        [
            "Story contains optional vague language such as 'if needed', 'where relevant', or 'as applicable'"
        ]
        if VAGUE_OPTIONAL_RE.search(text)
        else []
    )


def warn_removal_ambiguity(text: str) -> list[str]:
    """Signale les alternatives interdites dans les suppressions."""
    lowered = text.casefold()
    return (
        ["Removal story uses ambiguous 'replace or delete' language"]
        if "replace or delete" in lowered or "delete or replace" in lowered
        else []
    )


def warn_allowlist_without_expiry(text: str) -> list[str]:
    """Signale une allowlist dont l'expiration n'est pas visible."""
    section = get_section(text, "Allowlist / Exception Register")
    if (
        section
        and "not applicable" not in section.casefold()
        and not re.search(
            r"expiry|permanence|permanent|until|\d{4}-\d{2}-\d{2}",
            section,
            re.I,
        )
    ):
        return ["Allowlist appears to lack expiry or permanence decision"]
    return []


def warn_temporary_without_exit_condition(text: str) -> list[str]:
    """Signale temporary sans condition de sortie."""
    if re.search(r"\btemporary\b|\btemporaire\b", text, re.I) and not re.search(
        r"\d{4}-\d{2}-\d{2}|until|when|condition|issue|ticket",
        text,
        re.I,
    ):
        return ["Temporary exception lacks date, ticket, or exit condition"]
    return []


def warn_validation_plan_path_drift(text: str) -> list[str]:
    """Signale les plans avec cd et chemins qui semblent incoherents."""
    section = get_section(text, "Validation Plan")
    if re.search(r"\bcd\s+backend\b", section) and re.search(r"backend/", section):
        return ["Validation plan changes into backend then still uses backend/ paths"]
    if re.search(r"\bcd\s+frontend\b", section) and re.search(r"frontend/", section):
        return ["Validation plan changes into frontend then still uses frontend/ paths"]
    return []


def warn_generic_scans(text: str) -> list[str]:
    """Signale les scans trop generiques pour prouver une absence."""
    section = get_section(text, "Validation Plan")
    if re.search(r"\brg\s+['\"]?(legacy|fallback|alias)['\"]?\b", section, re.I):
        return [
            "Validation plan uses generic legacy/fallback/alias scan without targeted symbols"
        ]
    return []


def warn_behavior_no_contract_change(text: str) -> list[str]:
    """Signale une contradiction probable non bloquante dans le wording."""
    operation = get_section(text, "Operation Contract")
    if marker_value(operation, "Behavior change allowed").casefold() != "no":
        return []
    if re.search(r"\b(remove field|change response|drop detail)\b", text, re.I):
        return [
            "Behavior change is forbidden but the story mentions field/response removal"
        ]
    return []


def warn_keep_in_no_legacy(text: str) -> list[str]:
    """Signale keep dans No Legacy hors classification active canonique/externe."""
    section = get_section(text, "No Legacy / Forbidden Paths")
    if (
        re.search(r"\bkeep\b", section, re.I)
        and "canonical-active" not in text
        and "external-active" not in text
    ):
        return [
            "No Legacy section uses 'keep' outside canonical-active/external-active context"
        ]
    return []


def main() -> int:
    """Execute le lint depuis la ligne de commande."""
    parser = argparse.ArgumentParser(description="Lint a CONDAMAD story file.")
    parser.add_argument(
        "story", type=Path, help="Path to a CONDAMAD story markdown file."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when anti-flou warnings are detected.",
    )
    args = parser.parse_args()

    story_path = args.story.expanduser().resolve()
    errors = lint_story(story_path)
    if errors:
        print("CONDAMAD story lint: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    warnings = lint_warnings(story_path)
    if warnings:
        if args.strict:
            print("CONDAMAD story lint: FAIL")
            for warning in warnings:
                print(f"- Strict warning: {warning}")
            return 1
        print("CONDAMAD story lint: PASS with warnings")
        for warning in warnings:
            print(f"- Warning: {warning}")
        return 0
    print("CONDAMAD story lint: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
