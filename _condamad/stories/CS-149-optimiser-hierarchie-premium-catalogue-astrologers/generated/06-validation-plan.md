# Validation Plan

## Environment assumptions

- Frontend root: `frontend/`
- Package scripts: npm scripts from `frontend/package.json`
- Python commands, if used, must run after `.\.venv\Scripts\Activate.ps1`.

## Commands

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted frontend tests | `npm run test -- AstrologersPage design-system visual-smoke` | `frontend/` | yes | all targeted tests pass |
| Frontend lint/typecheck | `npm run lint` | `frontend/` | yes | exit 0 |
| App.css forbidden catalogue styles | `rg -n "people-page|person-card" src/App.css` | `frontend/` | yes | zero hits |
| Legacy selector scan | `rg -n "astrologer-" src/styles/app src/features/astrologers` | `frontend/` | yes | zero hits |
| Inline style scan | `rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers` | `frontend/` | yes | zero hits |
| Fragile featured/height scan | `rg -n "featured=\{index === 0\}|person-card--featured|height:\s*24[0-9]px|height:\s*25[0-9]px" src/features/astrologers src/styles/app src/tests` | `frontend/` | yes | zero hits |
| Diff check | `git diff --check` | repo root | yes | no whitespace/conflict errors |
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped files changed |

## Conditional checks

- Run local dev server and browser/runtime checks if feasible after code changes.
- Full `npm run test` may be skipped only with reason if targeted suite plus lint covers the story scope.
