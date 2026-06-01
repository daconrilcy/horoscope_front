# Story CS-431 contract-bound-llm-gateway-rejection-workflow: Contract Bound LLM Gateway And Rejection Workflow
Status: ready-to-dev

## Trigger / Source

Brief direct from `_story_briefs/cs-431-contract-bound-llm-gateway-rejection-workflow.md`.
The bounded problem is that the natal LLM gateway must execute a resolved generation contract snapshot as its runtime contract source.

## Objective

Make the backend LLM gateway execute a `ResolvedGenerationContractSnapshot` for theme natal generation.
The gateway must consume resolved engine, prompt, output schema, data contract, validators, strict JSON parsing, and rejection policy without owning natal business rules.

## Target State

- Theme natal generation enters the gateway through `ResolvedGenerationContractSnapshot`.
- The snapshot provides engine profile, prompt contract, output schema, data contract, contract hashes, and validators.
- The gateway does not choose Basic or Premium prompt behavior from raw use-case heuristics.
- `basic_natal_prompt_payload` cannot be injected into a Premium historical prompt carrier.
- JSON parsing is strict before schema validation.
- Invalid JSON or invalid schema can trigger exactly one form repair when the contract permits it.
- Invented facts, astrological contradictions, technical leaks, mechanical text, and empty text are rejected without content repair.
- Rejected attempts are persisted only in `llm_generation_runs`.
- Public reading routes expose accepted readings only.
- Natal-specific validators remain in natal modules and are injected by the contract or natal reading runtime.

## Brief Primitive Ledger

| Primitive | Source expectation | Story mapping |
|---|---|---|
| `ResolvedGenerationContractSnapshot` | Gateway input replaces raw legacy use case for natal generation. | AC1, AC2, Task 1. |
| engine profile | Runtime provider configuration comes from the snapshot. | AC3, Task 2. |
| prompt contract | Prompt selection comes from the snapshot. | AC4, AC5, Task 3. |
| output schema | Strict schema validation comes from the snapshot. | AC6, AC7, Task 4. |
| data contract | Prompt-visible, validation-only, and audit-only data roles come from the snapshot. | AC8, Task 5. |
| `basic_natal_prompt_payload` | Basic payload cannot enter Premium historical prompt flow. | AC9, Task 6. |
| strict JSON parsing | Provider output is decoded before schema validation. | AC10, Task 7. |
| form repair | JSON or schema shape errors get at most one repair attempt. | AC11, AC12, Task 8. |
| policy rejection | Factual, astrological, leak, mechanical, and empty text failures are rejected. | AC13, AC14, AC15, AC16, Task 9. |
| `llm_generation_runs` | Rejected attempts are audit-only. | AC17, Task 10. |
| public readings | Rejections never update accepted public readings. | AC18, Task 11. |
| contract hashes | Logs and runs contain contract versions or hashes. | AC19, AC22, Task 12. |
| natal validators | Business rules stay outside the gateway. | AC20, Task 13. |
| required validations | Backend lint, focused pytest, integration pytest, and scans are preserved. | Validation Plan. |
| non-goals | Frontend, cutover endpoint, physical historical deletion, and live provider calls stay outside scope. | Domain Boundary. |

## Current State Evidence

- Evidence 1: `_story_briefs/cs-431-contract-bound-llm-gateway-rejection-workflow.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-431`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer Mode contract read first.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-018`, `RG-021`, `RG-149`, `RG-150`, `RG-152`, `RG-155`, `RG-166`, and `RG-171` read.
- Evidence 5: `resolve_guardrails.py` - resolver run with backend LLM gateway, rejection workflow, snapshot, JSON, and schema scope.
- Evidence 6: `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - rejection and gateway risks checked.
- Evidence 7: `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md` - contract snapshot dependency checked.
- Evidence 8: `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md` - fake provider and invalid mode dependency checked.
- Evidence 9: `backend/app/domain/llm/runtime/gateway.py` - current gateway resolves plans from `LLMExecutionRequest` and raw `use_case`.
- Evidence 10: `backend/app/domain/llm/runtime/adapter.py` - current natal adapter still forwards `NatalExecutionInput` with Basic payload context.
- Evidence 11: `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` - natal validators and rejection builders checked.
- Evidence 12: `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` - existing rejected answer workflow checked.
- Source-alignment evidence: objectives, ACs, tasks, non-goals, guardrails, and validation commands map to the source brief without scope narrowing.

## Domain Boundary

- Domain: backend-domain
- In scope:
  - Backend LLM gateway contract-bound execution for theme natal generation.
  - Snapshot object definition and runtime use for engine, prompt, output schema, data contract, hashes, and validators.
  - Strict JSON parsing, bounded form repair, rejection classification, audit-only run persistence, and public boundary proof.
  - Tests for gateway snapshot execution, rejection workflow, and Basic/Premium prompt carrier separation.
- Out of scope:
  - Frontend UI, public cutover endpoint, live provider calls, auth, i18n, styling, build tooling, migrations, and physical historical deletion.
- Explicit non-goals:
  - No frontend route, screen, state, generated client, or CSS edit is authorized.
  - No live OpenAI or other provider request is required in tests.
  - No complete physical deletion of historical natal modules is required.
  - No public endpoint cutover is implemented by this story.
  - No natal business rule is coded directly inside `backend/app/domain/llm/runtime/gateway.py`.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the contract-bound theme natal gateway path and its rejection workflow proof.
  - Keep the gateway generic: execute the snapshot and invoke supplied validators.
  - Keep public reading routes accepted-only.
  - Keep frontend behavior unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-429 or CS-430 contract surfaces are unavailable at implementation start.
- Additional validation rules:
  - Runtime evidence must include `pytest -q backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py`.
  - Rejection evidence must include `pytest -q backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py`.
  - Integration evidence must include `pytest -q backend/tests/integration -k "gateway or rejection or generation_contract or theme_natal" --tb=short`.
  - Architecture evidence must include an `AST guard` proving natal business validators are not implemented in the gateway.
  - Persistence evidence must inspect DB schema or ORM models for `llm_generation_runs` rejection metadata.
  - Public boundary evidence must include `TestClient` or service tests proving rejected attempts are absent from public reads.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `TestClient`, `AST guard`, loaded config, and DB schema checks prove execution. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Gateway orchestration, natal validators, run persistence, and tests need canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this gateway contract path. |
| Contract Shape | yes | Snapshot, prompt payload, strict JSON, rejection reason, and run metadata are closed. |
| Batch Migration | no | No batch migration or mass historical conversion is in scope. |
| Reintroduction Guard | yes | Raw use-case routing, Premium carrier contamination, and public rejected payloads must stay absent. |
| Persistent Evidence | yes | Validation, scan, baseline, rejection, and public-boundary artifacts must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Gateway accepts a resolved snapshot input. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py`. |
| AC2 | Raw natal use-case is not the gateway contract source. | Evidence profile: ast_architecture_guard; `python` AST guard checks gateway call shape. |
| AC3 | Engine profile comes from the snapshot. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py`. |
| AC4 | Prompt contract comes from the snapshot. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py`. |
| AC5 | Premium prompt excludes Basic payload. | Evidence profile: targeted_forbidden_symbol_scan; `pytest` plus `rg` carrier scan. |
| AC6 | Output schema comes from the snapshot. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py`. |
| AC7 | Unknown JSON fields are rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py`. |
| AC8 | Data contract roles come from the snapshot. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py`. |
| AC9 | Basic payload cannot enter a Premium prompt. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans bounded backend roots. |
| AC10 | Provider output uses strict JSON parsing. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py`. |
| AC11 | Invalid JSON gets one form repair. | Evidence profile: json_contract_shape; `pytest` checks `backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py`. |
| AC12 | Schema shape gets one repair. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py`. |
| AC13 | Invented facts are rejected directly. | Evidence profile: json_contract_shape; `pytest` checks rejection workflow tests. |
| AC14 | Astrological contradictions are rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py`. |
| AC15 | Technical leaks are rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py`. |
| AC16 | Mechanical or empty text is rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py`. |
| AC17 | Rejections persist only in runs. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_contract_bound_llm_gateway_rejections.py`. |
| AC18 | Public readings stay accepted-only. | Evidence profile: api_error_shape_contract; `TestClient`; `pytest` checks integration rejection path. |
| AC19 | Runs log contract versions. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_contract_bound_llm_gateway_rejections.py`. |
| AC20 | Natal rules stay outside the gateway. | Evidence profile: ast_architecture_guard; `python` AST guard over `backend/app/domain/llm/runtime/gateway.py`. |
| AC21 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |
| AC22 | Runs log contract hashes. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_contract_bound_llm_gateway_rejections.py`. |

## Implementation Tasks

- [ ] Task 1: Define `ResolvedGenerationContractSnapshot` in the canonical contract owner. (AC: AC1)
- [ ] Task 2: Route theme natal gateway execution from the resolved snapshot instead of raw use-case ownership. (AC: AC1, AC2)
- [ ] Task 3: Read engine profile, prompt contract, output schema, and data contract from the snapshot. (AC: AC3, AC4, AC6, AC8)
- [ ] Task 4: Add Basic/Premium prompt-carrier separation checks in gateway-facing tests. (AC: AC5, AC9)
- [ ] Task 5: Apply strict JSON parsing before schema validation. (AC: AC10)
- [ ] Task 6: Allow exactly one contract-permitted form repair for JSON and schema shape failures. (AC: AC11, AC12)
- [ ] Task 7: Reject invented facts through injected natal validators. (AC: AC13, AC20)
- [ ] Task 8: Reject astrological contradictions through injected natal validators. (AC: AC14, AC20)
- [ ] Task 9: Reject technical leaks, mechanical text, and empty text through injected validators. (AC: AC15, AC16, AC20)
- [ ] Task 10: Persist rejected attempts in `llm_generation_runs` with reason and contract metadata. (AC: AC17, AC19, AC22)
- [ ] Task 11: Prove public routes expose accepted readings only after rejected attempts. (AC: AC18)
- [ ] Task 12: Add AST and targeted scan guards for gateway ownership and prompt-carrier contamination. (AC: AC2, AC5, AC9, AC20)
- [ ] Task 13: Persist validation, scan, baseline, rejection, and public-boundary evidence artifacts. (AC: AC21)

## Files to Inspect First

- `_story_briefs/cs-431-contract-bound-llm-gateway-rejection-workflow.md` - source contract.
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - rejection and prompt risk source.
- `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md` - snapshot and strict schema dependency.
- `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md` - invalid mode and fake provider dependency.
- `backend/app/domain/llm/runtime/gateway.py` - gateway owner to keep generic.
- `backend/app/domain/llm/runtime/adapter.py` - current natal gateway entry adapter.
- `backend/app/domain/llm/runtime/contracts.py` - canonical runtime contract types.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` - natal validator owner.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` - rejected answer workflow owner.
- `backend/app/infra/db/models/llm` - inspect `llm_generation_runs` model owner before persistence edits.
- `backend/tests/llm_orchestration` - gateway and rejection unit or orchestration test owner.
- `backend/tests/integration` - public boundary and persistence integration test owner.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest -q backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py`.
  - `pytest -q backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py`.
  - `pytest -q backend/tests/integration/test_contract_bound_llm_gateway_rejections.py`.
  - `pytest -q backend/tests/integration -k "gateway or rejection or generation_contract or theme_natal" --tb=short`.
  - `TestClient` public-boundary checks for rejected attempts.
  - `AST guard` checks on `backend/app/domain/llm/runtime/gateway.py`.
  - DB schema or ORM inspection for `llm_generation_runs` rejection metadata.
- Secondary evidence:
  - Targeted `rg` scans for Basic/Premium carrier contamination and old natal prompt keys.
- Static scans alone are not sufficient for this story because:
  - Runtime snapshot execution, repair count, rejection persistence, and public absence require executable tests.

## Contract Shape

- Contract type:
  - Backend runtime contract snapshot and rejection workflow.
- Fields:
  - `generation_contract_key`: versioned theme natal generation contract key.
  - `generation_contract_version`: immutable contract version used by the run.
  - `generation_contract_snapshot_id`: immutable resolved snapshot identifier.
  - `generation_contract_hash`: deterministic hash for the resolved snapshot.
  - `prompt_contract_version`: prompt contract version used by the run.
  - `output_schema_version`: output schema version used for strict validation.
  - `data_contract_version`: data contract version used for prompt and validation roles.
  - `engine_profile_version`: engine profile version used for provider execution.
  - `prompt_contract`: resolved prompt material and prompt-visible data mapping.
  - `output_schema`: strict JSON schema used by validation.
  - `data_contract`: prompt-visible, validation-only, and audit-only data roles.
  - `validators`: injected validation functions or validator descriptors supplied by the contract.
  - `repair_policy`: permits exactly one form repair for JSON or schema shape failures.
  - `rejection_reason`: structured reason for rejected provider output.
- Required fields:
  - All fields listed in the `Fields` block are required for the snapshot or run evidence.
- Optional fields:
  - none.
- Status codes:
  - Existing public route status behavior stays unchanged; rejected attempts are not public readings.
- Serialization names:
  - Serialization uses exact snake_case field names listed in the `Fields` block.
- Frontend type impact:
  - none; frontend generated client changes are out of scope.
- Generated contract impact:
  - No OpenAPI surface change is required by this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/gateway-before.txt`
  - `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/public-boundary-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/gateway-after.txt`
  - `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/public-boundary-after.txt`
- Expected invariant:
  - The only intended behavior delta is contract-bound theme natal gateway execution with audit-only rejection workflow.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Snapshot type | `backend/app/domain/llm/runtime/contracts.py` or CS-429 canonical owner | `frontend/src/**` |
| Gateway orchestration | `backend/app/domain/llm/runtime/gateway.py` | `backend/app/services/llm_generation/natal/**` business rules |
| Natal validators | `backend/app/services/llm_generation/natal` | `backend/app/domain/llm/runtime/gateway.py` |
| Rejection workflow | `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` or run owner | `frontend/src/**` |
| Run persistence | `backend/app/infra/db/models/llm` and canonical repository owner | `backend/app/api/**` direct SQL |
| Public boundary tests | `backend/tests/integration/test_contract_bound_llm_gateway_rejections.py` | `frontend/src/**` |
| Gateway tests | `backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py` | `backend/app/tests/**` duplicates |

## Mandatory Reuse / DRY Constraints

- Reuse CS-429 snapshot, contract key, schema, and hash primitives.
- Reuse CS-430 fake provider invalid modes for rejection workflow proof.
- Reuse existing `validate_output`, strict schema validation, and JSON parsing helpers unless they cannot support the snapshot contract.
- Reuse natal validator modules for invented facts, contradictions, technical leaks, mechanical text, and empty text checks.
- Reuse existing rejected answer workflow concepts for audit-only semantics.
- Reuse canonical run persistence owners for `llm_generation_runs`.
- Do not duplicate Basic/Premium product selection logic inside the gateway.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy raw natal use-case path may own theme natal prompt selection in the target gateway flow.
- No compatibility prompt path may inject `basic_natal_prompt_payload` into a Premium prompt carrier.
- No fallback public reading may be produced from rejected provider output.
- Do not add a second Basic/Premium selector in the gateway.
- Do not persist rejected provider output as an accepted public reading.
- Do not add frontend, live provider, public cutover endpoint, migration, or physical historical deletion work in this story.

## Reintroduction Guard

- Guard prompt carrier contamination with:
  - `rg -n "basic_natal_prompt_payload.*natal_interpretation|natal_interpretation.*basic_natal_prompt_payload" backend/app backend/tests`.
- Guard gateway ownership drift with:
  - `rg -n "ThemeNatal|natal_reading|basic_full_reading" backend/app/domain/llm/runtime/gateway.py`.
- Guard Premium leakage with:
  - `rg -n "EXIGENCE PREMIUM|AstroResponse_v3|fallback_default" backend/app/domain/llm backend/app/services/llm_generation/natal backend/tests`.
- Guard runtime behavior with:
  - `python -B -m pytest -q tests/llm_orchestration tests/integration -k "gateway or rejection or generation_contract or theme_natal" --tb=short`.
- Architecture guard:
  - `python` AST guard must prove gateway reintroduction is limited to orchestration and injected validators.
- Expected result:
  - Gateway references remain orchestration-only; natal-specific validation and product rules stay in canonical owners.

## Regression Guardrails

| Guardrail | scope -> invariant -> evidence |
|---|---|
| RG-018 | LLM prompting -> supported natal family does not regain prompt fallback ownership -> governance `pytest` and `rg`. |
| RG-021 | Prompt governance -> remaining fallback keys stay classified outside this story -> existing governance `pytest`. |
| RG-149 | Prompt cartography -> prompt-generation roles stay explicit for natal flow -> targeted `rg` and story evidence. |
| RG-150 | Public boundary -> rejected LLM payloads stay non-public -> integration `pytest` and `TestClient`. |
| RG-152 | Public narration -> technical traces stay rejected -> rejection workflow `pytest` and targeted `rg`. |
| RG-155 | Semantic integrity -> invalid narrative content stays audit-only -> rejection workflow `pytest`. |
| RG-166 | Basic validation -> form repair is single-attempt then rejected -> rejection workflow `pytest`. |
| RG-171 | Basic prompt -> Basic does not route through old natal prompt keys -> carrier `pytest` and `rg`. |

Needs-investigation:

- Resolver returned broad backend layout and unrelated frontend examples; the brief supplies exact local LLM and natal guardrails used above.
- Registry gap: no durable guardrail explicitly names `ResolvedGenerationContractSnapshot`; this story records the gap without editing the registry.
- Adjacent frontend, DB migration, style, build, and i18n guardrails were omitted because they do not match the local story domain.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/validation.txt` | Keep final command output. |
| Gateway baseline | `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/gateway-before.txt` | Prove initial gateway state. |
| Gateway result | `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/gateway-after.txt` | Prove snapshot execution. |
| Rejection output | `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/rejection-workflow.txt` | Prove rejection modes. |
| Public boundary output | `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/public-boundary-after.txt` | Prove accepted-only reads. |
| Prompt carrier scan | `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/prompt-carrier-scan.txt` | Prove Basic/Premium separation. |
| Review output | `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this contract-bound gateway story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/llm/runtime/contracts.py` - define or expose `ResolvedGenerationContractSnapshot`.
- `backend/app/domain/llm/runtime/gateway.py` - execute the resolved snapshot without owning natal rules.
- `backend/app/domain/llm/runtime/adapter.py` - adapt natal entry points to the snapshot contract path.
- `backend/app/domain/llm/runtime/output_validator.py` - inspect strict JSON and schema validation reuse before edits.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` - reuse natal-specific validators.
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` - reuse or extend rejected attempt workflow.
- `backend/app/infra/db/models/llm` - inspect `llm_generation_runs` persistence owner before rejection metadata edits.
- `backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py` - add snapshot gateway tests.
- `backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py` - add rejection workflow tests.
- `backend/tests/integration/test_contract_bound_llm_gateway_rejections.py` - add public boundary and run persistence tests.
- `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/gateway-before.txt` - before evidence.
- `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/gateway-after.txt` - runtime evidence.
- `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/rejection-workflow.txt` - rejection evidence.
- `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/public-boundary-after.txt` - public proof.
- `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/prompt-carrier-scan.txt` - scan proof.

Likely tests:

- `backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py` - contract-bound gateway execution.
- `backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py` - strict parse, repair, and rejection modes.
- `backend/tests/integration/test_contract_bound_llm_gateway_rejections.py` - run persistence and public accepted-only boundary.
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - supported family prompt fallback regression support.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - existing rejected public boundary support.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/api/**` - out of scope unless public accepted-only tests expose a missing adapter boundary.
- `backend/migrations/**` - out of scope because this story does not authorize schema migration work.
- `backend/app/infra/providers/**` - out of scope; no live provider behavior is required.

## 20. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: activate venv, then run from `backend`: `ruff format .`.
- VC2: activate venv, then run from `backend`: `ruff check .`.
- VC3: activate venv, then run from `backend`: `python -B -m pytest -q tests/llm_orchestration tests/integration`.
- VC3 filter: `-k "gateway or rejection or generation_contract or theme_natal" --tb=short`.
- VC4: activate venv, then `python -B -m pytest -q backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py`.
- VC5: activate venv, then `python -B -m pytest -q backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py`.
- VC6: activate venv, then `python -B -m pytest -q backend/tests/integration/test_contract_bound_llm_gateway_rejections.py`.
- VC7: activate venv, then run an `AST guard` proving natal validators are not implemented in `backend/app/domain/llm/runtime/gateway.py`.
- VC8 forbidden pattern: `basic_natal_prompt_payload.*natal_interpretation|natal_interpretation.*basic_natal_prompt_payload`.
- VC8 allowed fixture pattern: tests and evidence that assert the forbidden carrier combination is absent.
- VC8 scan roots: `backend/app`, `backend/tests`.
- VC8 command: `rg -n "basic_natal_prompt_payload.*natal_interpretation|natal_interpretation.*basic_natal_prompt_payload" backend/app backend/tests`.
- VC8 expected false positives: tests that assert the forbidden carrier combination remains absent.
- VC9 forbidden pattern: `ThemeNatal|natal_reading|basic_full_reading`.
- VC9 allowed fixture pattern: gateway orchestration references that call snapshot or injected validator abstractions only.
- VC9 scan roots: `backend/app/domain/llm/runtime/gateway.py`.
- VC9 command: `rg -n "ThemeNatal|natal_reading|basic_full_reading" backend/app/domain/llm/runtime/gateway.py`.
- VC9 expected false positives: generic orchestration labels with no natal business rule implementation.
- VC10 forbidden pattern: `EXIGENCE PREMIUM|AstroResponse_v3|fallback_default`.
- VC10 allowed fixture pattern: Premium contract owner, tests asserting Basic absence, and story evidence.
- VC10 scan roots: `backend/app/domain/llm`, `backend/app/services/llm_generation/natal`, `backend/tests`.
- VC10 command: `rg -n "EXIGENCE PREMIUM|AstroResponse_v3|fallback_default" backend/app/domain/llm backend/app/services/llm_generation/natal backend/tests`.
- VC10 expected false positives: Premium contract tests or negative assertions that prove Basic separation.
- VC11: persist final outputs under `_condamad/stories/CS-431-contract-bound-llm-gateway-rejection-workflow/evidence/validation.txt`.

## Regression Risks

- CS-429 and CS-430 may be ready-to-dev but not implemented when this story starts.
- The gateway can drift into product selection unless tests assert snapshot-owned prompt and schema resolution.
- A form repair path can become content repair unless rejection reasons are split by failure category.
- Rejected output can leak into public readings unless integration tests check accepted-only reads after failed attempts.
- Run metadata can omit hashes unless assertions cover every contract version and hash field.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all Python commands under `.\.venv\Scripts\Activate.ps1`.
- Keep comments and docstrings in French for new or significantly changed backend application files.
- Keep frontend edits, public endpoint cutover, live provider calls, migrations, and physical historical deletion out of the implementation diff.
- Keep natal business rules in injected validators or natal runtime modules, not in `backend/app/domain/llm/runtime/gateway.py`.

## References

- `_story_briefs/cs-431-contract-bound-llm-gateway-rejection-workflow.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md`
- `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/domain/llm/runtime/contracts.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/app/services/llm_generation/natal/rejected_answer_workflow.py`
