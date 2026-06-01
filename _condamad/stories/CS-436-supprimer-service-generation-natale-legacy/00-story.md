# Story CS-436 supprimer-service-generation-natale-legacy: Supprimer Service Generation Natale Legacy
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-436-supprimer-service-generation-natale-legacy.md`.
- Operating mode: Repo-informed story.
- Dependency: CS-426 to CS-435 are delivered and provide the Big Bang theme natal product-action foundation.
- Dependency: CS-434 allowlist classifies remaining legacy natal hits before this deeper service deletion.
- Problem statement: `NatalInterpretationService.interpret` and `AIEngineAdapter.generate_natal_interpretation` remain provider-capable.
- Source-alignment evidence: every source primitive maps to ACs, tasks, scans, evidence artifacts, non-goals, or blocker rules.

## Objective

Delete the remaining backend service path that can generate a natal reading through the historical provider entry point.
Keep historical persisted interpretations readable only through readonly projection code, while modern generation stays under `theme_natal`.

## Target State

- `NatalInterpretationService.interpret` is gone or made non-provider-capable by deleting its generator branch.
- `AIEngineAdapter.generate_natal_interpretation` is physically absent from `backend/app`.
- No backend runtime path builds `NatalExecutionInput` for `use_case_key="natal_interpretation"`.
- Public Basic generation uses `ThemeNatalBasicFullReadingRuntime` and `theme_natal` contracts.
- Premium public generation has no implicit legacy provider path.
- Historical `UserNatalInterpretationModel` rows remain readable through named readonly projection code.
- Remaining legacy errors fail before provider execution and mention `/v1/theme-natal/readings`.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-436-supprimer-service-generation-natale-legacy.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-436`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted ID search read the local guardrails from the brief.
- Evidence 4: `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md` was read.
- Evidence 5: `backend/app/services/llm_generation/natal/interpretation_service.py` still builds `NatalExecutionInput`.
- Evidence 6: `backend/app/domain/llm/runtime/adapter.py` still defines `AIEngineAdapter.generate_natal_interpretation`.
- Evidence 7: targeted test scan found nominal mocks and direct calls for `generate_natal_interpretation`.
- Evidence 8: reports from `2026-06-01` confirm that raw `natal_interpretation` generation must be extinguished.
- Evidence 9: delivery report CS-426 to CS-435 documents residual legacy risks after CS-434 and CS-435.
- Repository structure alert: expected backend roots exist in this workspace; no implementation-created backend root is required.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `NatalInterpretationService.interpret` | in scope | AC1, Task 1, Delete-Only Rule |
| `NatalExecutionInput` from natal service | in scope | AC2, Task 2, Reintroduction Guard |
| `AIEngineAdapter.generate_natal_interpretation` | in scope | AC3, Task 3, Generated Contract Check |
| `level`, `variant_code`, `module`, `question` provider inputs | in scope | AC2, AC10, Task 2 |
| `use_case_key=natal_interpretation` | in scope | AC2, AC10, Task 2 |
| Basic public generation | in scope | AC4, Task 4, Regression Guardrails |
| Premium public generation | in scope | AC5, Task 5, External Usage Blocker |
| `UserNatalInterpretationModel` readonly reading | in scope | AC6, Task 6, Allowlist Register |
| Legacy error response | in scope | AC7, Task 7, Contract Shape |
| Legacy nominal tests | in scope | AC8, Task 8, Reintroduction Guard |
| Reduced readonly allowlist | in scope | AC9, Task 9, Persistent Evidence |
| Premium runtime buildout | out of scope | Explicit non-goals |
| Historical data migration | out of scope | Explicit non-goals |
| GET/PDF historical route deletion | out of scope | Explicit non-goals |
| `_condamad/run-state.json` | out of scope | Explicit non-goals |

## Domain Boundary

- Domain: backend-llm-natal-generation
- In scope:
  - Backend natal generation service under `backend/app/services/llm_generation/natal/interpretation_service.py`.
  - LLM runtime adapter under `backend/app/domain/llm/runtime/adapter.py`.
  - Theme natal product-action and Basic runtime tests proving the canonical path.
  - Backend tests that currently preserve nominal legacy provider execution.
  - Story evidence under `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/**`.
- Out of scope:
  - Frontend UI, DB schema migration, auth, i18n, styling, build tooling, Stripe, route GET/PDF deletion, and `_condamad/run-state.json`.
- Explicit non-goals:
  - No Premium runtime completion.
  - No migration of historical persisted data.
  - No deletion of historical GET/PDF routes covered by CS-438.
  - No global entitlement `variant_code` rename.
  - No compatibility method, alias, facade, fallback, wrapper, stub, re-export, or soft-disabled provider entry point.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story deletes an internal provider-capable historical generation facade and its adapter entry point.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Historical reads remain readonly.
  - Public Basic generation remains on `theme_natal` product and LLM contracts.
  - Legacy attempts fail before provider execution.
  - The only allowed surface delta is deletion of the provider-capable legacy path.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: a production consumer proves that `generate_natal_interpretation` is externally active.
- Additional validation rules:
  - Use `pytest` and `TestClient` for public Basic and legacy-attempt behavior.
  - Use `app.routes` and `app.openapi()` only to prove public routes remain non-generative.
  - Use `AST guard` and bounded `rg` scans for removed symbols and provider-call absence.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pytest`, `TestClient`, `app.routes`, and `app.openapi()` prove runtime behavior. |
| Baseline Snapshot | yes | Before and after symbol scans prove the only allowed surface delta. |
| Ownership Routing | yes | Generation must stay owned by `theme_natal`, not the legacy service. |
| Allowlist Exception | yes | Remaining readonly helpers must be documented with owner and expiry decision. |
| Contract Shape | yes | Legacy failures must expose the replacement route without provider payloads. |
| Batch Migration | no | No historical data migration or bulk conversion is in scope. |
| Reintroduction Guard | yes | Deleted methods and input builders must fail deterministic guards. |
| Persistent Evidence | yes | Removal audit, allowlist, scans, tests, and review artifacts must be persisted. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `NatalInterpretationService.interpret` cannot call a provider. | Evidence profile: ast_architecture_guard; `pytest -q backend/tests/architecture`; `AST guard`. |
| AC2 | Legacy natal service no longer builds `NatalExecutionInput`. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `backend/app/services/llm_generation/natal`. |
| AC3 | `AIEngineAdapter.generate_natal_interpretation` is absent. | Evidence profile: python_import_absence; `python` import guard; `rg` scans `backend/app`. |
| AC4 | Basic public generation uses `theme_natal` contracts. | Evidence profile: no_legacy_contract; `pytest -q backend/tests/integration`. |
| AC5 | Premium legacy attempts fail before provider. | Evidence profile: external_usage_blocker; `pytest -q backend/tests/llm_orchestration/test_llm_legacy_extinction.py`. |
| AC6 | Readonly historical rows remain readable. | Evidence profile: json_contract_shape; `pytest -q backend/app/tests/unit/test_natal_interpretation_service_v2.py`. |
| AC7 | Legacy failure messages name `/v1/theme-natal/readings`. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration`. |
| AC8 | Nominal tests do not mock the removed adapter method. | Evidence profile: no_legacy_contract; `rg` scans `backend/tests backend/app/tests`. |
| AC9 | Readonly survivors are allowlisted. | Evidence profile: allowlist_register_validated; `python` checks `legacy-readonly-allowlist.md`. |
| AC10 | Removed generator symbols cannot reappear. | Evidence profile: reintroduction_guard; `AST guard`; `rg` scans symbols; `pytest -q backend/tests/architecture`. |

## Implementation Tasks

- [ ] Task 1: Delete the provider-capable body of `NatalInterpretationService.interpret`. (AC: AC1)
- [ ] Task 2: Remove `NatalExecutionInput` construction from the legacy natal service. (AC: AC2)
- [ ] Task 3: Physically delete `AIEngineAdapter.generate_natal_interpretation`. (AC: AC3)
- [ ] Task 4: Keep Basic generation routed only through product-action and Basic runtime owners. (AC: AC4)
- [ ] Task 5: Convert Premium legacy calls into pre-provider failures until an explicit Premium runtime exists. (AC: AC5)
- [ ] Task 6: Extract or retain readonly historical projection helpers with no provider access. (AC: AC6)
- [ ] Task 7: Preserve the replacement route message for remaining legacy failures. (AC: AC7)
- [ ] Task 8: Replace nominal mocks of the removed adapter method with extinction tests. (AC: AC8)
- [ ] Task 9: Persist a reduced readonly allowlist with owner and expiry decision. (AC: AC9)
- [ ] Task 10: Add or update architecture guards for removed symbols. (AC: AC10)
- [ ] Task 11: Persist before and after scans plus validation output. (AC: AC2, AC3, AC9, AC10)

## Files to Inspect First

- `_story_briefs/cs-436-supprimer-service-generation-natale-legacy.md` - source contract.
- `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md` - prior allowlist.
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md` - live-test source.
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - Big Bang architecture source.
- `_condamad/reports/cs-426-cs-427-cs-428-cs-429-cs-430-cs-431-cs-432-cs-433-cs-434-cs-435-delivery-report.md` - delivery source.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - legacy generator and readonly projection owner.
- `backend/app/domain/llm/runtime/adapter.py` - legacy provider adapter method owner.
- `backend/app/services/llm_generation/natal/theme_natal_product_actions.py` - canonical product-action owner.
- `backend/app/services/llm_generation/natal/theme_natal_basic_full_runtime.py` - canonical Basic runtime owner.
- `backend/app/domain/theme_natal/generation_contracts.py` - canonical generation contract owner.
- `backend/tests/architecture/test_llm_legacy_extinction.py` - existing architecture guard.
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py` - public product-action contract tests.
- `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py` - Basic runtime contract tests.
- `backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py` - gateway contract tests.
- `backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py` - rejection workflow tests.

## Runtime Source of Truth

- Primary source of truth:
  - `pytest`, `TestClient`, `AST guard`, `app.routes`, and `app.openapi()`.
- Secondary evidence:
  - Targeted `rg` scans for removed symbols, input builders, and nominal mocks.
- Static scans alone are not sufficient for this story because:
  - Legacy attempts must fail before provider execution and Basic must still run through the canonical runtime.

## Contract Shape

- Contract type:
  - Backend runtime deletion contract and controlled legacy failure contract.
- Fields:
  - `replacement`: exact value `/v1/theme-natal/readings` for remaining legacy failure responses.
- Required fields:
  - `replacement`.
- Optional fields:
  - none for the removed generator path.
- Forbidden runtime input builders:
  - `NatalExecutionInput` from `NatalInterpretationService`.
  - `use_case_key="natal_interpretation"` from legacy natal service.
  - Provider inputs derived from `level`, `variant_code`, `module`, or `question` inside the legacy path.
- Forbidden provider entry point:
  - `AIEngineAdapter.generate_natal_interpretation`.
- Status codes:
  - Existing controlled legacy surfaces must remain non-generative and fail before provider execution.
- Serialization names:
  - `replacement` is emitted as `replacement`.
- Frontend type impact:
  - none; frontend is out of scope.
- Generated contract impact:
  - `app.openapi()` and `app.routes` must not gain a new public generation path.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/legacy-service-scan-before.txt`
  - `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/openapi-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/legacy-service-scan-after.txt`
  - `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/openapi-after.json`
- Expected invariant:
  - The only allowed surface delta is removal of the provider-capable legacy service and adapter entry point.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Public Basic natal generation | `theme_natal_product_actions.py` and `theme_natal_basic_full_runtime.py` | `NatalInterpretationService.interpret` |
| Theme natal generation contracts | `backend/app/domain/theme_natal/generation_contracts.py` | Raw `natal_interpretation` use case |
| Provider execution | Contract-bound gateway and theme natal runtime | `AIEngineAdapter.generate_natal_interpretation` |
| Historical row reading | Readonly projection helpers in natal service module | Provider-capable generation branch |
| Legacy survivor classification | Story evidence allowlist | Untracked inline survival |

## Removal Classification Rules

- `canonical-active`: modern `theme_natal` generation owner or readonly projection still required by production code.
- `external-active`: generated contract, public doc, internal route, or known consumer still depends on the removed symbol.
- `historical-facade`: provider-capable path exists only to preserve historical generation behavior.
- `dead`: symbol has no production, test, docs, generated contract, or known external consumer after scans.
- `needs-user-decision`: scans prove unresolved deletion risk that cannot be closed inside this story.
- Required decision:
  - `historical-facade` and `dead` items must be deleted.
  - `external-active` items must block deletion until the user decision is recorded.

## Removal Audit Format

The implementation must persist:

`_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/removal-audit.md`

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
| Public product action | `theme_natal_product_actions.py` | Legacy level or variant routing |
| Provider request construction | Contract-bound gateway runtime | `NatalExecutionInput` inside legacy natal service |
| Historical interpretation display | Readonly projection helper | `AIEngineAdapter.generate_natal_interpretation` |
| Residual legacy proof | `legacy-readonly-allowlist.md` | Unclassified retained method |

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
- `app.openapi()` must prove no new public generation schema authorizes the removed service path.
- `app.routes` must prove no public route was added to preserve provider-capable legacy generation.
- OpenAPI before and after snapshots must be persisted under this story evidence directory.

## Mandatory Reuse / DRY Constraints

- Reuse CS-434 allowlist decisions instead of creating a second broad legacy inventory.
- Reuse existing theme natal product-action and Basic runtime tests for canonical path proof.
- Reuse or update `test_llm_legacy_extinction.py` instead of adding a duplicate architecture guard suite.
- Keep one reduced readonly allowlist artifact for retained historical helpers.
- Do not add a second provider adapter, prompt wrapper, or compatibility service.

## No Legacy / Forbidden Paths

- No legacy provider-capable natal generation path may remain.
- No compatibility provider-capable natal generation path may remain.
- No fallback provider-capable natal generation path may remain.
- Forbidden symbols in runtime scope:
  - `AIEngineAdapter.generate_natal_interpretation`
  - `async def generate_natal_interpretation`
  - `generate_natal_interpretation(`
  - `NatalInterpretationService.interpret(`
  - `NatalExecutionInput(`
  - `use_case_key="natal_interpretation"`
  - `use_case_key = "natal_interpretation"`
- Remaining hits must be readonly projection code, historical evidence, negative tests, or migration proof.

## Reintroduction Guard

- Add or update an architecture guard that fails when `AIEngineAdapter.generate_natal_interpretation` exists under `backend/app`.
- The implementation must require an architecture guard against reintroduction.
- The architecture guard must fail when a removed generator path is reintroduced.
- Add or update a guard that fails when `NatalInterpretationService.interpret` calls a provider or builds `NatalExecutionInput`.
- Add or update a guard that fails when runtime natal code builds `use_case_key="natal_interpretation"`.
- Add bounded `rg` scans with a documented allowed fixture pattern and expected false positives.
- Deterministic sources: importable Python modules, AST inspection, generated OpenAPI paths, registered routes, and forbidden symbols.

## Regression Guardrails

| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-001 `remove-historical-facade-routes` | legacy facade -> no wrapper or alias -> architecture `pytest` and `rg`. |
| RG-005 `remove-api-v1-router-logic` | API boundary -> no moved business logic -> import scans and API tests. |
| RG-006 `api-adapter-boundary-convergence` | API adapters -> schemas stay pure -> AST guard and targeted scans. |
| RG-018 `block-supported-family-prompt-fallbacks` | natal prompts -> no fallback owner -> llm orchestration `pytest` and `rg`. |
| RG-149 `CS-350-prompt-generation-current-implementation` | prompt map -> provider-capable flows remain classified -> targeted `rg`. |
| RG-150 `CS-384-separer-interpretations-natales-acceptees-rejets-llm` | rejected reads -> not public -> integration `pytest`. |
| RG-164 `CS-415` | Basic owner -> no legacy selection -> plan tests and owner scan. |
| RG-167 `CS-418` | Basic runtime -> only Basic engine persists -> Basic runtime `pytest`. |
| RG-168 `CS-409-contrats-versionnes-lecture-natale-basic-v2` | Basic contract -> strict public schema -> contract `pytest`. |
| RG-173 `CS-435` | public LLM generation -> product+LLM contracts only -> `pytest`, routes, OpenAPI, `rg`. |

- Needs-investigation: resolver returned generic RG-002 and RG-022 for the scope vector; brief-required IDs were loaded by targeted ID search.
- Registry gap: no exact `generate_natal_interpretation` invariant exists in the registry; normal story generation must not enrich the registry.
- Non-applicable example: RG-153 frontend `/natal` composition is outside this backend deletion scope.
- Non-applicable example: RG-154 frontend DOM denylist is outside this backend deletion scope.
- Non-applicable example: RG-170 DOM Basic V2 sources and legal mentions are outside this backend deletion scope.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Removal audit | `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/removal-audit.md` | Classify removed items. |
| Readonly allowlist | `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/legacy-readonly-allowlist.md` | Document survivors. |
| Scan before | `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/legacy-service-scan-before.txt` | Capture starting hits. |
| Scan after | `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/legacy-service-scan-after.txt` | Capture final hits. |
| OpenAPI before | `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/openapi-before.json` | Capture API baseline. |
| OpenAPI after | `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/openapi-after.json` | Capture API result. |
| Validation output | `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/validation.txt` | Store final commands. |
| Review output | `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist required: yes
- Required artifact:
  - `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/legacy-readonly-allowlist.md`
- Required operational columns for `legacy-readonly-allowlist.md`:
  - `symbol | file | reason | allowed_context | non_generative_proof | owner | expiry_decision`
- Required allowlist table:

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|

- Allowed contexts:
  - `historical-readonly`
  - `test-guard`
  - `migration-proof`
- Not allowed:
  - public runtime generation, provider call, unclassified fallback, hidden wrapper, stub, alias, or soft-disabled generator.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/services/llm_generation/natal/interpretation_service.py` - delete provider-capable legacy generator path.
- `backend/app/domain/llm/runtime/adapter.py` - delete `generate_natal_interpretation`.
- `backend/app/services/llm_generation/natal/theme_natal_product_actions.py` - preserve canonical product-action routing.
- `backend/app/services/llm_generation/natal/theme_natal_basic_full_runtime.py` - preserve canonical Basic runtime behavior.
- `backend/app/domain/theme_natal/generation_contracts.py` - preserve canonical generation contracts.
- `backend/tests/architecture/test_llm_legacy_extinction.py` - add or update removed-symbol guards.
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py` - prove public replacement route behavior.
- `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py` - prove Basic runtime path stays canonical.
- `backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py` - preserve gateway contract behavior.
- `backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py` - preserve rejection workflow behavior.
- `backend/app/tests/unit/test_natal_interpretation_service_v2.py` - preserve readonly historical projection tests.
- `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/**` - persist audit evidence.

Likely tests:

- `backend/tests/architecture/test_llm_legacy_extinction.py`
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py`
- `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`
- `backend/tests/integration/test_theme_natal_reading_slots.py`
- `backend/tests/integration/test_theme_natal_concurrency.py`
- `backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py`
- `backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py`
- `backend/app/tests/unit/test_natal_interpretation_service_v2.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope; no DB migration is authorized.
- `backend/alembic/**` - out of scope; no DB migration is authorized.
- `_condamad/run-state.json` - explicitly out of scope.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend
ruff check backend
python -B -m pytest -q backend/tests/unit/domain/theme_natal `
  backend/tests/integration/test_theme_natal_public_api_product_actions.py `
  backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py `
  backend/tests/integration/test_theme_natal_reading_slots.py `
  backend/tests/integration/test_theme_natal_concurrency.py --tb=short
python -B -m pytest -q backend/tests/llm_orchestration/test_contract_bound_llm_gateway.py `
  backend/tests/llm_orchestration/test_contract_bound_rejection_workflow.py --tb=short
```

Runtime contract commands:

```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "backend"
python -B -c "from app.main import app; assert '/v1/theme-natal/readings' in str(app.openapi())"
python -B -c "from app.main import app; assert any('/v1/theme-natal/readings' in getattr(r, 'path', '') for r in app.routes)"
python -B -c "from pathlib import Path; p=Path('backend/app/domain/llm/runtime/adapter.py'); assert 'generate_natal_interpretation' not in p.read_text()"
```

Scans:

```powershell
rg -n "AIEngineAdapter\.generate_natal_interpretation|async def generate_natal_interpretation|generate_natal_interpretation\(" backend/app
rg -n "use_case_key=.*natal_interpretation|natal_interpretation.*plan.*basic|legacy_basic_natal_generation_disabled" backend/app/services backend/app/domain
rg -n "patch\.object\(AIEngineAdapter, \"generate_natal_interpretation\"|fake_generate_natal_interpretation" backend/tests backend/app/tests
```

- Scan 1 forbidden pattern: removed adapter method definition or calls.
- Scan 1 roots: `backend/app`.
- Scan 1 allowed fixture pattern: none in runtime code.
- Scan 1 expected false positives: zero.
- Scan 2 forbidden pattern: legacy natal execution input, Basic raw use-case routing, or old Basic disable branch.
- Scan 2 roots: `backend/app/services backend/app/domain`.
- Scan 2 allowed fixture pattern: negative architecture guards only outside `backend/app`.
- Scan 2 expected false positives: zero in runtime code.
- Scan 3 forbidden pattern: tests that preserve nominal adapter method mocking.
- Scan 3 roots: `backend/tests backend/app/tests`.
- Scan 3 allowed fixture pattern: negative tests proving the symbol is absent.
- Scan 3 expected false positives: architecture guard strings only.

Evidence artifact checks:

```powershell
.\.venv\Scripts\Activate.ps1
python -B -c "from pathlib import Path; p=Path('_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/legacy-readonly-allowlist.md'); assert p.exists()"
python -B -c "from pathlib import Path; p=Path('_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/evidence/removal-audit.md'); assert p.exists()"
```

## Regression Risks

- Historical row reading may be deleted accidentally instead of being isolated as readonly projection.
- A nominal test may keep the removed provider method alive through a mock.
- A Premium path may silently retain raw `natal_interpretation` execution before the Premium runtime exists.
- A Basic path may bypass `theme_natal` contracts after the adapter method disappears.
- A future implementation may reintroduce the symbol as a stub unless the architecture guard is strict.

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

- `_story_briefs/cs-436-supprimer-service-generation-natale-legacy.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md`
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_condamad/reports/cs-426-cs-427-cs-428-cs-429-cs-430-cs-431-cs-432-cs-433-cs-434-cs-435-delivery-report.md`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/services/llm_generation/natal/theme_natal_product_actions.py`
- `backend/app/services/llm_generation/natal/theme_natal_basic_full_runtime.py`
- `backend/app/domain/theme_natal/generation_contracts.py`
