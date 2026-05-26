# Code Review — CS-323-retirer-provider-matomo-dormant-analytics

## Verdict

CLEAN

## Review scope

- Story: `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/00-story.md`
- Brief: `_story_briefs/cs-323-retirer-provider-matomo-dormant-analytics.md`
- Tracker row: `_condamad/stories/story-status.md` maps CS-323 to the story path and source brief.
- Implementation surfaces reviewed:
  - `frontend/src/config/analytics.ts`
  - `frontend/src/hooks/useAnalytics.ts`
  - `frontend/src/tests/useAnalytics.test.tsx`
  - `.env.example`
  - CS-323 evidence artifacts

## Findings

- No actionable implementation issue found.
- No acceptance-criteria drift found.
- No Matomo, `_paq`, compatibility alias, shim, re-export, or fallback provider path found in active frontend or backend surfaces.
- No CONDAMAD evidence issue found after fresh validation.

## AC alignment

| AC | Review result |
|---|---|
| AC1 | PASS: `AnalyticsProvider` exposes only `plausible` and `noop`. |
| AC2 | PASS: `_paq` is absent from `frontend/src/hooks/useAnalytics.ts`. |
| AC3 | PASS: `noop` remains the local default and unprepared providers normalize to `noop`. |
| AC4 | PASS: Plausible emission keeps sanitized props. |
| AC5 | PASS: no direct provider call was found outside `useAnalytics`. |
| AC6 | PASS: active frontend docs/config do not present Matomo as an active option. |
| AC7 | PASS: analytics and natal runtime redaction tests pass. |
| AC8 | PASS: backend scan found no Matomo or `_paq` path. |
| AC9 | PASS: before/after scan, removal audit and validation evidence exist. |

## Fresh validations

- `pnpm lint` from `frontend`: PASS.
- `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics` from `frontend`: PASS, 4 tests.
- `node .\scripts\run-vite-logged.mjs vitest vitest run useAnalytics natalInterpretation natalChartApi` from `frontend`: PASS, 56 tests.
- `node .\scripts\run-vite-logged.mjs vitest vitest run` from `frontend`: PASS, 116 files, 1280 passed, 8 existing skips.
- `pnpm build` from `frontend`: PASS.
- `rg -n "matomo|_paq" frontend/src .env.example docs`: PASS, no active match.
- `rg -n "matomo|_paq" backend`: PASS, no backend match.
- `rg -n "plausible\(" frontend/src/features frontend/src/components frontend/src/pages frontend/src/api`: PASS, no direct provider call.
- `condamad_validate.py _condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics`: PASS after venv activation.
- `condamad_story_validate.py _condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/00-story.md`: PASS after venv activation.
- `condamad_story_lint.py --strict _condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/00-story.md`: PASS after venv activation.

## Evidence reviewed

- `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/provider-scan-before.txt`
- `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/provider-scan-after.txt`
- `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/removal-audit.md`
- `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/evidence/validation-frontend.txt`
- `_condamad/stories/CS-323-retirer-provider-matomo-dormant-analytics/generated/10-final-evidence.md`

## Feedback loop routing

- no-propagation: no reusable process, guardrail or skill defect found; the review produced only story-local closure evidence.

## Residual risk

- Aucun risque restant identifie.
