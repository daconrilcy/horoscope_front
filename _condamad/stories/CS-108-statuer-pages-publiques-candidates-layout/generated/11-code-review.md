# CONDAMAD Code Review - CS-108

## Review target

- Story: `CS-108-statuer-pages-publiques-candidates-layout`
- Capsule: `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout`
- Verdict: `CLEAN`

## Inputs reviewed

- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `page-decisions-before.md`
- `page-decisions-after.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1532/02-finding-register.md`
- `_condamad/audits/frontend-layouts/2026-05-08-1532/03-story-candidates.md`
- `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md`
- `frontend/src/tests/page-architecture-allowlist.ts`
- `frontend/src/tests/page-architecture-guards.test.ts`
- `frontend/src/pages/index.ts`
- Current git diff and validation evidence.

## Diff summary

CS-108 changes are scoped to:

- decision artifacts and generated capsule evidence;
- CS-107 after inventory alignment;
- `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` structured decisions;
- page-architecture guards;
- removal of `HomePage` from the runtime page barrel.

No route file was changed, no page file was deleted, and no CSS/runtime UI implementation was changed.

## Review layers

| Layer | Result | Notes |
|---|---|---|
| Story conformance | CLEAN after fixes | AC2 evidence was strengthened with structured `decisionSource`; all ACs remain `PASS`. |
| Technical risk | CLEAN after fixes | Dead/unmounted candidates are guarded against route/import reattachment, including dynamic module imports and barrel exports. |
| Source finding closure | CLEAN | F-101 is closed for the bounded decision phase: five residual files have explicit retained decisions, owners and exit conditions. |
| Main CONDAMAD review | CLEAN | Required validations are present and passing; no forbidden compatibility or broad exception was introduced. |

## Findings

No remaining findings.

Resolved during review:

| Finding | Severity | Resolution |
|---|---|---|
| AC2 evidence only proved symbol presence and used self-referential text. | Medium | Added structured `decisionSource`, `expiresOn` and `removalStory`; updated evidence. |
| Dead candidates were not guarded against runtime reattachment. | Medium | Added route/import reattachment guard and removed `HomePage` barrel export. |
| Provenance guard used a story-specific string literal. | Low | Replaced literal check with structured metadata validation. |
| Dead candidate guard missed dynamic/raw module imports, nested relative imports and single-quoted exports. | Medium | Strengthened `sourceReattachesPage` to resolve module specifiers relative to each importer and added targeted guard cases. |
| Story/status registry still said ready-to-dev. | Low | Updated `00-story.md` and `story-status.md` to `done`. |

## Acceptance audit

| AC | Status | Evidence |
|---|---|---|
| AC1 | PASS | `page-decisions-before.md` lists the five residual files. |
| AC2 | PASS | `page-decisions-after.md` and allowlist entries include owner, `decisionSource`, `expiresOn` or `removalStory`. |
| AC3 | PASS | `routes.tsx` has no residual page symbol hit; page-architecture tests pass. |
| AC4 | PASS | No route was added; route owner tree unchanged. |
| AC5 | PASS | CS-107 after inventory mirrors CS-108 decisions. |
| AC6 | PASS | No page was deleted; `HomePage` barrel export removed; future removals require dedicated story. |
| AC7 | PASS | Frontend lint and targeted Vitest suites pass. |

## Validation audit

Recorded and re-run validation:

- `npm run test -- page-architecture layout` - PASS, 26 tests.
- `npm run test -- App router BillingSuccessPage` - PASS, 80 tests.
- `npm run test -- formatDate page-architecture` - PASS, 37 tests.
- `npm run lint` - PASS.
- Story validation and lint with `.\.venv\Scripts\Activate.ps1` - PASS.
- Targeted scans for residual route/barrel hits and old provenance literals - PASS.
- `git diff --check` - PASS with line-ending warnings only.

## DRY / No Legacy audit

- No route, redirect, compatibility wrapper, shim, fallback, alias route or broad page exception was introduced.
- `HomePage` is no longer available through `frontend/src/pages/index.ts`.
- `dead/unmounted-page-candidate` entries fail the guard if routed or runtime-imported without classification change, including nested relative imports.
- `needs-user-decision` entries fail the guard if routed.

## Commands run by reviewer

See `generated/10-final-evidence.md` for the full command table.

## Residual risks

No remaining CS-108 acceptance risk identified. Privacy/billing exposure and physical removals remain intentionally blocked behind named owner decisions or dedicated removal stories.

## Verdict

`CLEAN`
