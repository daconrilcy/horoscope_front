# Validation Plan

## Environment assumptions

- Repository root: `c:\dev\horoscope_front`
- Frontend root: `frontend`
- Package manager: npm scripts already present in `frontend/package.json`
- Python story validators must run only after `.\.venv\Scripts\Activate.ps1`

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Profile behavior and route tests | `npm run test -- AstrologersPage` | `frontend` | yes | all selected tests pass |
| Design-system and visual smoke | `npm run test -- AstrologersPage design-system visual-smoke` | `frontend` | yes | all selected tests pass |
| Inline/fallback/page architecture guards | `npm run test -- inline-style css-fallback page-architecture` | `frontend` | yes | all selected tests pass |
| Browser profile overflow guard | `npm run test:e2e -- astrologer-profile-ui.spec.ts` | `frontend` | yes | desktop and mobile profile assertions pass |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Frontend lint/type gate | `npm run lint` | `frontend` | yes | exit 0 |
| Frontend production build | `npm run build` | `frontend` | yes | exit 0 |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| App.css profile pollution | `rg -n "AstrologerProfile|profile-" src/App.css` | `frontend` | yes | zero hits |
| Inline styles in touched TSX | `rg -n "style=" src/pages/AstrologerProfilePage.tsx src/features/astrologers/components/AstrologerProfileSections.tsx` | `frontend` | yes | zero hits |
| No blunt overflow masking | `rg -n "overflow-x:\s*hidden" src/pages/AstrologerProfilePage.css` | `frontend` | yes | zero hits |
| Required profile rhythm selectors | `rg -n "profile-main-grid|specialties-card|profile-mission-card" src/pages/AstrologerProfilePage.css` | `frontend` | yes | required selectors present |
| Mobile/profile selectors | `rg -n "@media \(max-width: 768px\)|profile-hero|profile-mobile" src/pages/AstrologerProfilePage.css` | `frontend` | yes | required selectors present |
| Bounded legacy vocabulary | `rg -n "astrologer-card|astrologer-grid|compat|compatibility|legacy|alias|shim" src/pages/AstrologerProfilePage.css src/features/astrologers/components/AstrologerProfileSections.tsx src/pages/AstrologerProfilePage.tsx` | `frontend` | yes | zero active hits |

## Story validation

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story contract validate | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-129-ameliorer-ui-profil-astrologue/00-story.md` | repo root | yes | exit 0 |
| Story contract explain | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-129-ameliorer-ui-profil-astrologue/00-story.md` | repo root | yes | exit 0 |
| Story lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-129-ameliorer-ui-profil-astrologue/00-story.md` | repo root | yes | exit 0 |
| Strict story lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-129-ameliorer-ui-profil-astrologue/00-story.md` | repo root | yes | exit 0 |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped files changed |
| Whitespace/conflict marker check | `git diff --check` | repo root | yes | exit 0 |
| Final worktree status | `git status --short` | repo root | yes | expected story changes only |
