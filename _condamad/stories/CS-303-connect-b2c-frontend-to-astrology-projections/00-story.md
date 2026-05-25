# Story CS-303 connect-b2c-frontend-to-astrology-projections: Connect B2C Frontend To Astrology Projections
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-303-connect-b2c-frontend-to-astrology-projections.md`.
- Selected mode: Repo-informed story with Fast Story Writer Mode.
- Problem statement: the B2C React app does not yet consume `POST /v1/astrology/projections` for the public projection display.
- Source stakes: expose the delivered B2C projection value, keep projection logic in backend, show usable states, and preserve product disclaimers.
- Source-alignment evidence: PASS; objective, ACs, tasks, evidence, and guardrails preserve the brief without adding backend runtime work.

## Objective

Connect the existing B2C React natal experience to `POST /v1/astrology/projections` through the central API client, then render
`beginner_summary_v1` and `client_interpretation_projection_v1` with controlled loading, empty, degraded, entitlement, and error states.

## Target State

- The B2C frontend calls `POST /v1/astrology/projections` only through the central API client and authenticated request path.
- The `/natal` page or its existing interpretation module is the target B2C surface unless implementation evidence proves a better existing page.
- `beginner_summary_v1` is requested with `projection_version` from the backend public contract and rendered as a clear beginner summary.
- `client_interpretation_projection_v1` is requested with `projection_version` from the backend public contract and rendered as the client interpretation.
- Loading, error, empty, forbidden entitlement, and degraded states are explicit in the UI and covered by targeted frontend tests.
- Product disclaimer text is owned by app code and never taken from LLM or projection payload text.
- No secret, prompt, replay payload, provider payload, admin audit data, or internal projection identifier is exposed to B2C frontend users.
- Frontend evidence includes targeted API wrapper tests, component tests, lint, and runtime contract references to `app.openapi()` and `app.routes`.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-303-connect-b2c-frontend-to-astrology-projections.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-303` after `CS-302`.
- Evidence 3: `frontend/src/api/client.ts` - central `apiFetch`, timeout, token and API error normalization inspected.
- Evidence 4: `frontend/src/api/index.ts` - API barrel export pattern inspected.
- Evidence 5: `frontend/src/app/routes.tsx` - `/natal` authenticated B2C route inspected as the target surface.
- Evidence 6: `frontend/src/pages/NatalChartPage.tsx` - current natal data, entitlement and interpretation integration inspected.
- Evidence 7: `frontend/src/api/natal-chart/index.ts` - existing authenticated API hook and response parsing pattern inspected.
- Evidence 8: `frontend/src/features/natal-chart/NatalInterpretation.tsx` - current interpretation orchestration inspected.
- Evidence 9: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - current app-owned disclaimer rendering inspected.
- Evidence 10: `backend/app/services/api_contracts/public/projections.py` - public projection request and response schema inspected.
- Evidence 11: `docs/architecture/astrology-disclaimer-projection-policy.md` - app-controlled disclaimer policy inspected.
- Evidence 12: `_condamad/reports/CS-256-CS-291-delivery-report.md` - CS-291 endpoint delivery evidence inspected.
- Evidence 13: `_condamad/stories/regression-guardrails.md` - scoped resolver output and targeted ID lookup selected local guardrails only.
- Source-alignment evidence: PASS; story keeps React as consumer of the backend contract and forbids frontend projection rebuilding.

## Domain Boundary

- Domain: frontend-b2c
- In scope:
  - Frontend API wrapper or hook for `POST /v1/astrology/projections`.
  - B2C rendering of `beginner_summary_v1`.
  - B2C rendering of `client_interpretation_projection_v1`.
  - Loading, error, empty, entitlement refusal, and degraded display states.
  - App-owned disclaimer copy on the projection surface.
  - Tests for the API wrapper, target page or feature module, and non-exposure guards.
  - Frontend validation evidence plus bounded backend OpenAPI and route contract checks.
- Out of scope:
  - Backend projection implementation, builders, DB schema, auth redesign, admin replay, admin audit, marketing page, payments, and migrations.
  - Prompt/provider integration, generated OpenAPI client generation, B2B endpoints, landing page work, and registry enrichment.
  - Broad redesign of `/natal`, unrelated i18n rewrites, unrelated CSS migration, and unrelated component refactors.
- Explicit non-goals:
  - No backend route, builder, persistence, entitlement model, prompt, provider, admin, replay, or audit implementation.
  - No local reconstruction of `beginner_summary_v1` or `client_interpretation_projection_v1` payloads in React.
  - No disclaimer text sourced from LLM, prompt output, provider payload, admin payload, replay payload, or projection payload prose.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits the requested frontend B2C API consumption contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only the B2C frontend consumption and rendering path for the existing projection endpoint.
  - Reuse `frontend/src/api/client.ts`, existing authenticated hooks, existing `/natal` route, and current UI state components.
  - Keep backend projection route, schemas, builders, persistence, entitlement policy, prompt, provider, admin, and replay surfaces unchanged.
  - Keep CSS in stylesheet files and reuse existing frontend design tokens, state classes, cards, buttons, and notice styles.
  - Keep product disclaimers application-controlled and independent from LLM or payload-provided copy.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: no existing B2C target page can receive the projections without a product navigation decision.
- Additional validation rules:
  - Frontend tests must prove the central API wrapper sends both projection requests.
  - Frontend component tests must prove loading, error, empty, degraded, and entitlement states.
  - Runtime contract evidence must include `app.openapi()`, `app.routes`, and backend `pytest` or `TestClient` references.
  - Static guards must prove no prompt, replay, provider, admin audit, or internal projection payload is exposed in frontend source.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | `pnpm test`, `app.openapi()`, `app.routes`, backend `pytest`, and `TestClient` prove the frontend uses the delivered API. |
| Baseline Snapshot | yes | Frontend before/after notes and contract samples prove the UI/API surface delta. |
| Ownership Routing | yes | API calls, rendering, disclaimers, styles, and tests must stay in canonical frontend owners. |
| Allowlist Exception | no | No allowlist handling is authorized for this B2C projection wiring story. |
| Contract Shape | yes | The endpoint method, path, request fields, response fields, and displayed projection fields are explicit. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Backend projection logic, prompts, replay payloads, provider payloads, and admin payloads must not enter React. |
| Persistent Evidence | yes | Story evidence artifacts must be kept for review handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The central API client sends projection requests. | Evidence profile: json_contract_shape; `pnpm test -- astrologyProjectionsApi`; `TestClient`. |
| AC2 | `beginner_summary_v1` is displayed. | Evidence profile: frontend_typecheck_no_orphan; `pnpm test -- AstrologyProjections`. |
| AC3 | `client_interpretation_projection_v1` is displayed. | Evidence profile: frontend_typecheck_no_orphan; `pnpm test -- AstrologyProjections`. |
| AC4 | Loading state is visible. | Evidence profile: frontend_typecheck_no_orphan; `pnpm test -- AstrologyProjections`. |
| AC5 | Empty state is visible. | Evidence profile: frontend_typecheck_no_orphan; `pnpm test -- AstrologyProjections`. |
| AC6 | API error state is visible. | Evidence profile: api_error_shape_contract; `pnpm test -- AstrologyProjections`; `TestClient`. |
| AC7 | Entitlement refusal is visible. | Evidence profile: api_error_shape_contract; `pnpm test -- AstrologyProjections`. |
| AC8 | Degraded mode is visible. | Evidence profile: json_contract_shape; `pnpm test -- AstrologyProjections`. |
| AC9 | Disclaimers are app-owned. | Evidence profile: targeted_forbidden_symbol_scan; `pnpm test -- AstrologyProjections`; `rg` checks payload disclaimer use. |
| AC10 | Sensitive internals stay hidden. | Evidence profile: external_usage_blocker; `rg` checks frontend forbidden terms. |
| AC11 | Backend route contract is referenced. | Evidence profile: runtime_openapi_contract; `python` checks `app.openapi()` and `app.routes`; backend `pytest`. |
| AC12 | Frontend validation passes. | Evidence profile: frontend_typecheck_no_orphan; `pnpm lint`; `pnpm test`. |
| AC13 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-303 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect target `/natal` page, API client, existing hooks, disclaimer policy, and public projection schema before editing. (AC: AC1)
- [ ] Task 2: Add a typed API wrapper or hook for `POST /v1/astrology/projections` through the central `apiFetch` path. (AC: AC1)
- [ ] Task 3: Request `beginner_summary_v1` with the existing chart source and render the returned payload without rebuilding it. (AC: AC2)
- [ ] Task 4: Request `client_interpretation_projection_v1` with the existing chart source and render the returned payload without rebuilding it. (AC: AC3)
- [ ] Task 5: Add visible loading, empty, API error, entitlement refusal, and degraded states on the target B2C surface. (AC: AC4, AC5, AC6, AC7, AC8)
- [ ] Task 6: Render only app-owned disclaimer copy from the policy-backed frontend owner. (AC: AC9)
- [ ] Task 7: Add static guards against frontend exposure of prompts, provider payloads, replay payloads, admin audit data, and internal IDs. (AC: AC10)
- [ ] Task 8: Add targeted Vitest coverage for API wrapper calls and the target projection rendering module. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8)
- [ ] Task 9: Capture backend route contract checks using `app.openapi()`, `app.routes`, and existing backend `pytest` or `TestClient` evidence. (AC: AC11)
- [ ] Task 10: Persist validation output, contract samples, guardrail resolver output, and source checklist under the CS-303 evidence folder. (AC: AC12, AC13)

## Files to Inspect First

- `_story_briefs/cs-303-connect-b2c-frontend-to-astrology-projections.md` - source brief.
- `frontend/src/api/client.ts` - central API client and timeout/error behavior.
- `frontend/src/api/index.ts` - public API barrel export pattern.
- `frontend/src/api/natal-chart/index.ts` - existing authenticated hook and parsing pattern.
- `frontend/src/app/routes.tsx` - target B2C route confirmation.
- `frontend/src/pages/NatalChartPage.tsx` - likely target B2C page.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - likely orchestration owner.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - current display and disclaimer owner.
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts` - display type boundary.
- `frontend/src/features/natal-chart/NatalInterpretation.css` - existing stylesheet owner for added classes.
- `frontend/src/i18n/natalChart.ts` - existing app-owned user copy and disclaimers.
- `frontend/src/tests/natalInterpretation.test.tsx` - target component-test pattern.
- `frontend/src/tests/natalChartApi.test.tsx` - target API-test pattern.
- `backend/app/services/api_contracts/public/projections.py` - public projection API schema.
- `docs/architecture/astrology-disclaimer-projection-policy.md` - disclaimer ownership policy.
- `_condamad/reports/CS-256-CS-291-delivery-report.md` - CS-291 delivery reference.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - Frontend `pnpm lint`, targeted `pnpm test`, and full `pnpm test`.
  - Backend `app.openapi()`, `app.routes`, `pytest`, and `TestClient` references for the delivered API contract.
  - `backend/app/services/api_contracts/public/projections.py` for request and response fields.
- Secondary evidence:
  - Targeted `rg` scans in `frontend/src` for forbidden internal data names and payload-owned disclaimer copy.
  - Persisted frontend contract samples and validation output under the CS-303 evidence folder.
- Static scans alone are not sufficient because:
  - User-visible loading, error, empty, degraded, entitlement, and projection rendering states require component test evidence.

## Contract Shape

- Contract type:
  - Frontend API consumption and B2C rendering contract.
- Method and path:
  - `POST /v1/astrology/projections`.
- Fields:
  - `chart_id`: selected from the existing loaded natal chart when available.
  - `birth_input`: out of scope for the first B2C wiring unless the existing page lacks `chart_id`.
  - `projection_type`: `beginner_summary_v1` or `client_interpretation_projection_v1`.
  - `projection_version`: version value matched to the backend public contract.
  - `persist`: controlled frontend value, defaulting to the backend-supported behavior chosen by implementation evidence.
  - `chart_id`
  - `projection_type`
  - `projection_version`
  - `persisted`
  - `projection_hash`
  - `payload`
  - `metadata.source`
  - `metadata.plan_code`
  - `metadata.request_id`
- Required fields:
  - `projection_type`
  - `projection_version`
- Optional fields:
  - `chart_id`
  - `birth_input`
  - `persist`
- Displayed projection identifiers:
  - `beginner_summary_v1`
  - `client_interpretation_projection_v1`
- Status codes:
  - `200` or `201` for usable projection responses.
  - `401` for unauthenticated access mapped to the existing auth behavior.
  - `403` for entitlement refusal mapped to a user-facing upgrade or plan message.
  - `404`, `409`, and `422` mapped to bounded user-facing error states.
- Serialization names:
  - JSON keys are consumed exactly as backend emits them.
- Backend type impact:
  - none; backend schemas, routes, builders, persistence, entitlements, prompts, and provider code stay unchanged.
- Frontend type impact:
  - typed frontend request, response, payload, loading, error, empty, entitlement, and degraded view states are added.
- Generated contract impact:
  - no generated frontend client is introduced; `app.openapi()` remains reference evidence only.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-before.md`
  - `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/api-contract-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-after.md`
  - `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/api-contract-after.json`
  - `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/validation.txt`
- Expected invariant:
  - The only intended product delta is B2C frontend consumption and rendering of the existing projection endpoint.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| HTTP transport | `frontend/src/api/client.ts` and a domain API wrapper under `frontend/src/api/` | Page-local `fetch` calls |
| Projection display | Existing `/natal` page or `frontend/src/features/natal-chart/**` | Dashboard, landing, admin, or B2B pages |
| Projection payload typing | Frontend API/domain type file near the wrapper | Component-local untyped dictionaries |
| App disclaimers | `frontend/src/i18n/natalChart.ts` or a policy-named frontend copy owner | LLM payload, prompt payload, or backend admin payload |
| Styling | Existing CSS files near the touched component | Inline `style` attributes |
| Component tests | `frontend/src/tests/**` | Manual-only validation |
| Evidence artifacts | `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/` | Application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse `apiFetch`, `ApiError`, and `parseApiErrorDetails` instead of creating a second HTTP client.
- Reuse existing authentication token helpers and React Query patterns from `frontend/src/api/natal-chart/index.ts`.
- Reuse the existing `/natal` route and natal interpretation components unless target-page evidence proves a better existing B2C owner.
- Reuse existing UI state patterns such as skeleton, error, empty, locked, notice, and card classes.
- Reuse existing stylesheet variables and CSS tokens; add classes only in the appropriate CSS file.
- Do not add external packages, generated clients, backend wrappers, local projection builders, prompt readers, or duplicate disclaimer registries.

## No Legacy / Forbidden Paths

- No legacy frontend route may be added for projection display.
- No compatibility API client may be added for projection display.
- No fallback projection builder may be added in React.
- Do not create aliases, shims, wrappers, or parallel clients for the same endpoint.
- Do not call `fetch` directly from page or component files for this endpoint.
- Do not embed backend projection logic, entitlement policy, prompt logic, or provider response parsing in React.
- Forbidden frontend surfaces:
  - `frontend/src/pages/admin/**`
  - `frontend/src/features/admin-prompts/**`
  - `frontend/src/api/admin*.ts`
  - `frontend/src/api/b2b*.ts`
  - `frontend/src/pages/landing/**`
- Forbidden exposed data names:
  - `prompt`
  - `provider_response`
  - `raw_runtime`
  - `replay_snapshot`
  - `admin_answer_audit`
  - `expert_technical_projection_v1`
  - `astrology_full_data_v1`
  - `admin_chart_diagnostics_v1`

## Reintroduction Guard

- Guard target:
  - React must remain a consumer of `POST /v1/astrology/projections`.
  - App disclaimer text must stay outside LLM and projection payload ownership.
  - Internal projection identifiers and admin/replay/provider payload names must stay out of rendered B2C code.
  - The frontend must not introduce direct `fetch` calls for the projection endpoint outside the API wrapper.
- Guard mechanism:
  - Targeted Vitest coverage for API wrapper, rendering states, and disclaimer ownership.
  - `rg` scans over `frontend/src` for forbidden internal data names and direct endpoint fetch use.
  - Backend `app.openapi()` and `app.routes` checks to prove the canonical route remains the source reference.
- Guard evidence:
  - `pnpm test -- astrologyProjectionsApi`
  - `pnpm test -- AstrologyProjections`
  - `rg -n "provider_response|raw_runtime|replay_snapshot|admin_answer_audit|expert_technical_projection_v1|astrology_full_data_v1" frontend/src`
  - `python -B -c "from app.main import app; assert '/v1/astrology/projections' in app.openapi().get('paths', {})"`
  - `python -B -c "from app.main import app; assert '/v1/astrology/projections' in {getattr(r, 'path', '') for r in app.routes}"`

## Regression Guardrails

Scope vector:

- frontend B2C API consumption: yes;
- `/natal` page and natal interpretation module: yes;
- central API client and React Query pattern: yes;
- app-owned disclaimer display: yes;
- backend route contract reference: yes;
- backend implementation, DB, admin, replay, B2B, landing, migration, and build output: no.

Selected guardrails:

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | New TSX must not add static inline styles. | `pnpm test -- inline-style`; `rg` style scan. |
| RG-052 `CS-075-converger-namespaces-css-migration-only-restants` | New CSS must reuse canonical token namespaces. | design-token tests; CSS review. |
| RG-041 `CS-021-aligner-documentation-entitlement-canonique-runtime` | Entitlement refusal copy must align with canonical product policy. | targeted component tests. |
| Registry gap | No exact frontend guardrail exists for `POST /v1/astrology/projections`. | Story-local API and exposure guards. |

Non-applicable examples:

- RG-007 admin LLM observability is out of scope because no admin route or observability endpoint is touched.
- RG-027 prediction infra boundary is out of scope because this story does not modify backend domain or infra modules.
- RG-042 LLM docs source-of-truth is out of scope because no LLM documentation ownership is changed.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Guardrail resolver output | `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/guardrails.txt` | Preserve scoped guardrail selection. |
| Source checklist | `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/source-checklist.md` | Record inspected files and assumptions. |
| Frontend before notes | `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-before.md` | Capture baseline B2C projection state. |
| Frontend after notes | `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-after.md` | Capture final B2C projection state. |
| API contract before | `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/api-contract-before.json` | Capture source contract reference. |
| API contract after | `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/api-contract-after.json` | Capture final source contract reference. |
| Validation output | `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/validation.txt` | Preserve lint, tests and scans. |
| Review output | `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no allowlist handling is authorized for this B2C projection wiring story.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `frontend/src/api/astrologyProjections.ts` - typed wrapper or hook for `POST /v1/astrology/projections`.
- `frontend/src/api/index.ts` - export the new projection API owner.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - orchestrate B2C projection loading on the existing target surface.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - render projection payload sections and app-owned disclaimers.
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts` - add display types for projection payload consumption.
- `frontend/src/features/natal-chart/NatalInterpretation.css` - add projection display and state classes.
- `frontend/src/i18n/natalChart.ts` - add user-facing state copy owned by the app.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/guardrails.txt` - scoped guardrail selection.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/source-checklist.md` - source and reuse evidence.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-before.md` - baseline note.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-after.md` - final note.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/validation.txt` - validation transcript.

Likely tests:

- `frontend/src/tests/astrologyProjectionsApi.test.ts`
- `frontend/src/tests/AstrologyProjections.test.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/api-architecture.test.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`

Files not expected to change:

- `backend/app/**` - out of scope; backend route, schema, builders, persistence, entitlements, prompts, and providers stay unchanged.
- `backend/alembic/**` - out of scope; no migration is authorized.
- `frontend/src/pages/admin/**` - out of scope; no admin screen is touched.
- `frontend/src/features/admin-prompts/**` - out of scope; no prompt or admin sample payload surface is touched.
- `frontend/src/api/b2b*.ts` - out of scope; no B2B API client is touched.
- `frontend/src/pages/landing/**` - out of scope; no landing page is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pnpm --dir frontend lint`
- VC2: `pnpm --dir frontend test -- astrologyProjectionsApi`
- VC3: `pnpm --dir frontend test -- AstrologyProjections`
- VC4: `pnpm --dir frontend test -- natalInterpretation`
- VC5: `pnpm --dir frontend test -- api-architecture`
- VC6: `pnpm --dir frontend test -- inline-style`
- VC7: `pnpm --dir frontend test -- design-system`
- VC8: `pnpm --dir frontend test`
- VC9: `rg -n "provider_response|raw_runtime|replay_snapshot|admin_answer_audit|expert_technical_projection_v1|astrology_full_data_v1" frontend/src`
- VC10: `rg -n "fetch\\(.*/v1/astrology/projections|/v1/astrology/projections" frontend/src`
- VC11: `cd backend`
- VC12: `pytest -q tests/api/test_projection_openapi.py`
- VC13: `python -B -c "from app.main import app; assert '/v1/astrology/projections' in app.openapi().get('paths', {})"`
- VC14: `python -B -c "from app.main import app; assert '/v1/astrology/projections' in {getattr(r, 'path', '') for r in app.routes}"`
- VC15: `python -B -c "from pathlib import Path as P; assert P('../_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/validation.txt').exists()"`

Before VC12 through VC15, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- The frontend could rebuild projection content locally instead of rendering backend-owned payloads.
- The API wrapper could bypass the central client and lose timeout, auth, and error-envelope behavior.
- The UI could show generic errors for entitlement refusal and leave the upgrade path unclear.
- Disclaimer copy could drift into LLM or projection payload ownership.
- A direct render of payload objects could expose prompt, replay, provider, admin audit, or internal projection fields.
- Styling changes could introduce inline styles or non-canonical token names.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python, Ruff, or pytest command.
- Keep frontend files in React and TypeScript patterns already used by the repository.
- Keep all new or significantly modified applicative files with a French global file comment.
- Keep public and non-trivial function or component docstrings/comments in French when a comment is warranted.
- Put all styling in the appropriate CSS file and reuse existing variables before adding new ones.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-303-connect-b2c-frontend-to-astrology-projections.md`
- `_condamad/reports/CS-256-CS-291-delivery-report.md`
- `_condamad/stories/CS-291-generic-projection-endpoint-runtime/00-story.md`
- `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/00-story.md`
- `backend/app/services/api_contracts/public/projections.py`
- `docs/architecture/astrology-disclaimer-projection-policy.md`
- `frontend/src/api/client.ts`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts`
- `frontend/src/i18n/natalChart.ts`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
