"""Self-tests standard-library pour les helpers condamad-refactor-surgeon.

Ces tests valident les contrats critiques du skill sans dependance externe et
restent hors des conventions `test_*.py` pour eviter la collecte pytest hote.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPT_ROOT))

import condamad_refactor_collect_evidence as collect_evidence  # noqa: E402
import condamad_refactor_scan as scan_script  # noqa: E402
import condamad_refactor_validate as validate_script  # noqa: E402


def write(path: Path, content: str) -> None:
    """Ecrit un fichier de test en creant ses dossiers parents."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def valid_plan(refactor_type: str = "extract-function") -> str:
    """Retourne un plan valide minimal pour les tests."""
    return f"""# CONDAMAD Refactor Plan

## Refactor Type

`{refactor_type}`

## Primary Domain

- Domain: `backend/app/services`

## Current State Evidence

- Evidence 1: `rg "calculate_total" backend/app/services` - current function is embedded in service.

## Target State

- Extract calculation into a private helper in the same module.

## Behavior Invariants

- Existing inputs return identical totals and validation errors.

## Scope Boundary

In scope:

- `backend/app/services/billing/service.py`

Out of scope:

- API contract changes.

## No Legacy / DRY Constraints

- No compatibility wrappers, shims, aliases, re-exports, silent fallbacks, or legacy paths.
- One canonical implementation path after the refactor.

## Validation Plan

### Targeted Tests

```bash
pytest backend/app/tests/unit/test_billing.py -q
```

### Static Checks

```bash
ruff check backend/app/services/billing/service.py
```

### Negative Legacy Scans

```bash
python -B .agents/skills/condamad-refactor-surgeon/scripts/condamad_refactor_scan.py backend/app/services/billing --fail-on-hit
```

### Diff Review

```bash
git diff --check
git diff --stat
git diff --name-status
```

## Diff Review Plan

- Confirm only declared domain files changed.
- Confirm behavior-preserving diff.
"""


def valid_evidence() -> str:
    """Retourne une preuve finale valide minimale."""
    return """# CONDAMAD Refactor Evidence

## Refactor Summary

- Refactor Type: `extract-function`
- Primary Domain: `backend/app/services`
- Status: `PASS`

## Behavior Invariants Evidence

| Invariant | Evidence | Status |
| --- | --- | --- |
| Existing inputs return identical totals. | `pytest backend/app/tests/unit/test_billing.py -q` PASS | PASS |

## Validation Evidence

### Targeted Tests

- Command: `pytest backend/app/tests/unit/test_billing.py -q`
- Result: `PASS`

### Static Checks

- Command: `ruff check backend/app/services/billing/service.py`
- Result: `PASS`

### Negative Legacy Scans

- Command: `python -B .agents/skills/condamad-refactor-surgeon/scripts/condamad_refactor_scan.py backend/app/services/billing --fail-on-hit`
- Result: `PASS`

### Diff Review

- Command: `git diff --check`
- Result: `PASS`
- Review summary: only declared domain changed; behavior-preserving diff.

## Git Evidence Snapshot

<!-- CONDAMAD:REFACTOR-EVIDENCE:START -->
snapshot
<!-- CONDAMAD:REFACTOR-EVIDENCE:END -->

## Residual Risks

- None.
"""


class ValidateSkillRootSelfTest(unittest.TestCase):
    """Verifie la structure et les refus principaux du validateur."""

    def test_valid_package_passes(self) -> None:
        """Le package reel du skill doit passer la validation structurelle."""
        self.assertEqual(validate_script.validate_skill_root(SKILL_ROOT), [])

    def test_missing_skill_fails(self) -> None:
        """Un package sans SKILL.md est invalide."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skill"
            shutil.copytree(SKILL_ROOT, root)
            (root / "SKILL.md").unlink()
            errors = validate_script.validate_skill_root(root)
        self.assertTrue(any("SKILL.md" in error for error in errors))

    def test_missing_openai_yaml_fails(self) -> None:
        """Un package sans agents/openai.yaml est invalide."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skill"
            shutil.copytree(SKILL_ROOT, root)
            (root / "agents/openai.yaml").unlink()
            errors = validate_script.validate_skill_root(root)
        self.assertTrue(any("agents/openai.yaml" in error for error in errors))

    def test_implicit_invocation_true_fails(self) -> None:
        """L'invocation implicite doit rester interdite."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skill"
            shutil.copytree(SKILL_ROOT, root)
            path = root / "agents/openai.yaml"
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "allow_implicit_invocation: false",
                    "allow_implicit_invocation: true",
                ),
                encoding="utf-8",
            )
            errors = validate_script.validate_skill_root(root)
        self.assertTrue(any("allow_implicit_invocation" in error for error in errors))

    def test_forbidden_bytecode_artifacts_fail(self) -> None:
        """Les caches Python packages doivent etre refuses."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skill"
            shutil.copytree(SKILL_ROOT, root)
            write(root / "scripts/__pycache__/bad.pyc", "bytecode")
            errors = validate_script.validate_skill_root(root)
        self.assertTrue(any("Forbidden packaged artifact" in error for error in errors))


class ValidatePlanSelfTest(unittest.TestCase):
    """Verifie les garde-fous de plan avant refactorisation."""

    def validate_plan_text(self, content: str) -> list[str]:
        """Ecrit et valide un plan temporaire."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "refactor-plan.md"
            write(path, content)
            return validate_script.validate_plan(path)

    def test_valid_plan_passes(self) -> None:
        """Un plan complet minimal doit passer."""
        self.assertEqual(self.validate_plan_text(valid_plan()), [])

    def test_invalid_refactor_type_fails(self) -> None:
        """Un type non reference dans la taxonomie est refuse."""
        errors = self.validate_plan_text(valid_plan("rewrite-everything"))
        self.assertTrue(any("Invalid Refactor Type" in error for error in errors))

    def test_missing_domain_fails(self) -> None:
        """Le domaine primaire est obligatoire."""
        errors = self.validate_plan_text(valid_plan().replace("- Domain: `backend/app/services`\n", ""))
        self.assertTrue(any("Primary Domain" in error for error in errors))

    def test_multiple_primary_domains_fail(self) -> None:
        """Un run ne peut pas avoir plusieurs domaines primaires."""
        plan = valid_plan().replace(
            "- Domain: `backend/app/services`",
            "- Domain: `backend/app/services`\n- Domain: `frontend/src`",
        )
        errors = self.validate_plan_text(plan)
        self.assertTrue(any("exactly one" in error for error in errors))

    def test_missing_behavior_invariants_fail(self) -> None:
        """Les invariants comportementaux sont obligatoires."""
        plan = valid_plan().replace(
            "- Existing inputs return identical totals and validation errors.",
            "- <observable behavior that must remain unchanged>",
        )
        errors = self.validate_plan_text(plan)
        self.assertTrue(any("Behavior Invariants" in error for error in errors))

    def test_missing_scope_boundary_detail_fails(self) -> None:
        """Le perimetre doit contenir un in-scope concret et un out-of-scope."""
        plan = valid_plan().replace(
            "In scope:\n\n- `backend/app/services/billing/service.py`\n\nOut of scope:\n\n- API contract changes.",
            "In scope:\n\n- <path>\n",
        )
        errors = self.validate_plan_text(plan)
        self.assertTrue(any("Scope Boundary" in error for error in errors))

    def test_shim_fallback_authorization_fails(self) -> None:
        """Le plan ne doit pas autoriser de shim ou fallback."""
        plan = valid_plan().replace(
            "- One canonical implementation path after the refactor.",
            "- Allow shim and fallback during migration.",
        )
        errors = self.validate_plan_text(plan)
        self.assertTrue(any("forbidden legacy" in error for error in errors))

    def test_negated_fallback_wording_does_not_fail(self) -> None:
        """Une interdiction explicite avec le mot allow ne doit pas echouer."""
        plan = valid_plan().replace(
            "- One canonical implementation path after the refactor.",
            "- Do not allow fallback, shim, alias, or re-export paths.",
        )
        self.assertEqual(self.validate_plan_text(plan), [])

    def test_missing_validation_commands_fails(self) -> None:
        """Les commandes test/static et scan negatif sont obligatoires."""
        plan = valid_plan().replace("pytest backend/app/tests/unit/test_billing.py -q", "echo ok")
        plan = plan.replace("ruff check backend/app/services/billing/service.py", "echo lint")
        plan = plan.replace("condamad_refactor_scan.py backend/app/services/billing --fail-on-hit", "echo scan")
        errors = self.validate_plan_text(plan)
        self.assertTrue(any("test or static command" in error for error in errors))
        self.assertTrue(any("negative scan command" in error for error in errors))


class EvidenceAndScanSelfTest(unittest.TestCase):
    """Verifie la collecte de preuves et le scan de motifs interdits."""

    def test_valid_evidence_passes(self) -> None:
        """Une preuve finale complete doit passer."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "refactor-evidence.md"
            write(path, valid_evidence())
            self.assertEqual(validate_script.validate_evidence(path), [])

    def test_evidence_collector_replaces_markers_idempotently(self) -> None:
        """La collecte remplace la section marquee sans dupliquer les marqueurs."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            write(root / "tracked.txt", "one\n")
            subprocess.run(["git", "add", "tracked.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=root, check=True, capture_output=True)
            write(root / "tracked.txt", "one\ntwo\n")
            write(root / "staged.txt", "staged\n")
            subprocess.run(["git", "add", "staged.txt"], cwd=root, check=True)
            write(root / "untracked.txt", "untracked\n")
            output = root / "refactor-evidence.md"
            write(
                output,
                "before\n\n"
                f"{collect_evidence.START_MARKER}\nold\n{collect_evidence.END_MARKER}\n\n"
                "after\n",
            )
            first = collect_evidence.build_snapshot(root)[0]
            collect_evidence.write_snapshot(output, collect_evidence.wrap_snapshot(first))
            second = collect_evidence.build_snapshot(root)[0]
            collect_evidence.write_snapshot(output, collect_evidence.wrap_snapshot(second))
            content = output.read_text(encoding="utf-8")
        self.assertEqual(content.count(collect_evidence.START_MARKER), 1)
        self.assertEqual(content.count(collect_evidence.END_MARKER), 1)
        for expected in [
            "git status --short",
            "git diff --cached --name-status",
            "git diff HEAD --name-status",
            "git ls-files --others --exclude-standard",
            "git diff --check",
        ]:
            self.assertIn(expected, content)

    def test_scan_fail_on_hit_returns_non_zero(self) -> None:
        """Le scan retourne non-zero quand --fail-on-hit detecte un motif."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"
            write(target, "def fallback_path():\n    return 'legacy'\n")
            findings = scan_script.scan([target], scan_script.DEFAULT_PATTERNS, Path(tmp))
        self.assertGreaterEqual(len(findings), 1)

    def test_artifact_only_scan_detects_ignored_pycache_path(self) -> None:
        """Le mode artefacts doit inspecter les chemins ignores en scan texte."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = root / "__pycache__/bad.pyc"
            write(artifact, "bytecode")
            findings = scan_script.scan(
                [root],
                [r"__pycache__|\.pyc$|\.pyo$"],
                root,
                path_only=True,
            )
        self.assertTrue(any("__pycache__/bad.pyc" in finding[0] for finding in findings))


if __name__ == "__main__":
    unittest.main()
