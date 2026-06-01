# Story CS-438 remplacer-api-historique-interpretations-par-slots-theme-natal: Remplacer Api Historique Interpretations Par Slots Theme Natal
Status: ready-to-dev

## Trigger / Source

- Source brief: `_story_briefs/cs-438-remplacer-api-historique-interpretations-par-slots-theme-natal.md`.
- Operating mode: Repo-informed story.
- Fast Story Writer Mode: `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md` read first.
- Dependency: CS-436 must close the provider-capable legacy service before full public route removal.
- Dependency: CS-439 owns remaining frontend adapter removal after this contract story.
- Problem statement: historical public read, list, delete, PDF, and template routes still expose `/v1/natal/interpretations*`.
- Source-alignment evidence: every source primitive maps to ACs, tasks, validation commands, non-goals, or blocker rules.

## Objective

Replace the historical public natal interpretation API with the `theme_natal` accepted-slot public surface.
The nominal public API must expose modern readings from `theme_natal_reading_slots` and stop publishing the old routes in `app.routes` and `app.openapi()`.

## Target State

- Public GET, list, delete, PDF, and PDF-template access no longer uses `/v1/natal/interpretations*` or `/v1/natal/pdf-templates`.
- Modern public reads use `/v1/theme-natal/readings` or a sibling `theme-natal` route owned by the same product-action API contract.
- Public read and list responses are built from `theme_natal_reading_slots` rows with `status="accepted"` only.
- `llm_generation_runs` and rejected or technical runs stay audit-only and never become public read payloads.
- Frontend nominal calls use the `theme-natal` API surface for read, list, delete, and PDF/download behavior.
- The old route module is not mounted publicly, and no public `410` facade remains as the nominal contract.
- Public mappings no longer transform `natal_long_free` into `natal_interpretation_short`.
- Dev data rows in `user_natal_interpretations` are purged, debug-only, or documented as a blocked user decision in the removal audit.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-438-remplacer-api-historique-interpretations-par-slots-theme-natal.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-438`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - targeted IDs from the brief were read without loading the full registry.
- Evidence 4: `resolve_guardrails.py` - resolver run with backend API, frontend API, route, OpenAPI, slots, and no-legacy scope.
- Evidence 5: `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md` - live-test failure source read.
- Evidence 6: `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - Big Bang target source read.
- Evidence 7: `backend/app/api/v1/routers/public/natal_interpretation.py` still defines public GET, list, delete, PDF, and template routes.
- Evidence 8: `backend/app/api/v1/routers/public/theme_natal_readings.py` defines the product-action command route.
- Evidence 9: `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py` lists accepted slots only.
- Evidence 10: `frontend/src/api/natal-chart/index.ts` still calls `/v1/natal/interpretations*` for read, list, delete, and PDF.
- Repository structure alert: expected backend and frontend roots exist in this workspace; no root creation is required.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `GET /v1/natal/interpretations` | in scope | AC1, AC2, Task 1, Reintroduction Guard |
| `GET /v1/natal/interpretations/{id}` | in scope | AC1, AC3, Task 1, Task 3 |
| `DELETE /v1/natal/interpretations/{id}` | in scope | AC1, AC6, Task 4 |
| `GET /v1/natal/interpretations/{id}/pdf` | in scope | AC1, AC11, Task 11 |
| `GET /v1/natal/pdf-templates` | in scope | AC1, AC11, Task 11 |
| `/v1/theme-natal/readings` | in scope | AC2, AC3, AC4, Task 2 |
| `theme_natal_reading_slots` | in scope | AC3, AC4, Task 2, Task 5 |
| `llm_generation_runs` | in scope | AC4, Task 5 |
| accepted-only public slots | in scope | AC3, AC4, Task 5 |
| `user_natal_interpretations` old rows | in scope | AC7, Task 6, Removal Audit |
| `natal_long_free` public mapping | in scope | AC8, Task 7 |
| `natal_interpretation_short` public mapping | in scope | AC8, Task 7 |
| frontend API consumers | in scope | AC5, AC6, Task 8 |
| OpenAPI public surface | in scope | AC1, AC2, AC9, Task 9 |
| admin LLM routes | out of scope | Explicit non-goals |
| production data migration | out of scope | Explicit non-goals |
| astrology calculations | out of scope | Explicit non-goals |

## Domain Boundary

- Domain: public-theme-natal-reading-contract
- In scope:
  - Backend public API route inventory for historical natal interpretation routes.
  - Backend public `theme-natal` read/list/download/delete projection contract over accepted slots.
  - Public API schemas and services needed to expose accepted `theme_natal_reading_slots`.
  - First-party frontend API client calls that consume the public reading contract.
  - OpenAPI, `app.routes`, `TestClient`, frontend tests, and targeted scans for the public cutover.
- Out of scope:
  - Admin LLM routes, provider live QA, astrology calculations, auth redesign, i18n, styling, build tooling, and migrations.
- Explicit non-goals:
  - No production data migration.
  - No rewrite of the full PDF engine.
  - No frontend visual redesign.
  - No changes to astrology calculation outputs.
  - No public facade, wrapper, alias, compatibility route, fallback route, or re-export for the removed historical paths.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: the story removes historical public API facades and replaces nominal reads with accepted slot projections.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Remove only the historical public natal interpretation route surface.
  - Preserve modern `theme-natal` product-action generation behavior.
  - Expose only accepted public slots to read and list consumers.
  - Keep admin and debug-only surfaces outside public router mounting.
  - The only allowed surface delta is the public cutover from historical paths to `theme-natal` paths.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: old `user_natal_interpretations` rows must stay publicly readable after CS-436.
- Additional validation rules:
  - Use `app.routes` and `app.openapi()` to prove old public paths are absent and modern paths are present.
  - Use `pytest` and `TestClient` for accepted-only read/list behavior and removed-route behavior.
  - Use `AST guard` or bounded `rg` scans for removed path strings and public mapping absence.
  - Use frontend `pnpm` tests for no-call proof in the first-party API client and UI consumer.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, `TestClient`, `pytest`, and frontend tests prove runtime public contract behavior. |
| Baseline Snapshot | yes | OpenAPI before and after artifacts prove the only allowed public API surface delta. |
| Ownership Routing | yes | Read/list/PDF/delete ownership must move to `theme-natal` paths and accepted slot services. |
| Allowlist Exception | yes | Old rows or debug-only survivors must be classified outside public nominal routes. |
| Contract Shape | yes | Modern route methods, status codes, JSON fields, and accepted-only payload rules are closed. |
| Batch Migration | no | Production data migration is out of scope; dev purge or debug-only classification is enough. |
| Reintroduction Guard | yes | Historical public paths and mappings must stay absent from runtime, OpenAPI, and frontend calls. |
| Persistent Evidence | yes | Removal audit, OpenAPI, route inventory, scans, tests, and review artifacts must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Historical public routes are absent. | Evidence profile: route_absence_runtime; `python` checks `app.routes`; `pytest -q backend/tests/architecture`. |
| AC2 | OpenAPI exposes the modern readings path. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` for `/v1/theme-natal/readings`. |
| AC3 | Public read/list returns accepted slots. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_theme_natal_public_reads.py`. |
| AC4 | Rejected LLM runs stay non-public. | Evidence profile: json_contract_shape; `pytest -q backend/tests/integration/test_contract_bound_llm_gateway_rejections.py`. |
| AC5 | Frontend nominal calls use `theme-natal`. | Evidence profile: frontend_typecheck_no_orphan; `pnpm --dir frontend test -- natalChartApi.test.tsx`. |
| AC6 | Public delete behavior avoids historical paths. | Evidence profile: targeted_forbidden_symbol_scan; `pnpm --dir frontend test -- natalInterpretation.test.tsx`; `rg`. |
| AC7 | Old rows receive a public-surface decision. | Evidence profile: allowlist_register_validated; `python` checks `legacy-public-surface-audit.md`. |
| AC8 | Public mappings stop returning old use cases. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `natal_long_free` and `natal_interpretation_short`. |
| AC9 | Removed paths cannot reappear. | Evidence profile: reintroduction_guard; `AST guard`; `app.routes`; `app.openapi()`; `rg` scans. |
| AC10 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |
| AC11 | Public PDF/template behavior avoids historical paths. | Evidence profile: targeted_forbidden_symbol_scan; frontend test, OpenAPI, and `rg`. |

## Implementation Tasks

- [ ] Task 1: Remove the public mount for historical natal interpretation routes. (AC: AC1, AC9)
- [ ] Task 2: Add or finalize `theme-natal` read/list projections over accepted slots. (AC: AC2, AC3)
- [ ] Task 3: Replace public get-by-id behavior with modern slot-based lookup. (AC: AC3)
- [ ] Task 4: Replace or retire public delete actions under the modern route contract. (AC: AC6)
- [ ] Task 5: Keep rejected and technical LLM runs outside public read/list payloads. (AC: AC4)
- [ ] Task 6: Classify old `user_natal_interpretations` rows as dev purge, debug-only, or blocked user decision. (AC: AC7)
- [ ] Task 7: Remove public mappings from `natal_long_free` to `natal_interpretation_short`. (AC: AC8)
- [ ] Task 8: Update frontend API client and UI tests to stop calling historical routes. (AC: AC5, AC6, AC11)
- [ ] Task 9: Add route, OpenAPI, mapping, frontend, and architecture anti-return guards. (AC: AC1, AC2, AC8, AC9)
- [ ] Task 10: Persist before/after OpenAPI, route inventory, scan, audit, and validation evidence. (AC: AC7, AC10)
- [ ] Task 11: Replace or retire public PDF and PDF-template actions under the modern route contract. (AC: AC11)

## Files to Inspect First

- `_story_briefs/cs-438-remplacer-api-historique-interpretations-par-slots-theme-natal.md` - source contract.
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md` - live-test failure source.
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md` - architecture target source.
- `backend/app/api/v1/routers/public/natal_interpretation.py` - historical public route owner.
- `backend/app/api/v1/routers/public/theme_natal_readings.py` - modern product-action route owner.
- `backend/app/api/v1/routers/registry.py` - canonical public router mounting owner.
- `backend/app/services/api_contracts/public/natal_interpretation.py` - historical public schemas and mappings.
- `backend/app/services/api_contracts/public/theme_natal_readings.py` - modern public command schema owner.
- `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py` - accepted-slot service owner.
- `backend/app/infra/db/models/theme_natal_reading_slot.py` - slot lifecycle model.
- `backend/app/infra/db/models/llm_generation_run.py` - technical run model.
- `frontend/src/api/natal-chart/index.ts` - first-party API client owner.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - public UI consumer owner.
- `backend/tests/integration/test_theme_natal_public_reads.py` - expected modern read/list tests.
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py` - product-action API tests.
- `frontend/src/tests/natalChartApi.test.tsx` - frontend API client tests.
- `frontend/src/tests/natalInterpretation.test.tsx` - frontend UI consumer tests.

## Runtime Source of Truth

- Primary source of truth:
  - `app.routes`, `app.openapi()`, `TestClient`, `pytest`, and frontend `pnpm` tests.
- Secondary evidence:
  - Targeted `rg` scans for historical route paths, old use-case mappings, and frontend calls.
- Static scans alone are not sufficient for this story because:
  - Runtime route registration, OpenAPI exposure, accepted-only reads, and frontend call behavior must be proven.

## Contract Shape

- Contract type:
  - Public API route, OpenAPI path, accepted-slot JSON projection, and frontend API call contract.
- Fields:
  - `chart_id`: identifies the natal chart for modern list and read operations.
  - `reading_id` or `slot_id`: identifies the modern accepted slot when single-read or download requires an id.
  - `action`: product command such as `preview`, `generate_full`, `regenerate`, or `download`.
  - `state`: controlled public state for accepted, generating, rejected, locked, or unavailable outcomes.
  - `data`: public accepted slot payload only.
- Required fields:
  - `chart_id` for list/read commands.
  - `action` for command-style operations.
  - `data` only when the response state is accepted.
- Optional fields:
  - `persona_profile_id`, `locale`, `client_request_id`, and PDF template key under the modern route contract.
- Status codes:
  - `200` for successful accepted-slot read or list.
  - `202` for accepted command that remains generating.
  - `204` for modern delete or retire action when the product contract authorizes it.
  - `404` for missing modern slot or unauthorized access.
  - `422` for invalid modern command payload.
- Serialization names:
  - `chart_id`, `reading_id`, `slot_id`, `action`, `state`, and `data` are emitted as snake_case.
- Frontend type impact:
  - `frontend/src/api/natal-chart/index.ts` must expose modern route functions without historical URL constants.
- Generated contract impact:
  - `app.openapi()` must not expose `/v1/natal/interpretations`, `/v1/natal/interpretation`, or `/v1/natal/pdf-templates`.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-438-remplacer-api-historique-interpretations-par-slots-theme-natal/evidence/openapi-before.json`
  - `_condamad/stories/CS-438-remplacer-api-historique-interpretations-par-slots-theme-natal/evidence/routes-before.txt`
  - `_condamad/stories/CS-438-remplacer-api-historique-interpretations-par-slots-theme-natal/evidence/legacy-paths-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-438-remplacer-api-historique-interpretations-par-slots-theme-natal/evidence/openapi-after.json`
  - `_condamad/stories/CS-438-remplacer-api-historique-interpretations-par-slots-theme-natal/evidence/routes-after.txt`
  - `_condamad/stories/CS-438-remplacer-api-historique-interpretations-par-slots-theme-natal/evidence/legacy-paths-after.txt`
- Expected invariant:
  - The only intended public API surface delta is removal of historical routes and replacement by `theme-natal` accepted-slot routes.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Public read/list routes | `backend/app/api/v1/routers/public/theme_natal_readings.py` or sibling `theme_natal` router | `natal_interpretation.py` |
| Accepted public reading state | `ThemeNatalReadingSlotService` | `NatalInterpretationService.list_interpretations` |
| Technical run audit | `LlmGenerationRunModel` and audit-only services | Public read/list response |
| Public API schemas | `backend/app/services/api_contracts/public/theme_natal_readings.py` | inline route models |
| Frontend API calls | `frontend/src/api/natal-chart/index.ts` modern functions | historical URL strings |
| PDF or delete product action | `theme-natal` route contract | `/v1/natal/interpretations/{id}` |
| Legacy residual classification | story evidence removal audit | untracked source comments |

## Removal Classification Rules

- `canonical-active`: modern `theme-natal` route, schema, slot service, or frontend call still required.
- `external-active`: a known non-frontend consumer still calls the historical public route.
- `historical-facade`: public route or helper exists only to preserve historical interpretation API behavior.
- `debug-only`: survivor is explicitly outside public router mounting and has deterministic access proof.
- `dead`: symbol has no production, test, docs, generated contract, or known consumer after scans.
- `needs-user-decision`: scans prove unresolved public consumer or old-row policy risk.
- Required decision:
  - `historical-facade` and `dead` items must be deleted or unmounted.
  - `debug-only` items must be absent from public OpenAPI and public route inventory.
  - `external-active` and `needs-user-decision` items stop implementation for that item.

## Removal Audit Format

The implementation must persist:

`_condamad/stories/CS-438-remplacer-api-historique-interpretations-par-slots-theme-natal/evidence/legacy-public-surface-audit.md`

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

- `Classification` must use `canonical-active`, `external-active`, `historical-facade`, `debug-only`, `dead`, or `needs-user-decision`.
- `Decision` must use `keep`, `delete`, `unmount-public`, `replace-consumer`, `debug-only`, or `needs-user-decision`.
- `Proof` must include command output, file path evidence, `app.openapi()`, `app.routes`, `pytest`, `pnpm`, or `rg`.
- `Risk` must be filled for every `delete`, `unmount-public`, `debug-only`, or `needs-user-decision` row.

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Public readings API | `theme-natal` public router and schema owner | `/v1/natal/interpretations*` |
| Accepted public storage | `theme_natal_reading_slots` and slot service | `user_natal_interpretations` as nominal public source |
| Technical attempts | `llm_generation_runs` audit-only path | public read/list payloads |
| Frontend public client | modern `theme-natal` client functions | historical URL constants |
| Old row policy | `legacy-public-surface-audit.md` | implicit route behavior |

## Delete-Only Rule

- Removable historical public routes must be deleted or unmounted rather than redirected.
- Removable historical public routes are deleted, not repointed.
- No wrapper may preserve `/v1/natal/interpretations`.
- No alias may preserve `/v1/natal/interpretations`.
- No compatibility route may keep `/v1/natal/interpretations` nominal.
- No fallback route may preserve historical read, list, delete, PDF, or template behavior.
- No re-export may mount the historical router under another public prefix.
- Debug-only access is allowed only outside public route inventory with audit proof.

## External Usage Blocker

- External-active public consumers block route removal until a user decision is recorded in the removal audit.
- External-active items must not be deleted.
- The blocker must identify the consumer, exact route, deletion risk, and minimal safe next action.
- `needs-user-decision` rows must keep implementation stopped for that item.
- Historical dev data is not external-active by itself when it is purged or moved outside public nominal routes.

## Generated Contract Check

- Generated contract check: required
- `app.openapi()` must prove historical public paths are absent.
- `app.openapi()` must prove the modern `theme-natal` read/list/download contract is present.
- `app.routes` must prove no public route preserves historical interpretation read, list, delete, PDF, or template paths.
- OpenAPI before and after snapshots must be persisted under this story evidence directory.

## Mandatory Reuse / DRY Constraints

- Reuse `ThemeNatalReadingSlotService.list_public_slots` and `get_public_slot_by_key` for accepted-only reads.
- Reuse the existing `theme_natal_readings` public route ownership rather than creating a second product-action router family.
- Reuse public API error envelope owners instead of building route-local envelopes.
- Reuse frontend API client centralization in `frontend/src/api/natal-chart/index.ts`.
- Reuse existing integration tests for product actions and LLM rejection boundaries.
- Do not add external packages.
- Do not duplicate slot queries in route handlers when service helpers already own them.

## No Legacy / Forbidden Paths

- No legacy public route path may remain for historical natal interpretations.
- No compatibility public route path may remain for historical natal interpretations.
- No fallback public route path may remain for historical natal interpretations.
- Forbidden public route paths:
  - `/v1/natal/interpretations`
  - `/v1/natal/interpretations/{id}`
  - `/v1/natal/interpretations/{id}/pdf`
  - `/v1/natal/pdf-templates`
  - `/v1/natal/interpretation`
- Forbidden public mappings:
  - `natal_long_free` returned as `natal_interpretation_short`
  - `use_case=natal_interpretation_short` for a modern public reading
- Remaining hits must be negative tests, story evidence, debug-only proof, or historical audit rows.

## Reintroduction Guard

- Add or update an architecture guard that fails when historical public route paths appear in `app.routes`.
- Add an architecture guard against reintroduction of deleted public route paths.
- The implementation must require an architecture guard against reintroduction.
- The architecture guard must fail when a removed public route path is reintroduced.
- Add or update an OpenAPI guard that fails when historical public paths appear in `app.openapi()`.
- Add or update frontend tests that fail when nominal calls use `/v1/natal/interpretations`.
- Add a bounded `rg` scan with allowed fixture pattern and expected false positives documented in the Validation Plan.
- Add a guard that fails when public mapping code emits `natal_interpretation_short` from `natal_long_free`.
- The guard must check at least one deterministic source:
- Deterministic source: loaded app routes, generated OpenAPI paths, frontend API client tests, and targeted forbidden-symbol scans.

## Regression Guardrails

| Guardrail | Scope -> invariant -> evidence |
|---|---|
| RG-001 `remove-historical-facade-routes` | public historical routes -> no wrapper or alias -> `app.routes`, `app.openapi()`, `rg`. |
| RG-002 `refactor-api-v1-routers` | API routers -> route ownership remains clear -> API `pytest` and import review. |
| RG-003 `converge-api-v1-route-architecture` | API mount registry -> canonical route mounting only -> `app.routes` and OpenAPI snapshots. |
| RG-004 `centralize-api-http-errors` | API errors -> centralized envelope remains owner -> `pytest` error-shape tests. |
| RG-005 `remove-api-v1-router-logic` | API boundary -> route handlers stay thin -> architecture `pytest` and import scans. |
| RG-006 `api-adapter-boundary-convergence` | API adapters -> non-API layers avoid `app.api` imports -> AST guard and `rg`. |
| RG-150 `CS-384-separer-interpretations-natales-acceptees-rejets-llm` | LLM rejects -> not public -> integration `pytest`. |
| RG-157 `CS-398-rendre-quota-natal-complete-transactionnel-et-remedier-lectures-invalides` | quota -> debit after accepted read -> integration `pytest`. |
| RG-173 `CS-435` | public LLM generation -> product+LLM contracts only -> routes, OpenAPI, `pytest`, `rg`. |

- Needs-investigation: resolver returned broad frontend/style examples `RG-047` and `RG-052`; both are rejected as non-local to API cutover.
- Registry gap: no exact durable guardrail names `/v1/natal/interpretations` route removal; normal story generation does not enrich the registry.
- Non-applicable example: frontend CSS namespace guardrails are outside this route and API-client contract scope.
- Non-applicable example: DB migration guardrails are outside this story because production data migration is out of scope.
- Non-applicable example: admin LLM observability route guardrails are outside this public route cutover.

## Persistent Evidence Artifacts

Base path: `_condamad/stories/CS-438-remplacer-api-historique-interpretations-par-slots-theme-natal`.

| Artifact | Path | Purpose |
|---|---|---|
| Removal audit | `evidence/legacy-public-surface-audit.md` | Classify old routes and rows. |
| OpenAPI before | `evidence/openapi-before.json` | Capture public API baseline. |
| OpenAPI after | `evidence/openapi-after.json` | Capture public API result. |
| Routes before | `evidence/routes-before.txt` | Capture loaded route baseline. |
| Routes after | `evidence/routes-after.txt` | Prove route removal. |
| Legacy paths scan | `evidence/legacy-paths-after.txt` | Prove bounded scan result. |
| Frontend calls scan | `evidence/frontend-calls-after.txt` | Prove frontend cutover. |
| Validation output | `evidence/validation.txt` | Store final commands. |
| Review output | `generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist required: yes
- Required artifact:
  - `_condamad/stories/CS-438-remplacer-api-historique-interpretations-par-slots-theme-natal/evidence/legacy-public-surface-audit.md`
- Required operational columns for the audit:
  - `item | type | classification | consumers | canonical_replacement | decision | proof | risk`
- Required allowlist table:

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|

- Allowed contexts:
  - `debug-only`
  - `test-guard`
  - `story-evidence`
  - `historical-data-policy`
- Not allowed:
  - public nominal route, OpenAPI path, frontend nominal call, hidden wrapper, alias, fallback route, or unclassified survivor.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no production data migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/public/natal_interpretation.py` - remove or unmount historical public routes.
- `backend/app/api/v1/routers/public/theme_natal_readings.py` - add or finalize modern read/list/download/delete projections.
- `backend/app/api/v1/routers/registry.py` - ensure public router mounting uses only canonical modern routes.
- `backend/app/services/api_contracts/public/theme_natal_readings.py` - define modern accepted-slot public response contracts.
- `backend/app/services/api_contracts/public/natal_interpretation.py` - remove historical public mapping ownership.
- `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py` - reuse accepted-slot query helpers.
- `backend/app/infra/db/models/theme_natal_reading_slot.py` - inspect slot lifecycle without schema migration.
- `backend/app/infra/db/models/llm_generation_run.py` - inspect audit-only run lifecycle without schema migration.
- `frontend/src/api/natal-chart/index.ts` - replace historical URL calls with modern route calls.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - remove UI actions wired to historical routes.
- `backend/tests/integration/test_theme_natal_public_reads.py` - add accepted-only read/list contract tests.
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py` - preserve product-action route behavior.
- `backend/tests/integration/test_contract_bound_llm_gateway_rejections.py` - prove rejected runs stay non-public.
- `backend/tests/architecture` - add route and OpenAPI anti-return guards.
- `frontend/src/tests/natalChartApi.test.tsx` - prove frontend API client route cutover.
- `frontend/src/tests/natalInterpretation.test.tsx` - prove UI no-call behavior for delete/PDF/list actions.
- `_condamad/stories/CS-438-remplacer-api-historique-interpretations-par-slots-theme-natal/evidence/**` - persist audit evidence.

Likely tests:

- `backend/tests/integration/test_theme_natal_public_reads.py`
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py`
- `backend/tests/integration/test_contract_bound_llm_gateway_rejections.py`
- `backend/tests/architecture`
- `frontend/src/tests/natalChartApi.test.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`

Files not expected to change:

- `backend/alembic/**` - out of scope; no DB migration is authorized.
- `backend/migrations/**` - out of scope; no DB migration is authorized.
- `backend/app/api/v1/routers/admin/**` - out of scope; admin LLM routes stay untouched.
- `frontend/src/**/*.css` - out of scope; no styling change is required.
- `.env` - out of scope; no secret or environment change is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend
ruff check backend
python -B -m pytest -q `
  backend/tests/integration/test_theme_natal_public_reads.py `
  backend/tests/integration/test_theme_natal_public_api_product_actions.py `
  backend/tests/integration/test_contract_bound_llm_gateway_rejections.py `
  --tb=short
python -B -m pytest -q backend/app/tests/unit/test_backend_test_topology.py backend/tests/architecture --tb=short
```

Frontend:

```powershell
pnpm --dir frontend test -- natalChartApi.test.tsx natalInterpretation.test.tsx natalPublicDomGuard.test.tsx
```

Runtime contract commands:

```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "backend"
python -B -c "from app.main import app; paths={getattr(r,'path','') for r in app.routes}; assert '/v1/theme-natal/readings' in paths"
python -B -c "from app.main import app; paths={getattr(r,'path','') for r in app.routes}; assert all('/v1/natal/interpretations' not in p for p in paths)"
python -B -c "from app.main import app; paths=app.openapi()['paths']; assert '/v1/theme-natal/readings' in paths"
python -B -c "from app.main import app; paths=app.openapi()['paths']; assert all('/v1/natal/interpretations' not in p for p in paths)"
```

Scans:

```powershell
rg -n "/v1/natal/interpretations|/v1/natal/interpretation|/v1/natal/pdf-templates" frontend/src backend/app/api/v1/routers/public backend/app/services/api_contracts/public
rg -n "natal_long_free|natal_interpretation_short" frontend/src backend/app/api/v1/routers/public backend/app/services/api_contracts/public
rg -n "theme-natal/readings" frontend/src backend/app/api/v1/routers/public
```

- Scan 1 forbidden pattern: historical public route strings.
- Scan 1 allowed fixture pattern: negative tests, story evidence, and removal audit rows.
- Scan 1 roots: `frontend/src`, `backend/app/api/v1/routers/public`, `backend/app/services/api_contracts/public`.
- Scan 1 expected false positives: zero in production client and public route code.
- Scan 2 forbidden pattern: public `natal_long_free` to `natal_interpretation_short` mapping or modern public use-case output.
- Scan 2 allowed fixture pattern: negative tests, story evidence, and removal audit rows.
- Scan 2 roots: `frontend/src`, `backend/app/api/v1/routers/public`, `backend/app/services/api_contracts/public`.
- Scan 2 expected false positives: zero in public production code.
- Scan 3 forbidden pattern: missing modern route usage.
- Scan 3 allowed fixture pattern: canonical modern frontend client and backend route ownership.
- Scan 3 roots: `frontend/src`, `backend/app/api/v1/routers/public`.
- Scan 3 expected false positives: canonical route and tests only.

Evidence artifact checks:

```powershell
.\.venv\Scripts\Activate.ps1
$env:STORY_ROOT = '_condamad/stories/CS-438-remplacer-api-historique-interpretations-par-slots-theme-natal'
python -B -c "from pathlib import Path; import os; r=Path(os.environ['STORY_ROOT']); assert (r/'evidence/legacy-public-surface-audit.md').exists()"
python -B -c "from pathlib import Path; import os; r=Path(os.environ['STORY_ROOT']); assert (r/'evidence/openapi-after.json').exists()"
python -B -c "from pathlib import Path; import os; r=Path(os.environ['STORY_ROOT']); assert (r/'evidence/validation.txt').exists()"
```

## Regression Risks

- Removing historical read/list routes can break visible frontend actions unless those actions are replaced or retired in the same implementation.
- A public PDF button can stay visible while its route is gone unless frontend tests cover the action.
- Old `user_natal_interpretations` rows can leak back into nominal API responses without a removal audit decision.
- OpenAPI can still publish the old route if the router remains mounted through the registry.
- Accepted-only slot reads can accidentally include rejected runs if service ownership is bypassed.
- Frontend API helpers can keep hidden historical URL constants even after UI components are updated.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Run Python commands only after activating `.\.venv\Scripts\Activate.ps1`.
- Keep comments and docstrings in French for new or significantly modified application files.
- Do not add a public facade, wrapper, alias, compatibility route, fallback route, or re-export for removed historical paths.
- Keep admin LLM routes untouched.
- Keep DB schema migrations out of this implementation.

## References

- `_story_briefs/cs-438-remplacer-api-historique-interpretations-par-slots-theme-natal.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_condamad/stories/CS-432-public-api-cutover-product-actions/00-story.md`
- `_condamad/stories/CS-434-physical-delete-active-legacy-natal-generation-paths/00-story.md`
- `_condamad/stories/CS-436-supprimer-service-generation-natale-legacy/00-story.md`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/api/v1/routers/public/theme_natal_readings.py`
- `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py`
- `backend/app/infra/db/models/theme_natal_reading_slot.py`
- `backend/app/infra/db/models/llm_generation_run.py`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
