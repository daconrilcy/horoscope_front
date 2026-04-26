#!/usr/bin/env python3
"""Self-tests du validateur CONDAMAD Story Writer.

Ces tests couvrent un exemple valide et plusieurs refus essentiels du contrat.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys

SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from condamad_story_extract_ac import extract_acceptance_criteria  # noqa: E402
from condamad_story_validate import validate_story  # noqa: E402


VALID_STORY = """# Story test-story: Harden service imports

Status: ready-for-dev

## 1. Objective

Constrain service imports to the canonical billing namespace and prove that old imports are absent.

## 2. Trigger / Source

- Source type: audit
- Source reference: pasted audit
- Reason for change: duplicate billing import paths create architecture drift.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: backend/app/services/billing
- In scope:
  - Replace old billing imports in backend service consumers.
- Out of scope:
  - Frontend billing UI changes.
- Explicit non-goals:
  - Do not change entitlement behavior.

## 4. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/services/billing/quota_runtime.py` - canonical billing runtime exists.
- Evidence 2: `backend/app/tests/unit/test_billing_imports.py` - guard coverage is expected.

## 5. Target State

After implementation:

- Consumers use the canonical billing namespace.
- Old billing root imports are absent.
- Architecture guard tests prove the namespace boundary.

## 6. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Consumers import billing services from `backend/app/services/billing` only. | `rg "app.services.quota_usage_service" backend/app backend/tests` returns no nominal import. |
| AC2 | A guard test fails if the old root import returns. | `pytest -q backend/app/tests/unit/test_billing_imports.py` passes. |

## 7. Implementation Tasks

- [ ] Task 1 - Update import consumers (AC: AC1)
  - [ ] Subtask 1.1 - Inspect current billing imports.
- [ ] Task 2 - Add architecture guard coverage (AC: AC2)
  - [ ] Subtask 2.1 - Add a negative import test.

## 8. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/services/billing/quota_runtime.py` for billing runtime behavior.
- Do not recreate:
  - quota runtime calculations.
- Shared abstraction allowed only if:
  - two concrete billing consumers need the same behavior.

## 9. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `backend/app/services/quota_usage_service.py`

## 10. Files to Inspect First

Codex must inspect before editing:

- `backend/app/services/billing/quota_runtime.py`
- `backend/app/tests/unit/test_billing_imports.py`

## 11. Expected Files to Modify

Likely files:

- `backend/app/services/billing/quota_runtime.py` - verify canonical exports.

Likely tests:

- `backend/app/tests/unit/test_billing_imports.py` - architecture guard coverage.

Files not expected to change:

- `frontend/src` - outside backend billing domain.

## 12. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 13. Validation Plan

Run or justify why skipped:

```bash
pytest -q backend/app/tests/unit/test_billing_imports.py
ruff check .
rg "app.services.quota_usage_service" backend/app backend/tests
```

## 14. Regression Risks

- Risk: import migration breaks runtime billing consumers.
  - Guardrail: targeted billing import tests must pass.

## 15. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.

## 16. References

- `backend/app/services/billing/quota_runtime.py` - canonical runtime target.
"""


class CondamadStoryValidateSelfTest(unittest.TestCase):
    """Verifie le comportement attendu du validateur."""

    def write_story(self, content: str) -> Path:
        """Ecrit une story temporaire pour un test."""
        directory = Path(tempfile.mkdtemp())
        path = directory / "00-story.md"
        path.write_text(content, encoding="utf-8")
        return path

    def test_valid_story_passes(self) -> None:
        """Une story complete passe le contrat."""
        self.assertEqual(validate_story(self.write_story(VALID_STORY)), [])

    def test_ac_without_evidence_fails(self) -> None:
        """Un AC sans preuve de validation est refuse."""
        story = VALID_STORY.replace(
            '| AC1 | Consumers import billing services from `backend/app/services/billing` only. | `rg "app.services.quota_usage_service" backend/app backend/tests` returns no nominal import. |',
            "| AC1 | Consumers import billing services from `backend/app/services/billing` only. | ... |",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any("AC1 has no concrete validation evidence" in error for error in errors)
        )

    def test_task_without_ac_fails(self) -> None:
        """Une tache sans reference AC est refusee."""
        story = VALID_STORY.replace("(AC: AC1)", "")
        errors = validate_story(self.write_story(story))
        self.assertTrue(any("Task missing AC reference" in error for error in errors))

    def test_task_referencing_unknown_ac_fails(self) -> None:
        """Une tache ne peut pas cibler un AC absent de la table."""
        story = VALID_STORY.replace("(AC: AC1)", "(AC: AC99)")
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any("Task references unknown AC: AC99" in error for error in errors)
        )

    def test_weak_ac_evidence_fails(self) -> None:
        """Une preuve manuelle vague est refusee."""
        story = VALID_STORY.replace(
            "`pytest -q backend/app/tests/unit/test_billing_imports.py` passes.",
            "review manually",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any("AC2 has no concrete validation evidence" in error for error in errors)
        )

    def test_negative_cleanup_guardrail_is_allowed(self) -> None:
        """Un garde-fou negatif contenant cleanup ne declenche pas le scan vague."""
        story = VALID_STORY.replace(
            "- Do not broaden the domain.",
            "- Do not broaden the domain.\n- Do not perform unrelated cleanup.",
        )
        self.assertEqual(validate_story(self.write_story(story)), [])

    def test_empty_expected_files_block_fails(self) -> None:
        """Chaque bloc de fichiers attendus doit contenir une preuve concrete."""
        story = VALID_STORY.replace(
            "Likely tests:\n\n- `backend/app/tests/unit/test_billing_imports.py` - architecture guard coverage.",
            "Likely tests:\n",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any(
                "Expected Files to Modify block must contain a concrete path" in error
                for error in errors
            )
        )

    def test_backticked_non_path_fails_for_expected_files(self) -> None:
        """Un texte entre backticks ne suffit pas s'il ne ressemble pas a un chemin."""
        story = VALID_STORY.replace(
            "`frontend/src` - outside backend billing domain.",
            "`not-a-path` - outside backend billing domain.",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any(
                "Expected Files to Modify block must contain a concrete path" in error
                for error in errors
            )
        )

    def test_backticked_non_path_fails_for_inspect_first(self) -> None:
        """Files to Inspect First exige aussi un chemin concret."""
        story = VALID_STORY.replace(
            "Codex must inspect before editing:\n\n"
            "- `backend/app/services/billing/quota_runtime.py`\n"
            "- `backend/app/tests/unit/test_billing_imports.py`",
            "Codex must inspect before editing:\n\n- `package-x`\n- `another-token`",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any(
                "Files to Inspect First must list at least one concrete path" in error
                for error in errors
            )
        )

    def test_dependency_requires_explicit_justification_line(self) -> None:
        """Une dependance nommee doit avoir une ligne Justification dediee."""
        story = VALID_STORY.replace(
            "- New dependencies: none\n- Dependency changes allowed only if explicitly listed here with justification.",
            "- New dependencies: package-x\n- Dependency changes allowed only if explicitly listed here with justification.",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any("explicit 'Justification:' line" in error for error in errors)
        )

    def test_dependency_with_name_and_justification_passes(self) -> None:
        """Une dependance explicite avec justification est acceptee."""
        story = VALID_STORY.replace(
            "- New dependencies: none\n- Dependency changes allowed only if explicitly listed here with justification.",
            "- New dependencies: package-x\n- Justification: required because existing project dependencies cannot parse this format.",
        )
        self.assertEqual(validate_story(self.write_story(story)), [])

    def test_extract_acceptance_criteria(self) -> None:
        """L'extracteur retourne les AC avec leur preuve."""
        acs = extract_acceptance_criteria(VALID_STORY)
        self.assertEqual([item["ac"] for item in acs], ["AC1", "AC2"])
        self.assertIn("pytest", acs[1]["evidence"])


if __name__ == "__main__":
    unittest.main()
