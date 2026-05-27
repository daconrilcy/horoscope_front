# Story CS-339 aligner-provenance-audit-only-hors-prompt-llm-natal: Align Provenance Audit-Only Outside Natal LLM Prompt
Status: done

## Trigger / Source

Source brief: `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md`.

Mode selected: Repo-informed story.

Problem statement: `llm_astrology_input_v1` classifies hash provenance data as audit-only, but the natal LLM gateway currently renders
`provenance` in the prompt payload, exposing `projection_hash` and `llm_input_hash` to the generator.

Source stakes:

- User impact: the natal prompt must use rich astrological material without leaking audit hashes into generated content.
- Technical risk: the gateway can drift away from `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]`.
- Closure expectation: the runtime prompt projection matches the canonical prompt-visible roles.
- Forbidden regression: audit and persistence must still retain `projection_hash`, `llm_input_hash`, `contract_version`,
  `grounding_status`, and `evidence_refs`.

Source-alignment evidence: this story preserves all seven included scope items from the brief and keeps frontend, public API,
storage policy, provider calls, and hash semantic recalculation out of scope.

## Objective

Guarantee that no audit-only data from `llm_astrology_input_v1` is injected into the modern natal LLM prompt.

## Target State

- The gateway derives the natal prompt payload from `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]`.
- The prompt payload contains `facts`, `signals`, `limits`, `evidence`, and `shaping`.
- The prompt payload does not contain `provenance`, `projection_hash`, `llm_input_hash`, `provider_response`, or
  `persisted_answer`.
- Audit and persistence paths continue to read hashes and evidence metadata from the complete `llm_astrology_input_v1` object.
- Tests fail when gateway prompt projection and canonical data roles diverge.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-339`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted guardrail IDs `RG-002` and `RG-022` consulted.
- Evidence 4: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` - roles declare prompt-visible and audit-only data.
- Evidence 5: `backend/app/domain/llm/runtime/gateway.py` - current `LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS` includes `provenance`.
- Evidence 6: `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - current tests accept prompt provenance.
- Evidence 7: `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - current AST guard mirrors provenance as prompt-visible.
- Evidence 8: guardrail resolver command selected backend prompt-generation guardrails for this scope.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Runtime prompt projection for natal `llm_astrology_input_v1`.
  - Canonical role reuse from `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]`.
  - Boundary tests for prompt-visible versus audit-only data.
  - Audit and hash tests proving complete payload availability outside the prompt.
- Out of scope:
  - Frontend UI, public endpoints, database schema, auth, i18n, styling, build tooling, and migrations.
  - Real provider LLM calls.
  - Editorial prompt rewrites beyond removing reliance on non prompt-visible data.
  - Audit storage policy changes.
  - Recalculation semantics for `llm_input_hash`.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No reintroduction of `chart_json` or `natal_data` as a prompt carrier.
  - No alternate provenance projection unless a later user decision defines a redacted prompt-visible contract.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a backend runtime projection boundary between prompt-visible and audit-only data.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only the natal prompt projection boundary for `llm_astrology_input_v1`.
  - Keep audit, persistence, hash, and evidence metadata available outside the prompt.
  - Keep the prompt-visible block set limited to the canonical role list.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the implementation needs a redacted prompt-visible provenance contract.
- Additional validation rules:
  - AST guard proves the gateway imports or references the canonical prompt-visible role list.
  - Runtime prompt tests parse the rendered user payload before asserting keys.
  - Audit tests prove persisted model fields still receive hash and evidence values.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `TestClient` is not in scope; pytest and AST guard prove gateway runtime and architecture behavior. |
| Baseline Snapshot | yes | Prompt payload before and after artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Canonical ownership must stay in contract roles and gateway projection, not duplicated literals. |
| Allowlist Exception | no | No allowlist handling is authorized for this backend boundary update. |
| Contract Shape | yes | Prompt-visible and audit-only blocks have exact key membership rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Audit-only hash keys must stay out of the rendered prompt payload. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Gateway projection uses canonical roles. | Evidence profile: ast_architecture_guard; `pytest` runs `tests/architecture/test_llm_astrology_input_payload_boundaries.py`. |
| AC2 | Rendered prompt keeps prompt-visible blocks. | Evidence profile: json_contract_shape; `pytest` runs `tests/llm_orchestration/test_llm_astrology_input_boundaries.py`. |
| AC3 | Rendered prompt excludes audit-only keys. | Evidence profile: json_contract_shape; `pytest` runs `tests/llm_orchestration/test_llm_astrology_input_boundaries.py`. |
| AC4 | Audit persistence still receives hash metadata. | Evidence profile: json_contract_shape; `pytest` runs `tests/integration/llm/test_natal_llm_astrology_input_audit.py`. |
| AC5 | Existing hash behavior remains stable. | Evidence profile: json_contract_shape; `pytest -q backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py`. |
| AC6 | Legacy natal LLM guards still pass. | Evidence profile: no_legacy_contract; `pytest -q backend/tests/integration/test_llm_legacy_extinction.py --tb=short`. |
| AC7 | Evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks the story `evidence` directory. |

## Implementation Tasks

- [ ] Task 1: Import or reference `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]` in gateway prompt projection. (AC: AC1)
- [ ] Task 2: Remove `provenance` from the rendered natal prompt payload. (AC: AC2, AC3)
- [ ] Task 3: Update orchestration tests to assert canonical prompt-visible keys and audit-only key absence. (AC: AC2, AC3)
- [ ] Task 4: Update architecture guards so literals cannot diverge from the canonical role list. (AC: AC1, AC3)
- [ ] Task 5: Preserve audit and hash tests for complete `llm_astrology_input_v1` availability. (AC: AC4, AC5)
- [ ] Task 6: Run legacy extinction guards to prove no old natal prompt carrier returns. (AC: AC6)
- [ ] Task 7: Persist before and after prompt payload evidence for review. (AC: AC7)

## Files to Inspect First

- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py`
- `backend/tests/integration/test_llm_legacy_extinction.py`

## Runtime Source of Truth

- Primary source of truth:
  - `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]` in `llm_astrology_input_v1.py`.
  - Parsed rendered user payload from gateway tests.
  - AST guard over `gateway.py` and the architecture boundary test.
- Secondary evidence:
  - Targeted `rg` scan for `LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS`, `prompt_visible`, `audit_only`, hashes, and `provenance`.
- Static scans alone are not sufficient for this story because:
  - The rendered prompt payload must be parsed and asserted from runtime gateway composition.

## Contract Shape

- Contract type:
  - Backend runtime payload projection for natal LLM input.
- Fields:
  - `facts`: structured astrological facts.
  - `signals`: pre-narrative interpretive signals.
  - `limits`: missing data and limits visible to reduce invention.
  - `evidence`: compact grounding references visible to the prompt.
  - `shaping`: plan and editorial shaping material.
- Audit-only fields:
  - `provenance`: complete provenance block retained on the source payload.
  - `projection_hash`: retained for audit and persistence.
  - `llm_input_hash`: retained for audit and persistence.
  - `provider_response`: never prompt-visible through this contract.
  - `persisted_answer`: never prompt-visible through this contract.
- Required fields:
  - `facts`, `signals`, `limits`, `evidence`, and `shaping` in rendered prompt payload.
- Optional fields:
  - none for the rendered prompt block set.
- Status codes:
  - none; no public API route is changed.
- Serialization names:
  - Prompt payload keys are emitted as `facts`, `signals`, `limits`, `evidence`, and `shaping`.
- Frontend type impact:
  - none.
- Generated contract impact:
  - none; this is an internal runtime projection and test contract.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/evidence/prompt-payload-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/evidence/prompt-payload-after.json`
- Expected invariant:
  - The only intended prompt payload surface delta is removal of `provenance` and nested audit-only hash values.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Prompt-visible block list | `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]` | Duplicated literal tuple in `gateway.py` |
| Prompt projection rendering | `backend/app/domain/llm/runtime/gateway.py` | Contract builder or persistence model |
| Hash and provenance availability | `llm_astrology_input_v1` source payload and audit persistence tests | Rendered natal prompt payload |
| Boundary guard ownership | `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` | Ad hoc comments or manual-only review |

## Mandatory Reuse / DRY Constraints

- Reuse `LLM_ASTROLOGY_INPUT_DATA_ROLES["prompt_visible"]`; do not maintain a parallel prompt block list.
- Reuse existing gateway rendering helpers and boundary test utilities.
- Reuse existing hash and audit fixtures instead of creating a second payload fixture family.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy `chart_json` route back into natal prompt composition may be added.
- No compatibility path may preserve `provenance` in the rendered natal prompt.
- No fallback path may expose `projection_hash`, `llm_input_hash`, `provider_response`, or `persisted_answer` to prompt text.
- No alias, shim, or shadow constant may duplicate the canonical prompt-visible role list.
- The only allowed surface delta is the prompt projection boundary for `llm_astrology_input_v1`.

## Reintroduction Guard

- Guard exact forbidden prompt keys:
  - `provenance`
  - `projection_hash`
  - `llm_input_hash`
  - `provider_response`
  - `persisted_answer`
- Required deterministic guards:
  - `pytest -q backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
  - `pytest -q backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`
  - `rg -n "LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS|prompt_visible|audit_only|projection_hash|llm_input_hash|provenance" app tests`

## Regression Guardrails

Scope vector: operation `update`, domain `backend-domain`, paths `gateway.py`, `llm_astrology_input_v1.py`, backend boundary tests,
contracts `prompt-visible`, `audit-only`, and `llm_astrology_input_v1`.

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-002 `refactor-api-v1-routers` | Backend logic must not move into API routers. | Targeted `rg`; pytest boundary tests. |
| RG-022 `align-prompt-generation-story-validation-paths` | Prompt-generation validation paths must point to collected pytest files. | `pytest` commands in Validation Plan. |
| Registry gap | No exact guardrail exists for natal `llm_astrology_input_v1` audit-only prompt leakage. | Story AC3 and reintroduction guard cover it locally. |

Non-applicable examples:

- RG-047 is frontend TSX style scope and no frontend surface is touched.
- RG-052 is frontend CSS namespace scope and no style migration is touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before prompt payload | `evidence/prompt-payload-before.json` | Capture current rendered prompt keys. |
| After prompt payload | `evidence/prompt-payload-after.json` | Prove audit-only keys left the prompt. |
| Validation output | `_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/evidence/validation.txt` | Keep local command outcomes for review. |
| Review output | `_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this backend boundary update.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/llm/runtime/gateway.py` - derive prompt projection from canonical prompt-visible roles.
- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` - assert rendered prompt key membership and forbidden audit-only keys.
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` - assert no duplicated gateway block tuple can drift.
- `_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/evidence/prompt-payload-before.json` - persist baseline evidence.
- `_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/evidence/prompt-payload-after.json` - persist final evidence.
- `_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/evidence/validation.txt` - persist validation evidence.

Likely tests:

- `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`
- `backend/tests/integration/llm/test_natal_llm_astrology_input_audit.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_hash.py`
- `backend/tests/unit/domain/astrology/test_llm_astrology_input_evidence.py`
- `backend/tests/integration/test_llm_legacy_extinction.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope; no public endpoint is touched.
- `backend/app/infra/**` - out of scope; no persistence adapter or external client is touched.
- `backend/alembic/**` - out of scope; no database schema or migration is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

Run from repository root with the virtual environment active, then `cd backend`.

- VC1: `ruff format .`
- VC2: `ruff check .`
- VC3: `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py tests/unit/domain/astrology/test_llm_astrology_input_hash.py`
- VC4: `pytest -q tests/unit/domain/astrology/test_llm_astrology_input_evidence.py tests/llm_orchestration/test_llm_astrology_input_boundaries.py`
- VC5: `pytest -q tests/architecture/test_llm_astrology_input_payload_boundaries.py tests/integration/test_llm_legacy_extinction.py --tb=short`
- VC6: `pytest -q tests/integration/llm/test_natal_llm_astrology_input_audit.py --tb=short`
- VC7: `pytest -q tests --tb=short`
- VC8: `rg -n "LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS|prompt_visible|audit_only|projection_hash|llm_input_hash|provenance" app tests`
- VC9: `python -c "from pathlib import Path; assert Path('../_condamad/stories/CS-339-aligner-provenance-audit-only-hors-prompt-llm-natal/evidence').exists()"`

## Regression Risks

- Removing `provenance` from prompt rendering could accidentally remove hashes from audit persistence.
- Replacing the gateway tuple with a canonical import could create import-cycle risk.
- Tests can pass at the contract-builder level while rendered prompt text still leaks audit-only keys.
- Historical guard scans can be noisy; classify residual hits by active prompt path versus source/audit/test evidence.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all Python commands inside the activated virtual environment.
- Keep file comments and public or non-trivial docstrings in French for application or test files changed.
- Do not add inline frontend styles; frontend is out of scope.

## References

- `_story_briefs/cs-339-aligner-provenance-audit-only-hors-prompt-llm-natal.md`
- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_story_briefs/cs-333-aligner-hash-evidence-et-audit-entree-llm-astrologique.md`
- `_story_briefs/cs-335-ajouter-guards-non-invention-et-frontieres-payload-llm.md`
- `_story_briefs/cs-338-cloturer-extinction-legacy-injection-llm-natale.md`
- `_condamad/reports/cs-330-cs-331-cs-332-cs-333-cs-334-cs-335-cs-336-cs-337-cs-338-delivery-report.md`
- `_condamad/reports/extinction-legacy-injection-llm-natale/2026-05-27-0000/validation-extinction-legacy.md`
- `_condamad/stories/regression-guardrails.md`
