<!-- Carte des fichiers cibles CS-119 pour limiter le delta. -->

# Target Files - CS-119

## Must Read

- `_condamad/stories/CS-119-supprimer-composants-test-only-sans-ui-runtime/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/audits/frontend-components/2026-05-09-0031/00-audit-report.md`
- `_condamad/audits/frontend-components/2026-05-09-0031/01-evidence-log.md`
- `_condamad/audits/frontend-components/2026-05-09-0031/05-executive-summary.md`
- `_condamad/stories/CS-116-classer-fermer-composants-non-consommes/component-usage-classification.md`
- `frontend/package.json`
- `frontend/src/tests/component-usage-allowlist.ts`
- `frontend/src/tests/component-usage-guards.test.ts`
- `frontend/src/tests/component-architecture-allowlist.ts`
- `frontend/src/tests/component-architecture-guards.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/hooks/useDailyInsights.ts`

## Must Search

- `rg --files frontend/src/components -g "*.ts" -g "*.tsx"`
- Target symbol scans for B2B, ops, privacy, daily and prediction components.
- Target import path scans for `components/<deleted>` and
  `components/prediction/<deleted>`.
- Target CSS scans for the four orphan CSS files.
- Barrel scans under `frontend/src/components/**/index.ts?(x)`.

## Likely Modified

- `frontend/src/hooks/useDailyInsights.ts`
- `frontend/src/tests/component-usage-allowlist.ts`
- `frontend/src/tests/component-usage-guards.test.ts`
- `frontend/src/tests/component-architecture-allowlist.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`

## Likely Deleted

- Seeded `test-only` component files and dedicated CSS listed in `00-story.md`.
- Focused tests listed in `00-story.md`.

## Forbidden Unless Justified

- `backend/**`
- Runtime-used component files listed as non-goals.
- `frontend/src/features/natal-chart/**`
- Frontend route tables and API contracts.
