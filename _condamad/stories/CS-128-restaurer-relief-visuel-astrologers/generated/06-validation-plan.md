# Validation Plan

<!-- Plan de validation executable pour CS-128. -->

## Environment Assumptions

- Frontend commands run from `frontend/`.
- Python story validation runs from repo root after `.\.venv\Scripts\Activate.ps1`.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Astrologers route and guards | `npm run test -- AstrologersPage design-system visual-smoke` | `frontend/` | yes | all targeted tests pass |
| Frontend static guard clusters | `npm run test -- theme-tokens css-fallback inline-style legacy-style` | `frontend/` | yes | all targeted tests pass |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Lint/typecheck | `npm run lint` | `frontend/` | yes | no TypeScript errors |
| Production build | `npm run build` | `frontend/` | yes | build succeeds |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| App.css remains clean | `rg -n "person-card|people-page|astrologer" src/App.css` | `frontend/` | yes | zero hits |
| No legacy astrologer selectors | `rg -n "astrologer-card|astrologer-grid|compat|compatibility|legacy|alias|shim" src/styles/app src/pages src/features/astrologers` | `frontend/` | yes | zero active hits |
| No inline style on route/cards | `rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers/components/AstrologerCard.tsx src/features/astrologers/components/AstrologerGrid.tsx` | `frontend/` | yes | zero hits |
| Approved App CSS modules only | `rg --files src/styles/app` | `frontend/` | yes | only approved type modules |

## Story Validation

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validate | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` | repo root | yes | validation passes |
| Story validate contracts | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` | repo root | yes | validation passes |
| Story lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` | repo root | yes | lint passes |
| Story lint strict | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` | repo root | yes | strict lint passes |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff check | `git diff --check` | repo root | yes | no whitespace/conflict marker issue |
| Diff summary | `git diff --stat` | repo root | yes | story-scoped changes only |
| Worktree status | `git status --short` | repo root | yes | expected dirty files only |
