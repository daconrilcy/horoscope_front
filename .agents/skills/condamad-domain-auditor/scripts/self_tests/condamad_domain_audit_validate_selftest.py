#!/usr/bin/env python3
"""Self-tests du validateur CONDAMAD Domain Auditor.

Ces tests couvrent les invariants bloquants du rapport, le scanner de
dependances et le mode strict du linter.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from condamad_dependency_scan import scan_source  # noqa: E402
from condamad_audit_collect_evidence import evidence_row  # noqa: E402
from condamad_domain_audit_validate import validate_audit_folder  # noqa: E402


VALID_FILES = {
    "00-audit-report.md": """# CONDAMAD Domain Audit Report - services

## 1. Audit Scope

- Domain: backend/app/services
- Audit archetype: service-boundary-audit
- Date: 2026-04-27
- Read-only: yes
- Source request: self-test
- Repository root: temp

## 2. Executive Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 1 |
| Low | 0 |
| Info | 0 |

## 3. Domain Responsibility Contract

Expected responsibility:
- Orchestrate application use cases.

Forbidden responsibilities:
- Return HTTP responses.

## 4. Evidence Summary

- Files inspected: backend/app/services/sample.py
- Commands run: git status and targeted rg scan
- Commands skipped: none
- Runtime evidence: not applicable for this service audit
- Static evidence: dependency scan

## 5. Findings

See `02-finding-register.md`.

## 6. Risk Matrix

See `04-risk-matrix.md`.

## 7. Story Candidates

See `03-story-candidates.md`.

## 8. Limitations

- Self-test fixture only.

## 9. Recommended Next Step

- Create one bounded service-boundary story candidate.
""",
    "01-evidence-log.md": """# Evidence Log

| ID | Evidence type | Command / Source | Result | Notes |
|---|---|---|---|---|
| E-001 | repo-state | `git status --short` | PASS | clean |
| E-002 | static-scan | `rg -n "fastapi" backend/app/services` | PASS | no hit |
""",
    "02-finding-register.md": """# Finding Register

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Medium | High | missing-guard | backend/app/services | E-002 proves no current guard file covers service HTTP type imports. | Future HTTP response imports could enter services unnoticed. | Add a targeted architecture guard for service HTTP type imports. | yes |

## Finding Details

### F-001 - Missing service guard

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: backend/app/services
- Evidence:
  - id: E-002
  - path: backend/app/services
  - command: rg -n "fastapi" backend/app/services
- Expected rule: services do not return HTTP responses.
- Actual state: no guard evidence exists in this fixture.
- Impact: Future HTTP response imports could enter services unnoticed.
- Recommended action: Add a targeted architecture guard for service HTTP type imports.
- Story candidate: yes
- Suggested archetype: architecture-guard-hardening
""",
    "03-story-candidates.md": """# Story Candidates

## SC-001 - Add service boundary guard

- Source finding: F-001
- Suggested story title: Add service boundary guard
- Suggested archetype: architecture-guard-hardening
- Primary domain: backend/app/services
- Required contracts:
  - Service Boundary Audit Contract
- Draft objective:
  - Add a guard that prevents HTTP response imports in services.
- Must include:
  - A targeted negative dependency scan.
- Validation hints:
  - Run the architecture guard test.
- Blockers:
  - none
""",
    "04-risk-matrix.md": """# Risk Matrix

| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |
|---|---|---|---|---|---|---|
| F-001 | Medium | Medium | Services | Low | Small | P1 |
""",
    "05-executive-summary.md": """# Executive Summary

## Domain audited

backend/app/services.

## Overall assessment

The fixture contains one medium service-boundary guard risk with a mapped story candidate.

## Top risks

F-001: missing guard.

## Recommended actions

Create the guard story.

## Story candidates to create first

SC-001.
""",
}


class DomainAuditValidatorSelfTest(unittest.TestCase):
    """Couvre les cas critiques du contrat d'audit."""

    def make_audit(self, overrides: dict[str, str | None] | None = None) -> Path:
        """Cree un dossier d'audit temporaire."""
        root = Path(tempfile.mkdtemp())
        audit = root / "_condamad" / "audits" / "services" / "2026-04-27-1200"
        audit.mkdir(parents=True)
        files = dict(VALID_FILES)
        for name, content in (overrides or {}).items():
            if content is None:
                files.pop(name, None)
            else:
                files[name] = content
        for name, content in files.items():
            (audit / name).write_text(content, encoding="utf-8")
        return audit

    def assert_fails_with(self, audit: Path, expected: str) -> None:
        """Verifie qu'une erreur attendue est retournee."""
        errors = validate_audit_folder(audit, allow_any_path=True)
        self.assertTrue(any(expected in error for error in errors), errors)

    def test_valid_audit_report_passes(self) -> None:
        audit = self.make_audit()
        self.assertEqual([], validate_audit_folder(audit, allow_any_path=True))

    def test_explain_audit_outputs_summary(self) -> None:
        audit = self.make_audit()
        result = subprocess.run(
            [
                sys.executable,
                "-S",
                "-B",
                str(SCRIPT_DIR / "condamad_domain_audit_validate.py"),
                str(audit),
                "--explain-audit",
                "--allow-any-path",
            ],
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn(f"Audit folder: {audit.resolve()}", result.stdout)
        self.assertIn("Findings count: 1", result.stdout)
        self.assertIn("- Medium: 1", result.stdout)
        self.assertIn("Story candidates count: 1", result.stdout)
        self.assertIn("Validation status: PASS", result.stdout)

    def test_audit_folder_must_be_under_condamad_audits_by_default(self) -> None:
        root = Path(tempfile.mkdtemp())
        audit = root / "outside-audit"
        audit.mkdir()
        for name, content in VALID_FILES.items():
            (audit / name).write_text(content, encoding="utf-8")
        errors = validate_audit_folder(audit)
        self.assertTrue(
            any("_condamad/audits" in error for error in errors),
            errors,
        )

    def test_audit_folder_under_external_condamad_audits_fails_by_default(
        self,
    ) -> None:
        audit = self.make_audit()
        errors = validate_audit_folder(audit)
        self.assertTrue(
            any("_condamad/audits" in error for error in errors),
            errors,
        )

    def test_missing_required_report_file_fails(self) -> None:
        self.assert_fails_with(
            self.make_audit({"05-executive-summary.md": None}),
            "Missing required report file",
        )

    def test_empty_report_file_fails(self) -> None:
        self.assert_fails_with(
            self.make_audit({"05-executive-summary.md": ""}), "Empty report file"
        )

    def test_finding_register_missing_required_columns_fails(self) -> None:
        content = VALID_FILES["02-finding-register.md"].replace(
            "| ID | Severity | Confidence |", "| ID | Severity |"
        )
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}),
            "Finding register missing required columns",
        )

    def test_duplicate_finding_id_fails(self) -> None:
        content = VALID_FILES["02-finding-register.md"].replace(
            "| F-001 | Medium | High | missing-guard | backend/app/services | E-002 proves no current guard file covers service HTTP type imports. | Future HTTP response imports could enter services unnoticed. | Add a targeted architecture guard for service HTTP type imports. | yes |",
            "| F-001 | Medium | High | missing-guard | backend/app/services | E-002 proves no current guard file covers service HTTP type imports. | Future HTTP response imports could enter services unnoticed. | Add a targeted architecture guard for service HTTP type imports. | yes |\n| F-001 | Low | High | observability-gap | backend/app/services | E-002 | Minor observability gap. | Add a named signal check for this guard. | no |",
        )
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}), "Duplicate finding ID"
        )

    def test_invalid_severity_fails(self) -> None:
        content = VALID_FILES["02-finding-register.md"].replace(
            "| F-001 | Medium |", "| F-001 | Major |"
        )
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}), "invalid severity"
        )

    def test_high_finding_without_evidence_fails(self) -> None:
        content = VALID_FILES["02-finding-register.md"].replace(
            "| F-001 | Medium | High |", "| F-001 | High | High |"
        )
        content = content.replace(
            "| E-002 proves no current guard file covers service HTTP type imports. |",
            "|  |",
        )
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}), "without evidence"
        )

    def test_medium_finding_without_evidence_fails(self) -> None:
        content = VALID_FILES["02-finding-register.md"].replace(
            "| E-002 proves no current guard file covers service HTTP type imports. |",
            "|  |",
        )
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}), "without evidence"
        )

    def test_finding_references_unknown_evidence_fails(self) -> None:
        content = VALID_FILES["02-finding-register.md"].replace("E-002", "E-999")
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}),
            "references unknown evidence",
        )

    def test_finding_evidence_without_evidence_id_fails(self) -> None:
        content = VALID_FILES["02-finding-register.md"].replace(
            "E-002 proves no current guard file covers service HTTP type imports.",
            "Manual scan proves no current guard file covers service HTTP type imports.",
        )
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}),
            "evidence must reference an E-xxx ID",
        )

    def test_high_finding_without_recommended_action_fails(self) -> None:
        content = VALID_FILES["02-finding-register.md"].replace(
            "| F-001 | Medium | High |", "| F-001 | High | High |"
        )
        content = content.replace(
            "| Add a targeted architecture guard for service HTTP type imports. | yes |",
            "|  | yes |",
        )
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}),
            "without recommended action",
        )

    def test_story_candidate_yes_without_sc_entry_fails(self) -> None:
        self.assert_fails_with(
            self.make_audit({"03-story-candidates.md": "# Story Candidates\n"}),
            "without SC entry",
        )

    def test_story_candidate_missing_suggested_archetype_fails(self) -> None:
        content = VALID_FILES["03-story-candidates.md"].replace(
            "- Suggested archetype: architecture-guard-hardening",
            "- Suggested archetype:",
        )
        self.assert_fails_with(
            self.make_audit({"03-story-candidates.md": content}),
            "missing required field: Suggested archetype",
        )

    def test_story_candidate_missing_primary_domain_fails(self) -> None:
        content = VALID_FILES["03-story-candidates.md"].replace(
            "- Primary domain: backend/app/services",
            "- Primary domain:",
        )
        self.assert_fails_with(
            self.make_audit({"03-story-candidates.md": content}),
            "missing required field: Primary domain",
        )

    def test_story_candidate_missing_required_contracts_fails(self) -> None:
        content = VALID_FILES["03-story-candidates.md"].replace(
            "- Required contracts:\n  - Service Boundary Audit Contract",
            "- Required contracts:",
        )
        self.assert_fails_with(
            self.make_audit({"03-story-candidates.md": content}),
            "missing required field: Required contracts",
        )

    def test_story_candidate_missing_validation_hints_fails(self) -> None:
        content = VALID_FILES["03-story-candidates.md"].replace(
            "- Validation hints:\n  - Run the architecture guard test.",
            "- Validation hints:",
        )
        self.assert_fails_with(
            self.make_audit({"03-story-candidates.md": content}),
            "missing required field: Validation hints",
        )

    def test_sc_references_unknown_finding_fails(self) -> None:
        content = VALID_FILES["03-story-candidates.md"].replace(
            "Source finding: F-001", "Source finding: F-999"
        )
        self.assert_fails_with(
            self.make_audit({"03-story-candidates.md": content}),
            "references unknown finding",
        )

    def test_sc_references_finding_with_story_candidate_no_fails(self) -> None:
        content = (
            VALID_FILES["02-finding-register.md"]
            .replace(
                "| Add a targeted architecture guard for service HTTP type imports. | yes |",
                "| Add a targeted architecture guard for service HTTP type imports. | no |",
            )
            .replace("- Story candidate: yes", "- Story candidate: no")
        )
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}),
            "Story candidate value is not yes",
        )

    def test_risk_matrix_references_unknown_finding_fails(self) -> None:
        content = VALID_FILES["04-risk-matrix.md"].replace("| F-001 |", "| F-999 |")
        self.assert_fails_with(
            self.make_audit({"04-risk-matrix.md": content}),
            "Risk matrix references unknown finding",
        )

    def test_risk_matrix_missing_known_finding_fails(self) -> None:
        content = (
            "# Risk Matrix\n\n"
            "| Finding | Severity | Probability | Blast radius | Regression risk | Effort | Priority |\n"
            "|---|---|---|---|---|---|---|\n"
        )
        self.assert_fails_with(
            self.make_audit({"04-risk-matrix.md": content}),
            "Risk matrix missing finding",
        )

    def test_risk_matrix_missing_required_columns_fails(self) -> None:
        content = "# Risk Matrix\n\n| Finding |\n|---|\n| F-001 |\n"
        self.assert_fails_with(
            self.make_audit({"04-risk-matrix.md": content}),
            "Risk matrix missing required columns",
        )

    def test_risk_matrix_mismatched_severity_fails(self) -> None:
        content = VALID_FILES["04-risk-matrix.md"].replace(
            "| F-001 | Medium |", "| F-001 | Low |"
        )
        self.assert_fails_with(
            self.make_audit({"04-risk-matrix.md": content}),
            "Risk matrix severity for F-001 does not match finding table",
        )

    def test_invalid_story_candidate_value_fails(self) -> None:
        content = VALID_FILES["02-finding-register.md"].replace(
            "| Add a targeted architecture guard for service HTTP type imports. | yes |",
            "| Add a targeted architecture guard for service HTTP type imports. | maybe |",
        )
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}),
            "invalid Story candidate value",
        )

    def test_finding_without_detail_block_fails(self) -> None:
        content = VALID_FILES["02-finding-register.md"].replace(
            "### F-001 - Missing service guard",
            "### F-999 - Missing service guard",
        )
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}),
            "missing detail block",
        )

    def test_duplicate_finding_detail_block_fails(self) -> None:
        content = (
            VALID_FILES["02-finding-register.md"]
            + "\n### F-001 - Duplicate detail\n\n- Severity: Medium\n"
        )
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}),
            "Duplicate finding detail block",
        )

    def test_finding_detail_missing_expected_rule_fails(self) -> None:
        content = VALID_FILES["02-finding-register.md"].replace(
            "- Expected rule: services do not return HTTP responses.\n",
            "",
        )
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}),
            "missing required field: Expected rule",
        )

    def test_finding_detail_missing_actual_state_fails(self) -> None:
        content = VALID_FILES["02-finding-register.md"].replace(
            "- Actual state: no guard evidence exists in this fixture.\n",
            "",
        )
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}),
            "missing required field: Actual state",
        )

    def test_finding_detail_mismatched_severity_fails(self) -> None:
        content = VALID_FILES["02-finding-register.md"].replace(
            "- Severity: Medium",
            "- Severity: High",
        )
        self.assert_fails_with(
            self.make_audit({"02-finding-register.md": content}),
            "detail Severity does not match finding table",
        )

    def test_evidence_log_empty_fails(self) -> None:
        content = "# Evidence Log\n\n| ID | Evidence type | Command / Source | Result | Notes |\n|---|---|---|---|---|\n"
        self.assert_fails_with(
            self.make_audit({"01-evidence-log.md": content}),
            "Evidence log contains no command",
        )

    def test_evidence_log_invalid_id_fails(self) -> None:
        content = VALID_FILES["01-evidence-log.md"].replace("| E-001 |", "| X-001 |")
        self.assert_fails_with(
            self.make_audit({"01-evidence-log.md": content}),
            "Invalid evidence ID",
        )

    def test_evidence_log_missing_command_source_fails(self) -> None:
        content = VALID_FILES["01-evidence-log.md"].replace(
            "| E-001 | repo-state | `git status --short` | PASS | clean |",
            "| E-001 | repo-state |  | PASS | clean |",
        )
        self.assert_fails_with(
            self.make_audit({"01-evidence-log.md": content}),
            "missing Command / Source",
        )

    def test_evidence_log_invalid_result_fails(self) -> None:
        content = VALID_FILES["01-evidence-log.md"].replace(
            "| PASS | clean |", "| OK | clean |"
        )
        self.assert_fails_with(
            self.make_audit({"01-evidence-log.md": content}),
            "has invalid Result",
        )

    def test_evidence_log_duplicate_id_fails(self) -> None:
        content = VALID_FILES["01-evidence-log.md"] + (
            "| E-002 | static-scan | `rg -n \"HTTPException\" backend/app/services` | PASS | no hit |\n"
        )
        self.assert_fails_with(
            self.make_audit({"01-evidence-log.md": content}),
            "Duplicate evidence ID",
        )

    def test_evidence_log_missing_result_column_fails(self) -> None:
        content = VALID_FILES["01-evidence-log.md"].replace(
            "| ID | Evidence type | Command / Source | Result | Notes |",
            "| ID | Evidence type | Command / Source | Notes |",
        )
        self.assert_fails_with(
            self.make_audit({"01-evidence-log.md": content}),
            "Evidence log missing required columns: Result",
        )

    def test_evidence_log_unescaped_pipe_fails(self) -> None:
        content = VALID_FILES["01-evidence-log.md"].replace(
            "| E-001 | repo-state | `git status --short` | PASS | clean |",
            "| E-001 | repo-state | `git status --short` | PASS | clean | broken |",
        )
        self.assert_fails_with(
            self.make_audit({"01-evidence-log.md": content}),
            "Evidence log has malformed Markdown table row",
        )

    def test_evidence_log_malformed_separator_fails(self) -> None:
        content = VALID_FILES["01-evidence-log.md"].replace(
            "|---|---|---|---|---|",
            "|---|---|---|",
        )
        self.assert_fails_with(
            self.make_audit({"01-evidence-log.md": content}),
            "Evidence log has malformed Markdown table separator",
        )

    def test_packaged_pycache_fails(self) -> None:
        audit = self.make_audit()
        (audit / "__pycache__").mkdir()
        self.assert_fails_with(audit, "Packaged Python artifact")

    def test_packaged_pyc_fails(self) -> None:
        audit = self.make_audit()
        (audit / "bad.pyc").write_bytes(b"")
        self.assert_fails_with(audit, "Packaged Python artifact")

    def test_dependency_scan_detects_forbidden_import(self) -> None:
        root = Path(tempfile.mkdtemp())
        source = root / "sample.py"
        source.write_text("from app.api import router\n", encoding="utf-8")
        hits = scan_source(source, ["app.api"], [])
        self.assertEqual(1, len(hits))

    def test_dependency_scan_detects_forbidden_imported_symbol(self) -> None:
        root = Path(tempfile.mkdtemp())
        source = root / "sample.py"
        source.write_text("from fastapi import HTTPException\n", encoding="utf-8")
        hits = scan_source(source, ["HTTPException"], [])
        self.assertEqual(1, len(hits))

    def test_dependency_scan_ignores_comment_mentions(self) -> None:
        root = Path(tempfile.mkdtemp())
        source = root / "sample.py"
        source.write_text("# fastapi mention only\nvalue = 'fastapi'\n", encoding="utf-8")
        hits = scan_source(source, ["fastapi"], [])
        self.assertEqual([], hits)

    def test_dependency_scan_reports_syntax_error(self) -> None:
        root = Path(tempfile.mkdtemp())
        source = root / "sample.py"
        source.write_text("from fastapi import HTTPException\nif True\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                "-S",
                "-B",
                str(SCRIPT_DIR / "condamad_dependency_scan.py"),
                "--source",
                str(source),
                "--forbid",
                "fastapi",
            ],
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("parse-error", result.stdout)

    def test_dependency_scan_fail_on_hit_returns_non_zero(self) -> None:
        root = Path(tempfile.mkdtemp())
        source = root / "sample.py"
        source.write_text("from fastapi import HTTPException\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                "-S",
                "-B",
                str(SCRIPT_DIR / "condamad_dependency_scan.py"),
                "--source",
                str(source),
                "--forbid",
                "fastapi",
                "--fail-on-hit",
            ],
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
        self.assertNotEqual(0, result.returncode)

    def test_lint_strict_fails_on_vague_recommended_action(self) -> None:
        content = VALID_FILES["02-finding-register.md"].replace(
            "Add a targeted architecture guard for service HTTP type imports.", "fix"
        )
        audit = self.make_audit({"02-finding-register.md": content})
        result = subprocess.run(
            [
                sys.executable,
                "-S",
                "-B",
                str(SCRIPT_DIR / "condamad_domain_audit_lint.py"),
                str(audit),
                "--strict",
            ],
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
        self.assertNotEqual(0, result.returncode)

    def test_collect_evidence_dependency_scan_hit_is_fail(self) -> None:
        root = Path(tempfile.mkdtemp())
        repo = root / "repo"
        repo.mkdir()
        bad = repo / "bad.py"
        bad.write_text("from fastapi import HTTPException\n", encoding="utf-8")
        audit = repo / "_condamad" / "audits" / "services" / "2026-04-27-1300"
        audit.mkdir(parents=True)
        result = subprocess.run(
            [
                sys.executable,
                "-S",
                "-B",
                str(SCRIPT_DIR / "condamad_audit_collect_evidence.py"),
                str(audit),
                "--repo-root",
                str(repo),
                "--dependency-scan-source",
                str(bad),
                "--forbid",
                "fastapi",
            ],
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        evidence = (audit / "01-evidence-log.md").read_text(encoding="utf-8")
        self.assertIn("| E-002 | dependency-scan |", evidence)
        self.assertIn("| FAIL |", evidence)
        self.assertIn("forbidden fastapi", evidence)

    def test_collect_evidence_runtime_command(self) -> None:
        root = Path(tempfile.mkdtemp())
        repo = root / "repo"
        repo.mkdir()
        audit = repo / "_condamad" / "audits" / "services" / "2026-04-27-1400"
        audit.mkdir(parents=True)
        result = subprocess.run(
            [
                sys.executable,
                "-S",
                "-B",
                str(SCRIPT_DIR / "condamad_audit_collect_evidence.py"),
                str(audit),
                "--repo-root",
                str(repo),
                "--runtime-command",
                f'"{sys.executable}" -S -B -c "print(123)"',
            ],
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        evidence = (audit / "01-evidence-log.md").read_text(encoding="utf-8")
        self.assertIn("| E-002 | runtime-command |", evidence)
        self.assertIn("| PASS |", evidence)
        self.assertIn("123", evidence)

    def test_evidence_row_escapes_markdown_pipes(self) -> None:
        row = evidence_row("E-001", "static-scan", "rg a|b", "PASS", "hit | note")
        self.assertIn("a\\|b", row)
        self.assertIn("hit \\| note", row)

    def test_duplicate_story_candidate_id_fails(self) -> None:
        content = VALID_FILES["03-story-candidates.md"] + VALID_FILES[
            "03-story-candidates.md"
        ].replace("SC-001", "SC-001", 1)
        self.assert_fails_with(
            self.make_audit({"03-story-candidates.md": content}),
            "Duplicate story candidate ID",
        )

    def test_current_skill_package_has_no_python_artifacts(self) -> None:
        skill_root = Path(__file__).resolve().parents[2]
        artifacts = [
            path
            for path in skill_root.rglob("*")
            if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}
        ]
        self.assertEqual([], artifacts)


if __name__ == "__main__":
    unittest.main()
