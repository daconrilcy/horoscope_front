#!/usr/bin/env python3
"""Valide les rapports produits par le skill CONDAMAD Domain Auditor.

Le validateur verifie la presence des six artefacts, la coherence des findings,
les liens vers les story candidates et l'absence d'artefacts Python generes.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REQUIRED_FILES = [
    "00-audit-report.md",
    "01-evidence-log.md",
    "02-finding-register.md",
    "03-story-candidates.md",
    "04-risk-matrix.md",
    "05-executive-summary.md",
]
AUDIT_ROOT_PARTS = ("_condamad", "audits")
DEFAULT_REPO_ROOT = Path(__file__).resolve().parents[4]
FINDING_COLUMNS = [
    "ID",
    "Severity",
    "Confidence",
    "Category",
    "Domain",
    "Evidence",
    "Impact",
    "Recommended action",
    "Story candidate",
]
RISK_COLUMNS = [
    "Finding",
    "Severity",
    "Probability",
    "Blast radius",
    "Regression risk",
    "Effort",
    "Priority",
]
VALID_SEVERITIES = {"Critical", "High", "Medium", "Low", "Info"}
VALID_CONFIDENCE = {"High", "Medium", "Low"}
VALID_STORY_CANDIDATE_VALUES = {"yes", "no", "needs-user-decision"}
VALID_EVIDENCE_RESULTS = {"PASS", "FAIL", "SKIPPED", "LIMITATION"}
SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Info"]
EVIDENCE_ID_RE = re.compile(r"\bE-\d{3,}\b")
FINDING_ID_RE = re.compile(r"\bF-\d{3,}\b")
SC_ID_RE = re.compile(r"\bSC-\d{3,}\b")
SOURCE_FINDING_RE = re.compile(r"Source finding:\s*(F-\d{3,})", re.I)
PLACEHOLDER_RE = re.compile(r"^\s*(?:\.{3}|<[^>]+>|TODO|TBD|N/A|-)?\s*$", re.I)
FINDING_DETAIL_FIELDS = [
    "Severity",
    "Confidence",
    "Category",
    "Domain",
    "Evidence",
    "Expected rule",
    "Actual state",
    "Impact",
    "Recommended action",
    "Story candidate",
    "Suggested archetype",
]
STORY_CANDIDATE_FIELDS = [
    "Source finding",
    "Suggested story title",
    "Suggested archetype",
    "Primary domain",
    "Required contracts",
    "Draft objective",
    "Must include",
    "Validation hints",
    "Blockers",
]
BLOCK_FIELD_NAMES = set(FINDING_DETAIL_FIELDS) | set(STORY_CANDIDATE_FIELDS)


@dataclass(frozen=True)
class MarkdownTable:
    """Representation minimale d'un tableau Markdown."""

    headers: list[str]
    rows: list[list[str]]
    malformed_rows: list[int]
    malformed_separator: bool


def read_text(path: Path) -> str:
    """Lit un fichier Markdown en UTF-8."""
    return path.read_text(encoding="utf-8")


def split_row(line: str) -> list[str]:
    """Decoupe une ligne de tableau Markdown."""
    content = line.strip().strip("|")
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in content:
        if escaped:
            current.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            current.append(char)
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    cells.append("".join(current).strip())
    return cells


def parse_first_table(
    text: str, required_headers: list[str] | None = None
) -> MarkdownTable | None:
    """Retourne le premier tableau contenant les colonnes attendues."""
    lines = text.splitlines()
    for index, line in enumerate(lines[:-1]):
        if not line.strip().startswith("|"):
            continue
        headers = split_row(line)
        separator = lines[index + 1].strip()
        if not separator.startswith("|") or "---" not in separator:
            continue
        separator_cells = split_row(separator)
        malformed_separator = len(separator_cells) != len(headers)
        if required_headers and not all(
            header in headers for header in required_headers
        ):
            continue
        rows: list[list[str]] = []
        malformed_rows: list[int] = []
        for row_number, row_line in enumerate(lines[index + 2 :], start=index + 3):
            if not row_line.strip().startswith("|"):
                break
            row = split_row(row_line)
            if len(row) == len(headers):
                rows.append(row)
            else:
                malformed_rows.append(row_number)
        return MarkdownTable(
            headers=headers,
            rows=rows,
            malformed_rows=malformed_rows,
            malformed_separator=malformed_separator,
        )
    return None


def malformed_table_errors(label: str, table: MarkdownTable | None) -> list[str]:
    """Retourne les erreurs de forme d'un tableau Markdown."""
    if table is None:
        return []
    errors = [
        f"{label} has malformed Markdown table row at line {line}"
        for line in table.malformed_rows
    ]
    if table.malformed_separator:
        errors.append(f"{label} has malformed Markdown table separator")
    return errors


def cell(row: list[str], table: MarkdownTable, header: str) -> str:
    """Retourne la cellule correspondant a une colonne."""
    return row[table.headers.index(header)].strip()


def is_meaningful(value: str) -> bool:
    """Indique si une valeur contient une preuve exploitable."""
    return not PLACEHOLDER_RE.match(value.strip())


def is_audit_path(path: Path, repo_root: Path | None = None) -> bool:
    """Verifie que le dossier est sous _condamad/audits du repository."""
    root = (repo_root or DEFAULT_REPO_ROOT).resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError:
        return False
    return (
        len(relative.parts) >= 4
        and relative.parts[0:2] == AUDIT_ROOT_PARTS
        and all(part.strip() for part in relative.parts[2:])
    )


def heading_ids(text: str, prefix: str) -> list[str]:
    """Retourne les identifiants de headings dans leur ordre d'apparition."""
    pattern = re.compile(rf"^###?\s+({re.escape(prefix)}-\d{{3,}})\b.*$", re.M)
    return [match.group(1) for match in pattern.finditer(text)]


def story_candidate_sources(text: str) -> dict[str, str]:
    """Retourne les couples candidate -> finding references."""
    sources: dict[str, str] = {}
    current_sc: str | None = None
    for line in text.splitlines():
        heading = re.match(r"^##\s+(SC-\d{3,})\b", line)
        if heading:
            current_sc = heading.group(1)
            continue
        source = SOURCE_FINDING_RE.search(line)
        if current_sc and source:
            sources[current_sc] = source.group(1)
    return sources


def heading_blocks(text: str, prefix: str) -> dict[str, str]:
    """Decoupe des blocs Markdown par identifiant de heading."""
    blocks: dict[str, str] = {}
    pattern = re.compile(rf"^###?\s+({re.escape(prefix)}-\d{{3,}})\b.*$", re.M)
    matches = list(pattern.finditer(text))
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks[match.group(1)] = text[start:end]
    return blocks


def duplicate_heading_ids(text: str, prefix: str) -> list[str]:
    """Retourne les identifiants de headings presents plusieurs fois."""
    ids = heading_ids(text, prefix)
    return sorted({item for item in ids if ids.count(item) > 1})


def field_value(block: str, field: str) -> str | None:
    """Extrait la valeur d'un champ bullet, y compris ses lignes imbriquees."""
    lines = block.splitlines()
    prefix = f"- {field}:"
    for index, line in enumerate(lines):
        if line.strip().casefold().startswith(prefix.casefold()):
            value = line.split(":", 1)[1].strip()
            extra: list[str] = []
            for next_line in lines[index + 1 :]:
                stripped = next_line.strip()
                next_field = re.match(r"- ([^:]{1,80}):", stripped)
                if next_field and next_field.group(1) in BLOCK_FIELD_NAMES:
                    break
                if stripped:
                    extra.append(stripped)
            return " ".join([value, *extra]).strip()
    return None


def require_block_fields(
    block_id: str, block: str, fields: list[str], label: str
) -> list[str]:
    """Valide la presence de champs obligatoires non vides."""
    errors: list[str] = []
    for field in fields:
        value = field_value(block, field)
        if value is None or not is_meaningful(value):
            errors.append(f"{label} {block_id} missing required field: {field}")
    return errors


def referenced_findings_in_risk_matrix(text: str) -> set[str]:
    """Extrait les findings references par le tableau de risques."""
    table = parse_first_table(text, ["Finding"])
    if table is None:
        return set()
    return {
        match.group(0)
        for row in table.rows
        for match in FINDING_ID_RE.finditer(cell(row, table, "Finding"))
    }


def referenced_evidence_ids(value: str) -> set[str]:
    """Extrait les IDs d'evidence references dans une valeur textuelle."""
    return set(EVIDENCE_ID_RE.findall(value))


def has_packaged_python_artifacts(path: Path) -> list[Path]:
    """Detecte les artefacts Python qui ne doivent pas etre livres."""
    artifacts: list[Path] = []
    for candidate in path.rglob("*"):
        if candidate.name == "__pycache__" or candidate.suffix in {".pyc", ".pyo"}:
            artifacts.append(candidate)
    return artifacts


def audit_summary(
    audit_folder: Path, validation_errors: list[str]
) -> dict[str, object]:
    """Construit un resume lisible de l'audit valide ou partiellement valide."""
    summary: dict[str, object] = {
        "audit_folder": str(audit_folder),
        "findings_count": 0,
        "severities": {severity: 0 for severity in SEVERITY_ORDER},
        "story_candidates_count": 0,
        "validation_status": "PASS" if not validation_errors else "FAIL",
    }
    finding_path = audit_folder / "02-finding-register.md"
    if finding_path.exists():
        finding_table = parse_first_table(read_text(finding_path), FINDING_COLUMNS)
        if finding_table:
            summary["findings_count"] = len(finding_table.rows)
            severities = {severity: 0 for severity in SEVERITY_ORDER}
            for row in finding_table.rows:
                severity = cell(row, finding_table, "Severity")
                if severity in severities:
                    severities[severity] += 1
            summary["severities"] = severities
    story_path = audit_folder / "03-story-candidates.md"
    if story_path.exists():
        summary["story_candidates_count"] = len(
            heading_blocks(read_text(story_path), "SC")
        )
    return summary


def explain_audit(audit_folder: Path, validation_errors: list[str]) -> str:
    """Formate un resume CLI de l'audit."""
    summary = audit_summary(audit_folder, validation_errors)
    severities = summary["severities"]
    assert isinstance(severities, dict)
    lines = [
        f"Audit folder: {summary['audit_folder']}",
        f"Findings count: {summary['findings_count']}",
        "Severities count:",
        *[f"- {severity}: {severities[severity]}" for severity in SEVERITY_ORDER],
        f"Story candidates count: {summary['story_candidates_count']}",
        f"Validation status: {summary['validation_status']}",
    ]
    return "\n".join(lines)


def validate_audit_folder(
    audit_folder: Path,
    strict: bool = False,
    allow_any_path: bool = False,
    repo_root: Path | None = None,
) -> list[str]:
    """Retourne les erreurs bloquantes du dossier d'audit."""
    errors: list[str] = []
    if not audit_folder.exists() or not audit_folder.is_dir():
        return [f"Audit folder does not exist: {audit_folder}"]
    if not allow_any_path and not is_audit_path(audit_folder, repo_root):
        errors.append("Audit folder must be under _condamad/audits/**")

    for filename in REQUIRED_FILES:
        path = audit_folder / filename
        if not path.exists():
            errors.append(f"Missing required report file: {filename}")
        elif not read_text(path).strip():
            errors.append(f"Empty report file: {filename}")
    if errors:
        return errors

    finding_text = read_text(audit_folder / "02-finding-register.md")
    finding_table = parse_first_table(finding_text, FINDING_COLUMNS)
    if finding_table is None:
        errors.append("Finding register missing required columns")
        return errors
    errors.extend(malformed_table_errors("Finding register", finding_table))

    evidence_text = read_text(audit_folder / "01-evidence-log.md")
    evidence_table = parse_first_table(
        evidence_text, ["ID", "Evidence type", "Command / Source"]
    )
    errors.extend(malformed_table_errors("Evidence log", evidence_table))
    if evidence_table and "Result" not in evidence_table.headers:
        errors.append("Evidence log missing required columns: Result")
    has_evidence_row = bool(evidence_table and evidence_table.rows)
    has_limitation = (
        "explicit limitation" in evidence_text.casefold()
        or "limitation" in evidence_text.casefold()
    )
    if not has_evidence_row and not has_limitation:
        errors.append(
            "Evidence log contains no command/source and no explicit limitation"
        )
    evidence_ids: list[str] = []
    if evidence_table:
        for row in evidence_table.rows:
            evidence_id = cell(row, evidence_table, "ID")
            evidence_ids.append(evidence_id)
            evidence_type = cell(row, evidence_table, "Evidence type")
            command_source = cell(row, evidence_table, "Command / Source")
            if not EVIDENCE_ID_RE.fullmatch(evidence_id):
                errors.append(f"Invalid evidence ID: {evidence_id}")
            if not is_meaningful(evidence_type):
                errors.append(f"{evidence_id} missing Evidence type")
            if not is_meaningful(command_source):
                errors.append(f"{evidence_id} missing Command / Source")
            if "Result" not in evidence_table.headers:
                continue
            result = cell(row, evidence_table, "Result")
            if result not in VALID_EVIDENCE_RESULTS:
                errors.append(f"{evidence_id} has invalid Result: {result}")
    for duplicate in sorted(
        {item for item in evidence_ids if evidence_ids.count(item) > 1}
    ):
        errors.append(f"Duplicate evidence ID: {duplicate}")
    known_evidence = {
        evidence_id for evidence_id in evidence_ids if EVIDENCE_ID_RE.fullmatch(evidence_id)
    }

    finding_ids: list[str] = []
    finding_rows: dict[str, dict[str, str]] = {}
    story_yes_findings: set[str] = set()
    for row in finding_table.rows:
        finding_id = cell(row, finding_table, "ID")
        severity = cell(row, finding_table, "Severity")
        confidence = cell(row, finding_table, "Confidence")
        evidence = cell(row, finding_table, "Evidence")
        action = cell(row, finding_table, "Recommended action")
        story_candidate = cell(row, finding_table, "Story candidate").casefold()

        if not FINDING_ID_RE.fullmatch(finding_id):
            errors.append(f"Invalid finding ID: {finding_id}")
        finding_ids.append(finding_id)
        if severity not in VALID_SEVERITIES:
            errors.append(f"{finding_id} has invalid severity: {severity}")
        if confidence not in VALID_CONFIDENCE:
            errors.append(f"{finding_id} has invalid confidence: {confidence}")
        if story_candidate not in VALID_STORY_CANDIDATE_VALUES:
            errors.append(
                f"{finding_id} has invalid Story candidate value: {story_candidate}"
            )
        if not is_meaningful(evidence):
            errors.append(f"{finding_id} without evidence")
        evidence_refs = referenced_evidence_ids(evidence)
        if is_meaningful(evidence) and not evidence_refs:
            errors.append(f"{finding_id} evidence must reference an E-xxx ID")
        for evidence_ref in sorted(evidence_refs - known_evidence):
            errors.append(f"{finding_id} references unknown evidence: {evidence_ref}")
        if severity in {"High", "Critical"} and not (
            is_meaningful(action) or action == "needs-user-decision"
        ):
            errors.append(f"{finding_id} is {severity} without recommended action")
        if story_candidate == "yes":
            story_yes_findings.add(finding_id)
        finding_rows[finding_id] = {
            "Severity": severity,
            "Confidence": confidence,
            "Category": cell(row, finding_table, "Category"),
            "Domain": cell(row, finding_table, "Domain"),
            "Evidence": evidence,
            "Impact": cell(row, finding_table, "Impact"),
            "Recommended action": action,
            "Story candidate": story_candidate,
        }

    duplicates = sorted({item for item in finding_ids if finding_ids.count(item) > 1})
    for duplicate in duplicates:
        errors.append(f"Duplicate finding ID: {duplicate}")

    known_findings = set(finding_ids)
    finding_detail_blocks = heading_blocks(finding_text, "F")
    for duplicate in duplicate_heading_ids(finding_text, "F"):
        errors.append(f"Duplicate finding detail block: {duplicate}")
    for finding_id in sorted(known_findings):
        block = finding_detail_blocks.get(finding_id)
        if block is None:
            errors.append(f"{finding_id} missing detail block")
            continue
        errors.extend(
            require_block_fields(
                finding_id, block, FINDING_DETAIL_FIELDS, "Finding detail"
            )
        )
        for field in [
            "Severity",
            "Confidence",
            "Category",
            "Domain",
            "Impact",
            "Recommended action",
            "Story candidate",
        ]:
            value = field_value(block, field)
            if (
                value is not None
                and value.casefold() != finding_rows[finding_id][field].casefold()
            ):
                errors.append(
                    f"{finding_id} detail {field} does not match finding table"
                )
        detail_evidence = field_value(block, "Evidence")
        table_evidence_refs = referenced_evidence_ids(
            finding_rows[finding_id]["Evidence"]
        )
        detail_evidence_refs = referenced_evidence_ids(detail_evidence or "")
        if table_evidence_refs and not table_evidence_refs <= detail_evidence_refs:
            errors.append(f"{finding_id} detail Evidence does not include table evidence IDs")

    story_text = read_text(audit_folder / "03-story-candidates.md")
    for duplicate in duplicate_heading_ids(story_text, "SC"):
        errors.append(f"Duplicate story candidate ID: {duplicate}")
    sources = story_candidate_sources(story_text)
    story_blocks = heading_blocks(story_text, "SC")
    for sc_id, block in sorted(story_blocks.items()):
        errors.extend(
            require_block_fields(
                sc_id, block, STORY_CANDIDATE_FIELDS, "Story candidate"
            )
        )
    mapped_findings = set(sources.values())
    for finding_id in sorted(story_yes_findings - mapped_findings):
        errors.append(f"{finding_id} has story-candidate yes without SC entry")
    for sc_id, finding_id in sorted(sources.items()):
        if finding_id not in known_findings:
            errors.append(f"{sc_id} references unknown finding: {finding_id}")
        elif finding_id not in story_yes_findings:
            errors.append(
                f"{sc_id} references {finding_id} but its Story candidate value is not yes"
            )

    risk_text = read_text(audit_folder / "04-risk-matrix.md")
    risk_table = parse_first_table(risk_text, RISK_COLUMNS)
    if risk_table is None:
        errors.append("Risk matrix missing required columns")
        risk_findings: set[str] = set()
    else:
        risk_findings = {
            match.group(0)
            for row in risk_table.rows
            for match in FINDING_ID_RE.finditer(cell(row, risk_table, "Finding"))
        }
        for row in risk_table.rows:
            for match in FINDING_ID_RE.finditer(cell(row, risk_table, "Finding")):
                finding_id = match.group(0)
                if (
                    finding_id in finding_rows
                    and cell(row, risk_table, "Severity")
                    != finding_rows[finding_id]["Severity"]
                ):
                    errors.append(
                        f"Risk matrix severity for {finding_id} does not match finding table"
                    )
    errors.extend(malformed_table_errors("Risk matrix", risk_table))
    for finding_id in sorted(risk_findings - known_findings):
        errors.append(f"Risk matrix references unknown finding: {finding_id}")
    for finding_id in sorted(known_findings - risk_findings):
        errors.append(f"Risk matrix missing finding: {finding_id}")

    executive_text = read_text(audit_folder / "05-executive-summary.md").strip()
    if len(executive_text.split()) < (10 if strict else 3):
        errors.append("Executive summary is empty or too short")

    for artifact in has_packaged_python_artifacts(audit_folder):
        errors.append(f"Packaged Python artifact is forbidden: {artifact}")

    return errors


def main() -> int:
    """Execute le validateur depuis la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Validate a CONDAMAD domain audit folder."
    )
    parser.add_argument("audit_folder", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--explain-audit",
        action="store_true",
        help="Print audit folder, finding counts, severity counts, story candidate count, and validation status.",
    )
    parser.add_argument(
        "--allow-any-path",
        action="store_true",
        help="Validate report content even when the folder is outside _condamad/audits.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=DEFAULT_REPO_ROOT,
        help="Repository root used to enforce _condamad/audits/** path ownership.",
    )
    args = parser.parse_args()

    errors = validate_audit_folder(
        args.audit_folder.expanduser().resolve(),
        strict=args.strict,
        allow_any_path=args.allow_any_path,
        repo_root=args.repo_root.expanduser().resolve(),
    )
    if errors:
        if args.explain_audit:
            print(explain_audit(args.audit_folder.expanduser().resolve(), errors))
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.explain_audit:
        print(explain_audit(args.audit_folder.expanduser().resolve(), errors))
        return 0
    print("CONDAMAD domain audit validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
