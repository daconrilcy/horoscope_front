# Story CS-305 stabilize-frontend-full-vitest-suite-after-projection-wiring: Stabilize Frontend Full Vitest Suite After Projection Wiring
Status: ready-to-dev

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-305-stabilize-frontend-full-vitest-suite-after-projection-wiring.md`.
- Selected mode: Repo-informed story with Fast Story Writer Mode.
- Problem statement: the CS-302 to CS-304 delivery report remains partially delivered because the full frontend Vitest suite is not green.
- Source stakes: make full frontend validation usable, protect CS-303 projection wiring, and prevent unproved unrelated-failure claims.
- Source-alignment evidence: PASS; objective, ACs, tasks, evidence, and guardrails preserve the brief without expanding backend or UI product scope.

## Objective

Stabilize the complete frontend `vitest run` validation after CS-303 by reproducing, correcting, or formally classifying every initial failing test.
The story closes only when the full logged Vitest command passes and CS-303 targeted projection checks still pass.

## Target State

- `node .\scripts\run-vite-logged.mjs vitest vitest run` passes from `frontend`.
- Every initial failing test has a persisted disposition: corrected regression, corrected stale test fixture, or proven pre-existing non-CS-303 issue.
- CS-303 projection behavior remains unchanged: central API client, projection states, app-owned disclaimers, and hidden internal fields.
- Frontend lint and targeted CS-303 Vitest suites remain green after the full-suite stabilization.
- Evidence states whether `_condamad/reports/CS-302-CS-304-delivery-report.md` can remove the full frontend suite limitation.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-305-stabilize-frontend-full-vitest-suite-after-projection-wiring.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-305` after `CS-304`.
- Evidence 3: `_condamad/reports/CS-302-CS-304-delivery-report.md` - delivery report limitation inspected.
- Evidence 4: `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` - CS-303 limits inspected.
- Evidence 5: `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/11-code-review.md` - review verdict and failures inspected.
- Evidence 6: `frontend/scripts/run-vite-logged.mjs` - logged Vitest runner inspected.
- Evidence 7: `frontend/src/tests/**` - targeted test inventory read from `frontend/src/tests` only.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - scoped resolver output selected local guardrails only.
- Source-alignment evidence: PASS; the story addresses the report limitation and keeps CS-303 behavior out of scope for product changes.

## Domain Boundary

- Domain: frontend-validation
- In scope:
  - Reproducing the full frontend Vitest suite through the logged runner.
  - Classifying each initial failure with concrete evidence.
  - Correcting frontend tests, fixtures, mocks, translations, or code that cause the failing assertions.
  - Preserving CS-303 projection API consumption, projection states, disclaimers, and hidden internal fields.
  - Updating CS-303 evidence or the CS-302 to CS-304 delivery report only when validation status changes.
- Out of scope:
  - Backend projection implementation, backend schemas, DB schema, auth redesign, admin UI, migrations, and public API contract changes.
  - Rebuilding `/natal`, broad i18n rewrites, unrelated design-system migration, and suppressing tests to force a green run.
  - Registry enrichment for `_condamad/stories/regression-guardrails.md`.
- Explicit non-goals:
  - No backend route, serializer, projection builder, persistence, entitlement model, prompt, provider, admin, replay, or audit implementation.
  - No skipped, narrowed, deleted, or renamed tests solely to obtain a passing full suite.
  - No direct frontend HTTP bypass of the central projection API client.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a frontend full-suite stabilization and validation-closure contract.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Change only frontend code, tests, fixtures, mocks, translations, and evidence/report files required to close the full Vitest suite limitation.
  - Keep `POST /v1/astrology/projections` consumption routed through the central frontend API client.
  - Keep CS-303 user-facing projection states, app-owned disclaimer ownership, and hidden internal-field policy unchanged.
  - Keep CSS in stylesheet files and reuse existing frontend variables, classes, tokens, and component patterns.
  - Preserve public API contracts and backend behavior unchanged.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: a failing test encodes an unresolved product decision rather than stale validation or a real regression.
- Additional validation rules:
  - Initial full-suite output must be captured before fixes unless the first run is already green.
  - Every initial failure must map to a corrected file or a concrete classification artifact.
  - Targeted CS-303 Vitest commands must pass after the full-suite fix.
  - Static guards must prove no direct projection `fetch`, inline style, or forbidden internal projection field is introduced.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Logged `vitest run`, targeted Vitest commands, and `pnpm lint` prove frontend validation behavior. |
| Baseline Snapshot | yes | Initial and final full-suite logs prove the validation limitation was closed. |
| Ownership Routing | yes | Tests, fixtures, mocks, translations, API calls, and report evidence must stay in canonical owners. |
| Allowlist Exception | no | No allowlist handling is authorized for test suppression or broad failure waivers. |
| Contract Shape | yes | The validation contract defines exact commands, artifacts, and projection guard scans. |
| Batch Migration | no | No batch migration or multi-file conversion campaign is in scope. |
| Reintroduction Guard | yes | Direct projection HTTP calls, inline styles, and internal projection fields must stay absent. |
| Persistent Evidence | yes | Full-suite logs, failure ledger, validation output, and report status evidence must be kept. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The initial full-suite state is captured. | Evidence profile: baseline_before_after_diff; `node .\scripts\run-vite-logged.mjs vitest vitest run`. |
| AC2 | Every initial failing test has a disposition. | Evidence profile: baseline_before_after_diff; `python` checks CS-305 failure ledger. |
| AC3 | Frontend lint passes. | Evidence profile: frontend_typecheck_no_orphan; `pnpm lint` from `frontend`. |
| AC4 | API tests pass. | `frontend/src/tests/natalChartApi.test.tsx`; `node .\scripts\run-vite-logged.mjs vitest vitest run natalChartApi`. |
| AC5 | Rendering tests pass. | `frontend/src/tests/natalInterpretation.test.tsx`; `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation`. |
| AC6 | Arch guard. | `frontend/src/tests/component-architecture-guards.test.ts`; `vitest` through VC5 exact logged command. |
| AC7 | The complete frontend Vitest suite passes. | Evidence profile: frontend_typecheck_no_orphan; `node .\scripts\run-vite-logged.mjs vitest vitest run`. |
| AC8 | Projection guard scans stay clean. | Evidence profile: targeted_forbidden_symbol_scan; `rg` checks projection fetches, inline styles, and internals. |
| AC9 | Delivery limitation status is evidenced. | Evidence profile: baseline_before_after_diff; `python` checks CS-305 report-status artifact. |

## Implementation Tasks

- [ ] Task 1: Inspect the delivery report, CS-303 final evidence, CS-303 review, frontend tests, and logged Vitest runner. (AC: AC1)
- [ ] Task 2: Run the full logged Vitest suite and persist the initial output or the already-green explanation. (AC: AC1)
- [ ] Task 3: Create a failure ledger that maps every initial failing test to owner, cause, and disposition evidence. (AC: AC2)
- [ ] Task 4: Correct frontend code, tests, fixtures, mocks, or translations for each proven failing assertion. (AC: AC2, AC7)
- [ ] Task 5: Preserve CS-303 targeted projection behavior with all required targeted Vitest commands. (AC: AC4, AC5, AC6)
- [ ] Task 6: Run `pnpm lint` from `frontend` and fix frontend lint issues introduced by this story. (AC: AC3)
- [ ] Task 7: Run the full logged Vitest suite after fixes and persist the passing output. (AC: AC7)
- [ ] Task 8: Run the projection guard scans for direct HTTP bypass, inline styles, and forbidden internal fields. (AC: AC8)
- [ ] Task 9: Persist the final delivery-limitation decision and update CS-303 or report evidence only for validation-status closure. (AC: AC9)

## Files to Inspect First

- `_story_briefs/cs-305-stabilize-frontend-full-vitest-suite-after-projection-wiring.md` - source brief.
- `_condamad/reports/CS-302-CS-304-delivery-report.md` - current delivery limitation.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` - CS-303 final evidence.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/11-code-review.md` - CS-303 review and full-suite failure note.
- `frontend/scripts/run-vite-logged.mjs` - canonical logged Vitest runner.
- `frontend/src/tests/**` - failing tests and shared test utilities after the initial run identifies exact files.
- `frontend/src/api/astrologyProjections.ts` - CS-303 API owner that must remain central.
- `frontend/src/features/natal-chart/**` - CS-303 projection rendering area to preserve.
- `frontend/src/components/natal-interpretation/**` - CS-303 display and disclaimer area to preserve.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `node .\scripts\run-vite-logged.mjs vitest vitest run` from `frontend`.
  - Targeted CS-303 logged Vitest commands for `natalChartApi`, `natalInterpretation`, and component architecture guards.
  - `pnpm lint` from `frontend`.
  - `AST guard` coverage through frontend architecture and forbidden-symbol scans.
- Secondary evidence:
  - Failure ledger under `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/evidence/`.
  - Targeted `rg` scans in `frontend/src` for projection HTTP bypass and forbidden internal projection fields.
- Static scans alone are not sufficient because:
  - The story closes a test-suite limitation, so the logged full Vitest command is the decisive runtime validation.

## Contract Shape

- Contract type:
  - Frontend validation stabilization and evidence contract.
- Fields:
  - `test_file`: failing test file path from the initial full-suite run.
  - `test_name`: failing test name from Vitest output.
  - `initial_failure_symptom`: concise copied symptom from the logged run.
  - `classification`: final disposition value.
  - `changed_owner`: frontend file or artifact changed to close the failure.
  - `validation_command`: command proving the final status.
  - `final_status`: pass, already-green, or blocked-product-decision.
- Required fields:
  - `test_file`
  - `test_name`
  - `classification`
  - `validation_command`
  - `final_status`
- Optional fields:
  - `linked_report_update_path`
- Status codes:
  - none; this story does not change HTTP behavior or API response codes.
- Serialization names:
  - Ledger keys are written exactly as `test_file`, `test_name`, `classification`, `validation_command`, and `final_status`.
- Required commands:
  - `pnpm lint`
  - `node .\scripts\run-vite-logged.mjs vitest vitest run natalChartApi`
  - `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation`
  - `node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi`
  - `node .\scripts\run-vite-logged.mjs vitest vitest run`
- Required status values:
  - corrected-regression
  - corrected-test-fixture
  - corrected-mock-or-translation
  - already-green-with-evidence
  - blocked-product-decision
- Frontend type impact:
  - only type changes required by corrected frontend tests or code are authorized.
- Backend type impact:
  - none; backend API contracts remain unchanged.
- Generated contract impact:
  - no generated client or OpenAPI output change is authorized.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/evidence/full-vitest-before.txt`
  - `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/evidence/failure-ledger.md`
- Comparison after implementation:
  - `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/evidence/full-vitest-after.txt`
  - `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/evidence/validation.txt`
  - `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/evidence/report-status.md`
- Expected invariant:
  - The only intended validation delta is that the full frontend Vitest suite becomes green without weakening CS-303 projection behavior.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Full frontend suite execution | `frontend/scripts/run-vite-logged.mjs` | Ad hoc unlogged test command as final proof |
| Test fixes | `frontend/src/tests/**` and tested frontend owner files | Deleted or skipped tests for artificial green status |
| Projection API transport | `frontend/src/api/astrologyProjections.ts` through central client | Page-local direct `fetch` |
| Projection display behavior | `frontend/src/features/natal-chart/**` and `frontend/src/components/natal-interpretation/**` | Dashboard or admin surfaces |
| Styles | Existing `.css` files and design tokens | Inline `style` attributes in TSX |
| Evidence artifacts | CS-305 `evidence/` and generated review files | Application source folders |

## Mandatory Reuse / DRY Constraints

- Reuse existing frontend test utilities from `frontend/src/tests/test-utils.tsx`.
- Reuse existing mocks, fixtures, and API test patterns instead of creating parallel test harnesses.
- Reuse `frontend/scripts/run-vite-logged.mjs` for full-suite proof and targeted Vitest proof.
- Reuse `frontend/src/api/astrologyProjections.ts` and the central API client for any touched projection path.
- Reuse existing CSS variables and stylesheet files; do not add inline styles.
- Do not add external packages, generated clients, duplicate API clients, broad test helpers, or report-only fixes.

## No Legacy / Forbidden Paths

- No legacy test skip path may be added for the full frontend suite.
- No compatibility wrapper may be added around failing tests.
- No fallback projection API client may be added in React.
- Do not create aliases, shims, wrappers, or parallel validation commands to avoid the logged runner.
- Do not call `fetch` directly from page or component files for `/v1/astrology/projections`.
- Do not expose `provider_response`, `raw_runtime`, `replay_snapshot`, `admin_answer_audit`, or `expert_technical_projection_v1`.
- Do not change backend projection code, backend contracts, migrations, or public API schemas.

## Reintroduction Guard

- Guard path 1: `frontend/src` must not gain direct HTTP calls to `/v1/astrology/projections`.
- Guard path 2: touched TSX files must not gain inline `style` attributes.
- Guard path 3: frontend source must not expose internal projection fields named in the CS-305 validation plan.
- Required deterministic guards:
  - `rg -n "fetch\\(.*/v1/astrology/projections" src` from `frontend`.
  - `rg -n "style=" src -g "*.tsx"` from `frontend`.
  - `rg -n "provider_response|raw_runtime|replay_snapshot|admin_answer_audit|expert_technical_projection_v1|astrology_full_data_v1" src`.

## Regression Guardrails

| Guardrail | Applicability | Evidence |
|---|---|---|
| RG-047 `CS-029-encadrer-styles-inline-statiques-frontend` | Touched TSX files keep static styles out of inline attributes. | `rg` inline-style scan; `pnpm lint`. |
| Story-local projection guard | CS-303 projection API must stay central and public-only. | `rg` projection scans; targeted Vitest. |
| Needs-investigation | Resolver returned backend/docs guardrails for frontend scope; they are non-local to this story. | Resolver output stored in evidence. |

Non-applicable examples that prevent scope drift:

- RG-007 is not selected because admin LLM observability endpoints are out of scope.
- RG-041 is not selected because entitlement documentation is not edited.
- Backend route guardrails are not selected because backend runtime files are unchanged.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Initial full suite log | `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/evidence/full-vitest-before.txt` | Prove initial state. |
| Failure ledger | `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/evidence/failure-ledger.md` | Track every initial failing test. |
| Validation log | `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/evidence/validation.txt` | Validation proof. |
| Final full suite log | `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/evidence/full-vitest-after.txt` | Prove final full-suite pass. |
| Report status | `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/evidence/report-status.md` | Report decision. |
| Review output | `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/generated/11-code-review.md` | Review handoff. |

## Allowlist / Exception Register

- Allowlist register: not applicable
- Reason: no allowlist handling, test suppression, or broad failure waiver is authorized.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-step conversion is in scope.

## Expected Files to Modify

Likely files:

- `frontend/src/tests/**` - update failing tests, fixtures, mocks, or shared test setup after the initial ledger identifies exact owners.
- `frontend/src/pages/**` - update page code only for proven real frontend regressions found by failing tests.
- `frontend/src/components/**` - update component code only for proven real frontend regressions found by failing tests.
- `frontend/src/features/**` - preserve or correct feature behavior covered by failing tests.
- `frontend/src/i18n/**` - update translations only when a failing test proves stale localization data.
- `_condamad/stories/CS-305-stabilize-frontend-full-vitest-suite-after-projection-wiring/evidence/**` - persist validation evidence.
- `_condamad/reports/CS-302-CS-304-delivery-report.md` - update only when final evidence proves the limitation can be removed.
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md` - update only for validation-status closure.

Likely tests:

- `frontend/src/tests/DashboardPage.test.tsx` - possible owner for dashboard failures.
- `frontend/src/tests/DailyHoroscopePage.test.tsx` - possible owner for daily horoscope failures.
- `frontend/src/tests/ShortcutCard.test.tsx` - possible owner for shortcut failures.
- `frontend/src/tests/ConsultationsPage.test.tsx` - possible owner for consultation flow or localization failures.
- `frontend/src/tests/natalChartApi.test.tsx` - CS-303 targeted API regression guard.
- `frontend/src/tests/natalInterpretation.test.tsx` - CS-303 targeted projection rendering guard.
- `frontend/src/tests/component-architecture-guards.test.ts` - CS-303 architecture guard owner.

Files not expected to change:

- `backend/**` - out of scope; backend projection contracts and runtime behavior remain unchanged.
- `frontend/src/api/astrologyProjections.ts` - should remain unchanged unless a failing test proves CS-303 API wrapper regression.
- `frontend/package.json` - out of scope; no script or package change is authorized.
- `_condamad/stories/regression-guardrails.md` - out of scope; normal story generation must not enrich the registry.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run` before fixes and save output to CS-305 evidence.
- VC2: from `frontend`, run `pnpm lint`.
- VC3: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run natalChartApi`.
- VC4: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation`.
- VC5: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi`.
- VC6: from `frontend`, run `node .\scripts\run-vite-logged.mjs vitest vitest run` after fixes.
- VC7: from `frontend`, run `rg -n "fetch\\(.*/v1/astrology/projections" src`.
- VC8: from `frontend`, run `rg -n "style=" src -g "*.tsx"`.
- VC9: from `frontend`, run `rg -n "provider_response|raw_runtime|replay_snapshot|admin_answer_audit|expert_technical_projection_v1|astrology_full_data_v1" src`.
- VC10: from repo root with venv active, run `python -B` to assert CS-305 evidence paths exist.

## Regression Risks

- A stale test update could weaken user-facing behavior instead of correcting the tested expectation.
- A full-suite fix could accidentally change CS-303 projection behavior, especially central API usage or hidden internal fields.
- A report update could overstate delivery status without final full-suite proof.
- Windows Vitest logging can hide useful failure detail unless both stdout and stderr logs are preserved.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Start by running the full logged Vitest suite and creating the failure ledger.
- Keep every frontend style change in CSS files and reuse existing design tokens.
- Treat report and CS-303 evidence updates as validation-status artifacts only.

## References

- `_story_briefs/cs-305-stabilize-frontend-full-vitest-suite-after-projection-wiring.md`
- `_condamad/reports/CS-302-CS-304-delivery-report.md`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/11-code-review.md`
- `frontend/scripts/run-vite-logged.mjs`
- `frontend/src/tests/**`
- `_condamad/stories/regression-guardrails.md`
