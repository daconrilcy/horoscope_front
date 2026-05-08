# Final Evidence

## Current closure note

This file is historical evidence for the original CS-108 scope. The active
closure source for the residual page decisions is now
`_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/generated/10-final-evidence.md`.
CS-109 supersedes the original CS-108 blocker state by routing privacy and
billing callbacks, deleting `HomePage`, and owning `TestimonialsSection` from
`LandingPage`.

## Historical CS-108 story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-108-statuer-pages-publiques-candidates-layout`
- Source story: `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/00-story.md`
- Capsule path: `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: recorded in `generated/09-dev-log.md`
- Pre-existing dirty files: CS-103 to CS-107 story status/governance files, `regression-guardrails.md`, `story-status.md`, deleted `frontend/lint_output.txt`, untracked CS-108/audit artifacts
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes, missing generated files created during implementation

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story readable. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created for CS-108. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | ACs mapped. |
| `generated/04-target-files.md` | yes | yes | PASS | Target map created. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific guardrails created. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completion evidence in progress. |

## Historical AC validation for original CS-108 scope

The rows below are retained as evidence for the original CS-108 implementation
boundary only. They are not current-state claims after CS-109. Current route,
deletion and ownership truth is recorded in CS-109 final evidence.

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `page-decisions-before.md` liste les cinq residus avec classification, owner initial, route et preuve. | `rg -n "PrivacyPolicyPage|BillingSuccessPage" page-decisions-before.md` PASS. | PASS | Baseline historique complet. |
| AC2 | Dans le scope original CS-108, `frontend/src/tests/page-architecture-allowlist.ts` et `page-decisions-after.md` portaient owner, `decisionSource`, `expiresOn` ou `removalStory`. | `npm run test -- page-architecture layout` PASS; scan des cinq symboles dans `page-decisions-after.md` PASS. | PASS | Etat original supersede par CS-109. |
| AC3 | Dans le scope original CS-108, `frontend/src/app/routes.tsx` restait sans route pour les trois pages bloquees. | `npm run test -- page-architecture layout` PASS; scan `routes.tsx` zero-hit PASS. | PASS | Etat original supersede par CS-109. |
| AC4 | Dans le scope original CS-108, aucune route n'etait ajoutee. | `npm run test -- page-architecture layout` PASS. | PASS | Etat original supersede par CS-109. |
| AC5 | `page-layout-owner-after.md` aligne les cinq lignes avec l'allowlist CS-108. | `rg -n "HomePage" page-layout-owner-after.md` PASS; page-architecture PASS. | PASS | Inventaire CS-107 synchronise. |
| AC6 | Dans le scope original CS-108, aucune suppression physique de page n'etait faite; CS-109 supprime ensuite `HomePage`. | `git diff --stat` historique CS-108; page-architecture PASS; scan `src/pages/index.ts` zero-hit pour `HomePage`. | PASS | Etat original supersede par CS-109. |
| AC7 | Frontend change limite a l'allowlist et au guard. | `npm run lint` PASS; `npm run test -- App router BillingSuccessPage` PASS. | PASS | React Router warnings existants non bloquants dans les tests billing. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `generated/01-execution-brief.md` | added | Capsule execution contract. | all |
| `generated/03-acceptance-traceability.md` | added | AC traceability. | all |
| `generated/04-target-files.md` | added | Target file map. | all |
| `generated/05-implementation-plan.md` | added | Implementation plan. | all |
| `generated/06-validation-plan.md` | added | Validation plan. | all |
| `generated/07-no-legacy-dry-guardrails.md` | added | No Legacy evidence plan. | all |
| `generated/09-dev-log.md` | added | Preflight and decision log. | all |
| `generated/10-final-evidence.md` | added | Final evidence. | all |
| `page-decisions-before.md` | added | Baseline des cinq residus CS-107. | AC1 |
| `page-decisions-after.md` | added | Decisions finales et preuves. | AC2, AC6 |
| `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md` | modified | Alignement historique avec CS-108. | AC5 |
| `frontend/src/tests/page-architecture-allowlist.ts` | modified | Owners, raisons et sorties explicites pour les cinq residus. | AC2, AC3, AC5, AC6 |
| `frontend/src/tests/page-architecture-guards.test.ts` | modified | Guard contre decisions anonymes sur pages bloquees ou candidates mortes. | AC3, AC5, AC7 |
| `frontend/src/pages/index.ts` | modified | Retirer le re-export runtime de `HomePage` pour conserver la classification dead/unmounted. | AC6 |

## Historical files deleted

None by original CS-108. `HomePage.tsx` is deleted later by CS-109.

## Tests added or updated

- Updated `frontend/src/tests/page-architecture-guards.test.ts` with a decision-source guard for blocked or dead candidate page entries.
- Updated `frontend/src/tests/page-architecture-guards.test.ts` with a runtime route/import guard for dead candidate page entries.
- Strengthened `frontend/src/tests/page-architecture-guards.test.ts` so dead candidate detection resolves module specifiers relative to the importing file and covers nested relative imports, `@pages` imports, dynamic imports, barrel exports with single or double quotes, and JSX usage.
- Added a targeted guard unit proving `./sections/TestimonialsSection`, single-quoted `HomePage` barrel export, and `@pages/HomePage` dynamic import are detected.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `npm run test -- page-architecture layout` | `frontend/` | PASS | 0 | 3 files passed, 26 tests passed after final guard fix. |
| `npm run test -- App router BillingSuccessPage` | `frontend/` | PASS | 0 | 6 files passed, 80 tests passed; React Router future warnings only. |
| `npm run test -- formatDate page-architecture` | `frontend/` | PASS | 0 | 2 files passed, 37 tests passed; RG-067 regression subset. |
| `npm run lint` | `frontend/` | PASS | 0 | TypeScript lint projects passed. |
| `rg -n "PrivacyPolicyPage|BillingSuccessPage" page-decisions-before.md` | story directory | PASS | 0 | Baseline rows found. |
| `rg -n "PrivacyPolicyPage|BillingSuccessPage|BillingCancelPage|HomePage|TestimonialsSection" page-decisions-after.md` | story directory | PASS | 0 | Five after decision rows found. |
| `rg -n "PrivacyPolicyPage|BillingSuccessPage|BillingCancelPage|HomePage|TestimonialsSection|CS-108 2026-05-08|Decision sourcee CS-108" src/app src/pages/index.ts src/tests/page-architecture-allowlist.ts` | `frontend/` | PASS | 0 | Historical original CS-108 command; superseded by CS-109 route and allowlist evidence. |
| `rg -n "PrivacyPolicyPage|BillingSuccessPage|BillingCancelPage|HomePage|TestimonialsSection" src/app/routes.tsx` | `frontend/` | PASS | 0 | Historical original CS-108 `NO_HITS`; superseded by CS-109 route evidence. |
| `rg -n "HomePage" src/pages/index.ts` | `frontend/` | PASS | 0 | `NO_HITS`; no barrel re-export remains. |
| `rg -n "CS-108 2026-05-08|Decision sourcee CS-108" src/tests/page-architecture-allowlist.ts src/tests/page-architecture-guards.test.ts` | `frontend/` | PASS | 0 | `NO_HITS`; provenance is structured. |
| `rg -n <forbidden closure vocabulary pattern> page-decisions-after.md generated/10-final-evidence.md ../CS-107.../page-layout-owner-after.md` | `frontend/` | PASS | 0 | One allowed negative statement hit in CS-107 about absence of broad pattern exception; no active closure justification hit. |
| `rg -n "fetch\(|axios\.|\bany\b|style=\{\{" src/pages/index.ts src/tests/page-architecture-allowlist.ts src/tests/page-architecture-guards.test.ts` | `frontend/` | PASS | 0 | `NO_HITS`; no direct HTTP, `any`, or inline style in modified frontend files. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/00-story.md` | repo root | PASS | 0 | CONDAMAD story validation passed with venv active. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/00-story.md` | repo root | PASS | 0 | Required contracts present; no missing required contracts. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/00-story.md` | repo root | PASS | 0 | Story lint passed with venv active. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/00-story.md` | repo root | PASS | 0 | Strict story lint passed with venv active. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors or conflict markers; Git reported line-ending warnings only. |
| `git diff --stat` | repo root | PASS | 0 | Reviewed scope; includes pre-existing dirty files plus CS-108 files. |
| `git status --short` | repo root | PASS | 0 | Reviewed final worktree status. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `npm run test:e2e` | no | No runtime route or browser flow changed by CS-108. | Low browser-only risk. | Route/table guards and app/router tests passed. |
| Local dev server startup | no | Change limited to tests and governance registry; no runtime UI route changed. | Low startup risk. | `npm run lint` and targeted Vitest suites passed. |

## DRY / No Legacy evidence

- In original CS-108, no route, redirect, compatibility layer or alternate-path behavior was added.
- The original CS-108 `routes.tsx` no-hit evidence is historical; CS-109 now owns route closure.
- `frontend/src/pages/index.ts` no longer re-exports `HomePage`.
- `page-architecture-guards.test.ts` rejects `dead/unmounted-page-candidate` route/import reattachment by resolving module specifiers relative to each runtime source file.
- No broad pattern or folder-wide page exception was added.
- Existing CS-107 negative statement about broad pattern exceptions is an allowed proof statement, not an active exception.
- `HomePage.tsx` and `TestimonialsSection.tsx` were not deleted in original CS-108; `HomePage.tsx` is deleted by CS-109.

## Diff review

- `git diff --check` PASS.
- `git diff --stat` reviewed. Story-owned changes are CS-108 artifacts, CS-107 after inventory, `frontend/src/pages/index.ts`, and the two frontend test/allowlist files.
- Pre-existing unrelated dirty files remain present and were not reverted.

## Final worktree status

Final `git status --short` includes expected CS-108 untracked files plus pre-existing dirty CS-103 to CS-107 governance/status files, `regression-guardrails.md`, `story-status.md`, deleted `frontend/lint_output.txt`, and untracked audit folder.

## Remaining risks

None for CS-108 acceptance. The source audit finding that was still open after
CS-108 is closed by CS-109.

## Suggested reviewer focus

Review CS-109 for the current route/deletion/ownership closure. Review this file only as historical CS-108 evidence.

## Amendment - 2026-05-08 user decisions applied

After the follow-up audit, the user supplied the missing decisions. CS-109 is
the active closure story for these changes:

- `PrivacyPolicyPage` is now routed at `/privacy` under `LandingLayout`.
- `BillingSuccessPage` is now routed at `/billing/success` because backend checkout config defaults `STRIPE_CHECKOUT_SUCCESS_URL` to that path.
- `BillingCancelPage` is now routed at `/billing/cancel` because backend checkout config defaults `STRIPE_CHECKOUT_CANCEL_URL` to that path.
- `HomePage.tsx` was removed because the landing page replaces the old home page.
- `TestimonialsSection` is now composed by `LandingPage` and remains controlled by `VITE_SHOW_TESTIMONIALS`.

Updated validation:

- `npm run test -- page-architecture layout`: PASS.
- `npm run test -- App router BillingSuccessPage BillingCancelPage`: PASS.
- `npm run test -- LandingPage visual-smoke`: PASS.
- `npm run lint`: PASS.
