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

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | No runtime route, config, generated contract, persistence, or architecture rule is affected. |
| Baseline Snapshot | yes | Import convergence must preserve behavior and compare before/after import inventory. |
| Ownership Routing | yes | Billing application use cases must stay in the canonical services namespace. |
| Allowlist Exception | no | No exception is allowed for old root imports. |
| Contract Shape | no | No API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected. |
| Batch Migration | yes | Consumers must migrate by bounded import batches. |
| Reintroduction Guard | yes | The old root import must fail if reintroduced. |
| Persistent Evidence | yes | Baseline and after import inventories must be persisted. |

## 4a. Runtime Source of Truth

- Runtime source of truth: not applicable
- Reason: no runtime route, config, generated contract, persistence, or architecture rule is affected.

## 4b. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/test-story/billing-imports-before.txt`
- Comparison after implementation:
  - `_condamad/stories/test-story/billing-imports-after.txt`
- Expected invariant:
  - Runtime billing behavior remains unchanged while imports converge.

## 4c. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Application use case | `services/**` | `api/**` |

## 4d. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4d. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Billing imports | `backend/app/services/quota_usage_service.py` | `backend/app/services/billing/quota_runtime.py` | Backend service consumers | `backend/app/tests/unit/test_billing_imports.py` | `rg "app.services.quota_usage_service" backend/app backend/tests` returns no nominal import. | External consumer evidence appears. |

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4e. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Import baseline | `_condamad/stories/test-story/billing-imports-before.txt` | Proves the migration baseline before convergence. |

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

## 10a. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the
removed surface is reintroduced.

The guard must check at least one deterministic source:

- forbidden symbols

Required forbidden examples:

- `backend/app/services/quota_usage_service.py`

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q backend/app/tests/unit/test_billing_imports.py` checks `backend/app/services/quota_usage_service.py`.

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

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q backend/app/tests/unit/test_api_router_architecture.py` checks `/v1/ai`.

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
    .replace("- Replacement allowed: yes", "- Replacement allowed: no")
    .replace(
        "- Runtime source of truth: not applicable\n- Reason: no runtime route, config, generated contract, persistence, or architecture rule is affected.",
        "- Primary source of truth:\n  - `app.openapi()` runtime schema and `app.routes` route table.\n- Secondary evidence:\n  - Targeted `rg` scans for removed route symbols.\n- Static scans alone are not sufficient for this story because:\n  - Router registration and OpenAPI exposure are runtime outcomes.",
    )
    .replace(
        "| Runtime Source of Truth | no | No runtime route, config, generated contract, persistence, or architecture rule is affected. |\n"
        "| Baseline Snapshot | yes | Import convergence must preserve behavior and compare before/after import inventory. |\n"
        "| Ownership Routing | yes | Billing application use cases must stay in the canonical services namespace. |\n"
        "| Allowlist Exception | no | No exception is allowed for old root imports. |\n"
        "| Contract Shape | no | No API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected. |\n"
        "| Batch Migration | yes | Consumers must migrate by bounded import batches. |\n"
        "| Reintroduction Guard | yes | The old root import must fail if reintroduced. |\n"
        "| Persistent Evidence | yes | Baseline and after import inventories must be persisted. |",
        "| Runtime Source of Truth | yes | API route exposure is runtime-visible. |\n"
        "| Baseline Snapshot | yes | Route contract must be compared before and after removal. |\n"
        "| Ownership Routing | no | No responsibility move is required for the route deletion. |\n"
        "| Allowlist Exception | no | No exception is allowed for historical facade routes. |\n"
        "| Contract Shape | yes | OpenAPI route and response exposure must be explicit. |\n"
        "| Batch Migration | no | No multi-batch consumer migration is required. |\n"
        "| Reintroduction Guard | yes | Removed route prefixes must fail if reintroduced. |\n"
        "| Persistent Evidence | yes | Route audit and OpenAPI snapshots must be persisted. |",
    )
    .replace(
        "## 4c. Ownership Routing Rule\n\n"
        "| Responsibility type | Canonical owner | Forbidden destination |\n"
        "|---|---|---|\n"
        "| Application use case | `services/**` | `api/**` |",
        "## 4c. Ownership Routing Rule\n\n"
        "- Ownership routing: not applicable\n"
        "- Reason: no responsibility moves or boundary rules are affected.",
    )
    .replace(
        "## 4d. Batch Migration Plan\n\n"
        "| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |\n"
        "|---|---|---|---|---|---|---|\n"
        '| Billing imports | `backend/app/services/quota_usage_service.py` | `backend/app/services/billing/quota_runtime.py` | Backend service consumers | `backend/app/tests/unit/test_billing_imports.py` | `rg "app.services.quota_usage_service" backend/app backend/tests` returns no nominal import. | External consumer evidence appears. |\n\n'
        "## 4f. Contract Shape\n\n"
        "- Contract shape: not applicable\n"
        "- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.",
        "## 4d. Batch Migration Plan\n\n"
        "- Batch migration plan: not applicable\n"
        "- Reason: no multi-surface or multi-consumer migration is required.\n\n"
        "## 4f. Contract Shape\n\n"
        "- Contract type:\n"
        "  - OpenAPI route exposure\n"
        "- Fields:\n"
        "  - Route path and method entries for `/v1/ai/*` are removed.\n"
        "- Required fields:\n"
        "  - Remaining canonical route fields stay unchanged.\n"
        "- Optional fields:\n"
        "  - No optional legacy route fields remain.\n"
        "- Status codes:\n"
        "  - Removed routes produce no OpenAPI operation.\n"
        "- Serialization names:\n"
        "  - No legacy serialization names remain.\n"
        "- Frontend type impact:\n"
        "  - First-party frontend consumers use canonical generated types only.\n"
        "- Generated contract impact:\n"
        "  - `app.openapi()` no longer exposes `/v1/ai/*` paths.",
    )
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

    def test_ready_for_review_story_passes(self) -> None:
        """Une story livree pour revue reste valide structurellement."""
        story = VALID_STORY.replace(
            "Status: ready-for-dev",
            "Status: ready-for-review",
        )
        self.assertEqual(validate_story(self.write_story(story)), [])

    def test_unknown_status_fails(self) -> None:
        """Un statut hors cycle CONDAMAD connu est refuse."""
        story = VALID_STORY.replace("Status: ready-for-dev", "Status: completed")
        errors = validate_story(self.write_story(story))
        self.assertTrue(any("Story status must be one of" in error for error in errors))

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

    def test_runtime_ac_with_rg_only_fails(self) -> None:
        """Une preuve rg seule ne suffit pas pour un contrat runtime."""
        story = VALID_STORY.replace(
            "Consumers import billing services from `backend/app/services/billing` only.",
            "Runtime API route `/v1/billing` is absent from OpenAPI.",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(any("touches a runtime contract" in error for error in errors))

    def test_baseline_required_for_convergence(self) -> None:
        """Une convergence doit definir un baseline before/after."""
        story = VALID_STORY.replace(
            "## 4b. Baseline / Before-After Rule",
            "## 4b. Missing Baseline Rule",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(any("Baseline-triggering story" in error for error in errors))

    def test_allowlist_wildcard_fails(self) -> None:
        """Une allowlist ne peut pas accepter de wildcard."""
        story = VALID_STORY.replace(
            "Consumers import billing services from `backend/app/services/billing` only.",
            "One allowlist exception is documented for old billing root imports.",
        ).replace(
            "## 4e. Persistent Evidence Artifacts",
            "## 4d. Allowlist / Exception Register\n\n"
            "| File | Symbol / Route / Import | Reason | Expiry or permanence decision |\n"
            "|---|---|---|---|\n"
            "| `backend/app/**` | `*` | broad migration escape hatch | temporary |\n\n"
            "## 4e. Persistent Evidence Artifacts",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(any("must not use wildcards" in error for error in errors))

    def test_delete_only_replacement_contradiction_fails(self) -> None:
        """Delete-only et replacement autorise ne peuvent pas coexister."""
        story = VALID_REMOVAL_STORY.replace(
            "- Replacement allowed: no", "- Replacement allowed: yes"
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(any("Replacement allowed is yes" in error for error in errors))

    def test_persistent_evidence_required_for_baseline(self) -> None:
        """Un baseline actif doit produire un artefact persistant."""
        story = VALID_STORY.replace(
            "## 4e. Persistent Evidence Artifacts",
            "## 4e. Missing Persistent Evidence Artifacts",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(any("Persistent evidence story" in error for error in errors))

    def test_api_contract_story_without_contract_shape_fails(self) -> None:
        """Une story de contrat API doit materialiser Contract Shape."""
        story = (
            VALID_STORY.replace(
                "- Primary archetype: namespace-convergence",
                "- Primary archetype: api-contract-change",
            )
            .replace(
                "| Runtime Source of Truth | no | No runtime route, config, generated contract, persistence, or architecture rule is affected. |",
                "| Runtime Source of Truth | yes | OpenAPI exposure is runtime-visible. |",
            )
            .replace(
                "| Contract Shape | no | No API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected. |",
                "| Contract Shape | yes | API payload shape must be explicit. |",
            )
            .replace(
                "- Runtime source of truth: not applicable\n- Reason: no runtime route, config, generated contract, persistence, or architecture rule is affected.",
                "- Primary source of truth:\n  - `app.openapi()` runtime schema.\n- Secondary evidence:\n  - Targeted `rg` scans.\n- Static scans alone are not sufficient for this story because:\n  - OpenAPI exposure is runtime-visible.",
            )
            .replace("## 4f. Contract Shape", "## 4f. Missing Contract Shape")
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any("Contract Shape story missing" in error for error in errors)
        )

    def test_batch_migration_without_batch_plan_fails(self) -> None:
        """Une migration par lots doit materialiser Batch Migration Plan."""
        story = VALID_STORY.replace(
            "## 4d. Batch Migration Plan", "## 4d. Missing Batch Migration Plan"
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any("Batch migration story missing" in error for error in errors)
        )

    def test_required_contracts_missing_fails(self) -> None:
        """Les contrats requis doivent etre persistés dans la story."""
        story = VALID_STORY.replace(
            "## 4a. Required Contracts", "## 4a. Missing Contracts"
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any(
                "Missing required section: Required Contracts" in error
                for error in errors
            )
        )

    def test_required_contract_yes_with_not_applicable_section_fails(self) -> None:
        """Un contrat yes ne peut pas pointer vers une section N/A."""
        story = VALID_STORY.replace(
            "| Runtime Source of Truth | no | No runtime route, config, generated contract, persistence, or architecture rule is affected. |",
            "| Runtime Source of Truth | yes | Runtime truth is required. |",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any("marked yes but section is not applicable" in error for error in errors)
        )

    def test_required_contract_no_with_active_section_fails(self) -> None:
        """Un contrat no doit avoir une section N/A avec Reason."""
        story = VALID_STORY.replace(
            "| Baseline Snapshot | yes | Import convergence must preserve behavior and compare before/after import inventory. |",
            "| Baseline Snapshot | no | Baseline is disabled. |",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any("marked no but section is active" in error for error in errors)
        )

    def test_allowlist_required_by_archetype_requires_active_register(self) -> None:
        """Un contrat allowlist requis ne peut pas rester N/A."""
        story = (
            VALID_STORY.replace(
                "- Primary archetype: namespace-convergence",
                "- Primary archetype: api-error-contract-centralization",
            )
            .replace(
                "| Runtime Source of Truth | no | No runtime route, config, generated contract, persistence, or architecture rule is affected. |",
                "| Runtime Source of Truth | yes | Runtime API error behavior is observable. |",
            )
            .replace(
                "| Allowlist Exception | no | No exception is allowed for old root imports. |",
                "| Allowlist Exception | yes | API error centralization requires narrow exceptions. |",
            )
            .replace(
                "| Contract Shape | no | No API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected. |",
                "| Contract Shape | yes | HTTP error shape must be explicit. |",
            )
            .replace(
                "| Batch Migration | yes | Consumers must migrate by bounded import batches. |",
                "| Batch Migration | no | No multi-batch migration is required. |",
            )
            .replace(
                "| Persistent Evidence | yes | Baseline and after import inventories must be persisted. |",
                "| Persistent Evidence | no | No persisted evidence is required. |",
            )
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any(
                "Allowlist Exception" in error and "not applicable" in error
                for error in errors
            )
        )

    def test_reintroduction_guard_required_by_archetype_requires_active_guard(
        self,
    ) -> None:
        """Un contrat reintroduction yes exige un guard actif executable."""
        story = VALID_STORY.replace(
            "## 10a. Reintroduction Guard",
            "## 10a. Missing Reintroduction Guard",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any(
                "Reintroduction Guard" in error and "missing" in error
                for error in errors
            )
        )

    def test_required_contracts_must_list_every_known_contract(self) -> None:
        """La table Required Contracts doit etre exhaustive."""
        story = VALID_STORY.replace(
            "| Contract Shape | no | No API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected. |\n",
            "",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any(
                "must list every known contract: Contract Shape" in error
                for error in errors
            )
        )

    def test_required_contracts_unknown_contract_fails(self) -> None:
        """La table Required Contracts refuse les noms inconnus."""
        story = VALID_STORY.replace(
            "| Contract Shape | no | No API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected. |",
            "| Unknown Contract | no | Unknown contract should fail. |",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(any("unknown contract" in error for error in errors))

    def test_required_contracts_duplicate_contract_fails(self) -> None:
        """La table Required Contracts refuse les doublons."""
        story = VALID_STORY.replace(
            "| Persistent Evidence | yes | Baseline and after import inventories must be persisted. |",
            "| Persistent Evidence | yes | Baseline and after import inventories must be persisted. |\n"
            "| Persistent Evidence | yes | Duplicate row. |",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(any("duplicate contract row" in error for error in errors))

    def test_runtime_profile_with_rg_only_fails(self) -> None:
        """Un profil runtime avec seulement rg reste insuffisant."""
        story = VALID_STORY.replace(
            'Consumers import billing services from `backend/app/services/billing` only. | `rg "app.services.quota_usage_service" backend/app backend/tests` returns no nominal import.',
            'Runtime API route `/v1/billing` is absent from OpenAPI. | Evidence profile: `runtime_openapi_contract`; `rg "/v1/billing" backend/app` returns no nominal route.',
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(any("touches a runtime contract" in error for error in errors))

    def test_allowlist_not_applicable_reason_does_not_trigger_allowlist(self) -> None:
        """Une phrase negative sur exception register ne declenche pas l'allowlist."""
        story = VALID_STORY.replace(
            "Proves the migration baseline before convergence.",
            "Proves the migration baseline before convergence; no allowlist or exception register is required.",
        )
        self.assertFalse(
            any(
                "Allowlist / Exception Register" in error
                for error in validate_story(self.write_story(story))
            )
        )

    def test_reintroduction_guard_without_command_or_test_fails(self) -> None:
        """Un guard purement declaratif ne suffit pas."""
        story = VALID_REMOVAL_STORY.replace(
            "\nGuard evidence:\n\n"
            "- Evidence profile: `reintroduction_guard`; `pytest -q backend/app/tests/unit/test_api_router_architecture.py` checks `/v1/ai`.\n",
            "",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(
            any("Reintroduction Guard must include" in error for error in errors)
        )

    def test_behavior_change_constrained_requires_constraints(self) -> None:
        """Behavior change constrained doit borner le changement autorise."""
        story = VALID_STORY.replace(
            "- Behavior change allowed: no",
            "- Behavior change allowed: constrained",
        )
        errors = validate_story(self.write_story(story))
        self.assertTrue(any("Behavior change constraints" in error for error in errors))

    def test_legacy_guard_story_does_not_trigger_removal_contract(self) -> None:
        """Une story guard mentionnant legacy sans cible de suppression reste non-removal."""
        story = (
            VALID_STORY.replace(
                "Constrain service imports to the canonical billing namespace and prove that old imports are absent.",
                "Add an architecture guard against legacy fallback reintroduction without changing runtime behavior.",
            )
            .replace(
                "- Primary archetype: namespace-convergence",
                "- Primary archetype: test-guard-hardening",
            )
            .replace(
                "| Runtime Source of Truth | no | No runtime route, config, generated contract, persistence, or architecture rule is affected. |\n"
                "| Baseline Snapshot | yes | Import convergence must preserve behavior and compare before/after import inventory. |\n"
                "| Ownership Routing | yes | Billing application use cases must stay in the canonical services namespace. |\n"
                "| Allowlist Exception | no | No exception is allowed for old root imports. |\n"
                "| Contract Shape | no | No API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected. |\n"
                "| Batch Migration | yes | Consumers must migrate by bounded import batches. |\n"
                "| Reintroduction Guard | yes | The old root import must fail if reintroduced. |\n"
                "| Persistent Evidence | yes | Baseline and after import inventories must be persisted. |",
                "| Runtime Source of Truth | yes | AST architecture guard is the runtime-equivalent source for import boundaries. |\n"
                "| Baseline Snapshot | yes | Guard hardening must preserve import behavior. |\n"
                "| Ownership Routing | no | No responsibility move is required. |\n"
                "| Allowlist Exception | yes | The guard must document whether exceptions are allowed. |\n"
                "| Contract Shape | no | No API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected. |\n"
                "| Batch Migration | no | No multi-batch migration is required. |\n"
                "| Reintroduction Guard | yes | Legacy fallback reintroduction must fail. |\n"
                "| Persistent Evidence | yes | Guard baseline evidence must be persisted.",
            )
            .replace(
                "- Runtime source of truth: not applicable\n- Reason: no runtime route, config, generated contract, persistence, or architecture rule is affected.",
                "- Primary source of truth:\n  - AST guard over billing imports.\n- Secondary evidence:\n  - Targeted `rg` scans for legacy fallback symbols.\n- Static scans alone are not sufficient for this story because:\n  - Import boundary validity is enforced by an architecture guard.",
            )
            .replace(
                "## 4d. Allowlist / Exception Register\n\n"
                "- Allowlist / exception register: not applicable\n"
                "- Reason: no exception is allowed by this story.",
                "## 4d. Allowlist / Exception Register\n\n"
                "| File | Symbol / Route / Import | Reason | Expiry or permanence decision |\n"
                "|---|---|---|---|\n"
                "| `backend/app/tests/unit/test_billing_imports.py` | `backend/app/services/quota_usage_service.py` | Test guard fixture references the forbidden import string. | Permanent test fixture decision. |",
            )
            .replace(
                "## 4c. Ownership Routing Rule\n\n"
                "| Responsibility type | Canonical owner | Forbidden destination |\n"
                "|---|---|---|\n"
                "| Application use case | `services/**` | `api/**` |",
                "## 4c. Ownership Routing Rule\n\n"
                "- Ownership routing: not applicable\n"
                "- Reason: no responsibility moves or boundary rules are affected.",
            )
            .replace(
                "## 4d. Batch Migration Plan\n\n"
                "| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |\n"
                "|---|---|---|---|---|---|---|\n"
                '| Billing imports | `backend/app/services/quota_usage_service.py` | `backend/app/services/billing/quota_runtime.py` | Backend service consumers | `backend/app/tests/unit/test_billing_imports.py` | `rg "app.services.quota_usage_service" backend/app backend/tests` returns no nominal import. | External consumer evidence appears. |',
                "## 4d. Batch Migration Plan\n\n"
                "- Batch migration plan: not applicable\n"
                "- Reason: no multi-surface or multi-consumer migration is required.",
            )
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
        ).replace(
            "## 10a. Reintroduction Guard",
            "## 10a. Missing Reintroduction Guard",
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

    def test_skill_package_has_no_python_cache_artifacts(self) -> None:
        """Le skill ne doit pas contenir d'artefacts Python generes."""
        skill_dir = SCRIPT_DIR.parent
        forbidden = [
            path
            for path in skill_dir.rglob("*")
            if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}
        ]
        self.assertEqual(forbidden, [])


if __name__ == "__main__":
    unittest.main()
