# Story CS-407 refuser-downgrade-schema-v3-lecture-natale-complete: Refuser Downgrade Schema V3 Lecture Natale Complete
Status: ready-to-review

## Trigger / Source

- Source brief: `_story_briefs/cs-402-refuser-downgrade-schema-v3-lecture-natale-complete.md`.
- Selected mode: Repo-informed story in Fast Story Writer Mode.
- Source problem: une lecture natale `complete` Basic/Premium peut devenir publique apres echec V3 puis acceptation locale V2/V1.
- Source stakes: mismatch schema visible, rejet audite, free short preserve, gateway fallback explicite preserve, quota preserve.
- Source-alignment evidence: objectif, AC, taches, preuves et guardrails couvrent toutes les primitives du brief sans deplacer le sujet vers UI.

## Objective

Garantir qu'une generation natale `complete` non `free_short` et non issue d'un fallback gateway produit `AstroResponseV3`
ou un rejet audite `natal_complete_schema_mismatch`, sans conversion locale V2/V1 en lecture publique acceptee.

## Target State

- `complete` Basic/Premium avec `fallback_triggered=False` exige une deserialisation `AstroResponseV3`.
- `AstroErrorResponseV3` reste accepte uniquement pour les erreurs V3 conformes.
- Le rejet `natal_complete_schema_mismatch` contient le `request_id` et vit dans le flux d'audit existant.
- Aucun payload court V1/V2 rejete n'est persiste comme `UserNatalInterpretationModel` complete acceptee.
- Les endpoints publics `POST`, `GET` et `LIST` ne relisent pas le payload rejete comme lecture complete.
- Le quota `natal_chart_long` n'est pas consomme pour le rejet schema local.
- `free_short` conserve son schema court autorise.
- Un vrai `AstroResponseV3` reste persiste et relu avec `narrative_natal_reading_v1`.
- `GatewayResult.meta.fallback_triggered=True` conserve son comportement fallback explicite et observable.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-402-refuser-downgrade-schema-v3-lecture-natale-complete.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted; next available story number is `CS-407`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted lookup found `RG-150`, `RG-152`, `RG-155`, and `RG-157`.
- Evidence 4: guardrail resolver ran for backend runtime scope; unrelated frontend universal IDs were rejected from the local scope.
- Evidence 5: `interpretation_service.py` currently tries `AstroResponseV3`, then `AstroErrorResponseV3`, then `AstroResponseV2/V1`.
- Evidence 6: `interpretation_service.py` persists `fallback_triggered`, `validation_status`, `schema_version`, and `request_id`.
- Evidence 7: `schemas.py` shows `AstroResponseV3` is stricter than V2/V1 on summary, sections, highlights and advice.
- Evidence 8: `contracts.py` exposes `GatewayResult.meta.validation_status`, `repair_attempted`, and `fallback_triggered`.
- Repository structure alert: expected backend roots exist in this workspace; no implementation-created root directory is required.
- Scope vector:
  - operation `update`, domain `backend-natal-generation`
  - paths `backend/app/services/llm_generation/natal`, `backend/app/domain/llm/prompting`, `backend/app/domain/llm/runtime`
  - tests `backend/tests/unit`, `backend/tests/integration`
  - contracts `AstroResponseV3`, `AstroErrorResponseV3`, `narrative_natal_reading_v1`, `GatewayResult.meta`, `quota`

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `complete` Basic/Premium | in scope | AC1, AC2, AC3, Task 1, Task 2 |
| `fallback_triggered=False` | in scope | AC1, AC2, AC7, Task 1, Task 3 |
| `AstroResponseV3` | in scope | AC1, AC6, Task 2, Task 8 |
| `AstroErrorResponseV3` | in scope | AC5, Task 2 |
| `AstroResponseV2` | in scope | AC1, AC8, Task 2, Task 9 |
| `AstroResponseV1` | in scope | AC1, AC8, Task 2, Task 9 |
| `natal_complete_schema_mismatch` | in scope | AC2, AC9, Task 3, Task 4 |
| `request_id` | in scope | AC3, Task 4 |
| `UserNatalInterpretationModel` | in scope | AC4, AC10, Task 5 |
| Public `POST`, `GET`, `LIST` | in scope | AC4, Task 6 |
| `natal_chart_long` quota | in scope | AC11, Task 7 |
| `free_short` | in scope | AC12, Task 10 |
| gateway fallback explicite | in scope | AC7, Task 11 |
| Historical replay compatibility | out of scope | Non-goals and Regression Risks |
| Prompt schema changes | out of scope | Non-goals |

## Domain Boundary

- Domain: backend-natal-generation
- In scope:
  - Backend runtime schema decision for natal `complete` generation.
  - Backend audit/rejection path for local schema mismatch.
  - Backend persistence boundary for accepted and rejected natal interpretations.
  - Backend tests for V1/V2 short payloads, public boundary, free short, V3 acceptance and quota preservation.
- Out of scope:
  - Frontend UI, React rendering, CSS, prompts, pricing, auth, i18n, build tooling, DB migrations and schema class redesign.
- Explicit non-goals:
  - No frontend route, screen, client generation, prompt rewrite, quota model rewrite or deletion of historical V1/V2 schema classes.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Reject only local schema mismatch for `complete` non `free_short` with `fallback_triggered=False`.
  - Preserve `AstroErrorResponseV3` as the only accepted V3 error shape.
  - Preserve `free_short` short-schema behavior.
  - Preserve gateway fallback behavior only when `GatewayResult.meta.fallback_triggered=True`.
  - Preserve historical replay compatibility only outside the new generation acceptance path.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: product wants V2/V1 short payloads to remain public for new Basic/Premium complete generations.
- Additional validation rules:
  - Use `pytest -q backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py` for runtime schema mismatch behavior.
  - Use `pytest -q backend/tests/unit/test_natal_interpretation_stored_payload.py` for accepted versus rejected persistence.
  - Use `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` for public POST/GET/LIST boundary.
  - Use `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` for quota-on-acceptance behavior.
  - Use `AST guard` or targeted `rg` for forbidden local V3-to-V2/V1 generation conversion.
  - Use `app.openapi()` only to prove the public HTTP contract remains unchanged for existing natal routes.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `GatewayResult.meta`, `pytest`, `TestClient`, and `AST guard` prove runtime schema behavior. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta is local mismatch rejection. |
| Ownership Routing | yes | Schema selection, audit, persistence and quota responsibilities must stay canonical. |
| Allowlist Exception | no | No tolerance register is authorized for local V3-to-V2/V1 complete generation conversion. |
| Contract Shape | yes | Rejection cause, meta fields, accepted V3 and public response boundaries have exact rules. |
| Batch Migration | no | Historical payload migration or remediation is not in scope. |
| Reintroduction Guard | yes | Local V3-to-V2/V1 conversion must not return in the complete generation path. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Non-fallback complete V2/V1 output is rejected. | Evidence profile: json_contract_shape; `pytest` runs `tests/unit/test_natal_interpretation_service_v3_schema_guard.py`. |
| AC2 | Cause is `natal_complete_schema_mismatch`. | Evidence profile: json_contract_shape; `pytest` runs `tests/unit/test_natal_interpretation_service_v3_schema_guard.py`. |
| AC3 | The rejection audit records `request_id`. | Evidence profile: json_contract_shape; `pytest` runs `tests/unit/test_natal_interpretation_service_v3_schema_guard.py`. |
| AC4 | Rejected payloads stay private. | Evidence profile: json_contract_shape; `pytest` runs `tests/integration/test_natal_interpretation_rejected_public_boundary.py`. |
| AC5 | V3 error payloads remain accepted. | Evidence profile: json_contract_shape; `pytest` runs `tests/unit/test_natal_interpretation_service_v3_schema_guard.py`. |
| AC6 | Valid V3 complete payloads remain accepted. | Evidence profile: json_contract_shape; `pytest` runs `tests/unit/test_natal_interpretation_stored_payload.py`. |
| AC7 | Gateway fallback remains explicitly observable. | Evidence profile: json_contract_shape; `pytest` runs `tests/unit/test_natal_interpretation_service_v3_schema_guard.py`. |
| AC8 | The local generation path has no V3-to-V2/V1 conversion. | Evidence profile: ast_architecture_guard; `rg` checks forbidden constructors in the bounded service path. |
| AC9 | Mismatch rejection uses the narrative audit workflow. | Evidence profile: json_contract_shape; `pytest` runs `tests/unit/test_natal_interpretation_stored_payload.py`. |
| AC10 | Accepted persistence excludes rejected V2/V1. | Evidence profile: json_contract_shape; `pytest` runs `tests/unit/test_natal_interpretation_stored_payload.py`. |
| AC11 | `natal_chart_long` is not consumed on rejection. | Evidence profile: json_contract_shape; `pytest` runs `tests/unit/test_natal_chart_long_quota_on_acceptance.py`. |
| AC12 | `free_short` keeps its short-schema behavior. | Evidence profile: json_contract_shape; `pytest` runs `tests/unit/test_natal_interpretation_service_v3_schema_guard.py`. |
| AC13 | Public OpenAPI stays unchanged for natal routes. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()`. |
| AC14 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks

- [ ] Task 1: Trace the complete generation path and isolate the local schema mismatch decision. (AC: AC1, AC7)
- [ ] Task 2: Replace non-fallback complete V3 deserialization failure with `natal_complete_schema_mismatch` rejection. (AC: AC1, AC2, AC5)
- [ ] Task 3: Preserve gateway fallback only through `GatewayResult.meta.fallback_triggered=True`. (AC: AC7)
- [ ] Task 4: Attach `request_id` and the mismatch cause to the existing narrative audit outcome. (AC: AC2, AC3, AC9)
- [ ] Task 5: Prevent rejected mismatch payloads from becoming accepted `UserNatalInterpretationModel` records. (AC: AC4, AC10)
- [ ] Task 6: Prove public `POST`, `GET` and `LIST` exclude mismatch rejections. (AC: AC4)
- [ ] Task 7: Prove `natal_chart_long` is consumed only after accepted complete persistence. (AC: AC11)
- [ ] Task 8: Preserve valid `AstroResponseV3` persistence and replay. (AC: AC6)
- [ ] Task 9: Add an `AST guard` or targeted `rg` proof for the forbidden local V3-to-V2/V1 conversion. (AC: AC8)
- [ ] Task 10: Preserve `free_short` schema behavior with a focused unit test. (AC: AC12)
- [ ] Task 11: Record OpenAPI unchanged evidence for existing natal public routes. (AC: AC13)
- [ ] Task 12: Persist validation output and before/after evidence under this story directory. (AC: AC14)

## Files to Inspect First

- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`
- `backend/app/domain/llm/prompting/schemas.py`
- `backend/app/domain/llm/runtime/contracts.py`
- `backend/app/models/user_natal_interpretation.py`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/tests/unit/test_natal_interpretation_stored_payload.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`

## Runtime Source of Truth

- Primary source of truth:
  - `GatewayResult.meta`, `NatalInterpretationService.interpret`, `pytest`, `TestClient`, `AST guard`, and persisted model assertions.
- Runtime evidence:
  - `pytest -q backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py`.
  - `pytest -q backend/tests/unit/test_natal_interpretation_stored_payload.py`.
  - `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`.
  - `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`.
- Secondary evidence:
  - Targeted `rg` scan for local V3-to-V2/V1 conversion constructors.
  - `python -B -c "from app.main import app; app.openapi()"` to prove route contract availability.
- Static scans alone are not sufficient for this story because:
  - Runtime rejection, audit persistence, quota behavior and public boundary must be proven from executed code.

## Contract Shape

- Contract type:
  - Backend runtime schema validation and public persistence boundary.
- Fields:
  - `level`: `complete`.
  - `variant_code`: any value other than `free_short` for the guarded path.
  - `fallback_triggered`: `False` for mismatch rejection, `True` for explicit gateway fallback.
  - `schema_version`: `v3` for accepted complete V3, rejected state for mismatch payloads.
  - `validation_status`: rejected for mismatch payloads.
  - `rejection_cause`: `natal_complete_schema_mismatch`.
  - `request_id`: non-empty request correlation value copied to audit evidence.
  - `narrative_natal_reading_v1`: present only for accepted complete readings.
- Required fields:
  - `level`, `variant_code`, `fallback_triggered`, `validation_status`, `rejection_cause`, `request_id`.
- Optional fields:
  - `repair_attempted`, `validation_errors`, `latency_ms`, `tokens_in`, `tokens_out`.
- Status codes:
  - No new public 500 behavior is authorized for mismatch rejection.
- Serialization names:
  - Existing public response names stay unchanged.
- Frontend type impact:
  - none.
- Generated contract impact:
  - `app.openapi()` remains unchanged for the existing natal public endpoints.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-407-refuser-downgrade-schema-v3-lecture-natale-complete/evidence/schema-guard-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-407-refuser-downgrade-schema-v3-lecture-natale-complete/evidence/schema-guard-after.txt`
- Expected invariant:
  - The only intended behavior delta is rejection of non-fallback complete V2/V1 payloads during new generation.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Runtime schema decision | `backend/app/services/llm_generation/natal/interpretation_service.py` | API router |
| Schema definitions | `backend/app/domain/llm/prompting/schemas.py` | prompt text |
| Gateway fallback signal | `backend/app/domain/llm/runtime/contracts.py` | ad hoc dict keys |
| Narrative audit outcome | `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` | public response builder |
| Accepted persistence | `backend/app/models/user_natal_interpretation.py` | audit-only repository |
| Public boundary tests | `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` | manual-only QA |
| Quota acceptance tests | `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` | service comments |

## Mandatory Reuse / DRY Constraints

- Reuse existing `AstroResponseV3`, `AstroErrorResponseV3`, `AstroFreeResponseV1`, `GatewayResult.meta` and audit outcome patterns.
- Reuse the existing narrative rejection workflow; do not create a second rejection repository or status taxonomy.
- Centralize the complete-schema guard in one service helper or one contiguous decision block.
- Keep V1/V2 schemas available for historical or short surfaces already owning them.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy acceptance path may expose local V2/V1 payloads as new complete Basic/Premium readings.
- No compatibility route path may be added for rejected mismatch payloads.
- No fallback route path may be added for mismatch payloads.
- No shim or alias may translate local schema mismatch into `narrative_natal_reading_v1`.
- Forbidden behavior: `AstroResponseV2(**full_output)` after failed `AstroResponseV3` in non-fallback complete generation.
- Forbidden behavior: `AstroResponseV1(**full_output)` after failed `AstroResponseV3` in non-fallback complete generation.
- Forbidden behavior: consuming `natal_chart_long` before accepted complete persistence for the mismatch case.

## Reintroduction Guard

- Guard source:
  - `rg -n "AstroResponseV2\\(\\*\\*full_output\\)|AstroResponseV1\\(\\*\\*full_output\\)" backend/app/services/llm_generation/natal/interpretation_service.py`
- Runtime guard:
  - `pytest -q backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py`.
  - `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`.
- Architecture guard:
  - Add an `AST guard` or equivalent targeted test proving the non-fallback complete V3 failure path cannot instantiate V2/V1.
- Forbidden reintroduction:
  - Treating local schema mismatch as an accepted complete response.
  - Recording `schema_version="v2"` for newly accepted Basic/Premium complete generation outside historical replay.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-150 | scope -> rejected payload boundary -> rejected outputs stay outside public POST/GET/LIST. | boundary `pytest`; payload scan. |
| RG-152 | scope -> accepted complete readings -> `narrative_natal_reading_v1` remains public contract. | stored-payload `pytest`. |
| RG-155 | scope -> Basic/Premium complete integrity -> invalid complete readings are audited rejections. | schema-guard `pytest`. |
| RG-157 | scope -> complete acceptance -> quota debit stays after accepted persistence. | quota `pytest`. |
| RG-022 | scope -> story validation paths -> backend pytest paths must be collected. | exact validation commands. |

- Resolver note: `RG-002` was resolved through backend app paths but rejected from applicable scope because this story does not change API routers.
- Non-applicable example: frontend style guardrails are out of scope because no React or CSS file is listed.
- Non-applicable example: DB migration guardrails are out of scope because no schema migration is authorized.
- Non-applicable example: auth guardrails are out of scope because no authentication model change is authorized.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline before | `_condamad/stories/CS-407-refuser-downgrade-schema-v3-lecture-natale-complete/evidence/schema-guard-before.txt` | Record initial V3 mismatch behavior. |
| Baseline after | `_condamad/stories/CS-407-refuser-downgrade-schema-v3-lecture-natale-complete/evidence/schema-guard-after.txt` | Record final mismatch rejection behavior. |
| Validation output | `_condamad/stories/CS-407-refuser-downgrade-schema-v3-lecture-natale-complete/evidence/validation.txt` | Keep final lint, test and scan output. |
| OpenAPI unchanged | `_condamad/stories/CS-407-refuser-downgrade-schema-v3-lecture-natale-complete/evidence/openapi-unchanged.txt` | Prove public route contract stays stable. |
| Review output | `_condamad/stories/CS-407-refuser-downgrade-schema-v3-lecture-natale-complete/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | No tolerance entry is authorized for local V3-to-V2/V1 complete generation conversion. | permanent zero-entry register |

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration, remediation or historical payload conversion is in scope.

## Dependencies / Sequencing

- Depends on: `CS-401`.
- Sequencing rule: implementation must confirm the CS-401 Basic complete V3 routing contract before changing local mismatch handling.
- If CS-401 evidence is unavailable or contradicted, stop and record the blocker rather than preserving V2/V1 public downgrade behavior.

## Expected Files to Modify

Likely files:

- `backend/app/services/llm_generation/natal/interpretation_service.py` - enforce the complete schema guard and audit handoff.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` - reuse or extend rejection cause mapping.
- `_condamad/stories/CS-407-refuser-downgrade-schema-v3-lecture-natale-complete/evidence/**` - persist proof artifacts.

Likely tests:

- `backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py` - new focused runtime tests for V3 mismatch rejection.
- `backend/tests/unit/test_natal_interpretation_stored_payload.py` - cover accepted versus rejected persistence.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - cover POST, GET and LIST public boundary.
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` - cover quota-on-acceptance behavior.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/alembic/**` - out of scope; no migration is authorized.
- `backend/app/domain/llm/prompting/schemas.py` - out of scope unless tests require reading the existing contract.
- `backend/app/api/v1/routers/public/**` - out of scope unless public boundary tests reveal a direct leak.
- `backend/app/services/quota/**` - out of scope unless quota tests reveal debit before acceptance.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `.\.venv\Scripts\Activate.ps1`
- VC2: `cd backend`
- VC3: `ruff format .`
- VC4: `ruff check .`
- VC5: `python -B -m pytest -q tests/unit/test_natal_interpretation_service_v3_schema_guard.py --tb=short`
- VC6: `python -B -m pytest -q tests/unit/test_natal_interpretation_stored_payload.py --tb=short`
- VC7: `python -B -m pytest -q tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short`
- VC8: `python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short`
- VC9: `rg -n "AstroResponseV2\\(\\*\\*full_output\\)|AstroResponseV1\\(\\*\\*full_output\\)" app/services/llm_generation/natal/interpretation_service.py`
- VC10: `python -B -c "from app.main import app; app.openapi()"`
- VC11: `python -B -c "from pathlib import Path; assert Path('../_condamad/stories/CS-407-refuser-downgrade-schema-v3-lecture-natale-complete/evidence/validation.txt').exists()"`

`rg` scan details:

- VC9 forbidden pattern: `AstroResponseV2(**full_output)` or `AstroResponseV1(**full_output)` in the non-fallback complete generation block.
- VC9 allowed fixture pattern: historical replay or explicit gateway fallback code outside the guarded complete generation decision.
- VC9 roots: `app/services/llm_generation/natal/interpretation_service.py` after `cd backend`.
- VC9 expected false positives: zero inside the non-fallback complete V3 failure block; any remaining hit must be classified in validation evidence.

## Regression Risks

- Historical replay of older V2 readings can be broken if the guard is applied outside new complete generation.
- Gateway fallback can be confused with local schema mismatch if `fallback_triggered` is ignored.
- Public rejection can become a 500 response if the existing audit workflow is bypassed.
- Quota can still be consumed too early if the rejection happens after debit logic.
- Free short can be pulled into V3 validation if variant ownership is not checked explicitly.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep Python commands inside the activated `.venv`.
- Keep comments and docstrings in French for new or significantly modified application files.
- Do not update `_condamad/stories/regression-guardrails.md` during implementation of this story.
- Preserve CS-396, CS-397, CS-398 and CS-406 behavior while changing the local schema mismatch path.

## References

- `_story_briefs/cs-402-refuser-downgrade-schema-v3-lecture-natale-complete.md`
- `_condamad/stories/regression-guardrails.md#RG-150`
- `_condamad/stories/regression-guardrails.md#RG-152`
- `_condamad/stories/regression-guardrails.md#RG-155`
- `_condamad/stories/regression-guardrails.md#RG-157`
- `_condamad/stories/regression-guardrails.md#RG-022`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/app/domain/llm/prompting/schemas.py`
- `backend/app/domain/llm/runtime/contracts.py`
- `backend/tests/unit/test_natal_interpretation_stored_payload.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
