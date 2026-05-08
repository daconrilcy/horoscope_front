# Validation Plan

## Environment assumptions

- Frontend root: `frontend/`.
- Package manager used by repository scripts: `npm`.
- Python story tools must be run after `.\.venv\Scripts\Activate.ps1`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Page/layout guards | `npm run test -- page-architecture layout` | `frontend/` | yes | all tests pass |
| App/router/billing regression | `npm run test -- App router BillingSuccessPage` | `frontend/` | yes | all tests pass |
| Baseline proof | `rg -n "PrivacyPolicyPage|BillingSuccessPage" page-decisions-before.md` | story directory | yes | expected rows found |
| After proof | `rg -n "PrivacyPolicyPage|BillingSuccessPage|BillingCancelPage|HomePage|TestimonialsSection" page-decisions-after.md` | story directory | yes | five rows found |

## Unit tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Page architecture unit guards | `npm run test -- page-architecture layout` | `frontend/` | yes | guard suite passes |

## Integration tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| App route regression | `npm run test -- App router BillingSuccessPage` | `frontend/` | yes | app/router and billing tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Route ownership guard | `npm run test -- page-architecture layout` | `frontend/` | yes | blocked decisions are not route imports |
| Route table scan | `rg -n "PrivacyPolicyPage|BillingSuccessPage|BillingCancelPage|HomePage|TestimonialsSection" src/app/routes.tsx src/tests/page-architecture-allowlist.ts` | `frontend/` | yes | hits only in allowlist for unroute decisions |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden proof vocabulary | `rg -n "PASS with limitation|TODO|wildcard|compatibility wrapper|shim|alias|fallback|migration-only" ../_condamad/stories/CS-108-statuer-pages-publiques-candidates-layout ../_condamad/stories/CS-107-classer-pages-layout-owner/page-layout-owner-after.md` | `frontend/` | yes | no active final proof justification hits after implementation |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Frontend lint/typecheck | `npm run lint` | `frontend/` | yes | no TypeScript errors |
| Story validation | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/00-story.md` | repo root | yes | story validates |
| Story contracts explanation | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/00-story.md` | repo root | yes | contracts explain cleanly |
| Story lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/00-story.md` | repo root | yes | no story lint errors |
| Strict story lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-108-statuer-pages-publiques-candidates-layout/00-story.md` | repo root | yes | no strict story lint errors |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| RG-064/RG-068 frontend guards | `npm run test -- page-architecture layout` | `frontend/` | yes | guards pass |
| RG-066 page-size non-regression | `npm run test -- page-architecture` | `frontend/` | covered | included in targeted command |
| RG-067 no date-format page change | `git diff -- frontend/src/pages frontend/src/utils/formatDate.ts` | repo root | yes | no date-format code changes |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflict check | `git diff --check` | repo root | yes | no whitespace or conflict markers |
| Diff summary | `git diff --stat` | repo root | yes | only expected files changed |
| Worktree status | `git status --short` | repo root | yes | expected dirty files only |

## Commands that may be skipped only with justification

None for CS-108. E2E is not required because no runtime route or UI flow is changed.
