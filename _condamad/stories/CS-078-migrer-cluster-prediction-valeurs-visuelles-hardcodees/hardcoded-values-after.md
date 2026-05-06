# After Evidence - CS-078

Date: 2026-05-06

## Decision

Cluster borne DailyHoroscopePage, DailyAdviceCard, DailyPageHeader, DayStateBadge migre vers tokens/roles; vocabulaire fallback retire de prediction CSS; RG-055 ajoute.

## Files

frontend/src/pages/DailyHoroscopePage.css; frontend/src/components/prediction/DailyAdviceCard.css; frontend/src/components/prediction/DailyPageHeader.css; frontend/src/components/prediction/DayStateBadge.css; frontend/src/components/prediction/DayAgenda.css; frontend/src/components/prediction/KeyPointCard.css; frontend/src/components/prediction/TurningPointsList.css; frontend/src/tests/design-system-guards.test.ts; _condamad/stories/regression-guardrails.md

## Scans

prediction CSS fallback/legacy vocabulary: zero-hit; exact migrated literals guarded by design-system test

## Classification

- Decision: implemented without compatibility shim, alias, silent fallback, or duplicate active path.
- Remaining differences: none outside the story-declared allowed differences.
