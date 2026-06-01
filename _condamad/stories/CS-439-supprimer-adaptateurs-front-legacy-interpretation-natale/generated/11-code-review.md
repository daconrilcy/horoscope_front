# Implementation Review CS-439

Verdict: CLEAN.

## Review Scope

- Story: `_condamad/stories/CS-439-supprimer-adaptateurs-front-legacy-interpretation-natale/00-story.md`.
- Source brief: `_story_briefs/cs-439-supprimer-adaptateurs-front-legacy-interpretation-natale.md`.
- Tracker row: `CS-439`, matching story path and source brief, reviewed on 2026-06-01.
- Guardrails reviewed: `RG-047`, `RG-153`, `RG-154`, `RG-155`, `RG-158`, `RG-170`, `RG-173`.
- Implementation surfaces reviewed: frontend API hook, public `/natal` rendering, command body construction, DOM guard tests, evidence artifacts.

## Iteration 1 Findings

- Finding 1: final review evidence was stale.
  `generated/11-code-review.md` still contained the pre-implementation editorial story-contract review and explicitly stated it was obsolete
  for final implementation evidence.
- Finding 2: story status evidence drift.
  `story-status.md` already marked CS-439 as `done`, but `00-story.md` and `generated/10-final-evidence.md` still said
  `ready-to-review`.

## Fix Applied

- Replaced this file with a fresh implementation review verdict.
- Synchronized `00-story.md` and `generated/10-final-evidence.md` to the tracker status `done`.
- Initial bounded production scans found no old use-case adapter symbols in the public reading flow.
- The final code-vs-brief alignment pass found one residual `level` heuristic in public reading selection/rendering and removed it.
- Propagation decision: no-propagation; the correction is local to this story evidence.

## Iteration 2 Findings

- Finding 3: brief-level alignment gap.
  `NatalInterpretation.tsx` still used `item.level` to choose persisted short/complete readings, and
  `NatalInterpretationContent.tsx` used `meta.level` to decide whether to render the public body or the regeneration message.

## Iteration 2 Fix Applied

- `NatalInterpretation.tsx` now treats persisted complete readings as explicit persisted-reading rows via `persona_id` or
  `prompt_version_id`, not via `level`.
- Ambiguous preview rows from the history list are no longer reused as public readings; the modern product action supplies the
  preview payload.
- `NatalInterpretationContent.tsx` now renders from public schema presence (`theme_natal*`, narrative V1, Basic V2), not `level`.
- `natalInterpretation.test.tsx` proves a contradictory `level` cannot select the reading, and legacy short-history rows do not
  suppress the modern preview action.
- `NatalChartPage.test.tsx` fixture was updated to the public `theme_natal.preview.v1` schema instead of a generic `short` use case.

## Fresh Review After Fix

- AC1-AC4: public `theme_natal` API command and payload flow are implemented without the old DTO adapter target.
- AC5: remaining `variant_code` hits are entitlement gate/display reads only, not command construction.
- AC6-AC7: DOM guard and tests retain old symbols only as denylist literals, not positive fixtures.
- AC8: no inline style syntax is present in the bounded touched TSX surfaces.
- AC9: removed adapter symbols are absent from bounded production frontend roots.
- AC10: removal audit, before/after scans, validation output, and review evidence are persisted.
- AC11: PDF actions and generation actions use the modern product-action endpoint; no retired refresh control was found.
- Brief-specific level check: no `use_case` or `level` heuristic remains for public reading selection or content rendering; residual
  `level` hits are display badges only.

## Validation Results

- Frontend targeted tests covering API, rendering, DOM guard, and page flow.
  - Result: PASS, 4 files, 136 tests.
- `pnpm --dir frontend lint`
  - Result: PASS.
- Legacy use-case scan over `frontend/src`.
  - Result: PASS with expected denylist-only hit in `frontend/src/tests/natalPublicDomGuard.test.tsx`.
- Variant command scan over natal feature, component, API, and page roots.
  - Result: PASS with entitlement-only hits in `NatalChartPage.tsx` and `NatalAstrologerMode.tsx`.
- Removed adapter scan over natal API, feature, and component roots.
  - Result: PASS, zero hits.
- Inline-style scan over touched public reading TSX roots.
  - Result: PASS, zero hits.
- Level/use-case heuristic scan over natal API, feature, and component roots.
  - Result: PASS; residual `level` hits are display-only labels.
- Story validation after activating `.venv`.
  - Result: PASS.
- Strict story lint after activating `.venv`.
  - Result: PASS.
- Final capsule validation after activating `.venv`.
  - Result: PASS.
- Local Vite startup on `http://127.0.0.1:5176`.
  - Result: PASS, server reported ready and was stopped after the check.

## Residual Risk

- Historical stored rows without modern public `theme_natal` payload may no longer render through the modern public reading flow; this is the
  allowed story delta.
- History preview rows without explicit modern payload are no longer reused by ID; the frontend asks the modern product action for
  a preview instead of inferring from legacy `level`.
