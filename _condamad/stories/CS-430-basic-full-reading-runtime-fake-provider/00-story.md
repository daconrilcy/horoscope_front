# Story CS-430 basic-full-reading-runtime-fake-provider: Basic Full Reading Runtime With Fake Provider
Status: ready-to-review

## Trigger / Source

Brief direct from `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md`.
The bounded problem is the first executable Basic runtime path for `theme_natal.reading.basic_full_reading.v1`.

## Objective

Implement the backend Basic full-reading runtime with a deterministic fake provider.
The runtime must prove product routing, Basic payload construction, strict parsing, run persistence, public projection, slot state, and quota timing.

## Target State

- `basic + generate_full` resolves to `theme_natal.reading.basic_full_reading.v1`.
- The Basic runtime builds its prompt-visible payload from `BasicNatalReadingPlan` and existing Basic facts.
- The fake provider returns deterministic JSON modes for valid and invalid contract cases.
- Every provider attempt persists a technical `LlmGenerationRun` with contract metadata, schema metadata, and data hash.
- Only accepted Basic projections are persisted as public `ThemeNatalReadingSlot` readings.
- Public payloads exclude raw provider response data and technical traces.
- Invalid fake modes are rejected before public projection.
- Quota is consumed after accepted persistence only.
- A minimal contractual Free preview may exist only to support traversal tests.

## Brief Primitive Ledger

| Primitive | Source expectation | Story mapping |
|---|---|---|
| `theme_natal.reading.basic_full_reading.v1` | Execute Basic full-reading runtime. | AC1, AC2, AC3, Task 1. |
| `generate_full` | Route Basic product action to the target contract. | AC1, Task 1. |
| `BasicNatalReadingPlan` | Source Basic prompt material. | AC2, AC8, AC9, Task 2. |
| fake provider | Produce deterministic valid and invalid JSON modes. | AC3, AC6, AC7, AC8, AC9, AC10, AC11, AC12, Task 3. |
| `LlmGenerationRun` | Persist technical run metadata. | AC4, Task 4. |
| `ThemeNatalReadingSlot` | Persist accepted public reading state. | AC5, AC14, Task 5. |
| public projection | Exclude raw provider and technical traces. | AC5, AC6, AC10, Task 6. |
| idempotence | Same logical request keeps one slot result. | AC14, Task 7. |
| quota | Consume only after acceptance. | AC13, Task 8. |
| old natal use cases | Prove they are not called. | AC15, Task 9. |
| Free preview | Use contractual fake preview for traversal only. | AC16, Task 10. |
| required validations | Preserve backend lint, integration tests, and scans. | Validation Plan. |
| non-goals | Provider live, final prompt, frontend cutover, physical deletion, full Premium and Free runtime. | Domain Boundary. |

## Current State Evidence

- Evidence 1: `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-430`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer Mode contract read first.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - targeted guardrail IDs from the brief were read.
- Evidence 5: `resolve_guardrails.py` - resolver consulted with backend Basic runtime scope.
- Evidence 6: `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - Basic runtime target checked.
- Evidence 7: `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md` - product action dependency checked.
- Evidence 8: `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md` - slot and run dependency checked.
- Evidence 9: `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md` - generation contract dependency checked.
- Evidence 10: `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py` - Basic plan owner checked.
- Evidence 11: `backend/app/domain/astrology/reading/basic_natal_contracts.py` - Basic public contract owner checked.
- Source-alignment evidence: objectives, ACs, tasks, non-goals, and validations map to the brief without narrowing the runtime closure.

## Domain Boundary

- Domain: backend-runtime
- In scope:
  - Backend Basic full-reading runtime for `theme_natal.reading.basic_full_reading.v1`.
  - Deterministic fake provider modes for valid and rejected provider output.
  - Prompt-visible Basic payload assembly from existing Basic plan and facts.
  - Technical run persistence, accepted public slot persistence, idempotence, and quota timing.
  - Integration tests proving the complete Basic path without a live provider.
- Out of scope:
  - Frontend UI, live provider calls, final editorial live prompt, auth, i18n, styling, build tooling, physical historical code deletion, and Premium runtime.
- Explicit non-goals:
  - No OpenAI or other live provider request is added.
  - No frontend route, screen, React state, generated client, or CSS edit is authorized.
  - No physical deletion of historical natal modules is required in this story.
  - No complete Free or Premium runtime is implemented.
  - No prompt editorial finalization is included.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested backend domain contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the backend Basic fake-provider runtime path and its tests.
  - Keep public exposure limited to accepted Basic projections.
  - Keep live provider execution disabled for this story.
  - Keep frontend behavior unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: CS-427, CS-428, or CS-429 surfaces are unavailable at implementation start.
- Additional validation rules:
  - Runtime evidence must include `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`.
  - Runtime evidence must include `pytest -q backend/tests/integration -k "basic_full_reading or fake_provider or theme_natal" --tb=short`.
  - Architecture evidence must include an `AST guard` proving no call path reaches old natal generation use cases.
  - Persistence evidence must inspect loaded config, DB schema, or ORM models for `ThemeNatalReadingSlot` and `LlmGenerationRun`.
  - Public projection evidence must prove the raw provider response is absent from accepted payloads.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `TestClient`, fake provider modes, DB schema checks, and `AST guard` prove the runtime. |
| Baseline Snapshot | yes | Before and after artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Runtime, provider adapter, projection, persistence, and tests need canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this Basic fake-provider runtime. |
| Contract Shape | yes | Contract key, payload shape, provider JSON, run metadata, and public projection are closed. |
| Batch Migration | no | No batch migration or mass historical conversion is in scope. |
| Reintroduction Guard | yes | Old natal generation branches and invalid public outputs must stay absent. |
| Persistent Evidence | yes | Validation, scan, run, slot, and fake-provider artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Basic selects the target contract. | Evidence profile: json_contract_shape; `pytest` checks `tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC2 | Basic prompt payload is plan-backed. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC3 | Valid fake output is parsed strictly. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC4 | Run metadata persists. | Evidence profile: json_contract_shape; `pytest` checks `tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC5 | Accepted Basic reading persists. | Evidence profile: json_contract_shape; `pytest` checks `tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC6 | Public payload excludes raw provider data. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC7 | Invalid JSON mode is rejected. | Evidence profile: api_error_shape_contract; `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC8 | Unknown field mode is rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC9 | Empty source mode is rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC10 | Invented fact mode is rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC11 | Technical leak mode is rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC12 | Mechanical phrase mode is rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC13 | Short section mode is rejected. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC14 | Quota waits for acceptance. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC15 | Same request is idempotent. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC16 | Old natal use cases are not called. | Evidence profile: ast_architecture_guard; `python` AST guard; `rg` scan over backend runtime paths. |
| AC17 | Free preview traversal stays contractual. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC18 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence artifact paths. |

## Implementation Tasks

- [x] Task 1: Wire Basic `generate_full` to `theme_natal.reading.basic_full_reading.v1`. (AC: AC1)
- [x] Task 2: Build the Basic prompt-visible payload from `BasicNatalReadingPlan` and existing facts. (AC: AC2)
- [x] Task 3: Add a deterministic fake provider with valid and invalid output modes. (AC: AC3, AC7, AC8, AC9, AC10, AC11, AC12, AC13)
- [x] Task 4: Persist `LlmGenerationRun` metadata for every fake provider attempt. (AC: AC4)
- [x] Task 5: Persist accepted `ThemeNatalReadingSlot` payloads only after validation. (AC: AC5, AC6)
- [x] Task 6: Project public Basic readings without raw provider data or technical traces. (AC: AC6)
- [x] Task 7: Prove idempotence for repeated Basic full-reading requests. (AC: AC15)
- [x] Task 8: Consume quota only after accepted public persistence. (AC: AC14)
- [x] Task 9: Add AST and scan guards against old natal generation use cases. (AC: AC16)
- [x] Task 10: Add a minimal contractual fake Free preview only for traversal tests. (AC: AC17)
- [x] Task 11: Persist validation, scan, run, slot, and fake-provider evidence artifacts. (AC: AC18)

## Files to Inspect First

- `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md` - source contract.
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - target runtime architecture.
- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md` - product routing dependency.
- `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md` - slot and run persistence dependency.
- `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md` - strict schema and contract dependency.
- `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py` - Basic plan owner.
- `backend/app/domain/astrology/reading/basic_natal_contracts.py` - Basic public schema owner.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - old natal branch to avoid calling.
- `backend/app/api/v1/routers/public/natal_interpretation.py` - current public route adapter to inspect before routing edits.
- `backend/app/infra/db/models/user_natal_interpretation.py` - existing persistence model to inspect before slot integration.
- `backend/tests/integration` - integration test owner for complete runtime proof.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`.
  - `pytest -q backend/tests/integration -k "basic_full_reading or fake_provider or theme_natal" --tb=short`.
  - `TestClient` or service-level integration tests using loaded config and test DB state.
  - `AST guard` proving old natal generation use cases are not reachable.
- Secondary evidence:
  - Targeted `rg` scans for contract keys, fake provider modes, slot and run symbols, and old natal use-case calls.
- Static scans alone are not sufficient for this story because:
  - Runtime acceptance, rejection, persistence, idempotence, and quota order require executable integration tests.

## Contract Shape

- Contract type:
  - Backend runtime orchestration for one Basic full-reading generation contract.
- Fields:
  - `generation_contract_key`: exactly `theme_natal.reading.basic_full_reading.v1`.
  - `generation_contract_hash`: deterministic hash from the resolved contract snapshot.
  - `output_schema_version`: strict Basic output schema version used for fake provider parsing.
  - `data_hash`: deterministic hash of prompt-visible Basic payload data.
  - `provider_mode`: deterministic fake provider mode used by tests.
  - `slot_status`: one of `generating`, `accepted`, `rejected`, `failed_retriable`, or `superseded`.
  - `validation_status`: accepted or rejected provider result state.
  - `public_payload`: accepted projection without raw provider response.
  - `client_request_id`: idempotence key for repeated traversal.
- Required fields:
  - All fields listed in the `Fields` block are required for the Basic runtime evidence.
- Optional fields:
  - none.
- Status codes:
  - Existing public route status behavior stays unchanged unless CS-427 through CS-429 define the route contract by implementation time.
- Serialization names:
  - Serialization uses exact snake_case field names listed in the `Fields` block.
- Frontend type impact:
  - none; frontend generated client changes are out of scope.
- Generated contract impact:
  - No OpenAPI surface change is required by this story.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/runtime-before.txt`
  - `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/legacy-call-scan-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/runtime-after.txt`
  - `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/legacy-call-scan-after.txt`
- Expected invariant:
  - The only intended behavior delta is the Basic fake-provider full-reading runtime path.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Basic runtime orchestration | `backend/app/services/llm_generation/natal` | `frontend/src/**`, `backend/app/api/**` |
| Fake provider test adapter | `backend/tests/integration` or backend test helpers | `backend/app/infra/**` live clients |
| Basic prompt payload builder | `backend/app/services/llm_generation/natal` | `frontend/src/**` |
| Basic plan source | `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py` | `backend/app/api/**` |
| Basic public projection | `backend/app/domain/astrology/reading/basic_natal_contracts.py` | `frontend/src/**` |
| Slot and run persistence | CS-428 canonical infra or service owners | `backend/app/api/**` direct SQL |
| Runtime integration tests | `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py` | `frontend/src/**` |

## Mandatory Reuse / DRY Constraints

- Reuse the CS-427 product action resolver instead of adding a parallel Basic selector.
- Reuse CS-429 contract keys and strict schemas instead of hand-building unversioned payloads.
- Reuse `BasicNatalReadingPlan` and `basic_natal_contracts.py` for Basic material and public projection.
- Reuse CS-428 slot and run persistence owners instead of adding another public-reading table.
- Keep fake provider modes in one test adapter or one explicitly non-live backend adapter.
- Do not duplicate quota consumption logic.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy route through `natal_interpretation` may generate the new Basic full reading.
- No compatibility route through `natal_interpretation_short` may generate the new Basic full reading.
- No fallback route through `natal_long_free` may satisfy Basic traversal tests.
- Do not call `natal_interpretation`, `natal_interpretation_short`, or `natal_long_free` from the target Basic runtime.
- Do not expose raw provider response data in public payloads.
- Do not persist rejected provider output as an accepted public reading.
- Do not add frontend, live provider, prompt editor, or Premium runtime changes in this story.

## Reintroduction Guard

- Guard target contract key with:
  - `rg -n "theme_natal\\.reading\\.basic_full_reading\\.v1|basic_full_reading|fake_provider" backend/app backend/tests`.
- Guard old generation branches with:
  - `rg -n "natal_interpretation_short|natal_long_free|natal_interpretation" backend/app/services backend/tests/integration`.
- Guard slot and run symbols with:
  - `rg -n "ThemeNatalReadingSlot|LlmGenerationRun|free_preview" backend/app backend/tests`.
- Guard call graph with:
  - `python -B -m pytest -q tests/integration -k "basic_full_reading or fake_provider or theme_natal" --tb=short`.
- Expected result:
  - Target runtime hits appear only in canonical owners, tests, and persisted story evidence.

## Regression Guardrails

| Guardrail | scope -> invariant -> evidence |
|---|---|
| RG-150 | Public boundary -> rejected Basic provider payloads stay non-public -> integration `pytest`. |
| RG-152 | Public projection -> technical trace fields stay private -> projection `pytest` and targeted `rg`. |
| RG-155 | Semantic integrity -> empty sources and padding stay rejected -> fake-mode `pytest`. |
| RG-157 | Quota timing -> debit happens after accepted persistence -> integration `pytest`. |
| RG-164 | Basic source -> runtime uses `BasicNatalReadingPlan` -> unit and integration `pytest`. |
| RG-165 | Basic payload -> prompt-visible data excludes PII, raw scores, and raw IDs -> `pytest` and `rg`. |
| RG-166 | Basic validation -> invalid drafts are rejected before public exposure -> fake-mode `pytest`. |
| RG-167 | Basic runtime -> accepted Basic complete persists through Basic engine -> integration `pytest`. |
| RG-168 | Basic public contract -> unknown and technical fields stay rejected -> contract `pytest`. |
| RG-169 | Basic quality -> mechanical wording and short sections stay rejected -> fake-mode `pytest`. |

Needs-investigation:

- Resolver returned broad backend layout validation IDs, but the brief supplies exact Basic runtime guardrails used above.
- Registry gap: no durable guardrail explicitly names fake provider modes for Basic runtime; this story records the gap without editing the registry.
- Adjacent frontend and style guardrails were omitted because no frontend, CSS, or build surface is in scope.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/validation.txt` | Keep final command output. |
| Runtime output | `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/runtime-after.txt` | Prove accepted runtime path. |
| Fake modes output | `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/fake-provider-modes.txt` | Prove all fake modes. |
| Persistence output | `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/persistence-after.txt` | Prove run and slot state. |
| Legacy call scan | `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/legacy-call-scan-after.txt` | Prove old calls stay absent. |
| Review output | `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this Basic fake-provider runtime.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/services/llm_generation/natal` - add or wire the Basic full-reading runtime.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - inspect before avoiding old natal branches.
- `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py` - reuse Basic plan payload material.
- `backend/app/domain/astrology/reading/basic_natal_contracts.py` - reuse Basic public projection contract.
- `backend/app/api/v1/routers/public/natal_interpretation.py` - inspect route adapter before runtime wiring.
- `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py` - add complete fake-provider path tests.
- `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/runtime-before.txt` - before evidence.
- `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/runtime-after.txt` - runtime evidence.
- `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/fake-provider-modes.txt` - fake-mode evidence.
- `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/persistence-after.txt` - persistence evidence.
- `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/legacy-call-scan-after.txt` - scan evidence.

Likely tests:

- `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py` - complete Basic fake-provider flow.
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` - quota timing regression support.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - accepted-only public boundary support.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/app/infra/clients/**` - out of scope; no live provider client is touched.
- `backend/migrations/**` - out of scope unless CS-428 is not yet physically implemented.
- `backend/docs/**` - out of scope; no documentation mode change is authorized.

## 20. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: activate venv, then run from `backend`: `ruff format .`.
- VC2: activate venv, then run from `backend`: `ruff check .`.
- VC3: activate venv, then run from `backend`: `python -B -m pytest -q tests/integration -k "basic_full_reading or fake_provider or theme_natal" --tb=short`.
- VC4: activate venv, then `python -B -m pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`.
- VC5: activate venv, then run an `AST guard` through collected tests for old natal use-case calls.
- VC6 forbidden pattern: `natal_interpretation_short|natal_long_free|natal_interpretation`.
- VC6 allowed fixture pattern: tests that assert old use cases are not called and story evidence.
- VC6 scan roots: `backend/app/services`, `backend/tests/integration`.
- VC6 command: `rg -n "natal_interpretation_short|natal_long_free|natal_interpretation" backend/app/services backend/tests/integration`.
- VC6 expected false positives: fixtures or tests that assert non-use of the old branches.
- VC7 forbidden pattern: `basic_full_reading|fake_provider|ThemeNatalReadingSlot|LlmGenerationRun|free_preview`.
- VC7 allowed fixture pattern: canonical runtime owners, slot or run owners, tests, and story evidence.
- VC7 scan roots: `backend/app`, `backend/tests`.
- VC7 command: `rg -n "basic_full_reading|fake_provider|ThemeNatalReadingSlot|LlmGenerationRun|free_preview" backend/app backend/tests`.
- VC7 expected false positives: none outside canonical owners, tests, and evidence.
- VC8 forbidden pattern: `raw_provider_response|provider_raw|raw_response`.
- VC8 allowed fixture pattern: technical run storage, tests asserting public absence, and story evidence.
- VC8 scan roots: `backend/app/services`, `backend/tests/integration`.
- VC8 command: `rg -n "raw_provider_response|provider_raw|raw_response" backend/app/services backend/tests/integration`.
- VC8 expected false positives: technical run metadata and tests that assert public payload absence.
- VC9: persist final outputs under `_condamad/stories/CS-430-basic-full-reading-runtime-fake-provider/evidence/validation.txt`.

## Regression Risks

- Dependency risk at implementation start: CS-427, CS-428, and CS-429 surfaces had to be physically available before wiring CS-430.
- Fake provider tests can prove unit behavior without proving the complete Basic traversal.
- Raw provider response data can leak through public projection without a negative public payload assertion.
- Quota can be consumed before acceptance unless the integration test checks the rejected path.
- Minimal Free preview support can drift into a generative Free runtime unless it stays fake and contractual.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all Python commands under `.\.venv\Scripts\Activate.ps1`.
- Keep comments and docstrings in French for new backend application files.
- Keep live provider execution, frontend edits, full Free runtime, Premium runtime, and physical historical deletion out of the implementation diff.

## References

- `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md`
- `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md`
- `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md`
- `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py`
- `backend/app/domain/astrology/reading/basic_natal_contracts.py`
