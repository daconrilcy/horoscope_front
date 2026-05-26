# Dev Log

## Preflight

- Initial `git status --short`: `?? _condamad/critical-errors.jsonl`, `?? _condamad/run-state.json`
- Current branch: not-recorded
- Existing dirty files: two unrelated untracked CONDAMAD runtime files above.
- Resume context: prior logs showed story-writing/review completed and CS-323 registered as `ready-to-dev`; no prior app implementation found.

## Search evidence

- Baseline scan saved to `evidence/provider-scan-before.txt`.
- Active scan after implementation saved to `evidence/provider-scan-after.txt`.
- Story-status row verified against path and source brief before implementation.

## Implementation notes

- Repaired missing generated capsule files with `condamad_prepare.py --repair-generated-only`.
- Removed the dormant provider value from `AnalyticsProvider`.
- Removed the provider queue typing and branch from `useAnalytics`.
- Added a provider-normalization test without reintroducing forbidden symbols.
- Removed accidental generated parallel capsule `_condamad/stories/cs-323` created by the first prepare attempt.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only ...` | PASS | Run after venv activation. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py ...` | PASS | Run after venv activation. |
| `pnpm lint` | PASS | Frontend TypeScript lint/typecheck. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics` | PASS | 4 tests. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi` | PASS | 56 tests. |
| `node .\scripts\run-vite-logged.mjs vitest vitest run` | PASS | 116 files, 1280 passed, 8 existing skips. |
| `pnpm build` | PASS | `tsc -b` and Vite build. |
| `rg` negative scans for provider symbols and direct calls | PASS | Exit 1 treated as expected no-match. |
| `git diff --check` | PASS | No whitespace errors. |

## Issues encountered

- First capsule prepare attempt with `--story-key CS-323` created `_condamad/stories/cs-323`; removed after verifying it was inside the workspace and created by this run.

## Decisions made

- No Matomo replacement, alias, wrapper, re-export or soft-disable was added.
- `.env.example` needed no code change because it already documents empty local provider and Plausible host only.

## Final `git status --short`

- Pending final status captured in `generated/10-final-evidence.md`.
