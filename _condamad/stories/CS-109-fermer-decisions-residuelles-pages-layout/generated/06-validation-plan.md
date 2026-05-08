# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- Frontend root: `frontend/`
- Frontend package manager used by this repo: `npm`
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Page architecture and layout owners | `npm run test -- page-architecture layout` | `frontend/` | yes | all tests pass |
| App/router/billing coverage | `npm run test -- App router BillingSuccessPage BillingCancelPage` | `frontend/` | yes | all tests pass |
| Landing testimonials coverage | `npm run test -- LandingPage visual-smoke` | `frontend/` | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Removed HomePage file | `rg --files src/pages -g "*.tsx" \| rg "HomePage"` | `frontend/` | yes | no hit |
| Removed HomePage active references | `rg -n "HomePage" src/app src/pages/index.ts src/tests/page-architecture-allowlist.ts` | `frontend/` | yes | no hit |
| Canonical route/allowlist evidence | `rg -n "privacy\|billing/success\|billing/cancel" src/app/routes.tsx src/tests/page-architecture-allowlist.ts` | `frontend/` | yes | expected hits only |
| Testimonials owner evidence | `rg -n "TestimonialsSection" src/pages/landing/LandingPage.tsx src/tests/page-architecture-allowlist.ts` | `frontend/` | yes | expected hits only |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Frontend lint/typecheck script | `npm run lint` | `frontend/` | yes | exit 0 |
| Story validate | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` | repo root | yes | exit 0 |
| Story validate contracts | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` | repo root | yes | exit 0 |
| Story lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` | repo root | yes | exit 0 |
| Story strict lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` | repo root | yes | exit 0 |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflict check | `git diff --check` | repo root | yes | exit 0 |
| Diff summary | `git diff --stat` | repo root | yes | story scope only |
| Worktree status | `git status --short` | repo root | yes | expected dirty files classified |
