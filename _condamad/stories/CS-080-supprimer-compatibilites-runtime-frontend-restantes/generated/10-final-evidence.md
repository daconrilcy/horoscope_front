# Final Evidence - CS-080

## Status

Implementation status: ready-to-review before review loop.

## Files changed

- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/utils/dailySummaryHelper.ts`
- `frontend/src/i18n/predictions.ts`
- `frontend/src/components/DailyInsightsSection.tsx`
- `frontend/src/components/NatalInterpretation.tsx`
- `frontend/src/components/prediction/DayPredictionCard.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/dailySummaryHelper.test.ts`
- `frontend/src/tests/fixtures/dailyPredictionV4Flat.json`
- `frontend/src/tests/fixtures/dailyPredictionV4LowEvents.json`
- `frontend/src/tests/fixtures/dailyPredictionV4Polarized.json`
- `frontend/src/tests/fixtures/dailyPredictionV4TurningPoint.json`
- `frontend/src/tests/predictionI18n.test.ts`
- `frontend/src/tests/DashboardPage.test.tsx`
- `frontend/src/tests/DailyHoroscopePage.test.tsx`
- `frontend/src/tests/App.test.tsx`
- `frontend/src/tests/AppShell.test.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`
- `frontend/src/tests/router.test.tsx`
- `frontend/src/tests/setup.ts`
- `frontend/src/tests/test-utils.tsx`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/types/dailyPrediction.ts`
- `frontend/src/utils/dailyAdviceCardMapper.test.ts`
- `frontend/src/utils/predictionI18n.ts`
- `_condamad/stories/CS-080-supprimer-compatibilites-runtime-frontend-restantes/frontend-runtime-compatibility-before.md`
- `_condamad/stories/CS-080-supprimer-compatibilites-runtime-frontend-restantes/frontend-runtime-compatibility-after.md`

## Frontend subagent evidence

`condamad-frontend-dev` subagent used for the frontend slice.

Reported results:

- `npm run test -- ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage design-system` - PASS, 62 tests.
- `npm run test -- ChatPage dailySummaryHelper` - PASS, 25 tests.
- `npm run lint` - PASS.
- Local Vite startup on `127.0.0.1:5180` - PASS, HTTP 200, server stopped.
- Global E-009 vocabulary scan under `frontend/src` - zero hit.
- Targeted scans for `astrologerId`, `overall_summary`, `aspectLegacy`, and old driver event types - zero hit after review fixes.

## AC validation

| AC | Status | Evidence |
|---|---|---|
| AC1 | PASS | `frontend-runtime-compatibility-before.md`. |
| AC2 | PASS | `ChatPage.tsx` branch removed; targeted scans zero hit. |
| AC3 | PASS | `dailySummaryHelper.ts` fallback removed; helper tests added; `DayPredictionCard` consumes canonical helper; old field removed from type and fixtures. |
| AC4 | PASS | `predictions.ts` old mappings removed; scans zero hit. |
| AC5 | PASS | `DailyInsightsSection.tsx` no longer has compatibility wording or a default export facade. |
| AC6 | PASS | `NatalInterpretation.tsx` no longer parses `aspectLegacy`. |
| AC7 | PASS | Design-system guard CS-080 blocks vocabulary and concrete removed runtime shapes; targeted suite passes. |
| AC8 | PASS | After audit has no limitation marker. |

## Review findings fixed

- Extended the CS-080 guard beyond vocabulary scans to block concrete removed shapes: `astrologerId`, `overall_summary`, `aspectLegacy`, old uppercase natal aspect IDs, old prediction dictionary keys, old driver event mappings, and `export default` in `DailyInsightsSection`.
- Corrected `DailyInsightsSection` evidence: the inspected diff only proved compatibility wording removal; no active default export facade existed.
- Removed runtime support for old driver event types `exact`, `enter_orb`, and `exit_orb` from `predictionI18n.ts`.
- Removed `overall_summary` from frontend types, tests, JSON fixtures, and `DayPredictionCard` consumption.
- CS-079 guard additions live in the same `design-system-guards.test.ts` diff but are attributed to CS-079 evidence, not CS-080 acceptance evidence.

## No Legacy / DRY evidence

- No mapper, parser branch, default export facade, fallback, alias, or active exception registry was introduced.
- Removed compatibility vocabulary from source/tests so the E-009 guard can scan all `frontend/src`.
- Canonical replacements reuse existing contracts: `personaId`, `daily_synthesis`, `day_climate.summary`, canonical prediction dictionaries, named `DailyInsightsSection`, and `ASPECT_*` natal IDs.
- `DayPredictionCard` now consumes `getDailyEditorialSummary`, and `DailyPredictionSummary` no longer exposes `overall_summary`.
- `predictionI18n.ts` no longer humanizes old driver event types `exact`, `enter_orb`, or `exit_orb`.

## Commands run

- `npm run test -- ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage design-system` - PASS, 62 tests.
- `npm run test -- ChatPage dailySummaryHelper predictionI18n DayPredictionCard AppShell App router dailyAdviceCardMapper` - PASS, 108 tests.
- `npm run lint` - PASS.
- `rg -n "Deprecated:|backwards compatibility|backward compatibility|legacy fallback|Legacy codes|aspectLegacy|compatibility" src` - PASS, zero hit.
- `rg -n "astrologerId" src/pages/ChatPage.tsx` - PASS, zero hit.
- `rg -n "overall_summary" src` - PASS, zero hit.
- `rg -n "aspectLegacy" src/components/NatalInterpretation.tsx` - PASS, zero hit.
- `rg -n "eventType\s*===\s*['\"]exact['\"]|^\s*(exact|enter_orb|exit_orb|generic_event):" src/utils/predictionI18n.ts src/i18n/predictions.ts src/tests/predictionI18n.test.ts src/tests/DailyHoroscopePage.test.tsx` - PASS, zero hit.
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-080-supprimer-compatibilites-runtime-frontend-restantes/00-story.md` - PASS.
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-080-supprimer-compatibilites-runtime-frontend-restantes/00-story.md` - PASS.
- Local Vite startup - PASS via subagent.

## Commands not run

- `npm run test:e2e` - NOT_RUN; not required by story validation and covered by Vitest, lint, scans, and startup.

## Remaining risks

Old external clients still sending `astrologerId`, `overall_summary`, old
prediction codes, default imports, or old natal aspect IDs will not be supported
silently. This is the expected behavior change required by the story.
