# Final Evidence - cs-127-reduire-app-css-par-primitives-types-modulaires

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: cs-127-reduire-app-css-par-primitives-types-modulaires
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Story source: `_condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/00-story.md`
- Branch: `main`
- Pre-existing dirty files: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`
- AGENTS.md rules considered: Windows/PowerShell, React frontend, no inline styles, Python commands only after venv activation
- Capsule generated: yes

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | `condamad_story_validate.py` and strict lint pass |
| `generated/01-execution-brief.md` | yes | yes | PASS | generated capsule file |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | all AC statuses updated to PASS |
| `generated/04-target-files.md` | yes | yes | PASS | generated capsule file |
| `generated/06-validation-plan.md` | yes | yes | PASS | generated capsule file |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | generated capsule file |
| `generated/10-final-evidence.md` | yes | yes | PASS | this file |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `app-css-size-and-duplication-before.md` | baseline artifact present | PASS | App.css baseline: 4094 lines |
| AC2 | `App.css` import-only surface | `app-css-size-and-duplication-after.md` | PASS | App.css now 12 lines |
| AC3 | `frontend/src/styles/app/*.css` | `rg --files src/styles/app` | PASS | 11 typed modules |
| AC4 | `.notice`, `.state-centered`, `.select-card`, `.form-control`, `.stack`, `.cluster` | primitive scan and visual smoke tests | PASS | primitives consumed in TSX |
| AC5 | mechanical token cleanup | mechanical-token scan, `theme-tokens` | PASS | no `--app-...-2` mechanical token hits |
| AC6 | no alias/compat vocabulary in App CSS surface | legacy vocabulary scan | PASS | no hits |
| AC7 | `design-system-guards.test.ts` | `npm run test -- design-system` | PASS | guards cover modules, stale consumers, duplicate selectors, single-use vars |
| AC8 | TSX className migrations | `npm run lint`, `npm run build`, targeted Vitest | PASS | runtime build clean |
| AC9 | `app-css-variable-usage.md` | single-use guard | PASS | all retained variables documented |
| AC10 | TSX primitive composition | primitive TSX scan | PASS | selected consumers compose primitives |
| AC11 | `app-css-tsx-consumers.md` | stale TSX consumer guard | PASS | changed selectors mapped |
| AC12 | duplicate-body reduction | after metrics artifact | PASS | duplicate bodies 27 -> 10 |

## Files changed

- `frontend/src/App.css`
- `frontend/src/styles/app/*.css`
- selected TSX consumers under `frontend/src/app`, `frontend/src/components`, `frontend/src/features`, and `frontend/src/pages`
- frontend tests under `frontend/src/tests`
- CONDAMAD story capsule and generated evidence files

## Tests added or updated

- Updated App CSS design-system guards to read the full modular CSS surface.
- Updated theme, visual smoke, legacy style, css fallback, and BottomNav tests to avoid stale `App.css`-only reads.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `npm run test -- BottomNavPremium design-system theme-tokens visual-smoke` | `frontend` | PASS | 0 | 168 tests |
| `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | `frontend` | PASS | 0 | 153 tests |
| `npm run lint` | `frontend` | PASS | 0 | TypeScript lint configs |
| `npm run build` | `frontend` | PASS | 0 | Vite production build clean |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/00-story.md` | repo root | PASS | 0 | venv activated |
| `.\\.venv\\Scripts\\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/00-story.md` | repo root | PASS | 0 | venv activated |

## Commands skipped or blocked

- None.

## DRY / No Legacy evidence

- Duplicate declaration bodies reduced by 63.0%.
- Legacy/alias/compat scan returned no hits for `src/App.css` and `src/styles/app`.
- App CSS surface has guard coverage for module filenames, duplicate selectors/size regression, stale TSX consumers, and single-use custom-property decisions.

## Diff review

- `git diff --stat`: App CSS shrunk by roughly 4100 lines; new typed modules are untracked until commit/stage.
- `git diff --check`: PASS; only CRLF normalization warnings from Git on Windows.

## Final worktree status

- Modified and untracked files remain for user review; no commit was created.

## Remaining risks

- Visual drift risk is low but not zero because the CSS surface was split into modules and selected TSX class compositions changed.
- Story source was restored during implementation after a local generation incident; current `00-story.md` passes CONDAMAD validation and strict lint.

## Suggested reviewer focus

- Review `frontend/src/styles/app/media.css` and TSX primitive compositions for visual parity.
- Review design-system guard names and coverage against future App CSS regressions.
