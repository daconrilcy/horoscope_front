# Final Evidence — CS-380-durcir-natal-expert-panel-contre-payloads-partiels

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-380-durcir-natal-expert-panel-contre-payloads-partiels`
- Source story: `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/00-story.md`
- Source brief: `_story_briefs/cs-380-durcir-natal-expert-panel-contre-payloads-partiels-sans-masquer-contrat.md`
- Capsule path: `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: story-scope frontend files, generated/evidence files, and `story-status.md` were already dirty; `_condamad/run-state.json` was also untracked.
- Story registry check: `CS-380` row matched the requested story path and brief source.
- Capsule check: required generated files were already present; `condamad_validate.py` PASS.
- Skills applied: `condamad-dev-story`, `condamad-frontend-dev`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story unchanged. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Present before generated capsule reads. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Updated with AC-by-AC evidence. |
| `generated/04-target-files.md` | yes | yes | PASS | Present before generated capsule reads. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Present before generated capsule reads. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Present before generated capsule reads. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Updated for review handoff. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | Local runtime guard prevents direct `condition.hayz.is_hayz` reads on partial entries. | `partial-before.txt` captures failing test before implementation; `partial-after.txt` captures PASS after implementation. | PASS |
| AC2 | Partial entry renders `Contrat expert partiel` with localized copy. | `pnpm --dir frontend test -- NatalExpertPanel` PASS. | PASS |
| AC3 | Complete neighboring entries render through unchanged fact rows. | Vitest asserts complete `beta` fields remain visible. | PASS |
| AC4 | Complete expert payload still renders hayz/rejoicing labels. | Existing complete-payload test PASS. | PASS |
| AC5 | API nominal type contract unchanged and strict. | AST guard PASS; `pnpm --dir frontend build` PASS. | PASS |
| AC6 | No React-side astrology derivation added. | Added-line scan for forbidden derivation terms returns no matches. | PASS |
| AC7 | No inline style added. | Touched-file `style=` scan returns no matches; CSS owns visual state. | PASS |
| AC8 | Evidence artifacts persisted. | `evidence/partial-before.txt`, `partial-after.txt`, `validation.txt`, Vite startup logs present. | PASS |
| AC9 | No non-sensitive trace convention was applicable. | Touched-file `trackEvent|console\.` scan returns no matches. | PASS |

## Files changed

- `frontend/src/features/natal-chart/NatalExpertPanel.tsx`
- `frontend/src/features/natal-chart/NatalExpertPanel.css`
- `frontend/src/tests/NatalExpertPanel.test.tsx`
- `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/generated/**`
- `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/evidence/**`
- `_condamad/stories/story-status.md`

## Files deleted

- none

## Tests added or updated

- Added Vitest coverage for a runtime partial `traditional_conditions.alpha` entry missing `hayz`.
- Existing full expert rendering test remains active and passing.

## Commands run

| Command | Working directory | Result | Evidence |
|---|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py ...` | repo root with venv active | PASS | capsule structure valid |
| `pnpm --dir frontend test -- NatalExpertPanel` before fix | repo root | expected FAIL | `evidence/partial-before.txt` |
| `pnpm --dir frontend test -- NatalExpertPanel` after fix | repo root | PASS | `evidence/partial-after.txt`, `validation.txt` |
| `pnpm --dir frontend test -- BirthProfilePage NatalChartPage natalInterpretation` | repo root | PASS | 4 files / 149 tests passed |
| `pnpm --dir frontend test -- inline-style` | repo root | PASS | RG-047 guard passed |
| `pnpm --dir frontend test -- design-system theme-tokens legacy-style` | repo root | PASS | RG-052 guard passed |
| `rg -n "hayz: TraditionalHayzCondition|rejoicing: TraditionalRejoicingCondition" frontend/src/api/natal-chart/index.ts` | repo root | PASS | `validation.txt` |
| touched-file `rg` scans for `style=`, `trackEvent|console\.` | repo root | PASS | no matches on touched files |
| added-line diff scan for `calculate|score|infer|derive|doctrine|fallback` | repo root | PASS | no added matches |
| `pnpm --dir frontend lint` | repo root | PASS | `validation.txt` |
| `pnpm --dir frontend build` | repo root | PASS | `validation.txt` |
| `pnpm --dir frontend dev` | repo root | BLOCKED | port `5173` already in use; captured in `vite-dev-smoke.err.txt` |
| `pnpm --dir frontend dev -- --port 5174` | repo root | BLOCKED | project wrapper still starts Vite on `5173`; captured in retry logs |
| `pnpm --dir frontend exec vite --port 5174 --host 127.0.0.1` | repo root | PASS | server stayed up during smoke window, then was stopped |
| `pnpm --dir frontend exec vite --host 127.0.0.1 --port 5176 --strictPort` | repo root | PASS | HTTP smoke `200`; PID stopped after smoke |
| `git diff --check -- <story paths>` | repo root | PASS | no whitespace errors |

## Commands skipped or blocked

- Browser QA with login/generation not run; no backend server or manual browser session was required by the capsule. Risk: real generation flow remains covered indirectly by component-level runtime payload simulation.

## DRY / No Legacy evidence

- No API type weakening, global mapper, route-level masking, shim, alias, or compatibility service was added.
- Partial runtime tolerance remains local to `TraditionalConditionsBlock`.
- New CSS reuses existing premium tokens and adds no inline style.
- Static trace decision: no `trackEvent`/`console` added.

## Diff review

- `git diff --stat` limited to the expected frontend files before evidence/status edits.
- `git diff --check` PASS.
- Existing broad scans found unrelated pre-existing `style=`, `console.`, and domain `score` strings outside or before this story's added lines; touched-file and added-line scans are clean.

## Final worktree status

- Expected modified/untracked story files: frontend panel, panel CSS, panel test, generated/evidence artifacts, story status.
- Pre-existing untracked file still present: `_condamad/run-state.json`.

## Remaining risks

- Full E2E generation flow was not executed; reviewer should focus on whether component-level tolerance is sufficient for the navigation risk stated in AC7.

## Suggested reviewer focus

- Confirm that the local `unknown` runtime narrowing is acceptable and does not promote partial `traditional_conditions` to the nominal API contract.

## Feedback loop routing

- No reusable skill/guardrail update required; local Vitest and existing RG-047/RG-052 coverage are sufficient.
