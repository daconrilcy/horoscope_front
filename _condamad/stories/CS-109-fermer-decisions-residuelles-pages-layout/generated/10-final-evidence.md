# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-109-fermer-decisions-residuelles-pages-layout`
- Source story: `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md`
- Capsule path: `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: pre-existing dirty CS-107/CS-108/frontend files, deleted `frontend/lint_output.txt`, untracked audit `2026-05-08-1914`, untracked CS-109 and `BillingCancelPage.test.tsx`.
- Pre-existing dirty files: preserved and treated as story-context changes because CS-109 explicitly closes CS-107/CS-108/audit contradictions.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes
- Frontend subagent: used for `frontend/**`; main session integrated governance/evidence.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story readable. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Six ACs mapped. |
| `generated/04-target-files.md` | yes | yes | PASS | Target map created. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific No Legacy guardrails. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Final evidence complete. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `frontend/src/app/routes.tsx` routes `/privacy` under `LandingLayout`; `/billing/success` and `/billing/cancel` under `AppLayout`. `page-architecture-allowlist.ts` gives explicit owners. | `npm run test -- page-architecture layout` PASS; route/allowlist scan PASS. | PASS | Route owners are enforced by AST route guards. |
| AC2 | `frontend/src/pages/HomePage.tsx` is deleted; no route, barrel export, wrapper, alias or allowlist row remains. | `rg --files src/pages -g "*.tsx" \| rg "HomePage"` zero-hit; `rg -n "HomePage" src/app src/pages/index.ts src/tests/page-architecture-allowlist.ts` zero-hit; page architecture HomePage guard PASS. | PASS | `HomePage` only remains in test guard examples outside the required active-surface scan. |
| AC3 | `frontend/src/pages/landing/LandingPage.tsx` imports and renders `TestimonialsSection`; allowlist classifies it as `page-adjacent-component` owned by `LandingPage`. | `npm run test -- LandingPage visual-smoke` PASS; `rg -n "TestimonialsSection" src/pages/landing/LandingPage.tsx src/tests/page-architecture-allowlist.ts` PASS. | PASS | Display remains controlled by existing feature flag. |
| AC4 | Audit `2026-05-08-1914`, CS-107 inventory and CS-108 evidence now point to CS-109 as the active closure source. | Stale-blocked scan leaves only CS-109 source/negative-guard text; audit validation/lint PASS after update. | PASS | CS-108 original-scope evidence is marked historical/superseded. |
| AC5 | CS-109 capsule contains closure-before/after and generated final evidence; `story-status.md` contains CS-109 row. | `rg -n "CS-109" _condamad/stories` PASS; story validate/lint commands PASS with venv active. | PASS | Registry status synchronized during final closure. |
| AC6 | Frontend route regression tests, page architecture guards, lint and full Vitest suite pass. | `npm run lint` PASS; targeted tests PASS; `npm run test` PASS with 122 files, 1301 passed, 8 skipped. | PASS | React Router future warnings and jsdom canvas/navigation notices are non-blocking existing test-harness output. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/audits/frontend-layouts/2026-05-08-1914/00-audit-report.md` | modified | Mark F-201 closed by CS-109. | AC4 |
| `_condamad/audits/frontend-layouts/2026-05-08-1914/01-evidence-log.md` | modified | Replace stale current-state evidence with CS-109 closure evidence. | AC4, AC6 |
| `_condamad/audits/frontend-layouts/2026-05-08-1914/02-finding-register.md` | modified | Reclassify F-201 as closed by CS-109. | AC4 |
| `_condamad/audits/frontend-layouts/2026-05-08-1914/03-story-candidates.md` | modified | Mark SC-201 closed by CS-109. | AC4 |
| `_condamad/audits/frontend-layouts/2026-05-08-1914/05-executive-summary.md` | modified | Remove active blocked recommendation. | AC4 |
| `_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md` | modified | Align page inventory with runtime owner state. | AC4 |
| `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/generated/10-final-evidence.md` | modified | Historicalize CS-108 original-scope claims and point to CS-109. | AC4 |
| `_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/page-decisions-after.md` | modified | Align decision artifact with current closure. | AC4 |
| `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/closure-before.md` | added | Baseline contradictions and residual surfaces. | AC4, AC5 |
| `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/closure-after.md` | added | Closure proof for routes, deletion, ownership and governance. | AC1-AC5 |
| `_condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/generated/*.md` | added | CONDAMAD capsule and evidence. | AC5 |
| `_condamad/stories/story-status.md` | modified | Synchronize CS-109 status. | AC5 |
| `frontend/src/app/routes.tsx` | modified | Add/keep canonical privacy and billing callback routes. | AC1, AC6 |
| `frontend/src/pages/HomePage.tsx` | deleted | Remove old home page without shim. | AC2 |
| `frontend/src/pages/PrivacyPolicyPage.tsx` | modified | Minimal route/lint-level cleanup for public privacy page. | AC1 |
| `frontend/src/pages/billing/BillingSuccessPage.tsx` | modified | Minimal callback page alignment. | AC1 |
| `frontend/src/pages/billing/BillingCancelPage.tsx` | modified | Route retry actions to canonical subscription settings. | AC1 |
| `frontend/src/pages/landing/LandingPage.tsx` | modified | Compose `TestimonialsSection`. | AC3 |
| `frontend/src/tests/App.test.tsx` | modified | Add `/privacy` public layout coverage. | AC1, AC6 |
| `frontend/src/tests/BillingCancelPage.test.tsx` | added | Cover cancel retry routing. | AC1, AC6 |
| `frontend/src/tests/router.test.tsx` | modified | Assert privacy and billing callback routes. | AC1, AC6 |
| `frontend/src/tests/page-architecture-allowlist.ts` | modified | Move residual decision sources to CS-109 and exact owners. | AC1-AC4 |
| `frontend/src/tests/page-architecture-guards.test.ts` | modified | Add privacy/billing layout and HomePage reintroduction guards. | AC1, AC2, AC6 |

## Files deleted

| File | Reason |
|---|---|
| `frontend/src/pages/HomePage.tsx` | Deleted old home page; `LandingPage` is the canonical `/` owner. |
| `frontend/lint_output.txt` | Pre-existing deleted local output file remained deleted; not a runtime dependency. |

## Tests added or updated

- `frontend/src/tests/App.test.tsx`: `/privacy` renders under public landing layout.
- `frontend/src/tests/router.test.tsx`: route inventory includes `/privacy`, `/billing/success`, `/billing/cancel`.
- `frontend/src/tests/BillingCancelPage.test.tsx`: cancel page retry action targets `/settings/subscription`.
- `frontend/src/tests/page-architecture-guards.test.ts`: privacy under `LandingLayout`, billing callbacks under `AppLayout`, and `HomePage` anti-reintroduction guard.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `npm run test -- page-architecture layout` | `frontend/` | PASS | 0 | 3 files passed, 29 tests passed. |
| `npm run test -- App router BillingSuccessPage BillingCancelPage` | `frontend/` | PASS | 0 | 7 files passed, 83 tests passed. |
| `npm run test -- LandingPage visual-smoke` | `frontend/` | PASS | 0 | 1 file passed, 18 tests passed. |
| `npm run lint` | `frontend/` | PASS | 0 | TypeScript lint projects passed. |
| `npm run test` | `frontend/` | PASS | 0 | 122 files passed; 1301 passed, 8 skipped. |
| `rg --files src/pages -g "*.tsx" \| rg "HomePage"` | `frontend/` | PASS | 1 | No `HomePage.tsx` file found. |
| `rg -n "HomePage" src/app src/pages/index.ts src/tests/page-architecture-allowlist.ts` | `frontend/` | PASS | 1 | No active route/barrel/allowlist hit. |
| `rg -n "privacy\|billing/success\|billing/cancel" src/app/routes.tsx src/tests/page-architecture-allowlist.ts` | `frontend/` | PASS | 0 | Expected route and allowlist hits. |
| `rg -n "TestimonialsSection" src/pages/landing/LandingPage.tsx src/tests/page-architecture-allowlist.ts` | `frontend/` | PASS | 0 | Expected import/render and allowlist hits. |
| `rg -n "CS-108-statuer-pages-publiques-candidates-layout" src/tests/page-architecture-allowlist.ts` | `frontend/` | PASS | 1 | No stale CS-108 decision source in allowlist. |
| `rg -n "needs-user-decision\|dead/unmounted-page-candidate" src/tests/page-architecture-allowlist.ts` | `frontend/` | PASS | 0 | Hits only in type union definitions; no active entries. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` | repo root | PASS | 0 | Story validate, contract explain, lint and strict lint passed with venv active. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors or conflict markers; Git reported line-ending warnings only. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `npm run test:e2e` | no | Story validation plan does not require Playwright; route/layout behavior is covered by Vitest route and architecture guards plus full frontend test suite. | Low browser-only routing risk. | Targeted route tests, page architecture tests, visual-smoke tests and full Vitest suite passed. |

## DRY / No Legacy evidence

- `HomePage.tsx` is absent and has no active route/barrel/allowlist reference.
- No route compatibility alias, redirect, shim, fallback or wrapper was introduced.
- No wildcard or folder-wide page architecture exception was introduced.
- `PAGE_LAYOUT_OWNER_CLASSIFICATIONS` remains the single executable page ownership registry.
- CS-109 closure replaces the stale CS-108 blocker as active governance source.

## Diff review

- `git diff --check` PASS.
- `git diff --stat` reviewed; scope matches frontend runtime/tests plus required CS-107/CS-108/audit/CS-109 governance evidence.
- Pre-existing dirty files were in the story surface or preserved.

## Final worktree status

`git status --short` after final review:

- Modified governance/evidence: CS-107 after inventory, CS-108 final evidence, CS-108 decisions, `story-status.md`.
- Modified frontend runtime/tests: routes, privacy/billing pages, landing page, app/router/page-architecture tests.
- Deleted: `frontend/src/pages/HomePage.tsx`; pre-existing `frontend/lint_output.txt`.
- Untracked story/audit evidence: audit `2026-05-08-1914`, CS-109 capsule and `frontend/src/tests/BillingCancelPage.test.tsx`.

## Remaining risks

- External Stripe dashboard configuration is outside the repository and could override backend defaults.
- No unresolved in-domain CS-109 risk remains.

## Suggested reviewer focus

Review that CS-109 is the sole active closure source for F-201 and that CS-108 residual blocker text is clearly historical, not current state.
