# Validation Plan

## Environment Assumptions

- Frontend package root: `frontend/`.
- Package manager in this repo: npm scripts from `frontend/package.json`.
- Backend/Python commands are not expected for this frontend-only story.

## Targeted Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story behavior and architecture tests | `npm --prefix frontend run test -- component-architecture natalInterpretation NatalChartPage` | repo root | yes | targeted Vitest tests pass |

## Architecture / Import Guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Canonical owner export | `rg -n "export function NatalInterpretationSection" frontend/src/features/natal-chart` | repo root | yes | hit only in canonical feature owner |
| Old path absence | `rg -n "components/NatalInterpretation|components/natal-interpretation/NatalInterpretationPersonaSelector" frontend/src -g "*.ts" -g "*.tsx"` | repo root | yes | zero active hits |
| Allowlist cleanup | `rg -n "NatalInterpretation|NatalInterpretationPersonaSelector" frontend/src/tests/component-architecture-allowlist.ts` | repo root | yes | zero natal hits |
| Presentational children API-free | `if (Test-Path frontend/src/components/natal-interpretation) { rg -n "apiFetch\\(|fetch\\(|axios|from [\"'](?:.*api|.*features)" frontend/src/components/natal-interpretation -g "*.ts" -g "*.tsx" }` | repo root | yes | zero hits |

## Quality Checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Frontend static check | `npm --prefix frontend run lint` | repo root | yes | TypeScript lint scripts pass |

## DRY / No Legacy Scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| No shim/import compatibility | `rg -n "from [\"'](?:\\.\\./components/NatalInterpretation|@/components/NatalInterpretation)|components/NatalInterpretation|NatalInterpretationPersonaSelector" frontend/src -g "*.ts" -g "*.tsx"` | repo root | yes | only canonical feature/test/presentational references; no old path |

## Diff Review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-related frontend and evidence files changed |
| Whitespace/conflicts | `git diff --check` | repo root | yes | no conflict markers or whitespace errors |
| Worktree status | `git status --short` | repo root | yes | expected story files only plus pre-existing story governance files |

## Skips

No skip is planned. If any command cannot run, record exact reason, risk and
compensating evidence in `10-final-evidence.md`.
