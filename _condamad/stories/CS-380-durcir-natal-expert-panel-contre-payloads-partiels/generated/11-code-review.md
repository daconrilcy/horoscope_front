# CS-380 Implementation Review

Verdict: CLEAN

## Review Scope

- Story: `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/00-story.md`
- Source brief: `_story_briefs/cs-380-durcir-natal-expert-panel-contre-payloads-partiels-sans-masquer-contrat.md`
- Tracker row: `_condamad/stories/story-status.md`, source-matched row for `CS-380`
- Implementation files: `NatalExpertPanel.tsx`, `NatalExpertPanel.css`, `NatalExpertPanel.test.tsx`
- Guardrails checked: `RG-047`, `RG-052`

## Iteration 1 Findings

- Fixed: `hasTraditionalConditionBlocks` accepted `hayz: {}` and `rejoicing: {}` as complete blocks. This could render
  empty fact rows and mask a partial expert sub-block instead of showing the localized degraded state.
- Evidence added: `NatalExpertPanel.test.tsx` now covers a present-but-incomplete `hayz` sub-block and verifies that the
  neighboring valid `beta` traditional entry still renders `hayz.is_hayz` and `rejoicing.rejoicing_house`.

## Iteration 2 Findings

- Fixed: `hasTraditionalConditionBlocks` checked only key presence for required traditional facts. A runtime payload with
  `hayz.is_hayz: null` could still render an empty complete fact row and mask contract drift.
- Evidence added: `NatalExpertPanel.test.tsx` now covers a required `hayz` fact set to `null` and verifies that the valid
  neighboring `beta` traditional entry remains visible.

## Final Review

- Complete expert payload rendering remains unchanged and covered by Vitest.
- Partial `traditional_conditions` entries now degrade when a required `hayz` or `rejoicing` block is missing, incomplete,
  null, or undefined at runtime.
- Valid neighboring traditional entries remain visible.
- Nominal API types still require `TraditionalPlanetCondition.hayz` and `TraditionalPlanetCondition.rejoicing`.
- No React-side astrology calculation, scoring, doctrinal fallback, inline style, ad hoc trace, or console logging was added.
- Backend public-contract repair remains out of scope and routed to `CS-379`.

## Validation Results

- PASS: `pnpm --dir frontend test -- NatalExpertPanel` - 1 file, 7 tests.
- PASS: `pnpm --dir frontend lint`.
- PASS: `pnpm --dir frontend build`.
- PASS: `pnpm --dir frontend test -- BirthProfilePage NatalChartPage natalInterpretation` - 4 files, 149 tests.
- PASS: `pnpm --dir frontend test -- inline-style`.
- PASS: `pnpm --dir frontend test -- design-system theme-tokens legacy-style`.
- PASS: touched-file `style=` scan found no matches.
- PASS: added-line derivation scan found no added `calculate|score|infer|derive|doctrine|fallback`.
- PASS: touched-file `trackEvent|console\.` scan found no matches.
- PASS: RG-052 CSS stale-token scan found no `migration-only` or `--default_dropshadow`.
- PASS: nominal API type guard ran under active venv.
- PASS: `condamad_validate.py` ran under active venv.
- PASS: `condamad_story_validate.py` and `condamad_story_lint.py --strict` ran under active venv.
- PASS: `git diff --check` on touched story and frontend files.
- PASS: local Vite smoke returned `HTTP 200` on `http://127.0.0.1:5181`.

## Propagation

- no-propagation: the correction is local to this story implementation and does not reveal reusable process learning.

## Residual Risk

- None identified for this implementation review.
