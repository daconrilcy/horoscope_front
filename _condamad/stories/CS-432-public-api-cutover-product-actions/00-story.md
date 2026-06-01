# Story CS-432 public-api-cutover-product-actions: Public API Cutover To Product Actions
Status: ready-to-dev

## Trigger / Source

Brief direct from `_story_briefs/cs-432-public-api-cutover-product-actions.md`.
The bounded problem is that public natal generation must enter through product actions, not through client-selected technical generation fields.

## Objective

Cut over the public natal reading API to a backend product-action command surface.
The public API must accept product intent, reject technical client generation fields, use product contracts, expose accepted slots only.
It must also make the old public generator non-generative.

## Target State

- `POST /v1/theme-natal/readings` is the public command route for theme natal readings.
- The command body accepts `chart_id`, `action`, `persona_profile_id`, `locale`, and `client_request_id`.
- The route delegates to backend product-action owners using `ThemeNatalReadingProductContract`.
- `generate_full` for Basic resolves to `basic_full_reading`.
- `preview` for Basic does not call a short-generation branch.
- Public responses contain only accepted slot payloads or a controlled product state.
- Rejected runs return a controlled state and never expose provider payload data.
- `POST /v1/natal/interpretation` cannot trigger the old public generation path.
- `use_case`, `use_case_level`, `variant_code`, `plan`, and `forceRefresh` are explicitly rejected in the new body.
- OpenAPI documents the product action route and no longer presents technical generation fields on the new route.

## Brief Primitive Ledger

| Primitive | Source expectation | Story mapping |
|---|---|---|
| `POST /v1/theme-natal/readings` | Public API target for product actions. | AC1, AC2, Task 1. |
| request fields | Accept only product command fields. | AC3, AC4, Task 2. |
| technical fields | Reject old client generation controls explicitly. | AC4, AC11, Task 3. |
| `ThemeNatalReadingProductContract` | Backend product contract drives routing. | AC5, AC6, Task 4. |
| `generate_full` | Basic generation resolves to `basic_full_reading`. | AC5, Task 5. |
| `preview` | Basic preview does not generate short output. | AC6, Task 6. |
| slots and runs | Public responses expose accepted slots or controlled states. | AC7, AC8, Task 7. |
| old endpoint | `POST /v1/natal/interpretation` becomes non-generative. | AC9, Task 8. |
| centralized errors | Public errors use existing API error envelope owners. | AC10, Task 9. |
| OpenAPI | Contract documents action-based route. | AC2, Task 10. |
| required validations | Backend lint, focused API tests, OpenAPI diff, and scans are preserved. | Validation Plan. |
| non-goals | Frontend cutover, physical historical deletion, provider live QA, and mass migration stay outside scope. | Domain Boundary. |

## Current State Evidence

- Evidence 1: `_story_briefs/cs-432-public-api-cutover-product-actions.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-432`.
- Evidence 3: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` - Fast Story Writer Mode contract read first.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - targeted IDs `RG-002`, `RG-004`, `RG-005`, `RG-006`, `RG-150`, `RG-157`, and `RG-170` checked.
- Evidence 5: `resolve_guardrails.py` - resolver run with backend API, public route, OpenAPI, JSON response, product-action, and slots scope.
- Evidence 6: `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - public action cutover and non-generative old endpoint risks checked.
- Evidence 7: `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md` - product contract and action resolver dependency checked.
- Evidence 8: `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md` - slots, runs, accepted-only, and idempotence dependency checked.
- Evidence 9: `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md` - Basic fake runtime dependency checked.
- Evidence 10: `backend/app/api/v1/routers/public/natal_interpretation.py` - current old generator route and list/get routes inspected.
- Evidence 11: `backend/app/services/api_contracts/public/natal_interpretation.py` - current public request schema exposes technical fields.
- Evidence 12: `backend/app/api/v1/routers/registry.py` - current public router registry inspected by targeted search.
- Source-alignment evidence: objectives, ACs, tasks, non-goals, guardrails, and validations map to the brief without narrowing the cutover risk.

## Domain Boundary

- Domain: backend-api
- In scope:
  - Backend public API route `POST /v1/theme-natal/readings`.
  - Pydantic public command schemas for product action requests and controlled states.
  - API adapter delegation to product-action, slot, run, and Basic runtime owners.
  - Explicit 422 validation for technical generation fields on the new command route.
  - Non-generative behavior for `POST /v1/natal/interpretation`.
  - OpenAPI and `TestClient` tests for the public API contract.
- Out of scope:
  - Frontend UI, frontend generated client cutover, DB schema design, auth redesign, i18n, styling, build tooling, migrations, and provider live QA.
- Explicit non-goals:
  - No frontend route, screen, state, generated client, or CSS edit is authorized.
  - No physical deletion of historical natal modules is required in this story.
  - No provider live QA or real provider request is required.
  - No mass migration of old interpretations is included.
  - No new product resolver, slot model, or Basic runtime is invented outside the CS-427, CS-428, and CS-430 ownership.

## Operation Contract

- Operation type: create
- Primary archetype: api-contract-change
- Archetype reason: the story changes public API routes, OpenAPI, request schema, response shape, and route behavior.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add or expose only `POST /v1/theme-natal/readings` as the new product-action command surface.
  - Accept only the product command fields listed in this story on the new route.
  - Make `POST /v1/natal/interpretation` non-generative without physical historical deletion.
  - Keep frontend behavior unchanged in this story.
  - Keep DB schema changes out of scope unless already supplied by CS-428 implementation.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: CS-427, CS-428, or CS-430 surfaces are unavailable at implementation start.
- Additional validation rules:
  - Runtime API evidence must include `app.routes`, `app.openapi()`, and `TestClient`.
  - New-route tests must include `pytest -q backend/tests/integration/test_theme_natal_public_api_product_actions.py`.
  - Old-endpoint tests must prove no provider, old use-case, or old generation service path is called.
  - Error evidence must prove validation failures use the centralized public API error shape.
  - OpenAPI evidence must prove the new route documents product action fields and excludes old technical fields.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, and `TestClient` prove runtime API behavior. |
| Baseline Snapshot | yes | OpenAPI before and after artifacts prove the only allowed public API surface delta. |
| Ownership Routing | yes | API adapter, schemas, product command service, slots, runs, and tests need canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this public API cutover. |
| Contract Shape | yes | The new request fields, response states, status codes, and old route behavior are closed. |
| Batch Migration | no | No batch migration or mass historical conversion is in scope. |
| Reintroduction Guard | yes | Old technical fields and old generator paths must stay absent from the public command route. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The loaded app registers `POST /v1/theme-natal/readings`. | Evidence profile: runtime_openapi_contract; `python` checks `app.routes`. |
| AC2 | OpenAPI exposes product action fields. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()`. |
| AC3 | The new route accepts product command fields. | Evidence profile: json_contract_shape; `pytest` checks `test_theme_natal_public_api_product_actions.py`. |
| AC4 | The new route rejects old technical fields. | Evidence profile: api_error_shape_contract; `pytest` checks `test_theme_natal_public_api_product_actions.py`. |
| AC5 | Basic `generate_full` resolves to `basic_full_reading`. | Evidence profile: json_contract_shape; `pytest` checks `test_theme_natal_public_api_product_actions.py`. |
| AC6 | Basic `preview` avoids short generation. | Evidence profile: ast_architecture_guard; `pytest` plus `rg` scans old short branch calls. |
| AC7 | Public responses return accepted slots only. | Evidence profile: json_contract_shape; `TestClient`; `pytest` checks accepted slot response. |
| AC8 | Rejected runs return a controlled state. | Evidence profile: api_error_shape_contract; `pytest` checks `test_theme_natal_public_api_product_actions.py`. |
| AC9 | The old public endpoint is non-generative. | Evidence profile: route_absence_runtime; `TestClient`; `pytest` checks old endpoint no-call behavior. |
| AC10 | Public errors use centralized shape. | Evidence profile: api_error_shape_contract; `pytest` checks `tests/integration/test_theme_natal_public_api_product_actions.py`. |
| AC11 | New-route schema excludes old fields. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()`; `rg` scans public schemas. |
| AC12 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |

## Implementation Tasks

- [ ] Task 1: Register `POST /v1/theme-natal/readings` in the canonical public API router registry. (AC: AC1)
- [ ] Task 2: Define product command request and response schemas under public API contract ownership. (AC: AC2, AC3, AC11)
- [ ] Task 3: Configure strict validation that rejects `use_case`, `use_case_level`, `variant_code`, `plan`, and `forceRefresh`. (AC: AC4, AC11)
- [ ] Task 4: Delegate the route to the CS-427 product action resolver or command service owner. (AC: AC3, AC5)
- [ ] Task 5: Wire Basic `generate_full` through the CS-430 `basic_full_reading` path. (AC: AC5)
- [ ] Task 6: Prove Basic `preview` does not invoke the old short-generation branch. (AC: AC6)
- [ ] Task 7: Return accepted slots or controlled product states from CS-428 slot and run owners. (AC: AC7, AC8)
- [ ] Task 8: Change `POST /v1/natal/interpretation` to a non-generative response or strict command-service delegation. (AC: AC9)
- [ ] Task 9: Reuse centralized API error helpers for 422, 410, controlled states, and public envelopes. (AC: AC4, AC8, AC10)
- [ ] Task 10: Add OpenAPI, `app.routes`, `TestClient`, and no-call provider tests for the cutover. (AC: AC1, AC2, AC3, AC9, AC11)
- [ ] Task 11: Persist OpenAPI, scan, runtime, and validation evidence artifacts. (AC: AC12)

## Files to Inspect First

- `_story_briefs/cs-432-public-api-cutover-product-actions.md` - source contract.
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - public cutover and old-generator risk source.
- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md` - product action resolver dependency.
- `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md` - slots, runs, accepted-only, and idempotence dependency.
- `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md` - Basic runtime dependency.
- `backend/app/api/v1/routers/public/natal_interpretation.py` - current old public route owner.
- `backend/app/services/api_contracts/public/natal_interpretation.py` - current public schema with technical fields.
- `backend/app/api/v1/routers/registry.py` - public router registration owner.
- `backend/app/services/api_contracts/public` - inspect canonical public schema placement before adding product schemas.
- `backend/app/services/llm_generation/natal` - inspect command, slot, run, and Basic runtime owners supplied by dependencies.
- `backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py` - current public API contract test reference.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - accepted-only public boundary reference.

## Runtime Source of Truth

- Primary source of truth:
  - `app.routes` for registered `POST /v1/theme-natal/readings`.
  - `app.openapi()` for request fields, response statuses, and schema absence of old technical fields.
  - `TestClient` for HTTP status, payload, validation, controlled state, and old endpoint no-call behavior.
  - `pytest -q backend/tests/integration/test_theme_natal_public_api_product_actions.py`.
  - `pytest -q backend/tests/integration -k "theme_natal and api" --tb=short`.
- Secondary evidence:
  - Targeted `rg` scans for forbidden request fields, old route no-call behavior, product action symbols, and Basic runtime symbols.
- Static scans alone are not sufficient for this story because:
  - Route registration, schema publication, request validation, old endpoint behavior, and controlled responses require runtime API tests.

## Contract Shape

- Contract type:
  - Public API route and OpenAPI path.
- Fields:
  - `chart_id`: required string identifying the natal chart.
  - `action`: required product action such as `preview`, `generate_full`, `regenerate`, or `download`.
  - `persona_profile_id`: optional string for persona style selection.
  - `locale`: required locale string such as `fr-FR`.
  - `client_request_id`: required or optional idempotence key according to the CS-428 command owner contract.
  - `state`: controlled response state for accepted, locked, generating, rejected, or readonly outcomes.
  - `data`: public accepted slot payload when the state is accepted.
- Required fields:
  - `chart_id`, `action`, and `locale`.
- Optional fields:
  - `persona_profile_id` and `client_request_id` unless CS-428 requires a stricter command contract.
- Status codes:
  - `200` or `202` for accepted slot or controlled in-progress state on `POST /v1/theme-natal/readings`.
  - `410` for `POST /v1/natal/interpretation` when implemented as deprecated non-generative response.
  - `422` for forbidden technical fields on `POST /v1/theme-natal/readings`.
- Serialization names:
  - Public serialization uses exact snake_case names except forbidden client field `forceRefresh`, which is rejected as received.
- Frontend type impact:
  - none; frontend generated client cutover is out of scope.
- Generated contract impact:
  - `app.openapi()` must expose `/v1/theme-natal/readings` with method `post`.
  - `app.openapi()` must not expose old technical request fields on the new product-action schema.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/openapi-before.json`
  - `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/routes-before.txt`
  - `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/legacy-fields-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/openapi-after.json`
  - `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/routes-after.txt`
  - `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/legacy-fields-after.txt`
- Expected invariant:
  - The only intended public API surface delta is the product-action route and the non-generative old endpoint behavior.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Public route adapter | `backend/app/api/v1/routers/public` | `frontend/src/**` |
| Public request schemas | `backend/app/services/api_contracts/public` | `backend/app/api/**` inline models |
| Product action decision | CS-427 product resolver or command service owner | `backend/app/api/**` business rules |
| Slot and run state | CS-428 service or repository owner | `backend/app/api/**` direct SQL |
| Basic runtime | CS-430 Basic runtime owner | old short-generation branch |
| API error envelope | existing centralized API error helpers | local route-built JSON envelope |
| API contract tests | `backend/tests/integration/test_theme_natal_public_api_product_actions.py` | `frontend/src/**` |
| Evidence artifacts | `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence` | build outputs |

## Mandatory Reuse / DRY Constraints

- Reuse CS-427 `ThemeNatalReadingProductContract` and product action resolver instead of adding a second product selector.
- Reuse CS-428 slot, run, idempotence, and accepted-only owners instead of adding another public-reading persistence path.
- Reuse CS-430 Basic runtime and fake provider path for `basic_full_reading`.
- Reuse existing centralized API error helpers and public error envelope contracts.
- Reuse the canonical public router registry mechanism in `backend/app/api/v1/routers/registry.py`.
- Do not duplicate old `NatalInterpretationService.interpret` generation orchestration in the new public route.
- Do not add external packages.

## No Legacy / Forbidden Paths

- No legacy public generation path may be triggered by `POST /v1/natal/interpretation`.
- No compatibility path may accept old technical fields on `POST /v1/theme-natal/readings`.
- No fallback path may route Basic `preview` through a short-generation branch.
- Do not add aliases for `use_case`, `use_case_level`, `variant_code`, `plan`, or `forceRefresh`.
- Do not silently ignore forbidden technical fields in the new request body.
- Do not expose provider payload data or rejected run data in public responses.
- Do not add frontend, migration, style, build, auth redesign, or provider live QA work.

## Reintroduction Guard

- Guard new route runtime registration with:
  - `python -c "from app.main import app; assert any(getattr(r, 'path', '') == '/v1/theme-natal/readings' for r in app.routes)"`.
- Guard OpenAPI contract with:
  - `python -c "from app.main import app; assert '/v1/theme-natal/readings' in app.openapi()['paths']"`.
- Guard forbidden fields with:
  - `rg -n "use_case_level|variant_code|forceRefresh|plan|use_case" backend/app/services/api_contracts backend/app/api/v1/routers/public`.
- Guard old endpoint state with:
  - `rg -n "410|Gone|deprecated|readonly|client_request_id" backend/app/api/v1/routers/public backend/tests`.
- Guard product action symbols with:
  - `rg -n "POST /v1/theme-natal/readings|ThemeNatalReadingAction|generate_full" backend/app backend/tests`.
- Expected result:
  - Forbidden old fields appear only in negative validation tests, old schema owners being neutralized, and story evidence.

## Regression Guardrails

| Guardrail | scope -> invariant -> evidence |
|---|---|
| RG-002 | API routers -> route adapters stay thin and owned by public router paths -> API `pytest` and import review. |
| RG-004 | API errors -> validation and controlled states use centralized envelopes -> `pytest` error-shape tests. |
| RG-005 | API/service boundary -> product decisions stay outside route handlers -> AST or import guard and `pytest`. |
| RG-006 | API adapter boundary -> non-API layers do not import `app.api` -> targeted `rg` and AST guard. |
| RG-150 | Public boundary -> rejected runs stay non-public -> integration `pytest` and `TestClient`. |
| RG-157 | Quota timing -> Basic full reading debits after accepted persistence -> integration `pytest`. |

Needs-investigation:

- `RG-170` is adjacent frontend DOM scope; omitted because this story does not touch `/natal` rendering, sources, legal mentions, or CSS.
- Resolver returned broad frontend universal examples `RG-047` and `RG-052`; both are rejected because no frontend or style surface is in scope.
- Registry gap: no exact durable guardrail names `POST /v1/theme-natal/readings` product-action cutover; this story records the gap without editing the registry.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/validation.txt` | Keep final command output. |
| OpenAPI baseline | `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/openapi-before.json` | Prove initial API surface. |
| OpenAPI result | `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/openapi-after.json` | Prove final API surface. |
| Routes output | `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/routes-after.txt` | Prove loaded route registration. |
| Legacy fields scan | `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/legacy-fields-after.txt` | Prove forbidden field handling. |
| Old endpoint output | `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/old-endpoint-after.txt` | Prove old endpoint is non-generative. |
| Review output | `_condamad/stories/CS-432-public-api-cutover-product-actions/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this public API cutover story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/public/theme_natal_readings.py` - define `POST /v1/theme-natal/readings`.
- `backend/app/api/v1/routers/public/natal_interpretation.py` - make old `POST /v1/natal/interpretation` non-generative.
- `backend/app/api/v1/routers/registry.py` - register the new public router through the canonical registry.
- `backend/app/services/api_contracts/public/theme_natal_readings.py` - define product command request and response schemas.
- `backend/app/services/api_contracts/public/natal_interpretation.py` - neutralize old request schema exposure for generation.
- `backend/app/services/llm_generation/natal` - reuse product command, slot, run, and Basic runtime owners supplied by dependencies.
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py` - add route, schema, validation, and old endpoint tests.
- `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/openapi-before.json` - before OpenAPI artifact.
- `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/openapi-after.json` - after OpenAPI artifact.
- `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/routes-after.txt` - route runtime evidence.
- `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/legacy-fields-after.txt` - scan evidence.
- `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/old-endpoint-after.txt` - old endpoint evidence.

Likely tests:

- `backend/tests/integration/test_theme_natal_public_api_product_actions.py` - product API cutover contract.
- `backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py` - current OpenAPI and public schema reference.
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py` - accepted-only public boundary support.
- `backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py` - quota timing support.

Files not expected to change:

- `frontend/src/**` - out of scope; no frontend surface is touched.
- `backend/migrations/**` - out of scope because this story does not authorize schema migration work.
- `backend/app/infra/clients/**` - out of scope; no live provider client is touched.
- `backend/docs/**` - out of scope; no documentation mode change is authorized.

## 20. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: activate venv, then run from `backend`: `ruff format .`.
- VC2: activate venv, then run from `backend`: `ruff check .`.
- VC3: activate venv, then run from `backend`: `python -B -m pytest -q tests/integration -k "theme_natal and api" --tb=short`.
- VC4: activate venv, then `python -B -m pytest -q backend/tests/integration/test_theme_natal_public_api_product_actions.py`.
- VC5: activate venv, then run `python` over `app.routes` to prove `POST /v1/theme-natal/readings` is registered.
- VC6: activate venv, then run `python` over `app.openapi()` to prove the new route schema and old field absence.
- VC7 forbidden pattern: `use_case_level|variant_code|forceRefresh|plan|use_case`.
- VC7 allowed fixture pattern: negative validation tests, old schema owner under neutralization, and story evidence.
- VC7 scan roots: `backend/app/services/api_contracts`, `backend/app/api/v1/routers/public`.
- VC7 command: `rg -n "use_case_level|variant_code|forceRefresh|plan|use_case" backend/app/services/api_contracts backend/app/api/v1/routers/public`.
- VC7 expected false positives: tests and old schema code that remain only to reject or neutralize old input.
- VC8 forbidden pattern: `410|Gone|deprecated|readonly|client_request_id`.
- VC8 allowed fixture pattern: old endpoint non-generative response, product command idempotence, and tests.
- VC8 scan roots: `backend/app/api/v1/routers/public`, `backend/tests`.
- VC8 command: `rg -n "410|Gone|deprecated|readonly|client_request_id" backend/app/api/v1/routers/public backend/tests`.
- VC8 expected false positives: expected old endpoint response handling and idempotence tests.
- VC9 forbidden pattern: `POST /v1/theme-natal/readings|ThemeNatalReadingAction|generate_full`.
- VC9 allowed fixture pattern: canonical new route, product action owner, Basic runtime tests, and story evidence.
- VC9 scan roots: `backend/app`, `backend/tests`.
- VC9 command: `rg -n "POST /v1/theme-natal/readings|ThemeNatalReadingAction|generate_full" backend/app backend/tests`.
- VC9 expected false positives: none outside canonical route, product action owner, runtime owner, tests, and evidence.
- VC10: persist final outputs under `_condamad/stories/CS-432-public-api-cutover-product-actions/evidence/validation.txt`.

## Regression Risks

- CS-427, CS-428, and CS-430 may be ready-to-dev but not implemented when this story starts.
- The new API can accidentally become another generation orchestrator unless route handlers stay thin.
- The old endpoint can still call `NatalInterpretationService.interpret` unless no-call tests patch provider and service owners.
- OpenAPI can still publish old technical fields if the schema owner is not separated.
- Rejected runs can leak as public payloads unless the `TestClient` path checks controlled state and accepted-only slots.
- Quota can be consumed before acceptance unless the Basic action path reuses the CS-428 and CS-430 timing guarantees.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep all Python commands under `.\.venv\Scripts\Activate.ps1`.
- Keep comments and docstrings in French for new or significantly changed backend application files.
- Keep frontend cutover, provider live QA, physical historical deletion, migrations, and CSS work out of the implementation diff.
- Keep product decisions in product action owners, not in public route handlers.

## References

- `_story_briefs/cs-432-public-api-cutover-product-actions.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md`
- `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md`
- `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/services/api_contracts/public/natal_interpretation.py`
- `backend/app/api/v1/routers/registry.py`
