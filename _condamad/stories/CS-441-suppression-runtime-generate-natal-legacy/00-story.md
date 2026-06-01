# Story CS-441 suppression-runtime-generate-natal-legacy: Corriger Suppression Runtime Generate Natal Legacy
Status: done

## Trigger / Source

- Source brief: `_story_briefs/cs-441-corriger-suppression-runtime-generate-natal-legacy.md`.
- Operating mode: Repo-informed story.
- Fast Story Writer Mode: active; `writer-contract-cheatsheet.md` was used as the priority validator contract.
- Problem statement: CS-436 did not close the executable backend path around `AIEngineAdapter.generate_natal_interpretation`.
- Review trigger: CS-440 review finding `CR-4` blocks closure because positive Basic and Free tests still exercise the old adapter method.
- Source-alignment evidence: every source primitive maps to ACs, tasks, scans, evidence artifacts, non-goals, or blocker rules.

## Objective

Delete the executable natal generation entry point `AIEngineAdapter.generate_natal_interpretation` from `backend/app`.
Remove application calls and positive mocks that keep this provider-capable path alive.
Keep historical readonly reading and the modern `theme_natal` Basic runtime functional.

## Target State

- `backend/app/domain/llm/runtime/adapter.py` no longer defines `AIEngineAdapter.generate_natal_interpretation`.
- `NatalInterpretationService` no longer calls `AIEngineAdapter.generate_natal_interpretation`.
- Runtime natal code no longer builds `NatalExecutionInput` for `use_case_key="natal_interpretation"`.
- `level` and `variant_code` no longer select a provider runtime through the removed path.
- Positive Basic and Free tests no longer mock `generate_natal_interpretation`.
- Historical readonly rows remain readable without invoking a provider.
- `ThemeNatalBasicFullReadingRuntime` remains the canonical Basic generation runtime.
- CS-440 `CR-4` is closed for the runtime adapter and positive-test portion.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-441-corriger-suppression-runtime-generate-natal-legacy.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-441`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted ID search read local guardrails only.
- Evidence 4: `_story_briefs/cs-436-supprimer-service-generation-natale-legacy.md` - upstream deletion intent was read.
- Evidence 5: `_condamad/reports/cs-439-cs-440-delivery-report.md` - CS-440 partial-delivery state was read.
- Evidence 6: `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md` - CS-440 residual risks were read.
- Evidence 7: `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md` - `CR-4` blocker was read.
- Evidence 8: `backend/app/domain/llm/runtime/adapter.py` still defines `async def generate_natal_interpretation`.
- Evidence 9: `backend/app/services/llm_generation/natal/interpretation_service.py` still builds `NatalExecutionInput`.
- Evidence 10: targeted scans found positive mocks in `backend/tests` and `backend/app/tests`.
- Repository structure alert: expected backend roots exist in this workspace; no implementation-created backend root is required.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `AIEngineAdapter.generate_natal_interpretation` | in scope | AC1, Task 1, Delete-Only Rule |
| `NatalInterpretationService` provider call | in scope | AC2, Task 2, Runtime Source of Truth |
| `NatalExecutionInput` from natal service | in scope | AC3, Task 3, Reintroduction Guard |
| `use_case_key=natal_interpretation` | in scope | AC4, Task 3, Contract Shape |
| `variant_code` provider selection | in scope | AC5, Task 4, Ownership Routing |
| `level` provider selection | in scope | AC5, Task 4, Ownership Routing |
| Positive adapter mocks | in scope | AC6, Task 5, Reintroduction Guard |
| Historical readonly rows | in scope | AC7, Task 6, Allowlist Register |
| `theme_natal` Basic runtime | in scope | AC8, Task 7, Regression Guardrails |
| CS-440 `CR-4` runtime blocker | in scope | AC9, Task 8, Persistent Evidence |
| Before and after scans | in scope | AC10, Task 9, Baseline Snapshot |
| Catalogues, seeds, scripts | out of scope | Explicit non-goals; CS-442 owns them |
| Public historical API deletion | out of scope | Explicit non-goals; CS-443 owns it |
| Astrological calculations | out of scope | Explicit non-goals |
| `_condamad/run-state.json` | out of scope | Explicit non-goals |

## Domain Boundary

- Domain: backend-llm-natal-generation
- In scope:
  - Backend runtime adapter deletion under `backend/app/domain/llm/runtime/adapter.py`.
  - Backend natal service call removal under `backend/app/services/llm_generation/natal/interpretation_service.py`.
  - Backend tests that currently preserve positive execution of the removed adapter method.
  - Backend architecture guards that enforce zero runtime hit for removed symbols.
  - Story evidence under `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence`.
- Out of scope:
  - Frontend UI, DB schema migration, auth, i18n, styling, build tooling, prompt catalogues, seeds, scripts, and public route deletion.
- Explicit non-goals:
  - No catalogue, seed, script, or prompt cleanup owned by CS-442.
  - No removal of the public historical API owned by CS-443.
  - No changes to astrological calculations.
  - No modification of `_condamad/run-state.json`.
  - No stub, alias, wrapper, compatibility method, fallback, or runtime guard named `generate_natal_interpretation`.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story removes an internal provider-capable historical generation facade and its adapter entry point.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Historical reads remain readonly.
  - Basic public generation remains under `theme_natal` product and LLM contracts.
  - Legacy generation attempts fail before provider request construction.
  - The only allowed surface delta is removal of the old provider-capable runtime entry point.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: a production consumer proves that the removed adapter method is externally active.
- Additional validation rules:
  - Use `AST guard` and bounded `rg` scans to prove removed symbols are absent from `backend/app`.
  - Use full targeted pytest paths for Basic runtime, readonly, and architecture behavior.
  - Use `app.routes` and `app.openapi()` to prove no public route preserves the removed runtime path.
  - Treat `rg` code 1 as PASS only for documented zero-hit scans.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `AST guard`, `app.routes`, and `app.openapi()` prove runtime behavior. |
| Baseline Snapshot | yes | Before and after scans prove the only allowed surface delta. |
| Ownership Routing | yes | Basic generation must stay owned by `theme_natal`, not the legacy service. |
| Allowlist Exception | yes | Remaining readonly historical helpers must be documented and non-generative. |
| Contract Shape | yes | Legacy rejections must name `/v1/theme-natal/readings` without provider payloads. |
| Batch Migration | no | No data migration, prompt migration, or bulk conversion is in scope. |
| Reintroduction Guard | yes | The removed method and input builder must fail deterministic guards. |
| Persistent Evidence | yes | Scans, validation output, audit, and review handoff must be persisted. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The removed adapter method is absent from `backend/app`. | Evidence profile: python_import_absence; `rg` scans `backend/app`; `AST guard`. |
| AC2 | Service cannot call the removed method. | Evidence profile: ast_architecture_guard; `python` AST guard. |
| AC3 | The natal service no longer builds `NatalExecutionInput`. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `backend/app/services/llm_generation/natal`. |
| AC4 | The old runtime use case is not executable. | Evidence profile: no_legacy_contract; `AST guard`; `tests/architecture/test_llm_legacy_extinction.py`. |
| AC5 | `level` no longer selects a provider runtime. | Evidence profile: ast_architecture_guard; `AST guard`; `rg` scans natal service and adapter. |
| AC6 | Positive tests no longer mock the removed adapter method. | Evidence profile: no_legacy_contract; `rg` scans `backend/tests backend/app/tests`. |
| AC7 | Historical readonly rows remain readable without provider access. | Evidence profile: json_contract_shape; `backend/tests/integration/test_theme_natal_public_reads.py`. |
| AC8 | Basic runtime uses `theme_natal` slots. | Evidence profile: no_legacy_contract; `pytest -q backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`. |
| AC9 | CS-440 `CR-4` adapter blocker is resolved. | Evidence profile: baseline_before_after_diff; `AST guard`; `pytest`. |
| AC10 | Zero-hit evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks evidence artifact paths. |
| AC11 | Public routes do not preserve the removed runtime path. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes` and `app.openapi()`. |

## Implementation Tasks

- [x] Task 1: Delete `AIEngineAdapter.generate_natal_interpretation` from the runtime adapter. (AC: AC1)
- [x] Task 2: Remove the `NatalInterpretationService` call to the deleted adapter method. (AC: AC2)
- [x] Task 3: Remove `NatalExecutionInput` construction from the natal service generator path. (AC: AC3, AC4)
- [x] Task 4: Delete provider selection branches driven by `level` and `variant_code` in the removed path. (AC: AC5)
- [x] Task 5: Replace positive adapter mocks with rejection, extinction, or readonly tests. (AC: AC6)
- [x] Task 6: Preserve readonly historical reading tests without provider invocation. (AC: AC7)
- [x] Task 7: Prove Basic runtime still uses `theme_natal` slots and contracts. (AC: AC8)
- [x] Task 8: Update CS-440 guard coverage for zero-hit `generate_natal_interpretation` in `backend/app`. (AC: AC9)
- [x] Task 9: Persist before and after scans, validation output, and CR-4 closure notes. (AC: AC10)
- [x] Task 10: Add runtime route and OpenAPI checks proving no public preservation route. (AC: AC11)

## Files to Inspect First

- `_story_briefs/cs-441-corriger-suppression-runtime-generate-natal-legacy.md` - source contract.
- `_story_briefs/cs-436-supprimer-service-generation-natale-legacy.md` - upstream deletion contract.
- `_condamad/reports/cs-439-cs-440-delivery-report.md` - delivery context.
- `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md` - zero-hit residual context.
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md` - `CR-4` blocker.
- `backend/app/domain/llm/runtime/adapter.py` - runtime adapter owner.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - legacy generator and readonly projection owner.
- `backend/app/services/llm_generation/natal/theme_natal_basic_full_runtime.py` - canonical Basic runtime owner.
- `backend/app/domain/theme_natal/generation_contracts.py` - canonical generation contract owner.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - zero-hit architecture guard owner.
- `backend/tests/architecture/test_llm_legacy_extinction.py` - LLM extinction guard owner.
- `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py` - Basic runtime behavior tests.
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py` - product-action behavior tests.
- `backend/tests/integration/test_theme_natal_public_reads.py` - readonly historical read behavior tests.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, `TestClient`, `AST guard`, `app.routes`, and `app.openapi()`.
- Secondary evidence:
  - Targeted `rg` scans for removed symbols, positive mocks, and unauthorized runtime inputs.
- Static scans alone are not sufficient for this story because:
  - Readonly behavior and Basic runtime persistence must still execute through tests.

## Contract Shape

- Contract type:
  - Backend runtime removal contract and controlled legacy rejection contract.
- Fields:
  - `replacement`: exact value `/v1/theme-natal/readings` for remaining legacy rejection responses.
- Required fields:
  - `replacement`.
- Optional fields:
  - none for the removed generator path.
- Forbidden runtime input builders:
  - `NatalExecutionInput` from `NatalInterpretationService`.
  - `use_case_key="natal_interpretation"` from legacy natal service.
  - Provider input selection from `level` or `variant_code` inside the removed path.
- Forbidden provider entry point:
  - `AIEngineAdapter.generate_natal_interpretation`.
- Status codes:
  - Existing controlled legacy surfaces remain non-generative and fail before provider execution.
- Serialization names:
  - `replacement` is emitted as `replacement`.
- Frontend type impact:
  - none; frontend is out of scope.
- Generated contract impact:
  - `app.openapi()` and `app.routes` must not gain a public preservation route for the removed runtime path.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/runtime-generate-natal-before.txt`
  - `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/positive-mocks-before.txt`
  - `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/runtime-generate-natal-after.txt`
  - `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/positive-mocks-after.txt`
  - `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/openapi-after.json`
- Expected invariant:
  - The only allowed surface delta is deletion of the provider-capable adapter path and replacement of positive tests.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Public Basic natal generation | `theme_natal_basic_full_runtime.py` | `NatalInterpretationService.interpret` |
| Theme natal generation contracts | `backend/app/domain/theme_natal/generation_contracts.py` | Raw `natal_interpretation` runtime |
| Provider request construction | Contract-bound gateway and theme natal runtime | `AIEngineAdapter.generate_natal_interpretation` |
| Historical row reading | Readonly projection helpers in natal service module | Provider-capable generation branch |
| CS-440 zero-hit enforcement | Architecture guard tests | Broad allowlist or positive mock |

## Removal Classification Rules

- `canonical-active`: modern `theme_natal` runtime owner or readonly projection required by production code.
- `external-active`: generated contract, public doc, route, or known consumer still depends on the removed symbol.
- `historical-facade`: provider-capable path exists only to preserve historical generation behavior.
- `dead`: symbol has zero production, test, docs, generated contract, and known external consumers after scans.
- `needs-user-decision`: scans prove unresolved deletion risk that cannot be closed inside this story.
- Required decision:
  - `historical-facade` and `dead` items must be deleted.
  - `external-active` items must block deletion until the user decision is recorded.

## Removal Audit Format

The implementation must persist:

`_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/removal-audit.md`

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

- `Classification` must use `canonical-active`, `external-active`, `historical-facade`, `dead`, or `needs-user-decision`.
- `Decision` must use `keep`, `delete`, `replace-consumer`, or `needs-user-decision`.
- `Proof` must include command output, file path evidence, `app.openapi()`, `app.routes`, `pytest`, or `rg`.
- `Risk` must be filled for every `delete` or `needs-user-decision` row.

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Public Basic generation | `ThemeNatalBasicFullReadingRuntime` | `NatalInterpretationService.interpret` |
| Public product action | `theme_natal` product-action resolver | Legacy `level` or `variant_code` routing |
| Provider request construction | Contract-bound gateway runtime | Removed adapter method |
| Historical interpretation display | Readonly projection helper | Provider-capable service branch |
| Residual legacy proof | Architecture guards and story evidence | Unclassified test mock |

## Delete-Only Rule

- Removable legacy generator paths must be deleted rather than redirected.
- Removable legacy generator paths are deleted, not repointed.
- No wrapper may preserve the removed adapter method.
- No alias may preserve the removed adapter method.
- No compatibility method may keep provider-capable legacy generation active.
- No fallback may replace the deleted provider branch.
- No re-export may preserve the deleted import path.
- Readonly projection is allowed only with deterministic provider-call prevention.

## External Usage Blocker

- External-active consumers block deletion until a user decision is recorded in the removal audit.
- External-active items must not be deleted.
- The blocker must identify the consumer, exact surface, deletion risk, and minimal safe next action.
- `needs-user-decision` rows must keep implementation stopped for that item.
- Historical persisted data is not external-active by itself when it remains readable without provider calls.

## Generated Contract Check

- Generated contract check: required
- `app.openapi()` must prove no new public generation schema authorizes the removed runtime path.
- `app.routes` must prove no public route was added to preserve provider-capable legacy generation.
- OpenAPI before and after snapshots must be persisted under this story evidence directory.

## Mandatory Reuse / DRY Constraints

- Reuse CS-440 architecture guard files instead of creating a second zero-hit guard suite.
- Reuse existing theme natal product-action and Basic runtime tests for canonical path proof.
- Reuse readonly historical projection helpers instead of duplicating projection logic.
- Keep one removal audit artifact for this corrective runtime deletion.
- Do not add a second provider adapter, prompt wrapper, compatibility service, or fallback route.

## No Legacy / Forbidden Paths

- No legacy provider-capable natal generation path may remain.
- No compatibility provider-capable natal generation path may remain.
- No fallback provider-capable natal generation path may remain.
- Forbidden symbols in runtime scope:
  - `AIEngineAdapter.generate_natal_interpretation`
  - `async def generate_natal_interpretation`
  - `generate_natal_interpretation(`
  - `NatalExecutionInput(`
  - `use_case_key="natal_interpretation"`
  - `use_case_key = "natal_interpretation"`
- Remaining hits must be readonly projection code, historical evidence, negative tests, or migration proof.

## Reintroduction Guard

- Add or update an architecture guard that fails when `generate_natal_interpretation` exists under `backend/app`.
- Add or update an architecture guard that fails when `NatalInterpretationService` builds `NatalExecutionInput`.
- Add or update a guard that fails when positive tests mock the removed adapter method.
- The implementation must require an architecture guard against reintroduction.
- The architecture guard must fail when a removed generator path is reintroduced.
- Add bounded `rg` scans with documented allowed fixture patterns and expected false positives.
- Deterministic sources: importable Python modules, AST inspection, generated OpenAPI paths, registered routes, and forbidden symbols.

## Regression Guardrails

| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-001 `remove-historical-facade-routes` | old facade -> no wrapper or alias -> architecture `pytest` and `rg`. |
| RG-005 `remove-api-v1-router-logic` | API boundary -> no moved business logic -> `app.routes` and import scans. |
| RG-006 `api-adapter-boundary-convergence` | adapter boundary -> non-API layers avoid `app.api` -> `AST guard`. |
| RG-018 `block-supported-family-prompt-fallbacks` | natal prompts -> no fallback owner -> llm extinction `pytest`. |
| RG-149 `CS-350-prompt-generation-current-implementation` | prompt map -> provider-capable flows classified -> targeted `rg`. |
| RG-150 `CS-384-separer-interpretations-natales-acceptees-rejets-llm` | rejected reads -> not public -> readonly `pytest`. |
| RG-164 `CS-415` | Basic owner -> no old selection -> owner scan and runtime tests. |
| RG-167 `CS-418` | Basic runtime -> Basic engine persists through slots -> Basic runtime `pytest`. |
| RG-173 `CS-435` | public generation -> product+LLM contracts only -> `pytest`, routes, OpenAPI, `rg`. |
| RG-174 `CS-440` | zero runtime hit -> removed symbols absent from public/runtime paths -> architecture `pytest` and scans. |

- Needs-investigation: resolver returned only generic `RG-002`; brief-required IDs were loaded by targeted ID search.
- Registry gap: no exact route-specific invariant for `generate_natal_interpretation`; normal generation must not enrich the registry.
- Non-applicable example: frontend DOM guardrails are outside this backend runtime deletion scope.
- Non-applicable example: DB migration guardrails are outside this no-migration scope.
- Non-applicable example: CSS/style guardrails are outside this backend-only scope.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Removal audit | `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/removal-audit.md` | Classify removed items. |
| Runtime scan before | `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/runtime-generate-natal-before.txt` | Capture starting hits. |
| Runtime scan after | `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/runtime-generate-natal-after.txt` | Capture final hits. |
| Positive mocks before | `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/positive-mocks-before.txt` | Capture test mocks. |
| Positive mocks after | `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/positive-mocks-after.txt` | Prove test mocks are gone. |
| OpenAPI before | `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/openapi-before.json` | Capture API baseline. |
| OpenAPI after | `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/openapi-after.json` | Capture API result. |
| Validation output | `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/validation.txt` | Store final commands. |
| Review output | `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist required: yes
- Required artifact:
  - `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/removal-audit.md`
- Required operational columns for readonly survivors:
  - `symbol | file | reason | allowed_context | non_generative_proof | owner | expiry_decision`
- Allowed contexts:
  - `historical-readonly`
  - `test-guard`
  - `migration-proof`
- Not allowed:
  - public runtime generation, provider call, unclassified fallback, hidden wrapper, stub, alias, or soft-disabled generator.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `interpretation_service.py` | Readonly projection helpers | Historical rows stay readable. | Keep until CS-443 retires the historical API. |

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/domain/llm/runtime/adapter.py` - delete `generate_natal_interpretation`.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - remove deleted adapter calls and input construction.
- `backend/app/services/llm_generation/natal/theme_natal_basic_full_runtime.py` - preserve canonical Basic runtime behavior.
- `backend/app/domain/theme_natal/generation_contracts.py` - preserve canonical generation contracts.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - update zero-hit guard.
- `backend/tests/architecture/test_llm_legacy_extinction.py` - update removed-symbol guard.
- `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py` - prove Basic runtime path.
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py` - prove product-action path.
- `backend/tests/integration/test_theme_natal_public_reads.py` - prove readonly historical reads.
- `backend/app/tests/unit/test_ai_engine_adapter.py` - remove positive adapter-method tests.
- `backend/app/tests/unit/test_natal_interpretation_service.py` - replace positive adapter mocks.
- `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence` - persist audit evidence.

Likely tests:

- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`
- `backend/tests/architecture/test_llm_legacy_extinction.py`
- `backend/tests/unit/domain/theme_natal`
- `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py`
- `backend/tests/integration/test_theme_natal_public_reads.py`
- `backend/app/tests/unit/test_natal_interpretation_service.py`
- `backend/app/tests/unit/test_ai_engine_adapter.py`

Files not expected to change:

- `frontend/src` - out of scope; no frontend surface is touched.
- `backend/migrations` - out of scope; no DB migration is authorized.
- `backend/alembic` - out of scope; no DB migration is authorized.
- `_condamad/run-state.json` - explicitly out of scope.
- `_condamad/stories/regression-guardrails.md` - normal story generation must not enrich the registry.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
Push-Location backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/domain/theme_natal `
  tests/integration/test_theme_natal_basic_full_reading_runtime.py `
  tests/integration/test_theme_natal_public_api_product_actions.py `
  tests/integration/test_theme_natal_public_reads.py --tb=short
python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py tests/architecture/test_llm_legacy_extinction.py --tb=short
Pop-Location
```

Runtime contract commands from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "backend"
python -B -c "from app.main import app; assert '/v1/theme-natal/readings' in str(app.openapi())"
python -B -c "from app.main import app; assert any('/v1/theme-natal/readings' in getattr(r, 'path', '') for r in app.routes)"
python -B -c "from pathlib import Path; p=Path('backend/app/domain/llm/runtime/adapter.py'); assert 'generate_natal_interpretation' not in p.read_text()"
python -B -c "from pathlib import Path; p=Path('_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/removal-audit.md'); assert p.exists()"
```

Scans from repository root:

```powershell
rg -n "generate_natal_interpretation" backend/app
rg -n "AIEngineAdapter\.generate_natal_interpretation|fake_generate_natal_interpretation" `
  backend/tests backend/app/tests
rg -n "patch\.object\(AIEngineAdapter, `"generate_natal_interpretation`"" `
  backend/tests backend/app/tests
rg -n "NatalExecutionInput\(|use_case_key=.*natal_interpretation" `
  backend/app/services/llm_generation/natal backend/app/domain/llm/runtime
```

- Scan 1 forbidden pattern: `generate_natal_interpretation`.
- Scan 1 roots: `backend/app`.
- Scan 1 allowed fixture pattern: none in runtime code.
- Scan 1 expected false positives: zero.
- Scan 2 forbidden pattern: positive tests that preserve adapter method mocking.
- Scan 2 roots: `backend/tests backend/app/tests`.
- Scan 2 allowed fixture pattern: negative architecture guards proving the symbol is absent.
- Scan 2 expected false positives: architecture guard literals only.
- Scan 3 forbidden pattern: legacy natal execution input or old runtime use case.
- Scan 3 roots: `backend/app/services/llm_generation/natal backend/app/domain/llm/runtime`.
- Scan 3 allowed fixture pattern: none in runtime code.
- Scan 3 expected false positives: zero.

## Regression Risks

- Historical row reading may lose readonly projection behavior while removing provider calls.
- A positive test may keep the deleted adapter method alive through a mock.
- Basic generation may regress if tests stop proving `theme_natal` slot persistence.
- A future implementation may recreate the symbol as a stub unless architecture guards reject it.
- CS-440 may remain blocked if `CR-4` closure evidence is not persisted.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Run Python commands only after activating `.\.venv\Scripts\Activate.ps1`.
- Keep comments and docstrings in French for new or significantly modified application files.
- Do not add a compatibility shim, alias, fallback, wrapper, stub, or re-export for the deleted adapter method.
- Keep `_condamad/run-state.json` unchanged.

## References

- `_story_briefs/cs-441-corriger-suppression-runtime-generate-natal-legacy.md`
- `_story_briefs/cs-436-supprimer-service-generation-natale-legacy.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/cs-439-cs-440-delivery-report.md`
- `_condamad/reports/cs-440-zero-hit-legacy-natal-tests-guards.md`
- `_condamad/stories/CS-440-zero-hit-legacy-natal-tests-guards/generated/11-code-review.md`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/theme_natal_basic_full_runtime.py`
- `backend/app/domain/theme_natal/generation_contracts.py`
