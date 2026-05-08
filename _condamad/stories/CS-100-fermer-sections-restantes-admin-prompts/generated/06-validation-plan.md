# Validation Plan - CS-100

## Environment assumptions

- Frontend package manager requested by story: `npm`.
- Python commands, if run, must follow `.\\.venv\\Scripts\\Activate.ps1`.
- Backend commands are out of scope.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| AdminPrompts behavior | `npm run test -- AdminPromptsPage AdminPromptsRouting AdminPromptsCatalogFlow page-architecture` | `frontend/` | yes | all targeted tests pass |
| Page architecture guard | `npm run test -- page-architecture` | `frontend/` | yes | page architecture guard passes |

## Static / forbidden scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| TS/API bypass scan | `rg -n "@ts-nocheck|@ts-ignore|apiFetch\\(" src/pages/admin/AdminPromptsPage.tsx src/features/admin-prompts -g "*.tsx"` | `frontend/` | yes | zero hits |
| AdminPrompts page-size closure | `rg -n "pages/admin/AdminPromptsPage.tsx" src/tests/page-architecture-allowlist.ts` | `frontend/` | yes | zero hits if exception removed |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Type/lint | `npm run lint` | `frontend/` | yes | exits 0 |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only scoped files changed |
| Worktree status | `git status --short` | repo root | yes | expected dirty files plus pre-existing user changes |
