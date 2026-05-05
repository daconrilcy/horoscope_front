# Final Evidence - CS-052

## Story status

- Validation outcome: PASS_WITH_LIMITATIONS
- Ready for review: yes
- Story key: CS-052-reduire-cluster-restant-fallbacks-css-natal-chart
- Source story: `_condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart/00-story.md`
- Capsule path: `_condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: story-status modified; audit and CS-052..CS-055 story folders untracked before implementation.
- AGENTS.md files considered: root `AGENTS.md`
- Capsule generated: yes, `generated/` created in the requested CS-052 folder.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story intact. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC6 completed. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Frontend plan replaces generic template. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `css-fallbacks-before.md` captures 33 initial NatalChart fallbacks. | Before/after artifact comparison. | PASS | Lot bounded to `NatalChartPage.css`. |
| AC2 | `NatalChartPage.css` now removes 30 fallbacks whose `--premium-*` tokens are declared in `premium-theme.css` and imported by `main.tsx`. | `npm run test -- css-fallback design-system theme-tokens` PASS. | PASS | No fallback replacement introduced. |
| AC3 | `css-fallback-allowlist.md` and `design-system-allowlist.ts` keep 3 matching NatalChart exceptions. | Design-system/fallback guard PASS. | PASS | Registries synchronized. |
| AC4 | `css-fallbacks-after.md` classifies `--premium-text-muted` and `--premium-glass-border-soft` as `needs-user-decision`. | `rg -n "needs-user-decision\|premium" css-fallbacks-*.md` PASS. | PASS_WITH_LIMITATIONS | Product/theme decision still required. |
| AC5 | No new fallback added. | Final CSS fallback scan shows only allowlisted hits; 3 NatalChart hits remain classified. | PASS | Other files remain out of scope. |
| AC6 | CSS/allowlist changes only. | `npm run lint` PASS. | PASS | No E2E needed for static fallback migration. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `frontend/src/pages/NatalChartPage.css` | modified | Remove guaranteed fallbacks. | AC2, AC5 |
| `frontend/src/styles/css-fallback-allowlist.md` | modified | Keep only remaining NatalChart fallback exceptions. | AC3, AC4 |
| `frontend/src/tests/design-system-allowlist.ts` | modified | Synchronize executable fallback exceptions. | AC3 |
| `_condamad/stories/CS-052-.../css-fallbacks-before.md` | added | Baseline. | AC1 |
| `_condamad/stories/CS-052-.../css-fallbacks-after.md` | added | Final classification. | AC1-AC5 |

## Files deleted

- None.

## Tests added or updated

- Updated executable fallback allowlist in `frontend/src/tests/design-system-allowlist.ts`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `npm run test -- css-fallback design-system theme-tokens` | `frontend` | PASS | 0 | 103 tests passed. |
| `npm run lint` | `frontend` | PASS | 0 | TypeScript lint/typecheck passed. |
| `rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," src -g "*.css"` | `frontend` | PASS | 0 | Remaining hits are allowlisted/classified; 3 in NatalChart. |
| `rg -n "needs-user-decision\|premium" css-fallbacks-*.md` | story folder | PASS | 0 | Ambiguous premium fallbacks documented. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; CRLF warnings only. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart/00-story.md` | repo root after venv activation | PASS | 0 | CONDAMAD story validation passed. |
| `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-052-reduire-cluster-restant-fallbacks-css-natal-chart/00-story.md` | repo root after venv activation | PASS | 0 | CONDAMAD story lint passed. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `npm run test:e2e` | no | Static CSS fallback migration; no route logic or user flow changed. | Low visual regression risk. | Targeted Vitest guards and lint passed. |

## DRY / No Legacy evidence

- `NatalChartPage.css` fallback count reduced from 33 to 3.
- Removed fallbacks were deleted, not replaced by alternate literals.
- Remaining fallback exceptions are exact and classified `needs-user-decision`.

## Diff review

- `git diff --stat`: reviewed; CS-052 files are scoped to NatalChart CSS and fallback allowlists.
- `git diff --check`: PASS with CRLF warnings only.

## Final worktree status

- Worktree remains dirty with the requested CS-052..CS-055 changes and pre-existing `_condamad` audit/story files.

## Remaining risks

- `--premium-text-muted` and `--premium-glass-border-soft` remain unresolved because the tokens are not declared in `premium-theme.css`.

## Suggested reviewer focus

- Confirm the three retained premium fallback blockers require product/theme decision before token declaration or deletion.
