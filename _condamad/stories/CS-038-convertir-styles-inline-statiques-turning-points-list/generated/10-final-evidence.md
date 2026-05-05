# CS-038 - Final Evidence

## Summary

Story status: done.

`TurningPointsList.tsx` no longer contains inline styles. Static declarations moved to adjacent CSS in `TurningPointsList.css`; the previous cursor branch is represented as a conditional class.

## Acceptance Evidence

| AC | Evidence | Result |
|---|---|---|
| AC1 | `inline-styles-before.md` classifies 38 initial `style={` attributes. | PASS |
| AC2 | `rg -n "style=\{" frontend/src/components/prediction/TurningPointsList.tsx` returns no hit. | PASS |
| AC3 | CSS uses existing variables and design tokens. | PASS |
| AC4 | `INLINE_STYLE_EXCEPTIONS` has no `TurningPointsList.tsx` entry. | PASS |
| AC5 | `npm run test -- inline-style design-system TurningPointsEnriched css-fallback Button Card Field Modal Select UserAvatar Skeleton` passed, including `TurningPointsEnriched`. | PASS |
| AC6 | `npm run lint` passed. | PASS |

## Validation

- `npm run test -- inline-style design-system TurningPointsEnriched css-fallback Button Card Field Modal Select UserAvatar Skeleton` - PASS, 18 files / 219 tests.
- `npm run test -- design-system theme-tokens inline-style css-fallback` - PASS, 4 files / 106 tests.
- `npm run lint` - PASS.
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-038-convertir-styles-inline-statiques-turning-points-list/00-story.md` - PASS.
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-038-convertir-styles-inline-statiques-turning-points-list/00-story.md` - PASS.

## Guardrails

- RG-047: PASS.
- RG-050: PASS.

## Remaining Risk

`npm run test` complet reste en echec sur `src/tests/HelpPage.test.tsx` uniquement en execution globale concurrente. Le test cible `npm run test -- HelpPage` passe, et les guards de cette story passent.
