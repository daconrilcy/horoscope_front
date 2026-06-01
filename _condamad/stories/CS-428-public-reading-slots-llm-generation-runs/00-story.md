# Story CS-428 public-reading-slots-llm-generation-runs: Public Reading Slots And LLM Generation Runs
Status: ready-to-review

## Trigger / Source

Brief direct, repo-informed story compiled from `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md`.

Source problem: public natal readings currently share persistence concerns with LLM technical attempts, so a rejected provider result,
a retry, a fallback, or a concurrent generation can drift toward public state mutation.

Source-alignment review: the story preserves the brief stakes by separating public slots from LLM runs, proving accepted-only reads,
SQLite idempotence, concurrency control, `client_request_id`, quota-on-acceptance, and the CS-427 product key dimensions.

## Objective

Create backend persistence for `ThemeNatalReadingSlot` and `LlmGenerationRun` so public accepted readings are structurally distinct
from technical generation attempts.

## Target State

- `ThemeNatalReadingSlot` owns the public reading lifecycle for theme natal slots.
- `LlmGenerationRun` records each technical generation attempt without owning public visibility.
- The slot uniqueness key includes `user_id`, `chart_id`, `feature`, `reading_kind`, `product_plan`, `output_variant`,
  `persona_profile_id`, and `contract_version`.
- Public GET/list behavior reads only slots with status `accepted`.
- SQLite proves idempotence by unique constraint, transaction, and explicit `IntegrityError` handling.
- DB engines with row locking may add a `SELECT FOR UPDATE`-style row lock or an application lock as a complementary guard.
- Provider calls, prompt creation, frontend cutover, legacy deletion, and mass migration remain out of scope.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `ThemeNatalReadingSlot` | in scope | AC1, AC3, AC4, Task 1, Task 2 |
| `LlmGenerationRun` | in scope | AC2, AC9, AC10, Task 1, Task 3 |
| DB migrations/tables | in scope | AC1, AC2, AC3, VC3, Task 2 |
| Slot uniqueness dimensions | in scope | AC3, AC11, Task 2, VC9 |
| Slot statuses | in scope | AC4, Task 1, Task 2 |
| Idempotence/concurrency | in scope | AC7, AC8, AC9, AC10, Task 4 |
| Lock strategy | in scope | AC7, Task 4, VC4 |
| `client_request_id` | in scope | AC9, AC10, Task 3, VC7 |
| Accepted-only public reads | in scope | AC6, Task 5, VC4 |
| CS-427 product decision | dependency | Files to Inspect First, Ownership Routing, References |
| Provider call | out of scope | Non-goals |
| New prompt | out of scope | Non-goals |
| Frontend cutover | out of scope | Non-goals |
| Physical legacy deletion | out of scope | Non-goals |
| Mass migration | out of scope | Batch Migration Plan |

## Current State Evidence

- Evidence 1: `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-428`.
- Evidence 3: `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - slot/run target read.
- Evidence 4: `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md` - product contract dependency read.
- Evidence 5: `backend/app/infra/db/models/user_natal_interpretation.py` - current mixed persistence model inspected.
- Evidence 6: `backend/app/services/llm_generation/natal/interpretation_service.py` - current cache/write paths inspected.
- Evidence 7: `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - public rejection boundary tests inspected.
- Evidence 8: `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` - quota-on-acceptance tests inspected.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - targeted guardrail IDs read, not the full registry.
- Evidence 10: `resolve_guardrails.py` - scope vector used with backend DB, service, test, idempotence, quota, and no-legacy contracts.
- Repository structure note: `backend`, `backend/app/infra/db`, `backend/migrations`, `backend/tests/integration`, and `backend/tests/unit` exist.

## Domain Boundary

- Domain: backend-persistence
- In scope:
  - Backend SQLAlchemy models for public theme natal slots and LLM generation runs.
  - Schema migration under the existing `backend/migrations` root.
  - Service-level slot claim, idempotence, accepted-only public lookup, and quota-on-acceptance integration.
  - Backend tests for schema, idempotence, concurrency, public reads, and quota.
- Out of scope:
  - Frontend UI, provider calls, prompt authoring, mass migration, auth changes, i18n, styling, and build tooling.
  - Physical deletion of `UserNatalInterpretationModel` or historical rows.
- Explicit non-goals:
  - No frontend route, screen, client generation, or UI validation.
  - No new prompt, provider integration, or provider response parser.
  - No mass backfill of historical interpretations.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend persistence and concurrency contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only theme natal public slot and LLM generation run persistence behavior.
  - Public reads expose only accepted public slots.
  - Failed or rejected technical runs do not mutate an accepted public slot.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-427 product dimensions are unavailable as backend contract names during implementation.
- Additional validation rules:
  - `AST guard` or focused `rg` must prove new tests do not import `SessionLocal` or `engine` directly.
  - `pytest -q backend/tests/integration -k "theme_natal and slot" --tb=short` must cover SQLite idempotence.
  - `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short` must cover quota after acceptance.
  - DB schema evidence must include unique constraints for slot identity and `client_request_id` idempotence.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, DB schema inspection, and `AST guard` prove persistence behavior. |
| Baseline Snapshot | yes | Before/after schema artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Slot/run persistence must not be hidden in API, frontend, or provider code. |
| Allowlist Exception | no | No allowlist handling is authorized for this persistence story. |
| Contract Shape | yes | Slot and run fields, statuses, keys, and JSON visibility are exact contracts. |
| Batch Migration | no | No mass conversion of historical interpretation rows is in scope. |
| Reintroduction Guard | yes | Mixed public/run writes must not return as the canonical path. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `ThemeNatalReadingSlot` stores public slot state. | Evidence profile: json_contract_shape; pytest integration slot tests. |
| AC2 | `LlmGenerationRun` stores technical attempt state. | Evidence profile: json_contract_shape; pytest integration slot tests. |
| AC3 | Slot identity is DB-unique on the full product key. | Evidence profile: json_contract_shape; AST guard; pytest slot tests. |
| AC4 | Slot status is constrained to the approved lifecycle. | Evidence profile: json_contract_shape; pytest integration slot tests. |
| AC5 | Rejected run leaves payload unchanged. | Evidence profile: no_legacy_contract; pytest rejected boundary. |
| AC6 | Public GET/list sees accepted slots only. | Evidence profile: json_contract_shape; pytest integration slot tests. |
| AC7 | Concurrent claims create one slot per product key. | Evidence profile: runtime_openapi_contract; pytest integration slot tests. |
| AC8 | Concurrent accepted persistence consumes one quota unit. | Evidence profile: runtime_openapi_contract; pytest quota acceptance. |
| AC9 | Reused `client_request_id` returns the same logical state. | Evidence profile: runtime_openapi_contract; pytest integration slot tests. |
| AC10 | Reused `client_request_id` creates no extra run. | Evidence profile: runtime_openapi_contract; pytest integration slot tests. |
| AC11 | `chart_id` participates in slot identity. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "chart_id" backend/app backend/tests`. |
| AC12 | `created_at` is immutable; `accepted_at` changes only on acceptance. | Evidence profile: baseline_before_after_diff; pytest slot tests. |

## Implementation Tasks

- [ ] Task 1: Define slot and run domain statuses with explicit public visibility semantics. (AC: AC1, AC2, AC4)
- [ ] Task 2: Add SQLAlchemy models and migration tables under the canonical backend DB ownership. (AC: AC1, AC2, AC3, AC11)
- [ ] Task 3: Persist `client_request_id` idempotence on the run or a dedicated idempotence table. (AC: AC9, AC10)
- [ ] Task 4: Implement slot claim/update logic with transaction, unique constraint, `IntegrityError` handling, and row/app lock. (AC: AC7)
- [ ] Task 5: Route public lookup/list behavior through accepted-slot filtering. (AC: AC5, AC6, AC12)
- [ ] Task 6: Keep quota consumption after accepted slot publication. (AC: AC8)
- [ ] Task 7: Add integration and unit tests for schema, public boundary, idempotence, concurrency, and quota. (AC: AC1, AC6, AC7, AC8, AC9, AC10)
- [ ] Task 8: Persist evidence artifacts for schema, scans, and validation output. (AC: AC3, AC11, AC12)

## Files to Inspect First

- `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md` - source brief.
- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md` - product dimensions dependency.
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - target architecture.
- `_condamad/stories/regression-guardrails.md` - targeted guardrail IDs.
- `backend/app/infra/db/models/user_natal_interpretation.py` - current mixed persistence.
- `backend/app/infra/db/models/__init__.py` - model export ownership.
- `backend/migrations` - existing migration root.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - current generation write path.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - public boundary coverage.
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` - quota acceptance coverage.

## Runtime Source of Truth

- Primary source of truth:
  - SQLAlchemy metadata, migrated SQLite schema, targeted `pytest`, and `AST guard`.
- Secondary evidence:
  - Targeted `rg` scans for slot/run symbols, idempotence symbols, and mixed legacy selectors.
- Static scans alone are not sufficient for this story because:
  - Concurrency, SQLite uniqueness, and accepted-only public reads must be proven through executed tests.

## Contract Shape

- Contract type:
  - Backend persistence models, service behavior, and DB schema.
- Fields:
  - Slot fields:
  - `user_id`: required owner identifier.
  - `chart_id`: required chart identity dimension.
  - `feature`: required feature code, expected `theme_natal`.
  - `reading_kind`: required product reading kind.
  - `product_plan`: required backend-resolved plan.
  - `output_variant`: required output variant from CS-427.
  - `persona_profile_id`: nullable persona dimension.
  - `contract_version`: required immutable public contract version.
  - `status`: one of `empty`, `generating`, `accepted`, `rejected`, `failed_retriable`, `superseded`.
  - `public_payload`: visible only for accepted public slots.
  - `accepted_at`: set only on accepted public publication.
  - `source_generation_run_id`: points to the accepted source run.
  - Run fields:
  - `slot_id`: required slot relation.
  - `client_request_id`: required idempotence token for client-triggered generation.
  - `status`: technical generation state.
  - `raw_provider_response`: technical trace, not public output.
  - `parsed_raw_response`: technical trace, not public output.
  - `validation_errors`: technical rejection evidence.
  - `rejection_reason`: technical rejection reason.
  - `prompt_hash`, `data_hash`, `engine_profile_version`, `output_schema_version`: technical reproducibility metadata.
- Required fields:
  - Slot identity key fields, `status`, `created_at`, and run relation fields.
- Optional fields:
  - `persona_profile_id`, rejected-run technical traces, and accepted publication metadata before acceptance.
- Status codes:
  - none; this story does not define an API route.
- Serialization names:
  - DB column names use the snake_case names listed in `Fields:`.
- Frontend type impact:
  - none; no frontend generated client or TypeScript type is in scope.
- Generated contract impact:
  - migrated SQLAlchemy metadata must expose slot and run tables with the declared fields.
- Public serialization impact:
  - Public GET/list must use accepted slots only and must not serialize raw provider traces.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/evidence/schema-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/evidence/schema-after.txt`
- Expected invariant:
  - The only intended persistence surface delta is new slot/run schema and service integration for theme natal readings.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Public slot model | `backend/app/infra/db/models/theme_natal_reading_slot.py` | frontend or API router modules |
| LLM run model | `backend/app/infra/db/models/llm_generation_run.py` | public response schemas |
| Slot orchestration | `backend/app/services/llm_generation/natal` | provider gateway client |
| Migration | `backend/migrations` | ad hoc SQL in UI or service methods |
| Tests | `backend/tests/integration` and `backend/tests/unit` | generated story-only test names |

## Mandatory Reuse / DRY Constraints

- Reuse CS-427 product dimensions for `feature`, `reading_kind`, `product_plan`, `output_variant`, persona, and contract version.
- Reuse existing backend DB base, session fixtures, migration style, and quota services.
- Do not duplicate public payload validation logic inside the persistence model.
- Do not create a second interpretation formatter for the same public response.
- Keep helper functions small and named after slot claim, run creation, accepted publication, and public lookup responsibilities.

## No Legacy / Forbidden Paths

- No legacy persistence owner may become the canonical slot/run model.
- No compatibility table, view, or facade may mirror the old mixed interpretation table.
- No fallback write path may update an accepted public payload from a failed or rejected run.
- `UserNatalInterpretationModel` may remain only as existing historical persistence outside the new slot/run ownership.
- New public slot reads must not infer public state from raw LLM run rows.

## Reintroduction Guard

- Forbidden symbols or patterns:
  - New canonical slot identity implemented only with `UserNatalInterpretationModel.user_id` plus `level`.
  - Public GET/list behavior reading rejected, failed, or raw technical run payloads.
  - Quota debit before accepted slot publication.
- Required guards:
  - `pytest -q backend/tests/integration -k "theme_natal and slot" --tb=short`.
  - `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short`.
  - `rg -n "client_request_id|idempot" backend/app backend/tests`.
  - `rg -n "UserNatalInterpretationModel\\.user_id == user_id,[\\s\\S]*UserNatalInterpretationModel\\.level" backend/app/services/llm_generation/natal`.

## Regression Guardrails

Scope vector: create, backend-persistence, backend-services, `backend/migrations`, SQLite idempotence, public accepted-only boundary,
quota-on-acceptance, no-legacy.

Applicable guardrails:

| Guardrail | scope -> invariant -> evidence |
|---|---|
| RG-011 `converge-db-test-fixtures` | backend tests -> canonical DB fixtures -> `AST guard` plus targeted `pytest`. |
| RG-150 `CS-384-separer-interpretations-natales-acceptees-rejets-llm` | public persistence -> rejected rows hidden -> integration `pytest`. |
| RG-152 `CS-392-implementer-generation-narrative-natal-reading-v1` | public payload -> no technical leaks -> boundary `pytest` and `rg`. |
| RG-155 `CS-396-refuser-padding-semantique-lecture-natale-et-sources-vides` | accepted payload -> no padding publication -> integration `pytest`. |
| RG-157 `CS-398-rendre-quota-natal-complete-transactionnel-et-remedier-lectures-invalides` | quota -> debit after acceptance -> quota `pytest`. |
| RG-168 `CS-409-contrats-versionnes-lecture-natale-basic-v2` | Basic public contract -> strict public shape -> contract `pytest` and `rg`. |

Needs-investigation and registry gaps:

- Registry gap: no exact `ThemeNatalReadingSlot` or `LlmGenerationRun` guardrail exists in the registry yet.
- Adjacent only: `RG-002` applies only if implementation edits API routers for public GET/list wiring.
- Non-applicable examples: `RG-047` frontend inline styles and `RG-052` frontend CSS namespaces are outside this backend story.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Schema before | `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/evidence/schema-before.txt` | Capture pre-change schema. |
| Schema after | `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/evidence/schema-after.txt` | Capture new slot/run schema. |
| Validation output | `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/evidence/validation.txt` | Keep final validation output. |
| Guard scans | `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/evidence/guard-scans.txt` | Keep targeted scan output. |
| Review output | `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling is authorized for this story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion of historical rows is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/infra/db/models/theme_natal_reading_slot.py` - define public slot persistence.
- `backend/app/infra/db/models/llm_generation_run.py` - define technical generation run persistence.
- `backend/app/infra/db/models/__init__.py` - export the new models for metadata registration.
- `backend/migrations` - add schema migration for slot/run tables and constraints.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - integrate accepted-slot publication.
- `backend/app/services/llm_generation/natal/reading_slot_service.py` - expected slot claim and idempotence owner.
- `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/evidence/schema-after.txt` - persist schema evidence.
- `_condamad/stories/CS-428-public-reading-slots-llm-generation-runs/evidence/validation.txt` - persist validation evidence.

Likely tests:

- `backend/tests/integration/test_theme_natal_reading_slots.py` - cover schema, public reads, idempotence, and concurrency.
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` - extend quota-on-acceptance concurrency coverage.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - preserve accepted-only public behavior.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend cutover is touched.
- `backend/app/api/v1/routers/**` - out of scope unless public GET/list wiring has no service boundary to reuse.
- `backend/app/services/llm_gateway/**` - out of scope; provider calls are not touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

Run from repository root, with the Python venv activated before every Python, Ruff, or pytest command.

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `ruff format backend`
- VC3: `ruff check backend`
- VC4: `python -B -m pytest -q backend/tests/integration -k "theme_natal and slot" --tb=short`
- VC5: `python -B -m pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short`
- VC6: `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
- VC7: `pytest -q backend/tests/integration/test_theme_natal_reading_slots.py`
- VC8: `rg -n "ThemeNatalReadingSlot|LlmGenerationRun|accepted_at|source_generation_run_id" backend/app backend/tests`
  - Forbidden pattern: missing slot/run symbols or missing accepted publication fields.
  - Allowed fixture pattern: test model factories and migration assertions.
  - Scan roots: `backend/app`, `backend/tests`.
  - Expected false positives: model declarations, migration code, and tests.
- VC9: `rg -n "client_request_id|idempot" backend/app backend/tests`
  - Forbidden pattern: idempotence absent from implementation or tests.
  - Allowed fixture pattern: idempotence test data and service method names.
  - Scan roots: `backend/app`, `backend/tests`.
  - Expected false positives: comments in focused tests are acceptable.
- VC10: `rg -n "UserNatalInterpretationModel\\.user_id == user_id,[\\s\\S]*UserNatalInterpretationModel\\.level" backend/app/services/llm_generation/natal`
  - Forbidden pattern: new canonical slot selection using only user plus level.
  - Allowed fixture pattern: none in new slot claim code.
  - Scan roots: `backend/app/services/llm_generation/natal`.
  - Expected false positives: pre-existing historical cache selectors outside the new slot owner.

## Regression Risks

- Concurrent requests may pass local tests but fail under another DB engine if the unique constraint is not the primary guard.
- Rejected runs may remain hidden in tests while a public service path still reads the old mixed table.
- Quota behavior may debit twice if accepted publication and quota consumption are not in the same transaction boundary.
- CS-427 primitives may be unavailable at implementation time, forcing a narrow backend decision before coding.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all new or materially changed backend files documented with a French file-level comment and French docstrings.
- Use the existing `backend/migrations` root and existing DB fixtures; do not add a new backend base directory.
- Preserve the source brief validation commands unless a path is proven uncollectable, then record the exact blocker.

## References

- `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md`
- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/infra/db/models/user_natal_interpretation.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
