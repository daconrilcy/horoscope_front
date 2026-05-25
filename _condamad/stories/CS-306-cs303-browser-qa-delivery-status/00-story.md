# Story CS-306 cs303-browser-qa-delivery-status: Close CS-303 Browser QA And Refresh Delivery Status
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-306-close-cs303-browser-qa-and-refresh-delivery-status.md`.
- Selected mode: Repo-informed story with Fast Story Writer Mode.
- Problem statement: the CS-302 to CS-304 delivery report remains partially delivered because CS-303 lacks browser QA and full-suite closure proof.
- Source stakes: prove `/natal` projection rendering in a real browser, preserve CS-303 public-only projection behavior, and update delivery status only with proof.
- Source-alignment evidence: PASS; objective, ACs, tasks, evidence, and guardrails preserve the brief without expanding backend or admin scope.

## Objective

Validate `/natal` in a real browser with CS-303 B2C projections and refresh the CS-302 to CS-304 delivery report from the gathered proof.
The final report may say `Delivered` only when CS-303 browser QA is green and the full frontend suite limitation is closed by CS-305 or equivalent proof.

## Target State

- The local frontend and required services start, or a startup blocker is recorded with a concrete cause and next action.
- `/natal` is opened in a real browser and shows `beginner_summary_v1` and `client_interpretation_projection_v1` through the existing CS-303 UI.
- Loading, success, controlled error, entitlement, empty, and degraded projection states are verified through reproducible browser or targeted test evidence.
- Desktop and mobile browser checks prove projection text does not hide or overlap the primary `/natal` controls.
- CS-303 targeted validations and the full frontend suite status are referenced from persisted evidence.
- `_condamad/reports/CS-302-CS-304-delivery-report.md` reflects `Delivered` only when all blocking limits are proven closed.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-306-close-cs303-browser-qa-and-refresh-delivery-status.md` - source brief read for this story.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-306` after `CS-305`.
- Evidence 3: `_condamad/reports/CS-302-CS-304-delivery-report.md` - current report shows CS-303 browser QA and full suite gaps.
- Evidence 4: `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` - CS-303 limits inspected.
- Evidence 5: `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-after.md` - frontend projection state inspected.
- Evidence 6: `frontend/src/features/natal-chart/NatalInterpretation.tsx` - `/natal` projection orchestration owner inspected.
- Evidence 7: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - projection rendering owner inspected.
- Evidence 8: `frontend/src/api/astrologyProjections.ts` - central projection API owner inspected.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - scoped resolver output selected local frontend guardrails only.
- Source-alignment evidence: PASS; the story closes the exact report gaps while keeping product, backend, and admin surfaces unchanged.

## Domain Boundary

- Domain: frontend-browser-qa
- In scope:
  - Starting the local frontend and required services through repository scripts.
  - Browser QA for `/natal` projection rendering on desktop and mobile viewport sizes.
  - Capturing browser QA logs, screenshots, validation output, and delivery-report status evidence under the CS-306 capsule.
  - Replaying CS-303 targeted frontend validations and referencing CS-305 full-suite proof or an equivalent explicit full-suite pass.
  - Updating `_condamad/reports/CS-302-CS-304-delivery-report.md` only for proof-backed delivery status closure.
- Out of scope:
  - Backend business behavior, DB schema, auth redesign, admin CS-304 flows, migrations, generated clients, and new product navigation.
  - New projection types, provider/prompt exposure, replay/admin audit exposure, and broad `/natal` redesign.
  - Registry enrichment for `_condamad/stories/regression-guardrails.md`.
- Explicit non-goals:
  - No backend route, serializer, projection builder, persistence, entitlement policy, prompt, provider, admin, replay, or audit implementation.
  - No UI state removal to make browser QA easier.
  - No report status promotion without browser evidence and full-suite closure proof.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a browser QA and delivery-report refresh contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only QA evidence, report status text, and minimal frontend test or UI defects that block `/natal` browser validation.
  - Keep `POST /v1/astrology/projections` consumption routed through `frontend/src/api/astrologyProjections.ts`.
  - Keep CS-303 loading, success, controlled error, entitlement, empty, degraded, and app-owned disclaimer behavior unchanged.
  - Keep CSS in stylesheet files and reuse existing frontend variables, classes, tokens, and component patterns.
  - Preserve public API contracts, backend behavior, and admin flows unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the report cannot become `Delivered` because CS-305 proof or equivalent full-suite proof is unavailable.
- Additional validation rules:
  - Browser QA evidence must include date, route, viewport, projection state, and result.
  - The report must retain `Partially delivered` when the full-suite limitation remains open.
  - The report may use `Delivered` only when browser QA and full frontend suite closure are both evidenced.
  - Static scans must prove no direct projection HTTP bypass, inline style, or forbidden internal projection field is introduced.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Browser QA, logged Vitest commands, `pnpm lint`, and backend contract checks prove the delivery status. |
| Baseline Snapshot | yes | Before and after report snapshots prove the only allowed surface delta. |
| Ownership Routing | yes | QA evidence, report changes, frontend fixes, and API calls must stay in canonical owners. |
| Allowlist Exception | no | No allowlist handling or broad waiver is authorized for report promotion. |
| Contract Shape | yes | The QA ledger and report decision have exact fields and status values. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Direct projection HTTP calls, inline styles, and internal projection fields must stay absent. |
| Persistent Evidence | yes | Browser QA, validation output, report snapshots, and review handoff must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Local startup state is recorded. | Evidence profile: baseline_before_after_diff; `python` checks startup log path and recorded result. |
| AC2 | `/natal` browser success rendering is proven. | Evidence profile: baseline_before_after_diff; `python` checks desktop and mobile browser QA artifacts. |
| AC3 | Projection state coverage is documented. | Evidence profile: json_contract_shape; `pytest` or `vitest` evidence plus browser QA ledger checks state rows. |
| AC4 | CS-303 frontend validations pass. | Evidence profile: frontend_typecheck_no_orphan; `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation`. |
| AC5 | The full frontend suite status is proven. | Evidence profile: frontend_typecheck_no_orphan; `node .\scripts\run-vite-logged.mjs vitest vitest run`. |
| AC6 | Backend projection contract remains intact. | Evidence profile: runtime_openapi_contract; `pytest -q backend/tests/api/test_projection_openapi.py` and `app.openapi()`. |
| AC7 | Public projection ownership stays central. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks direct fetch and forbidden internal fields. |
| AC8 | Delivery report status is correct. | Evidence profile: baseline_before_after_diff; `python` checks final report status and CS-306 report-status artifact. |
| AC9 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-306 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Inspect the report, CS-303 evidence, frontend projection owners, and CS-305 closure evidence. (AC: AC1, AC5)
- [ ] Task 2: Start local services and persist the startup log or actionable startup blocker. (AC: AC1)
- [ ] Task 3: Open `/natal` in a real browser with the authorized test user only when authentication is required. (AC: AC2)
- [ ] Task 4: Capture desktop and mobile browser evidence for projection rendering and primary controls. (AC: AC2)
- [ ] Task 5: Verify projection loading, success, controlled error, entitlement, empty, and degraded states through browser or targeted tests. (AC: AC3)
- [ ] Task 6: Replay the CS-303 targeted frontend validations from the logged runner. (AC: AC4)
- [ ] Task 7: Prove the full frontend suite status from CS-305 final evidence or a fresh logged full-suite run. (AC: AC5)
- [ ] Task 8: Replay backend projection OpenAPI and route contract checks with the venv active. (AC: AC6)
- [ ] Task 9: Run projection ownership, forbidden internal-field, and inline-style scans. (AC: AC7)
- [ ] Task 10: Refresh the CS-302 to CS-304 delivery report with the proven final status. (AC: AC8)
- [ ] Task 11: Persist CS-306 evidence artifacts and final validation output under the story capsule. (AC: AC9)

## Files to Inspect First

- `_story_briefs/cs-306-close-cs303-browser-qa-and-refresh-delivery-status.md` - source brief.
- `_condamad/reports/CS-302-CS-304-delivery-report.md` - current delivery status and report gaps.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` - CS-303 validation limits.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-after.md` - final frontend wiring summary.
- `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/generated/10-final-evidence.md` - full-suite proof source.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - `/natal` projection orchestration owner.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - projection rendering and disclaimer owner.
- `frontend/src/api/astrologyProjections.ts` - central B2C projection API owner.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - Real browser QA on `/natal` with desktop and mobile viewport evidence.
  - `node .\scripts\run-vite-logged.mjs vitest vitest run` from `frontend`.
  - Targeted CS-303 logged Vitest commands for `natalChartApi`, `natalInterpretation`, and component architecture guards.
  - `pnpm lint` from `frontend`.
  - Backend `pytest`, `app.openapi()`, and `app.routes` checks for the projection endpoint.
- Secondary evidence:
  - Report before and after snapshots under the CS-306 evidence directory.
  - Targeted `rg` scans in `frontend/src` for projection HTTP bypass and forbidden internal projection fields.
- Static scans alone are not sufficient because:
  - This story closes browser QA and delivery status; the browser run and validation logs are decisive.

## Contract Shape

- Contract type:
  - Browser QA and delivery-report status evidence contract.
- Fields:
  - `artifact_type`: startup-log, browser-screenshot, browser-log, validation-log, report-snapshot, report-status.
  - `route`: `/natal` for browser QA artifacts.
  - `viewport`: desktop, mobile, or not-browser.
  - `projection_state`: loading, success, controlled-error, entitlement, empty, degraded, or not-projection-state.
  - `command`: validation command or manual browser action.
  - `result`: pass, blocked-startup, blocked-full-suite, or retained-partial-status.
  - `report_status`: Delivered or Partially delivered.
- Required fields:
  - `artifact_type`
  - `command`
  - `result`
  - `report_status`
- Optional fields:
  - `blocker_cause`
  - `screenshot_path`
  - `linked_cs305_evidence`
- Status codes:
  - none; this story does not change HTTP response codes.
- Serialization names:
  - Ledger keys are written exactly as `artifact_type`, `route`, `viewport`, `projection_state`, `command`, `result`, and `report_status`.
- Required commands:
  - `pnpm lint`
  - `node .\scripts\run-vite-logged.mjs vitest vitest run natalChartApi`
  - `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation`
  - `node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi`
  - `node .\scripts\run-vite-logged.mjs vitest vitest run`
  - `python -B -m pytest -q tests\api\test_projection_openapi.py tests\api\test_projection_endpoint.py tests\api\test_projection_authorization.py --tb=short`
- Frontend type impact:
  - only minimal type changes required by a proven `/natal` browser QA blocker are authorized.
- Backend type impact:
  - none; backend API contracts remain unchanged.
- Generated contract impact:
  - no generated client or OpenAPI output change is authorized.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/report-before.md`
  - `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/browser-qa-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/report-after.md`
  - `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/browser-qa-after.md`
  - `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/validation.txt`
  - `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/report-status.md`
- Expected invariant:
  - The only intended delivery-report delta is replacing CS-303 gaps with proof-backed status, or retaining partial status with explicit blockers.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Browser QA evidence | CS-306 `evidence/` directory | Application source folders |
| Delivery status text | `_condamad/reports/CS-302-CS-304-delivery-report.md` | CS-303 source story text |
| Projection API transport | `frontend/src/api/astrologyProjections.ts` through central client | Page-local direct `fetch` |
| Projection display behavior | `frontend/src/features/natal-chart/**` and `frontend/src/components/natal-interpretation/**` | Admin or dashboard surfaces |
| Styles | Existing `.css` files and design tokens | Inline `style` attributes in TSX |
| Backend contract proof | Existing backend projection tests and runtime checks | New backend behavior files |

## Mandatory Reuse / DRY Constraints

- Reuse repository scripts for local startup and logged Vitest execution.
- Reuse the authorized test user only when a real browser authenticated session is required.
- Reuse `frontend/src/api/astrologyProjections.ts` and the central API client for projection requests.
- Reuse existing CS-303 targeted tests for projection rendering and state coverage.
- Reuse existing CSS variables and stylesheet files; do not add inline styles.
- Do not add external packages, generated clients, duplicate API clients, broad QA harnesses, or report-only proof substitutes.

## No Legacy / Forbidden Paths

- No legacy browser QA shortcut may replace a real browser check.
- No compatibility report wording may mark delivery green without full proof.
- No fallback projection API client may be added in React.
- Do not create aliases, shims, wrappers, or parallel validation commands to avoid the logged runner.
- Do not call `fetch` directly from page or component files for `/v1/astrology/projections`.
- Do not expose `provider_response`, `raw_runtime`, `replay_snapshot`, `admin_answer_audit`, or `expert_technical_projection_v1`.
- Do not change backend projection code, backend contracts, migrations, public API schemas, or admin CS-304 flows.

## Reintroduction Guard

- Guard path 1: `frontend/src` must not gain direct HTTP calls to `/v1/astrology/projections`.
- Guard path 2: touched TSX files must not gain inline `style` attributes.
- Guard path 3: frontend source must not expose internal projection fields named in the CS-306 validation plan.
- Guard path 4: the delivery report must not say `Delivered` unless browser QA and full-suite proof are both present.
- Required deterministic guards:
  - `rg -n "fetch\\(.*/v1/astrology/projections" src` from `frontend`.
  - `rg -n "style=" src -g "*.tsx"` from `frontend`.
  - `rg -n "provider_response|raw_runtime|replay_snapshot|admin_answer_audit|expert_technical_projection_v1|astrology_full_data_v1" src`.
  - `python -B` check over `_condamad/reports/CS-302-CS-304-delivery-report.md` and CS-306 report-status evidence.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Touched TSX files keep static styles out of inline attributes. | `rg` inline-style scan; `pnpm lint`. |
| RG-052 `CS-075-converger-namespaces-css-migration-only-restants` | CSS fixes keep canonical frontend style owners. | `rg` token scan; targeted Vitest. |
| Story-local report guard | Delivery status cannot promote without browser QA and full-suite proof. | `python` report-status check. |
| Needs-investigation | Resolver returned backend/docs guardrails for frontend QA scope; they are non-local to this story. | Resolver output stored in evidence. |

Non-applicable examples that prevent scope drift:

- RG-007 is not selected because admin LLM observability endpoints are out of scope.
- RG-041 is not selected because entitlement documentation is not edited.
- Backend route guardrails are not selected because backend runtime files are unchanged.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Startup log | `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/startup-log.txt` | Prove local startup or blocker. |
| Browser QA ledger | `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/browser-qa.md` | Track browser route, viewport, states, and results. |
| Browser screenshots | `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/browser-screenshots/` | Store desktop and mobile visual proof. |
| Report before | `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/report-before.md` | Prove original report status. |
| Report after | `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/report-after.md` | Prove final report text. |
| Report status | `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/report-status.md` | Explain Delivered or partial outcome. |
| Validation log | `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/validation.txt` | Keep final validation commands and results. |
| Review output | `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling, test suppression, or broad waiver is authorized.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `_condamad/reports/CS-302-CS-304-delivery-report.md` - update delivery status only from proof.
- `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/**` - persist browser QA and validation evidence.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - change only for a proven browser QA blocker.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - change only for a proven rendering blocker.
- `frontend/src/features/natal-chart/NatalInterpretation.css` - change only for a proven desktop or mobile layout blocker.
- `frontend/src/tests/natalChartApi.test.tsx` - targeted CS-303 API regression guard.
- `frontend/src/tests/natalInterpretation.test.tsx` - targeted projection rendering guard.
- `frontend/src/tests/component-architecture-guards.test.ts` - architecture guard owner.

Likely tests:

- `frontend/src/tests/natalChartApi.test.tsx` - B2C projection API client tests.
- `frontend/src/tests/natalInterpretation.test.tsx` - projection rendering state tests.
- `frontend/src/tests/component-architecture-guards.test.ts` - architecture and ownership guards.
- `backend/tests/api/test_projection_openapi.py` - backend OpenAPI projection route proof.
- `backend/tests/api/test_projection_endpoint.py` - backend projection behavior proof.
- `backend/tests/api/test_projection_authorization.py` - entitlement proof.

Files not expected to change:

- `backend/app/**` - out of scope; backend projection runtime behavior remains unchanged.
- `backend/alembic/**` - out of scope; no migration is touched.
- `frontend/package.json` - out of scope; no script or package change is authorized.
- `_condamad/stories/regression-guardrails.md` - out of scope; normal story generation must not enrich the registry.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: start the local frontend and required services through repository scripts; persist output in CS-306 evidence.
- VC2: open `/natal` in a real browser on desktop and mobile viewport sizes; persist screenshots and browser QA ledger.
- VC3: from `frontend`, run `pnpm lint`.
- VC4: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run natalChartApi`.
- VC5: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation`.
- VC6: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi`.
- VC7: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run`.
- VC8: from repo root with venv active, run backend projection pytest from the Contract Shape command.
- VC9: from `backend` with venv active, run a `python -B -c` check proving `/v1/astrology/projections` in `app.openapi()` and `app.routes`.
- VC10: from `frontend`, run `rg -n "fetch\\(.*/v1/astrology/projections" src`.
- VC11: from `frontend`, run `rg -n "style=" src -g "*.tsx"`.
- VC12: from `frontend`, run `rg -n "provider_response|raw_runtime|replay_snapshot|admin_answer_audit|expert_technical_projection_v1|astrology_full_data_v1" src`.
- VC13: from repo root with venv active, run `python -B` to assert CS-306 evidence paths exist and report status matches proof.

## Regression Risks

- Browser QA could be documented without a real `/natal` run, leaving the CS-303 visual startup gap open.
- The report could overstate delivery status while CS-305 full-suite proof is still missing.
- A small UI fix for browser QA could accidentally change CS-303 projection ownership or app-owned disclaimer behavior.
- Windows local startup or Vitest logging could fail for environment reasons and require a precise blocker instead of report promotion.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Start by checking whether CS-305 has final full-suite proof.
- Keep every frontend style change in CSS files and reuse existing design tokens.
- Treat the delivery report as a proof artifact, not as a substitute for validation.

## References

- `_story_briefs/cs-306-close-cs303-browser-qa-and-refresh-delivery-status.md`
- `_condamad/reports/CS-302-CS-304-delivery-report.md`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-after.md`
- `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/00-story.md`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/api/astrologyProjections.ts`
- `_condamad/stories/regression-guardrails.md`
