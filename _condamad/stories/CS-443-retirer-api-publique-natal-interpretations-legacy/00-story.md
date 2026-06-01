# Story CS-443 retirer-api-publique-natal-interpretations-legacy: Remove Public Legacy Natal Interpretations API
Status: done

## Trigger / Source

- Mode: Repo-informed story.
- Source brief: `_story_briefs/cs-443-corriger-suppression-api-publique-natal-interpretations-legacy.md`.
- Bounded problem: the historical public natal interpretations API still exposes runtime routes after CS-438.
- Closure expectation: remove the public API facade from route inventory, OpenAPI, frontend callers, and public mappings.
- Source-alignment evidence: ACs, tasks, forbidden paths, snapshots, and guardrails map back to every named brief stake.

## Brief Primitive Ledger

| Primitive | Classification | Story mapping |
|---|---|---|
| `POST /v1/natal/interpretation` | in scope | AC1, AC3, AC10, Task 1 |
| `/v1/natal/interpretations*` | in scope | AC2, AC3, AC10, Task 1 |
| `/v1/natal/pdf-templates` | in scope | AC7, Task 4 |
| `/v1/theme-natal/readings` | in scope | AC4, AC6, AC7, Task 2 |
| `theme_natal_reading_slots` | in scope | AC4, Task 2 |
| `accepted` slots | in scope | AC4, Task 2 |
| `natal_long_free -> natal_interpretation_short` | in scope | AC5, Task 3 |
| frontend callers | in scope | AC6, AC7, Task 4 |
| snapshots before/after | in scope | AC9, Task 6 |
| CS-440 strict route absence | in scope | AC10, Task 5 |
| runtime provider removal | out of scope | Non-goals |
| seeds and prompt catalog removal | out of scope | Non-goals |
| `_condamad/run-state.json` | out of scope | Non-goals |

## Objective

Retirer la facade publique historique des interpretations natales sans chemin de compatibilite, puis faire converger les lectures publiques nominales
vers les slots `theme_natal` acceptes.

## Target State

- The loaded FastAPI app has no public route for `POST /v1/natal/interpretation`.
- The loaded FastAPI app has no public route under `/v1/natal/interpretations`.
- Public OpenAPI exposes no historical natal interpretation path.
- First-party frontend code no longer calls historical natal interpretation URLs.
- Modern public reads use `theme_natal_reading_slots` rows with status `accepted`.
- Public API code no longer maps `natal_long_free` to `natal_interpretation_short`.
- CS-440 can replace the "old route is gone or removed" check with strict public route absence evidence.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-443-corriger-suppression-api-publique-natal-interpretations-legacy.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-443`.
- Evidence 3: `backend/app/api/v1/routers/public/natal_interpretation.py` - historical public router still defines old routes.
- Evidence 4: `backend/app/api/v1/routers/registry.py` - registry still imports and registers `natal_interpretation_router`.
- Evidence 5: `frontend/src/api/natal-chart/index.ts` - frontend still calls historical list, get, delete, PDF, and templates URLs.
- Evidence 6: `_condamad/reports/cs-439-cs-440-delivery-report.md` - CS-440 remains blocked by unfinished CS-438 closure.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - targeted IDs RG-001, RG-002, RG-003, RG-004, RG-005, RG-006, RG-150, RG-157, RG-173, RG-174 consulted.
- Evidence 8: guardrail resolver executed with remove scope over backend public routes, frontend natal chart API, OpenAPI, runtime routes, and `/v1/theme-natal/readings`.

## Domain Boundary

- Domain: public-natal-api-contract
- In scope:
  - Remove historical public natal interpretation API routes from the mounted public API.
  - Keep or complete modern public read actions under `/v1/theme-natal/readings`.
  - Update first-party frontend calls that still target historical natal interpretation URLs.
  - Persist route, OpenAPI, frontend, and symbol evidence for review.
- Out of scope:
  - Runtime provider deletion, prompt catalogue deletion, production data migration, admin LLM routes, auth redesign, i18n, styling, and build tooling.
- Explicit non-goals:
  - No production data migration.
  - No public 410 facade for the historical natal interpretation endpoint.
  - No rewrite of the PDF rendering engine.
  - No modification of `_condamad/run-state.json`.

## Operation Contract

- Operation type: remove
- Primary archetype: api-route-removal
- Archetype reason: the story removes historical public API routes and proves the replacement public contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Remove only the historical public natal interpretation API surface.
  - Add or complete only the modern public read behavior needed by current first-party consumers.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: the route consumption audit classifies a historical URL as `external-active`.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `app.routes`, `app.openapi()`, and `TestClient` prove public route behavior. |
| Baseline Snapshot | yes | Route and OpenAPI before/after artifacts prove the only allowed surface delta. |
| Ownership Routing | yes | Canonical ownership is required because public route and frontend client owners change. |
| Allowlist Exception | no | No broad allowlist is authorized for historical public URLs. |
| Contract Shape | yes | The modern public route has explicit method, path, status, and JSON response shape. |
| Batch Migration | no | Production data migration is outside this story. |
| Reintroduction Guard | yes | Historical public URLs and public mappings must stay absent. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `POST /v1/natal/interpretation` is absent at runtime. | Evidence profile: route_absence_runtime; `python` checks `app.routes`; `pytest` architecture guard. |
| AC2 | No runtime public route remains under `/v1/natal/interpretations`. | Evidence profile: route_absence_runtime; `python` checks `app.routes`; `pytest` architecture guard. |
| AC3 | Public OpenAPI omits historical natal interpretation paths. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()`; targeted `pytest`. |
| AC4 | Public read responses expose accepted theme-natal slots only. | Evidence profile: json_contract_shape; `pytest` public reads; `TestClient` covers accepted-only reads. |
| AC5 | Public code omits old product mapping conversion. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans bounded public roots. |
| AC6 | Frontend nominal calls avoid historical natal URLs. | Evidence profile: frontend_typecheck_no_orphan; `pnpm` tests frontend URL denial. |
| AC7 | Visible history actions have a modern disposition. | Evidence profile: frontend_typecheck_no_orphan; `pnpm` tests action disposition. |
| AC8 | Consumption audit artifact is persisted. | Evidence profile: external_usage_blocker; `python` checks route audit artifact. |
| AC9 | Contract snapshot artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks story evidence paths. |
| AC10 | Reintroduction guard fails on historical public URLs. | Evidence profile: reintroduction_guard; `pytest` architecture guard; `rg` scans forbidden URLs. |

## Implementation Tasks

- [x] Task 1: Remove the historical natal interpretation public router from canonical public route registration. (AC: AC1, AC2, AC3)
- [x] Task 2: Complete modern public reads through `theme_natal_reading_slots` with accepted-only visibility. (AC: AC4)
- [x] Task 3: Remove public mapping from `natal_long_free` to `natal_interpretation_short`. (AC: AC5)
- [x] Task 4: Move frontend history, PDF, delete, list, get, and template flows to a modern disposition. (AC: AC6, AC7)
- [x] Task 5: Add or update backend architecture guards for removed public paths and old mapping symbols. (AC: AC1, AC2, AC3, AC5, AC10)
- [x] Task 6: Persist route inventory, OpenAPI snapshots, route consumption audit, scans, and validation output. (AC: AC8, AC9, AC10)

## Files to Inspect First

- `_story_briefs/cs-443-corriger-suppression-api-publique-natal-interpretations-legacy.md`
- `_story_briefs/cs-438-remplacer-api-historique-interpretations-par-slots-theme-natal.md`
- `_condamad/reports/cs-439-cs-440-delivery-report.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/api/v1/routers/registry.py`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/api/v1/routers/public/theme_natal_readings.py`
- `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py`
- `backend/app/infra/db/models/theme_natal_reading_slot.py`
- `backend/app/infra/db/models/llm_generation_run.py`
- `backend/app/services/api_contracts/public/natal_interpretation.py`
- `backend/app/services/api_contracts/public/theme_natal_readings.py`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`

## Runtime Source of Truth

- Primary source of truth:
  - `app.routes`, `app.openapi()`, and `TestClient`.
- Secondary evidence:
  - Targeted `rg` scans for historical public URLs and mapping symbols.
- Static scans alone are not sufficient for this story because:
  - Route registration and OpenAPI exposure must be proven from the loaded app.

## Contract Shape

- Contract type:
  - Public API route and OpenAPI paths.
- Fields:
  - `state`: public action state emitted by `/v1/theme-natal/readings`.
  - `data`: accepted public payload or null according to action state.
  - `details`: structured public action metadata.
- Required fields:
  - `state`
  - `data`
  - `details`
- Optional fields:
  - none for the response envelope keys.
- Historical paths that must be absent:
  - `POST /v1/natal/interpretation`
  - `GET /v1/natal/interpretations`
  - `GET /v1/natal/interpretations/{interpretation_id}`
  - `DELETE /v1/natal/interpretations/{interpretation_id}`
  - `GET /v1/natal/interpretations/{interpretation_id}/pdf`
  - `GET /v1/natal/pdf-templates`
- Modern path:
  - `POST /v1/theme-natal/readings`
- Required response state for public reads:
  - accepted slot payloads only.
- Status codes:
  - `200` for successful modern read action responses.
- Serialization names:
  - modern public payload fields keep their `theme_natal` schema names.
- Frontend type impact:
  - Historical helper types and URL builders are removed from nominal frontend flows.
- Generated contract impact:
  - `app.openapi()` must omit historical public paths and expose the modern route.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/evidence/openapi-before.json`
  - `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/evidence/routes-before.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/evidence/openapi-after.json`
  - `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/evidence/routes-after.txt`
- Expected invariant:
  - The intended public API delta removes historical natal interpretation paths.
  - A documented `/v1/theme-natal/readings` completion is allowed only when needed for current first-party actions.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Public route registration | `backend/app/api/v1/routers/registry.py` plus `theme_natal_readings.py` | historical `natal_interpretation_router` |
| Public read persistence | `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py` | `NatalInterpretationService` public read path |
| Public frontend reading client | `frontend/src/api/natal-chart/index.ts` theme-natal action client | historical `/v1/natal/interpretations` helpers |
| Public mapping contract | `backend/app/services/api_contracts/public/theme_natal_readings.py` | `natal_long_free -> natal_interpretation_short` |

## Mandatory Reuse / DRY Constraints

- Reuse the existing FastAPI app, router registry, public theme-natal contracts, and frontend API client patterns.
- Reuse `ThemeNatalReadingSlotService` for accepted-only public read state.
- Do not duplicate route registration, payload normalization, frontend fetch wrappers, or public mapping logic.
- Keep business decisions out of React components and FastAPI route handlers.

## No Legacy / Forbidden Paths

- No legacy route path may remain mounted for historical natal interpretations.
- No compatibility route path may remain mounted for historical natal interpretations.
- No fallback route path may keep the old public API alive.
- Forbidden public URLs:
  - `/v1/natal/interpretation`
  - `/v1/natal/interpretations`
  - `/v1/natal/interpretations/{interpretation_id}`
  - `/v1/natal/interpretations/{interpretation_id}/pdf`
  - `/v1/natal/pdf-templates`
- Forbidden public mapping:
  - `natal_long_free` converted to `natal_interpretation_short`.

## Removal Classification Rules

- Classify every historical public route, frontend helper, contract type, and public mapping as one of:
  - `canonical-active`
  - `external-active`
  - `historical-facade`
  - `dead`
  - `needs-user-decision`
- A `historical-facade` item must be deleted after scans prove no external blocker.
- An `external-active` item blocks deletion until the user provides an explicit decision.
- A `canonical-active` item must stay under the canonical owner listed in this story.

## Removal Audit Format

The implementation must write `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/route-consumption-audit.md`.

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

- `Decision` must be one of `keep`, `delete`, `replace-consumer`, or `needs-user-decision`.
Every row must include command output, file path evidence, or an explicit source document reference in `Proof`.

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Modern public read action | `backend/app/api/v1/routers/public/theme_natal_readings.py` | `backend/app/api/v1/routers/public/natal_interpretation.py` |
| Accepted public slot storage | `ThemeNatalReadingSlotService` | `user_natal_interpretations` public list/get/read path |
| Frontend public reading action | `requestThemeNatalReadingAction` | `useNatalInterpretationsList`, `useNatalInterpretationById`, old delete/PDF helpers |
| Public generated contract | `app.openapi()` from loaded app | stale generated clients or route docs containing historical paths |

## Delete-Only Rule

- Removable historical public items must be deleted, not repointed.
- Removable historical public items must be deleted from public mounting, not repointed.
- Do not redirect historical URLs to modern URLs.
- Do not preserve wrappers, aliases, soft-disabled handlers, re-exports, or readonly public 410 behavior.

## External Usage Blocker

- Any `external-active` route or public contract item blocks deletion.
- An `external-active` item must not be deleted.
- The blocker must name the external consumer, exact evidence path, deletion risk, and required user decision.
- No item may be silently reclassified from `external-active` to `historical-facade`.

## Generated Contract Check

- Generated contract check: required
- Required evidence:
  - `app.openapi()` path inventory before implementation.
  - `app.openapi()` path inventory after implementation.
  - Generated or checked public frontend contract artifacts containing no historical public URL.

## Reintroduction Guard

- Add or update a deterministic guard that fails when historical public URLs return to `app.routes` or `app.openapi()`.
- Add or update an architecture guard against reintroduction of the removed public API surface.
- Add or update an architecture guard that fails if the removed surface is reintroduced.
- Deterministic sources: registered router prefixes, generated OpenAPI paths, frontend URL calls, and forbidden symbols.
- Add or update a bounded scan that fails on unauthorized `natal_long_free` or `natal_interpretation_short` in public code.
- The guard must allow only named historical proof artifacts under this story evidence directory.

## Regression Guardrails

Applicable guardrails:

| Guardrail | scope -> invariant -> evidence |
|---|---|
| RG-001 `remove-historical-facade-routes` | public natal API -> no historical facade -> `app.routes`, `app.openapi()`, `rg` forbidden URLs. |
| RG-002 `refactor-api-v1-routers` | API v1 routers -> clear responsibility -> router architecture tests and route diff. |
| RG-003 `converge-api-v1-route-architecture` | route architecture -> canonical registry only -> runtime inventory and OpenAPI snapshots. |
| RG-004 `centralize-api-http-errors` | API errors -> centralized envelopes -> targeted `rg` for local HTTP response construction. |
| RG-005 `remove-api-v1-router-logic` | API/service boundary -> no business logic in routes -> architecture tests and handler review. |
| RG-006 `api-adapter-boundary-convergence` | API adapter boundary -> non-API layers do not import API -> AST guard or targeted `rg`. |
| RG-150 `accepted-rejected-boundary` | public reads -> rejected payloads stay hidden -> `pytest` accepted-only public read tests. |
| RG-157 `quota-on-acceptance` | product action -> quota only after valid acceptance -> entitlement and acceptance tests. |
| RG-173 `product-llm-contracts-public` | public generation -> product+LLM contracts only -> OpenAPI/routes plus product action tests. |
| RG-174 `zero-public-runtime-hit` | legacy natal deletion -> zero public/runtime hit -> architecture guard plus bounded scans. |

Adjacent non-applicable examples:

- RG-047 inline TSX styling is not local because this story does not authorize style changes.
- RG-052 CSS namespace migration is not local because no CSS migration is in scope.
- RG-027 prediction infra boundary is not local because prediction surfaces are not touched.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Route audit | `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/route-consumption-audit.md` | Classify removed routes and consumers. |
| Routes before | `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/evidence/routes-before.txt` | Capture runtime route baseline. |
| Routes after | `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/evidence/routes-after.txt` | Prove removed routes stay absent. |
| OpenAPI before | `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/evidence/openapi-before.json` | Capture public contract baseline. |
| OpenAPI after | `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/evidence/openapi-after.json` | Prove generated contract delta. |
| Forbidden scan | `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/evidence/forbidden-scan-after.txt` | Persist bounded URL and symbol scan. |
| Validation log | `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/evidence/validation.txt` | Store validation command output. |
| Review output | `_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: no allowlist handling is authorized for historical public URLs.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no production data migration or multi-step data conversion is in scope.

## Expected Files to Modify

Likely files:

- `backend/app/api/v1/routers/registry.py` - remove the public historical router registration.
- `backend/app/api/v1/routers/public/natal_interpretation.py` - delete or demote public historical route code.
- `backend/app/api/v1/routers/public/theme_natal_readings.py` - complete modern public read behavior.
- `backend/app/services/api_contracts/public/theme_natal_readings.py` - align modern response contract.
- `backend/app/services/llm_generation/natal/theme_natal_reading_slots.py` - keep accepted-only public read logic.
- `backend/tests/integration/test_theme_natal_public_reads.py` - prove accepted-only modern reads.
- `backend/tests/integration/test_theme_natal_public_api_product_actions.py` - prove product actions.
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py` - enforce removed public paths.
- `frontend/src/api/natal-chart/index.ts` - remove historical URL helpers.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - remove or modernize visible history actions.
- `frontend/src/tests/natalChartApi.test.tsx` - prove frontend API calls.
- `frontend/src/tests/natalInterpretation.test.tsx` - prove UI action disposition.
- `frontend/src/tests/natalPublicDomGuard.test.tsx` - prove public DOM denies historical symbols.
- `frontend/src/tests/NatalChartPage.test.tsx` - prove page-level action behavior.

Likely tests:

- `backend/tests/integration/test_theme_natal_public_api_product_actions.py`
- `backend/tests/integration/test_theme_natal_public_reads.py`
- `backend/tests/integration/test_contract_bound_llm_gateway_rejections.py`
- `backend/tests/architecture/test_legacy_natal_generation_inventory_guard.py`
- `frontend/src/tests/natalChartApi.test.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`

Files not expected to change:

- `_condamad/run-state.json` - explicitly out of scope.
- `backend/app/api/v1/routers/admin/**` - admin LLM routes are out of scope.
- `backend/app/infra/db/migrations/**` - no production data migration is in scope.
- `frontend/src/styles/**` - no styling change is authorized.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Story Dependencies / Handoff

- May be implemented after or alongside CS-441.
- Must be complete before CS-444.
- CS-440 handoff: replace the permissive "old route is gone or removed" check with strict absence evidence.

## Validation Plan

Run Python commands only after activating the venv.

Backend validation:

```powershell
.\.venv\Scripts\Activate.ps1
Push-Location backend
ruff format .
ruff check .
python -B -m pytest -q tests/integration/test_theme_natal_public_api_product_actions.py `
  tests/integration/test_theme_natal_public_reads.py `
  tests/integration/test_contract_bound_llm_gateway_rejections.py --tb=short
python -B -m pytest -q tests/architecture/test_legacy_natal_generation_inventory_guard.py --tb=short
Pop-Location
```

Runtime route and OpenAPI checks:

```powershell
.\.venv\Scripts\Activate.ps1
Push-Location backend
python -B -c "from app.main import app; paths={getattr(r,'path','') for r in app.routes}; assert '/v1/natal/interpretation' not in paths"
python -B -c "from app.main import app; paths={getattr(r,'path','') for r in app.routes}; assert all(not p.startswith('/v1/natal/interpretations') for p in paths)"
python -B -c "from app.main import app; assert all(not p.startswith('/v1/natal/interpretations') for p in app.openapi()['paths'])"
python -B -c "from app.main import app; assert '/v1/theme-natal/readings' in app.openapi()['paths']"
Pop-Location
```

Frontend validation:

```powershell
pnpm --dir frontend test -- natalChartApi.test.tsx natalInterpretation.test.tsx natalPublicDomGuard.test.tsx NatalChartPage.test.tsx
pnpm --dir frontend lint
```

Scans:

```powershell
rg -n "/v1/natal/interpretation|/v1/natal/interpretations|/v1/natal/pdf-templates" `
  backend/app/api/v1/routers/public frontend/src
```

- Forbidden pattern: historical public natal interpretation URLs.
- Allowed fixture pattern: only this story evidence directory and explicit anti-return tests.
- Scan roots: `backend/app/api/v1/routers/public`, `frontend/src`.
- Expected false positives: zero in production code.

```powershell
rg -n "natal_long_free|natal_interpretation_short" `
  backend/app/api/v1/routers/public backend/app/services/api_contracts/public frontend/src/api/natal-chart frontend/src/features/natal-chart
```

- Forbidden pattern: old product mapping symbols in public API and frontend nominal flows.
- Allowed fixture pattern: explicit architecture guard strings and this story evidence directory.
- Scan roots: public backend routers, public API contracts, frontend natal chart API, frontend natal chart feature.
- Expected false positives: zero in production code.

Story evidence check:

```powershell
.\.venv\Scripts\Activate.ps1
$p = '_condamad/stories/CS-443-retirer-api-publique-natal-interpretations-legacy'
python -B -c "from pathlib import Path; p=Path('$p'); assert (p/'route-consumption-audit.md').exists()"
python -B -c "from pathlib import Path; p=Path('$p'); assert (p/'evidence/openapi-after.json').exists()"
```

## Regression Risks

- Removing list/get/delete/PDF public routes can break visible history actions unless each action has a tested modern disposition.
- Keeping a public 410 route would fail the route and OpenAPI absence contract.
- Moving accepted-only logic into a route handler would weaken the API/service boundary.
- Leaving stale frontend helpers can reintroduce historical URLs without backend coverage.
- Broad scans can hide legitimate blockers; scans must stay bounded and classify allowed proof artifacts.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Keep markdown evidence under the story directory.
- Do not update `_condamad/stories/regression-guardrails.md` during this implementation.
- Do not modify `_condamad/run-state.json`.
- Use small cohesive commits only if the user asks for a commit.

## References

- `_story_briefs/cs-443-corriger-suppression-api-publique-natal-interpretations-legacy.md`
- `_story_briefs/cs-438-remplacer-api-historique-interpretations-par-slots-theme-natal.md`
- `_condamad/reports/cs-439-cs-440-delivery-report.md`
- `_condamad/stories/regression-guardrails.md`
- `.agents/skills/condamad-story-writer/references/writer-contract-cheatsheet.md`
- `.agents/skills/condamad-story-writer/references/removal-story-contract.md`
