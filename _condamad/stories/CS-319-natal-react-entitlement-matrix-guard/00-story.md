# Story CS-319 natal-react-entitlement-matrix-guard: Add Natal React Entitlement Matrix Guard
Status: done

## Trigger / Source

- Source type: brief direct with repository-informed boundary.
- Source reference: `_story_briefs/cs-319-ajouter-garde-react-entitlement-matrix-natal.md`.
- Related source: `_condamad/reports/CS-312-CS-316-delivery-report.md`.
- Related decision: `docs/architecture/natal-projection-plan-matrix-product-decision.md`.
- Related story: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md`.
- Selected story writer mode: Fast Story Writer Mode.
- Problem statement: `/natal` must not grow a React-owned free/basic/premium entitlement matrix.
- Source-alignment evidence: PASS; the story keeps the brief focused on a targeted frontend drift guard.

## Objective

Add one automated frontend guard that fails when `/natal` projection React owners introduce a local free/basic/premium policy matrix.

The implementation must keep backend responses as the access source, preserve backend-shaped fixtures as test data, and avoid product,
backend, UI, style, build or dependency changes.

## Target State

- `frontend/src/tests/component-architecture-guards.test.ts` or an already-used frontend guard file detects local `/natal` plan policy.
- The guard scopes only the natal projection owners and their tests.
- Backend-shaped fixtures in `frontend/src/tests/natalInterpretation.test.tsx` remain allowed as response simulations.
- A React policy table, branch set or accepted matrix for `free`, `basic` and `premium` in active `/natal` source fails deterministically.
- CS-309 and CS-315 rendering evidence remains backed by existing natal Vitest targets.
- No backend, product decision, CSS, build tooling, auth, DB, migration or entitlement runtime behavior changes.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-319-ajouter-garde-react-entitlement-matrix-natal.md` - source brief read.
- Evidence 2: `_condamad/stories/story-status.md` - tracker consulted to assign `CS-319`.
- Evidence 3: `_condamad/reports/CS-312-CS-316-delivery-report.md` - follow-up recommendation read.
- Evidence 4: `docs/architecture/natal-projection-plan-matrix-product-decision.md` - CS-315 decision boundary read.
- Evidence 5: `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md` - related story read.
- Evidence 6: `frontend/src/features/natal-chart/NatalInterpretation.tsx` - natal container owner read.
- Evidence 7: `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - presentational owner read.
- Evidence 8: `frontend/src/tests/component-architecture-guards.test.ts` - nearest frontend architecture guard read.
- Evidence 9: `frontend/src/tests/natalInterpretation.test.tsx` - CS-309 backend-shaped fixture tests read.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - scoped resolver and targeted ID lookup consulted.
- Source-alignment evidence: PASS; objective, ACs, tasks, guardrails and validations map to every brief acceptance item.

## Domain Boundary

- Domain: frontend-architecture-guard
- In scope:
  - Static or test-based frontend guard for `/natal` projection entitlement drift.
  - Owners under `frontend/src/features/natal-chart`, `frontend/src/components/natal-interpretation`, `frontend/src/pages`, and tests.
  - Existing backend-shaped frontend fixtures that simulate success and 403 projection responses.
  - Validation through `pnpm lint`, targeted Vitest, and bounded `rg` scans.
- Out of scope:
  - Backend entitlement, product matrix, API contracts, docs product changes, auth, DB, migrations, CSS, build tooling and copy changes.
  - Global script creation when the existing component architecture guard can own the check.
  - Registry enrichment in `_condamad/stories/regression-guardrails.md` during normal story generation.
- Explicit non-goals:
  - No React-owned authorization matrix, plan gate, pricing policy, subscription rule or alternate access source.
  - No backend route, service, schema, migration, OpenAPI, Stripe, checkout or billing catalog change.
  - No broad repository scan that blocks unrelated fixtures, backend test data or documentation evidence.

## Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: no supported archetype exactly fits a frontend architecture guard against local entitlement policy drift.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Add only a targeted frontend guard and minimal supporting helper code inside existing frontend test surfaces.
  - Keep React as a renderer of backend success and 403 responses.
  - Keep backend-shaped fixtures allowed in test files when they simulate backend responses.
  - Keep product matrix documents and backend entitlement runtime unchanged.
  - Keep validation bounded to natal projection owners and existing frontend test commands.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: the nearest existing frontend guard cannot express the forbidden patterns without blocking legitimate fixtures.
- Additional validation rules:
  - The guard must inspect active natal projection React source separately from fixture-only test data.
  - The forbidden pattern must include local `free`, `basic`, `premium` plan policy in active `/natal` React owners.
  - The guard must allow `frontend/src/tests/natalInterpretation.test.tsx` backend-shaped response fixtures.
  - The validation plan must include `pnpm lint`, targeted Vitest, and the bounded entitlement scan from the brief.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Vitest proves the guard executes and natal rendering tests still consume backend-shaped fixtures. |
| Baseline Snapshot | yes | Before/after guard evidence proves the only intended surface delta is frontend guard coverage. |
| Ownership Routing | yes | Frontend guard ownership and backend entitlement ownership must remain separate. |
| Allowlist Exception | no | No broad allowlist handling is authorized; only fixture classification is allowed. |
| Contract Shape | yes | The guard needs exact scoped roots, forbidden patterns and fixture classification rules. |
| Batch Migration | no | No batch migration or multi-file conversion is in scope. |
| Reintroduction Guard | yes | Local React entitlement policy must stay absent after this story. |
| Persistent Evidence | yes | Story validation output and review artifacts must be kept for handoff. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | The frontend guard detects local natal plan policy. | Evidence profile: targeted_forbidden_symbol_scan; `pnpm` Vitest runs `component-architecture-guards`. |
| AC2 | The guard scopes active natal projection owners. | Evidence profile: ast_architecture_guard; `rg` checks guarded roots in `frontend/src/tests`. |
| AC3 | Backend-shaped fixture data remains allowed. | Evidence profile: frontend_typecheck_no_orphan; `pnpm` Vitest runs `natalInterpretation`. |
| AC4 | React does not own the plan matrix. | Evidence profile: targeted_forbidden_symbol_scan; `rg` scans `frontend/src/features/natal-chart` and components. |
| AC5 | Existing natal rendering tests still pass. | Evidence profile: frontend_typecheck_no_orphan; `pnpm` Vitest runs `NatalChartPage natalChartApi`. |
| AC6 | No backend or product decision file changes. | Evidence profile: repo_wide_negative_scan; `rg` checks story evidence and `git diff --name-only`. |
| AC7 | Story evidence artifacts are persisted. | Evidence profile: baseline_before_after_diff; `python` checks CS-319 evidence paths. |

## Implementation Tasks

- [ ] Task 1: Identify the nearest existing frontend architecture guard and keep the new check in that ownership path. (AC: AC1, AC2)
- [ ] Task 2: Define scoped active-source roots for natal projection React owners. (AC: AC2, AC4)
- [ ] Task 3: Add a deterministic forbidden-pattern check for local free/basic/premium policy in active source. (AC: AC1, AC4)
- [ ] Task 4: Classify `natalInterpretation.test.tsx` backend-shaped fixtures as allowed test response data. (AC: AC3)
- [ ] Task 5: Keep CS-309/CS-315 natal rendering tests green through targeted Vitest. (AC: AC3, AC5)
- [ ] Task 6: Prove no backend or product decision artifact changed for this frontend guard story. (AC: AC6)
- [ ] Task 7: Persist validation output and source-alignment notes under the CS-319 evidence folder. (AC: AC7)

## Files to Inspect First

- `_story_briefs/cs-319-ajouter-garde-react-entitlement-matrix-natal.md` - source contract.
- `_condamad/reports/CS-312-CS-316-delivery-report.md` - follow-up recommendation.
- `docs/architecture/natal-projection-plan-matrix-product-decision.md` - accepted product/backend boundary.
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md` - related CS-315 constraints.
- `frontend/src/features/natal-chart/NatalInterpretation.tsx` - active natal container owner.
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` - active presentational projection owner.
- `frontend/src/tests/component-architecture-guards.test.ts` - likely canonical guard owner.
- `frontend/src/tests/natalInterpretation.test.tsx` - backend-shaped fixture and rendering evidence.
- `_condamad/stories/regression-guardrails.md` through scoped resolver output and targeted ID lookup only.

## Runtime Source of Truth

- Primary source of truth:
  - `AST guard` encoded in frontend Vitest for forbidden local entitlement policy patterns.
  - `frontend/src/tests/component-architecture-guards.test.ts` through `pnpm` Vitest for architecture guard execution.
  - `frontend/src/tests/natalInterpretation.test.tsx` through `pnpm` Vitest for backend-shaped rendering behavior.
  - `docs/architecture/natal-projection-plan-matrix-product-decision.md` for the product/backend ownership boundary.
- Secondary evidence:
  - Targeted `rg` scans over natal projection owners and frontend tests.
  - `git diff --name-only` after implementation to prove backend and product decision files are unchanged.
- Static scans alone are not sufficient because:
  - The guard itself must execute inside the frontend test runner and preserve existing rendering fixtures.

## Contract Shape

- Contract type:
  - Frontend architecture guard for React-owned `/natal` projection entitlement drift.
- Fields:
  - `guard_owner`: existing frontend test file that owns component architecture guards.
  - `active_source_roots`: natal feature, natal presentational component and page roots scanned as active source.
  - `fixture_roots`: frontend tests that may contain backend-shaped free/basic/premium response fixtures.
  - `forbidden_pattern`: local plan policy matrix or accepted matrix in active React source.
  - `allowed_fixture_pattern`: backend-shaped success and 403 fixture data in test files.
  - `validation_commands`: lint, targeted Vitest and bounded scan commands.
- Required fields:
  - `guard_owner`
  - `active_source_roots`
  - `fixture_roots`
  - `forbidden_pattern`
  - `allowed_fixture_pattern`
  - `validation_commands`
- Optional fields:
  - none
- Status codes:
  - none; no API route or HTTP contract changes.
- Serialization names:
  - none; no runtime JSON serializer is added.
- Frontend type impact:
  - test-only TypeScript guard logic may be added; production React types remain unchanged.
- Generated contract impact:
  - none; no OpenAPI path, generated client, generated manifest or backend schema is changed.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `frontend/src/tests/component-architecture-guards.test.ts`
  - `frontend/src/tests/natalInterpretation.test.tsx`
  - `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/guard-scan-before.txt`
- Comparison after implementation:
  - `frontend/src/tests/component-architecture-guards.test.ts` or the selected existing guard owner.
  - `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/guard-scan-after.txt`
  - `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/validation.txt`
- Expected invariant:
  - The only intended repository delta is the targeted frontend guard, CS-319 story artifacts and validation evidence.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Natal entitlement policy | backend entitlement owner and CS-315 decision doc | React components or frontend tests as policy source |
| React projection rendering | `frontend/src/features/natal-chart/NatalInterpretation.tsx` | backend entitlement implementation |
| Presentational projection display | `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | plan authorization logic |
| Architecture drift guard | `frontend/src/tests/component-architecture-guards.test.ts` | ad hoc global scripts |
| Backend-shaped fixtures | `frontend/src/tests/natalInterpretation.test.tsx` | active production source roots |
| Story evidence | `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/` | application runtime folders |

## Mandatory Reuse / DRY Constraints

- Reuse the existing component architecture guard pattern before creating another guard file.
- Reuse `listFiles`, `readFrontendFile` and existing path helpers from `component-architecture-guards.test.ts`.
- Reuse existing natal rendering tests instead of duplicating CS-309 fixture scenarios.
- Reuse the CS-315 product decision document as the boundary reference.
- Keep one canonical guard for this drift check.
- Do not add external packages, scripts, production hooks, API clients, generated clients, backend helpers or CSS files.

## No Legacy / Forbidden Paths

- No legacy plan matrix may be introduced under active React source.
- No compatibility plan gate may be added to frontend source.
- No fallback branch may translate product policy into local UI authorization.
- Do not create aliases, shims, wrappers or parallel guard mechanisms for the same drift check.
- Do not add a hardcoded entitlement table under `frontend/src/features/natal-chart/**`.
- Do not add a hardcoded entitlement table under `frontend/src/components/natal-interpretation/**`.
- Do not change backend entitlement behavior in this story.
- Forbidden surfaces:
  - `backend/app/**`
  - `backend/tests/**`
  - `docs/architecture/natal-projection-plan-matrix-product-decision.md`
  - CSS, SCSS, build tooling, auth, DB and migration files

## Reintroduction Guard

- Guard target:
  - React cannot become the source of `/natal` plan authorization.
  - Active natal projection owners cannot contain a local free/basic/premium matrix.
  - Test fixtures can keep backend-shaped plan response data without becoming policy.
  - CS-309/CS-315 rendering evidence cannot be replaced by React access logic.
- Guard mechanism:
  - targeted Vitest architecture check;
  - targeted Vitest natal rendering check;
  - bounded scan for `free`, `basic`, `premium`, `accepted_matrix`, `entitlement matrix`, and `plan_code ===`;
  - persisted evidence under the CS-319 evidence folder.
- Guard owner:
  - `frontend/src/tests/component-architecture-guards.test.ts`;
  - `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/validation.txt`.
- Guard evidence:
  - `pnpm --dir frontend exec node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards`;
  - `pnpm --dir frontend exec node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi`;
  - bounded `rg` scan from VC4.

## Regression Guardrails

Scope vector:

- operation: create targeted frontend guard;
- domain: frontend-architecture-guard;
- paths: `frontend/src/features/natal-chart`, `frontend/src/components/natal-interpretation`, `frontend/src/tests`;
- contracts: entitlement boundary, no local policy, architecture guard;
- route surface: `/natal`;
- out of scope: backend, DB, auth, i18n, style, build and migration.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-041 | Entitlement docs and runtime evidence must stay aligned. | CS-315 boundary plus natal Vitest evidence. |
| Registry gap | No exact `/natal` React entitlement-matrix guardrail was returned. | Story-local guard and bounded scan. |

Non-applicable examples:

- RG-047 inline styles are out of scope because no TSX style work is requested.
- RG-052 CSS namespace migration is out of scope because no CSS or build output is touched.
- RG-027 prediction infra is out of scope because this story does not touch backend prediction files.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Guard scan before | `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/guard-scan-before.txt` | Capture baseline scan output. |
| Guard scan after | `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/guard-scan-after.txt` | Prove the final scan result. |
| Validation output | `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/validation.txt` | Keep command results. |
| Source alignment | `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/source-alignment.md` | Prove brief stakes stayed covered. |
| Review output | `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/generated/11-code-review.md` | Keep automatic review in a separate generated file. |

## Allowlist / Exception Register

- Allowlist handling: not applicable
- Reason: no broad allowlist handling is authorized for this frontend guard story.
- Allowed fixture classification:
  - `frontend/src/tests/natalInterpretation.test.tsx` may contain backend-shaped plan response data for success and 403 scenarios.
  - Fixture data must stay in tests and must not be imported by production React code.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no batch migration or multi-file conversion is in scope.

## Expected Files to Modify

Likely files:

- `frontend/src/tests/component-architecture-guards.test.ts` - add the targeted natal entitlement drift guard.
- `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/guard-scan-before.txt` - persist baseline scan output.
- `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/guard-scan-after.txt` - persist final scan output.
- `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/validation.txt` - validation transcript.
- `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/source-alignment.md` - source coverage evidence.

Likely tests:

- `frontend/src/tests/component-architecture-guards.test.ts` - guard behavior and pattern classification.
- `frontend/src/tests/natalInterpretation.test.tsx` - backend-shaped success and 403 rendering evidence.
- `frontend/src/tests/NatalChartPage.test.tsx` - page-level natal projection rendering evidence.
- `frontend/src/tests/natalChartApi.test.ts` - API client response-shape evidence.

Files not expected to change:

- `backend/**` - out of scope; no backend entitlement or API behavior is touched.
- `docs/architecture/natal-projection-plan-matrix-product-decision.md` - out of scope; product decision stays unchanged.
- `frontend/src/**/*.css` and `frontend/src/**/*.scss` - out of scope; no style change is touched.
- `package.json`, lockfiles and build config - out of scope; no dependency or tooling change is touched.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

- VC1: `pnpm --dir frontend lint`
- VC2: `pnpm --dir frontend exec node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards`
- VC3: `pnpm --dir frontend exec node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi`
- VC4:

```powershell
cd frontend; rg -n "free.*basic.*premium|accepted_matrix|entitlement matrix|plan_code.*===" src/features/natal-chart src/components/natal-interpretation src/pages src/tests
```
- VC5: `git diff --name-only -- backend docs/architecture/natal-projection-plan-matrix-product-decision.md`
- VC6: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/validation.txt').exists()"`
- VC7: `python -c "from pathlib import Path; assert Path('_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/evidence/source-alignment.md').exists()"`

Before VC6 and VC7, activate the venv with `. .\.venv\Scripts\Activate.ps1`.

## Regression Risks

- A guard that scans all tests could block legitimate backend-shaped fixture data.
- A guard that scans too little could miss a local React plan matrix in a natal owner.
- A local React branch could hide product/backend divergence instead of rendering backend 403 responses.
- A new global script could duplicate existing frontend architecture guard ownership.
- A frontend test-only story could drift into product decision, backend entitlement, CSS or build changes.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.
- Activate `.\.venv\Scripts\Activate.ps1` before every Python command in this repository.
- Keep file-level comments in French for new or significantly modified application and test files.
- Keep the guard in existing frontend architecture test ownership unless a blocker is recorded.
- Persist the required evidence artifacts before requesting review.

## References

- `_story_briefs/cs-319-ajouter-garde-react-entitlement-matrix-natal.md`
- `_condamad/reports/CS-312-CS-316-delivery-report.md`
- `docs/architecture/natal-projection-plan-matrix-product-decision.md`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/tests/component-architecture-guards.test.ts`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `_condamad/stories/regression-guardrails.md`
