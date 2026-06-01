# Story CS-434 physical-delete-active-legacy-natal-generation-paths: Physically Delete Active Legacy Natal Generation Paths
Status: ready-to-review

## Trigger / Source

- Source brief: `_story_briefs/cs-434-physical-delete-active-legacy-natal-generation-paths.md`.
- Operating mode: Repo-informed story.
- Dependency: CS-426 must provide the legacy generation classification before destructive edits begin.
- Dependency: CS-431 must provide the contract-bound gateway path before active legacy generation paths are deleted.
- Dependency: CS-432 must provide the public product-action API cutover before old public generation is physically closed.
- Recommended adjacency: CS-433 reduces frontend technical generation controls but is not required for this backend deletion.
- Problem statement: public natal generation can still reach old prompt keys, fallback paths, and nominal legacy tests.
- Source-alignment evidence: every source primitive maps to ACs, tasks, scans, evidence artifacts, or non-goals.

## Objective

Physically delete or neutralize active legacy natal generation paths so no public endpoint can generate through
`natal_interpretation_short`, `natal_long_free`, `natal_interpretation` Basic routing, public prompt fallbacks, or premium prompt
injection of `basic_natal_prompt_payload`.

## Target State

- Public natal generation uses only the contract-bound product-action path delivered by CS-431 and CS-432.
- Historical natal rows remain readable only through strictly non-generative readonly code.
- `natal_interpretation_short` is absent from public provider-capable generation branches.
- `natal_long_free` is absent from public provider-capable generation branches.
- Basic public generation no longer routes through the premium `natal_interpretation` prompt key.
- `basic_natal_prompt_payload` is not injected into a premium historical prompt path.
- Public deterministic prompt fallbacks for natal generation are deleted or classified outside public runtime.
- Historical hits that remain are documented in a persisted allowlist with non-generative proof.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-434-physical-delete-active-legacy-natal-generation-paths.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-434`.
- Evidence 3: `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md` - classification dependency read.
- Evidence 4: `_story_briefs/cs-431-contract-bound-llm-gateway-rejection-workflow.md` - gateway dependency read.
- Evidence 5: `_story_briefs/cs-432-public-api-cutover-product-actions.md` - public cutover dependency read.
- Evidence 6: `_condamad/stories/regression-guardrails.md` was consulted by resolver scope and targeted ID search.
- Evidence 7: `backend/app/services/llm_generation/natal/interpretation_service.py` contains legacy use-case branches and constants.
- Evidence 8: `backend/app/domain/llm/runtime/gateway.py` contains `PAID_USE_CASES` and `BASIC_NATAL_PROMPT_PAYLOAD_KEY` handling.
- Evidence 9: `backend/app/domain/llm/prompting/catalog.py` contains legacy natal prompt runtime entries.
- Evidence 10: targeted scans found legacy hits in backend tests, bootstrap seeds, prompt catalog, gateway, and natal service.
- Repository structure alert: expected backend roots exist in this workspace; no implementation-created backend root is required.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `natal_interpretation_short` | in scope | AC1, AC7, Task 1, Reintroduction Guard |
| `natal_long_free` | in scope | AC2, AC7, Task 1, Reintroduction Guard |
| `natal_interpretation` as Basic generator | in scope | AC3, Task 2, Canonical Ownership |
| `basic_natal_prompt_payload` premium injection | in scope | AC4, Task 3, Contract Shape |
| Public deterministic fallbacks | in scope | AC5, Task 4, Regression Guardrails |
| Obsolete seeds from CS-426 | in scope | AC6, Task 5, Removal Audit |
| Legacy nominal tests and mocks | in scope | AC7, Task 6, Reintroduction Guard |
| Readonly historical compatibility | in scope | AC8, Task 7, External Usage Blocker |
| Historical allowlist | in scope | AC9, Task 8, Persistent Evidence |
| `_condamad/run-state.json` | out of scope | Explicit non-goals |
| New runtime, frontend redesign, mass data migration | out of scope | Explicit non-goals |

## Domain Boundary

- Domain: backend-llm-natal-generation
- In scope:
  - Backend public natal API generation path under `backend/app/api/v1/routers/public/**`.
  - Natal generation orchestration under `backend/app/services/llm_generation/natal/**`.
  - LLM gateway and prompt catalog surfaces under `backend/app/domain/llm/**`.
  - LLM bootstrap seeds under `backend/app/ops/llm/bootstrap/**` and backend scripts.
  - Backend tests under `backend/tests/**` and `backend/app/tests/**` that keep legacy generation nominal.
- Out of scope:
  - Frontend redesign, DB schema migration, auth redesign, i18n copy work, Stripe, style, build tooling, and `_condamad/run-state.json`.
- Explicit non-goals:
  - No new runtime model.
  - No mass migration of historical persisted readings.
  - No frontend cutover implementation.
  - No soft wrapper, alias, fallback, or compatibility generator for deleted legacy paths.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story deletes historical public generation facades across API, gateway, prompt catalog, seeds, and tests.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Public natal generation may only use the product-action contract path from CS-431 and CS-432.
  - Historical readonly reads may remain only without provider calls.
  - Admin-only or bootstrap-only residues must be classified in the allowlist before they remain.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: CS-426 classifies a hit as `needs-decision` or external-active with generation risk.
- Additional validation rules:
  - Use `app.routes` and `app.openapi()` to prove public route contract deltas.
  - Use `pytest` and `TestClient` for public API behavior and provider-call prevention.
  - Use `AST guard` or bounded `rg` scans for gateway, catalog, seed, and test legacy symbol absence.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `pytest`, and `TestClient` prove public generation cannot use legacy paths. |
| Baseline Snapshot | yes | Before/after route, OpenAPI, and scan artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Public API, gateway, prompt catalog, seed, and test ownership must stay canonical. |
| Allowlist Exception | yes | Historical residual hits must be documented with non-generative proof. |
| Contract Shape | yes | Public API contract must reject or avoid legacy generation controls and provider payloads. |
| Batch Migration | no | No mass data migration or batch conversion is in scope. |
| Reintroduction Guard | yes | Deleted generator paths must fail deterministic scans or architecture tests. |
| Persistent Evidence | yes | Removal audit, allowlist, scan, OpenAPI, and validation artifacts must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Public generation cannot use `natal_interpretation_short`. | Evidence profile: route_absence_runtime; `pytest -q backend/tests/integration`; `app.routes`; `rg`. |
| AC2 | Public generation cannot use `natal_long_free`. | Evidence profile: route_absence_runtime; `pytest -q backend/tests/llm_orchestration`; `rg`. |
| AC3 | Basic generation does not route through `natal_interpretation`. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/integration`; `app.openapi()`. |
| AC4 | Premium prompts do not receive `basic_natal_prompt_payload`. | Evidence profile: no_legacy_contract; `pytest -q backend/tests/llm_orchestration`; `rg`. |
| AC5 | Public natal fallback configs contain no generator key. | Evidence profile: targeted_forbidden_symbol_scan; `python` inspects prompt catalog; `pytest`. |
| AC6 | Obsolete natal seeds are deleted or classified. | Evidence profile: batch_migration_mapping; `python` checks removal audit and allowlist artifacts. |
| AC7 | Legacy nominal tests stop preserving public generation. | Evidence profile: no_legacy_contract; `rg` scans backend tests; `pytest -q backend/tests/llm_orchestration`. |
| AC8 | Readonly legacy compatibility cannot call a provider. | Evidence profile: external_usage_blocker; `pytest -q backend/tests/integration`; `TestClient`. |
| AC9 | Historical residual hits are allowlisted. | Evidence profile: allowlist_register_validated; `python` checks `legacy-allowlist.md`; `rg` scans symbols. |
| AC10 | Deleted generator paths cannot reappear. | Evidence profile: reintroduction_guard; `AST guard`; `python` checks `app.routes`; `rg` scans symbols. |

## Implementation Tasks

- [ ] Task 1: Delete provider-capable branches for `natal_interpretation_short` and `natal_long_free`. (AC: AC1, AC2)
- [ ] Task 2: Remove Basic routing through the premium `natal_interpretation` prompt key. (AC: AC3)
- [ ] Task 3: Remove premium prompt injection of `basic_natal_prompt_payload`. (AC: AC4)
- [ ] Task 4: Remove public deterministic fallback ownership for natal generator keys. (AC: AC5)
- [ ] Task 5: Apply CS-426 classification to obsolete natal seeds and scripts. (AC: AC6, AC9)
- [ ] Task 6: Delete or reclassify tests and mocks that preserve legacy paths as nominal. (AC: AC7)
- [ ] Task 7: Keep historical compatibility strictly readonly and provider-call-free. (AC: AC8)
- [ ] Task 8: Create the historical residual hit allowlist with non-generative proof. (AC: AC9)
- [ ] Task 9: Add deterministic anti-return tests or architecture guards. (AC: AC10)
- [ ] Task 10: Persist before/after OpenAPI, scan, audit, and validation evidence. (AC: AC6, AC9, AC10)

## Files to Inspect First

- `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md` - source classification contract.
- `_story_briefs/cs-431-contract-bound-llm-gateway-rejection-workflow.md` - contract-bound gateway prerequisite.
- `_story_briefs/cs-432-public-api-cutover-product-actions.md` - public product-action cutover prerequisite.
- `backend/app/api/v1/routers/public/natal_interpretation.py` - current public route behavior.
- `backend/app/services/api_contracts/public/natal_interpretation.py` - current public request and response contracts.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - legacy generation branches.
- `backend/app/domain/llm/runtime/gateway.py` - gateway prompt payload and use-case routing.
- `backend/app/domain/llm/runtime/adapter.py` - provider-call handoff.
- `backend/app/domain/llm/prompting/catalog.py` - prompt runtime and fallback registry.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - canonical and fallback target keys.
- `backend/app/ops/llm/bootstrap/**` - seed files requiring CS-426 classification.
- `backend/scripts/**` - scripts that may keep public generator seeds or scans.
- `backend/tests/**` and `backend/app/tests/**` - nominal legacy tests to remove or convert to guards.

## Runtime Source of Truth

- Primary source of truth:
  - `app.routes`, `app.openapi()`, `pytest`, and `TestClient`.
- Secondary evidence:
  - Targeted `rg` scans for forbidden generator symbols and prompt payload injections.
- Static scans alone are not sufficient for this story because:
  - Provider-call prevention and public API route behavior must be proven from loaded runtime paths.

## Contract Shape

- Contract type:
  - Public API generation contract and LLM gateway execution contract.
- Fields:
  - `chart_id`, `action`, and `client_request_id` belong to the CS-432 product-action public path.
  - `use_case`, `use_case_level`, `variant_code`, `plan`, and `forceRefresh` are not public generator inputs.
- Required fields:
  - The active public product-action path requires the CS-432 command fields.
- Optional fields:
  - none for removed legacy generation controls.
- Public generation fields:
  - `chart_id`: accepted only through the product-action public path from CS-432.
  - `action`: accepted only through the product-action public path from CS-432.
  - `client_request_id`: public idempotency marker for the product-action path.
- Forbidden public generator inputs:
  - `use_case`, `use_case_level`, `variant_code`, `plan`, and `forceRefresh`.
- Forbidden provider-capable prompt keys:
  - `natal_interpretation_short`, `natal_long_free`, and Basic use of `natal_interpretation`.
- Forbidden prompt payload injection:
  - `basic_natal_prompt_payload` into a premium historical prompt path.
- Status codes:
  - Existing readonly or deprecated public surfaces must return a controlled non-generative response.
- Serialization names:
  - Removed legacy generator controls must not be emitted in public OpenAPI schemas.
- Frontend type impact:
  - none in this story; CS-433 owns frontend request type removal.
- Generated contract impact:
  - `app.openapi()` must show no public schema that authorizes the removed generation controls.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/openapi-before.json`
  - `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-scan-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/openapi-after.json`
  - `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-scan-after.txt`
- Expected invariant:
  - The only allowed surface delta is removal or readonly neutralization of public legacy natal generation paths.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Public product-action generation | `backend/app/api/v1/routers/public/theme_natal*.py` or CS-432 owner | Legacy natal interpretation route |
| Natal generation orchestration | Contract-bound natal runtime service from CS-431 | `natal_interpretation_short` branch |
| Prompt runtime config | `backend/app/domain/llm/prompting/catalog.py` governed entries | Public fallback default branch |
| Provider handoff | `backend/app/domain/llm/runtime/gateway.py` contract execution | Readonly compatibility code |
| Historical read formatting | `backend/app/services/llm_generation/natal/interpretation_service.py` readonly path | Provider-capable generation branch |
| Legacy residual classification | Story evidence allowlist and removal audit | Inline comments without proof |

## Removal Classification Rules

- `canonical-active`: CS-431 or CS-432 canonical owner still required by production code.
- `external-active`: public docs, generated OpenAPI clients, analytics, or known consumers still call the surface.
- `historical-facade`: surface only exists to preserve old public generation fields, prompt keys, or route behavior.
- `dead`: surface has no production, test, docs, generated contract, or external consumers after scans.
- `needs-user-decision`: scans prove ambiguity or deletion risk that cannot be closed inside this story.
- Required decision:
  - `historical-facade` and `dead` items must be deleted.
  - `external-active` items must block deletion until the user decision is recorded.

## Removal Audit Format

The implementation must persist:

`_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/removal-audit.md`

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

- `Classification` must use `canonical-active`, `external-active`, `historical-facade`, `dead`, or `needs-user-decision`.
- `Decision` must use `keep`, `delete`, `replace-consumer`, or `needs-user-decision`.
- `Proof` must include command output, file path evidence, `app.openapi()`, `app.routes`, `pytest`, or `rg`.
- `Risk` must be filled for every `delete` or `needs-user-decision` row.

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Public natal generation | CS-432 product-action command service | `POST /v1/natal/interpretation` generator branch |
| Contract-bound gateway execution | CS-431 resolved contract snapshot path | Raw legacy use-case routing |
| Basic public reading generation | Basic product contract and Basic runtime | Premium `natal_interpretation` prompt key |
| Historical reading display | Readonly persisted interpretation formatter | Provider-capable compatibility branch |
| Prompt fallback governance | Prompt governance registry and classified fallbacks | Public fallback default generator key |
| Residual legacy hit documentation | `legacy-allowlist.md` evidence artifact | Untracked inline survival |

## Delete-Only Rule

- Removable legacy generator paths must be deleted rather than redirected.
- Removable legacy generator paths are deleted, not repointed.
- No wrapper may preserve a removed public generation path.
- No alias may preserve a removed public generation path.
- No compatibility route may keep provider-capable legacy generation active.
- No fallback may replace a deleted public generator branch.
- No re-export may preserve a deleted import path.
- Readonly compatibility is allowed only with deterministic provider-call prevention.

## External Usage Blocker

- External-active public consumers block deletion until a user decision is recorded in the removal audit.
- External-active items must not be deleted.
- The blocker must identify the consumer, exact surface, deletion risk, and minimal safe next action.
- `needs-user-decision` rows must keep the story implementation stopped for that item.
- Historical persisted data is not external-active by itself when it remains readable without provider calls.

## Generated Contract Check

- Generated contract check: required
- `app.openapi()` must prove public schemas do not authorize `use_case`, `use_case_level`, `variant_code`, `plan`, or `forceRefresh`.
- `app.routes` must prove no added public route restores `natal_interpretation_short` or `natal_long_free`.
- OpenAPI before and after snapshots must be persisted under this story evidence directory.

## Mandatory Reuse / DRY Constraints

- Reuse CS-426 classification instead of creating a second legacy inventory format.
- Reuse CS-431 gateway contract tests instead of duplicating gateway setup.
- Reuse CS-432 product-action public API contract tests for public cutover behavior.
- Keep one historical allowlist artifact for all accepted residual hits.
- Do not add a second prompt fallback registry or test-only legacy catalog.

## No Legacy / Forbidden Paths

- No legacy public generator path may remain provider-capable.
- No compatibility public generator path may remain provider-capable.
- No fallback public generator path may remain provider-capable.
- Forbidden symbols in public generation scope:
  - `natal_interpretation_short`
  - `natal_long_free`
  - `basic_natal_prompt_payload.*natal_interpretation`
  - `template_source=.*fallback_default`
  - `EXIGENCE PREMIUM`
  - `AstroResponse_v3`
- Remaining hits must be historical, test-guard, bootstrap-classified, admin-only, or readonly non-generative.

## Reintroduction Guard

- Add or update architecture tests that fail on provider-capable use of `natal_interpretation_short`.
- Add an architecture guard against reintroduction of deleted public generator paths.
- The implementation must require an architecture guard against reintroduction.
- The architecture guard must fail when a removed generator path is reintroduced.
- Add or update architecture tests that fail on provider-capable use of `natal_long_free`.
- Add or update a prompt guard that fails on `basic_natal_prompt_payload` injected into premium prompt execution.
- Add or update a fallback guard that fails on public natal generator keys in `PROMPT_FALLBACK_CONFIGS`.
- Add a deterministic `python` guard over `app.routes` and `app.openapi()` for public route and schema absence.
- Deterministic source: registered router prefixes, generated OpenAPI paths, and forbidden symbols.
- Add bounded `rg` scans with a documented allowed fixture pattern and expected false positives.

## Regression Guardrails

| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-001 `remove-historical-facade-routes` | public legacy generation -> no wrapper or alias -> `app.routes`, `pytest`, `rg`. |
| RG-002 `refactor-api-v1-routers` | public router -> adapter only -> `pytest` API tests and import review. |
| RG-018 `block-supported-family-prompt-fallbacks` | natal prompts -> no public fallback owner -> `pytest` and prompt `rg`. |
| RG-021 `classify-converge-remaining-prompt-fallbacks` | fallback keys -> every survivor classified -> allowlist and `pytest`. |
| RG-022 `align-prompt-generation-story-validation-paths` | prompt tests -> collected pytest paths -> `pytest -q backend/tests/llm_orchestration`. |
| RG-149 `CS-350-prompt-generation-current-implementation` | prompt cartography -> generation map remains explicit -> targeted `rg`. |
| RG-150 `CS-384-separer-interpretations-natales-acceptees-rejets-llm` | rejected reads -> not public -> `pytest` integration tests. |
| RG-171 `CS-424` | Basic prompt -> no old natal prompt key -> `pytest` and carrier scans. |

- Needs-investigation: resolver returned only RG-002 and RG-022 for the scope vector; brief-required IDs were loaded by targeted ID search.
- Registry gap: no exact CS-434 route-specific invariant was added because normal story generation must not enrich the registry.
- Non-applicable example: RG-047 frontend inline styles is outside this backend deletion scope.
- Non-applicable example: RG-052 frontend CSS namespaces is outside this backend deletion scope.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Removal audit | `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/removal-audit.md` | Classify each legacy item. |
| Historical allowlist | `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md` | Document accepted residual hits. |
| OpenAPI before | `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/openapi-before.json` | Capture public API baseline. |
| OpenAPI after | `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/openapi-after.json` | Capture public API result. |
| Scan before | `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-scan-before.txt` | Capture starting hits. |
| Scan after | `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-scan-after.txt` | Capture final hits. |
| Validation output | `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/validation.txt` | Store final commands. |
| Review output | `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/generated/11-code-review.md` | Keep review in a generated file. |

## Allowlist / Exception Register

- Allowlist required: yes
- Required artifact:
  - `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md`
- Required operational columns for `legacy-allowlist.md`:
  - `symbol | file | reason | allowed_context | non_generative_proof | owner`
- Required allowlist table:

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|

- Allowed contexts:
  - `historical-readonly`
  - `test-guard`
  - `bootstrap-classified`
  - `admin-only-non-public`
  - `documentation`
- Not allowed:
  - public runtime generation, public provider call, unclassified fallback, hidden wrapper, or soft-disabled generator.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no mass data migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/public/natal_interpretation.py` - remove or neutralize public legacy generator entry.
- `backend/app/services/api_contracts/public/natal_interpretation.py` - remove public legacy generation controls from schemas.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - delete active legacy generator branches.
- `backend/app/domain/llm/runtime/gateway.py` - remove Basic carrier injection into premium legacy prompt paths.
- `backend/app/domain/llm/runtime/adapter.py` - keep provider handoff aligned with contract-bound execution only.
- `backend/app/domain/llm/prompting/catalog.py` - delete or classify public natal fallback prompt entries.
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py` - remove obsolete fallback targets.
- `backend/app/ops/llm/bootstrap/**` - delete or classify obsolete natal seeds from CS-426.
- `backend/scripts/**` - remove or classify legacy natal generation helpers.
- `backend/tests/**` and `backend/app/tests/**` - convert nominal legacy tests into anti-return guards.
- `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/**` - persist audit evidence.

Likely tests:

- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- `backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
- `backend/tests/integration/test_natal_basic_complete_v3_runtime.py`
- `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend implementation belongs to this story.
- `backend/alembic/**` - out of scope; no DB migration is authorized.
- `_condamad/run-state.json` - explicitly out of scope.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

Backend commands:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend
ruff check backend
python -B -m pytest -q backend/tests/llm_orchestration backend/tests/integration -k "theme_natal or legacy or gateway" --tb=short
```

Runtime contract commands:

```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "backend"
python -B -c "from app.main import app; assert all('natal_interpretation_short' not in getattr(r, 'path', '') for r in app.routes)"
python -B -c "from app.main import app; assert 'natal_interpretation_short' not in str(app.openapi())"
python -B -c "from app.domain.llm.prompting.catalog import PROMPT_FALLBACK_CONFIGS; assert not {'natal_interpretation_short','natal_long_free'} & set(PROMPT_FALLBACK_CONFIGS)"
```

Scans:

```powershell
rg -n "natal_interpretation_short|natal_long_free|basic_natal_prompt_payload.*natal_interpretation|template_source=.*fallback_default" backend/app backend/tests
rg -n "EXIGENCE PREMIUM|AstroResponse_v3" backend/app/domain backend/app/services backend/tests
rg -n "use_case_level|variant_code|forceRefresh" backend/app frontend/src
```

- Scan 1 forbidden pattern: legacy natal generator keys, premium payload injection, and fallback default ownership.
- Scan 1 roots: `backend/app backend/tests`.
- Scan 1 allowed fixture pattern: historical allowlist, test-guard assertions, bootstrap-classified seeds, and readonly formatters.
- Scan 1 expected false positives: rows documented in `legacy-allowlist.md` only.
- Scan 2 forbidden pattern: premium prompt carriers in Basic or public natal generation.
- Scan 2 roots: `backend/app/domain backend/app/services backend/tests`.
- Scan 2 allowed fixture pattern: schema definitions, negative tests, and allowlisted admin-only catalog evidence.
- Scan 2 expected false positives: rows documented in `legacy-allowlist.md` only.
- Scan 3 forbidden pattern: public technical generation controls.
- Scan 3 roots: `backend/app frontend/src`.
- Scan 3 allowed fixture pattern: frontend CS-433 scope, entitlement-only `variant_code`, DB/reference variant fields, and negative tests.
- Scan 3 expected false positives: frontend or entitlement hits outside this backend deletion scope.

Evidence artifact checks:

```powershell
.\.venv\Scripts\Activate.ps1
python -B -c "from pathlib import Path; p=Path('_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/legacy-allowlist.md'); assert p.exists()"
python -B -c "from pathlib import Path; p=Path('_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/evidence/removal-audit.md'); assert p.exists()"
```

## Regression Risks

- A historical readonly path may still call the provider indirectly through a shared service.
- A fallback key may survive in prompt catalog or bootstrap seeds and become public again later.
- A Basic path may silently reuse `natal_interpretation` because the gateway still normalizes it.
- Tests may keep legacy use cases as nominal fixtures unless converted to guard-only expectations.
- Frontend technical fields may still exist until CS-433 is implemented; this story only blocks backend public generation.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Treat CS-426 classification as the source for delete, readonly, keep, and needs-decision outcomes.
- Stop on any external-active public generator surface and record the blocker in the removal audit.
- Keep comments and docstrings in French for new or significantly modified application files.
- Run Python commands only after activating `.\.venv\Scripts\Activate.ps1`.

## References

- `_story_briefs/cs-434-physical-delete-active-legacy-natal-generation-paths.md`
- `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md`
- `_story_briefs/cs-431-contract-bound-llm-gateway-rejection-workflow.md`
- `_story_briefs/cs-432-public-api-cutover-product-actions.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/prompting/catalog.py`
