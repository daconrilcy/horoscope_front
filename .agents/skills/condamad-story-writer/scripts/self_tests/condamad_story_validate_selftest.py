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

## 4. Operation Contract

- Operation type: converge
- Primary archetype: namespace-convergence
- Archetype reason: billing imports must converge on one canonical namespace.
- Behavior change allowed: no
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: repository evidence shows an external consumer of the old import path.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/services/billing/quota_runtime.py` - canonical billing runtime exists.
- Evidence 2: `backend/app/tests/unit/test_billing_imports.py` - guard coverage is expected.

## 6. Target State

After implementation:

- Consumers use the canonical billing namespace.
- Old billing root imports are absent.
- Architecture guard tests prove the namespace boundary.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Consumers import billing services from `backend/app/services/billing` only. | `rg "app.services.quota_usage_service" backend/app backend/tests` returns no nominal import. |
| AC2 | A guard test fails if the old root import returns. | `pytest -q backend/app/tests/unit/test_billing_imports.py` passes. |

## 8. Implementation Tasks

- [ ] Task 1 - Update import consumers (AC: AC1)
  - [ ] Subtask 1.1 - Inspect current billing imports.
- [ ] Task 2 - Add architecture guard coverage (AC: AC2)
  - [ ] Subtask 2.1 - Add a negative import test.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/services/billing/quota_runtime.py` for billing runtime behavior.
- Do not recreate:
  - quota runtime calculations.
- Shared abstraction allowed only if:
  - two concrete billing consumers need the same behavior.

## 10. No Legacy / Forbidden Paths

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

## 11. Files to Inspect First

Codex must inspect before editing:

- `backend/app/services/billing/quota_runtime.py`
- `backend/app/tests/unit/test_billing_imports.py`

## 12. Expected Files to Modify

Likely files:

- `backend/app/services/billing/quota_runtime.py` - verify canonical exports.

Likely tests:

- `backend/app/tests/unit/test_billing_imports.py` - architecture guard coverage.

Files not expected to change:

- `frontend/src` - outside backend billing domain.

## 13. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 14. Validation Plan

Run or justify why skipped:

```bash
pytest -q backend/app/tests/unit/test_billing_imports.py
ruff check .
rg "app.services.quota_usage_service" backend/app backend/tests
```

## 15. Regression Risks

- Risk: import migration breaks runtime billing consumers.
  - Guardrail: targeted billing import tests must pass.

## 16. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 17. References

- `backend/app/services/billing/quota_runtime.py` - canonical runtime target.
"""

REMOVAL_SECTIONS = """
## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, email templates, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions:

- `keep`
- `delete`
- `replace-consumer`
- `needs-user-decision`

Audit output path when applicable:

- `_condamad/stories/remove-api-facade/route-consumption-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Public AI generation | `/v1/chat/*` | `/v1/ai/*` |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev
agent must stop or record an explicit user decision with external evidence and
deletion risk.

## 16. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the
removed surface is reintroduced.

The guard must check at least one deterministic source:

- registered router prefixes
- generated OpenAPI paths

Required forbidden examples:

- `/v1/ai`
- `backend/app/api/v1/routers/public/ai.py`

## 17. Generated Contract Check

Required generated-contract evidence:

- OpenAPI path absence
- generated client/schema absence
"""

VALID_REMOVAL_STORY = (
    VALID_STORY.replace(
        "# Story test-story: Harden service imports",
        "# Story remove-api-facade: Remove historical API facade",
    )
    .replace(
        "Constrain service imports to the canonical billing namespace and prove that old imports are absent.",
        "Remove the historical `/v1/ai/*` facade routes after deterministic classification and prove they cannot reappear.",
    )
    .replace("- Source type: audit", "- Source type: refactor")
    .replace(
        "- Reason for change: duplicate billing import paths create architecture drift.",
        "- Reason for change: historical facade routes preserve a legacy API surface.",
    )
    .replace(
        "- Domain: backend/app/services/billing",
        "- Domain: backend/app/api/v1/routers/public",
    )
    .replace(
        "- Operation type: converge",
        "- Operation type: remove",
    )
    .replace(
        "- Primary archetype: namespace-convergence",
        "- Primary archetype: api-route-removal",
    )
    .replace(
        "- Archetype reason: billing imports must converge on one canonical namespace.",
        "- Archetype reason: the story removes historical public API route surfaces.",
    )
    .replace("- Deletion allowed: no", "- Deletion allowed: yes")
    .replace(
        "## 11. Files to Inspect First",
        f"{REMOVAL_SECTIONS}\n## 18. Files to Inspect First",
    )
    .replace("## 12. Expected Files to Modify", "## 19. Expected Files to Modify")
    .replace("## 13. Dependency Policy", "## 20. Dependency Policy")
    .replace("## 14. Validation Plan", "## 21. Validation Plan")
    .replace("## 15. Regression Risks", "## 22. Regression Risks")
    .replace("## 16. Dev Agent Instructions", "## 23. Dev Agent Instructions")
    .replace("## 17. References", "## 24. References")
)


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

    def test_valid_removal_story_passes(self) -> None:
        """Une story de suppression complete applique le contrat Removal."""
        self.assertEqual(validate_story(self.write_story(VALID_REMOVAL_STORY)), [])

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

    def test_evidence_profile_without_command_fails(self) -> None:
        """Un profil de preuve seul ne suffit pas sans commande ou test concret."""
        story = VALID_STORY.replace(
            "`pytest -q backend/app/tests/unit/test_billing_imports.py` passes.",
            "Evidence profile: `route_removed`",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any("AC2 has no concrete validation evidence" in error for error in errors)
        )

    def test_evidence_profile_with_command_passes(self) -> None:
        """Un profil de preuve est accepte avec une commande concrete."""
        story = VALID_STORY.replace(
            "`pytest -q backend/app/tests/unit/test_billing_imports.py` passes.",
            "Evidence profile: `route_removed`; `pytest -q backend/app/tests/unit/test_billing_imports.py` passes.",
        )
        self.assertEqual(validate_story(self.write_story(story)), [])

    def test_legacy_guard_story_does_not_trigger_removal_contract(self) -> None:
        """Une story guard mentionnant legacy sans cible de suppression reste non-removal."""
        story = VALID_STORY.replace(
            "Constrain service imports to the canonical billing namespace and prove that old imports are absent.",
            "Add an architecture guard against legacy fallback reintroduction without changing runtime behavior.",
        ).replace(
            "- Primary archetype: namespace-convergence",
            "- Primary archetype: test-guard-hardening",
        )
        self.assertEqual(validate_story(self.write_story(story)), [])

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

    def test_removal_story_without_classification_rules_fails(self) -> None:
        """Une suppression sans classification deterministe est refusee."""
        story = VALID_REMOVAL_STORY.replace(
            "## 11. Removal Classification Rules",
            "## 11. Missing Removal Classification Rules",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any(
                "Removal story missing required section: Removal Classification Rules"
                in error
                for error in errors
            )
        )

    def test_removal_story_without_audit_format_fails(self) -> None:
        """Une suppression sans format d'audit strict est refusee."""
        story = VALID_REMOVAL_STORY.replace(
            "## 12. Removal Audit Format",
            "## 12. Missing Removal Audit Format",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any(
                "Removal story missing required section: Removal Audit Format" in error
                for error in errors
            )
        )

    def test_removal_story_without_delete_only_rule_fails(self) -> None:
        """Une suppression sans Delete-Only Rule est refusee."""
        story = VALID_REMOVAL_STORY.replace(
            "## 14. Delete-Only Rule",
            "## 14. Missing Delete-Only Rule",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any(
                "Removal story missing required section: Delete-Only Rule" in error
                for error in errors
            )
        )

    def test_removal_story_without_canonical_ownership_fails(self) -> None:
        """Une suppression sans proprietaire canonique est refusee."""
        story = VALID_REMOVAL_STORY.replace(
            "## 13. Canonical Ownership",
            "## 13. Missing Canonical Ownership",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any(
                "Removal story missing required section: Canonical Ownership" in error
                for error in errors
            )
        )

    def test_removal_story_without_reintroduction_guard_fails(self) -> None:
        """Une suppression No Legacy sans guard de reintroduction est refusee."""
        story = VALID_REMOVAL_STORY.replace(
            "## 16. Reintroduction Guard",
            "## 16. Missing Reintroduction Guard",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any(
                "Removal story missing required section: Reintroduction Guard" in error
                for error in errors
            )
        )

    def test_non_generated_removal_can_skip_generated_contract_with_reason(
        self,
    ) -> None:
        """Une suppression interne non exposee peut justifier generated contract N/A."""
        story = (
            VALID_REMOVAL_STORY.replace(
                "- Primary archetype: api-route-removal",
                "- Primary archetype: dead-code-removal",
            )
            .replace(
                "- Archetype reason: the story removes historical public API route surfaces.",
                "- Archetype reason: the story removes a dead internal helper module.",
            )
            .replace(
                "Required generated-contract evidence:\n\n- OpenAPI path absence\n- generated client/schema absence",
                "- Generated contract check: not applicable\n- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.",
            )
        )
        self.assertEqual(validate_story(self.write_story(story)), [])

    def test_api_removal_cannot_skip_generated_contract_check(self) -> None:
        """Une suppression API doit garder une preuve OpenAPI/generated active."""
        story = VALID_REMOVAL_STORY.replace(
            "Required generated-contract evidence:\n\n- OpenAPI path absence\n- generated client/schema absence",
            "- Generated contract check: not applicable\n- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(any("cannot be not applicable" in error for error in errors))

    def test_generated_contract_not_applicable_requires_reason(self) -> None:
        """Un N/A generated contract hors API doit expliquer pourquoi."""
        story = VALID_REMOVAL_STORY.replace(
            "- Primary archetype: api-route-removal",
            "- Primary archetype: dead-code-removal",
        ).replace(
            "Required generated-contract evidence:\n\n- OpenAPI path absence\n- generated client/schema absence",
            "- Generated contract check: not applicable",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any("not applicable must include a reason" in error for error in errors)
        )

    def test_extract_acceptance_criteria(self) -> None:
        """L'extracteur retourne les AC avec leur preuve."""
        acs = extract_acceptance_criteria(VALID_STORY)
        self.assertEqual([item["ac"] for item in acs], ["AC1", "AC2"])
        self.assertIn("pytest", acs[1]["evidence"])


if __name__ == "__main__":
    unittest.main()
