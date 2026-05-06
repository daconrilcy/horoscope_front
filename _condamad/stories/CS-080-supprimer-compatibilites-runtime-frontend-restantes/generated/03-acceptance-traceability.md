# Acceptance Traceability - CS-080

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Baseline exact des cinq surfaces `E-009`. | `frontend-runtime-compatibility-before.md` liste les cinq surfaces. | Baseline `rg` documente. | PASS |
| AC2 | `ChatPage.tsx` sans commentaire compat. | `astrologerId` branch removed; canonical `personaId` remains. | `rg -n "Deprecated:|backwards compatibility" src/pages/ChatPage.tsx` zero hit. | PASS |
| AC3 | `dailySummaryHelper.ts` sans fallback legacy. | Helper and `DayPredictionCard` return only `daily_synthesis`, `day_climate.summary`, or empty string; `DailyPredictionSummary` no longer exposes the old field. | `dailySummaryHelper.test.ts`; `rg -n "overall_summary" src` zero hit. | PASS |
| AC4 | `predictions.ts` sans mapping legacy. | Old category/note/driver mappings removed. | `rg -n "Legacy codes|compatibility|legacy" src/i18n/predictions.ts` zero hit. | PASS |
| AC5 | `DailyInsightsSection.tsx` sans export compat. | Named export retained; compatibility wording removed; no active default export facade existed in the inspected diff. | `rg -n "backward compatibility|export default" src/components/DailyInsightsSection.tsx` zero hit. | PASS |
| AC6 | `NatalInterpretation.tsx` sans `aspectLegacy`. | Old aspect parser/category branch removed. | `rg -n "aspectLegacy|legacy|compatibility" src/components/NatalInterpretation.tsx` zero hit. | PASS |
| AC7 | Reintroduction legacy runtime bloquee. | Design-system guard E-009 / CS-080 added for vocabulary and removed contract shapes, including old driver event types. | `npm run test -- ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage design-system` PASS. | PASS |
| AC8 | Aucun resultat final limite. | `frontend-runtime-compatibility-after.md` has delete decisions only. | `rg -n "PASS with limitation|TODO|temporary" frontend-runtime-compatibility-after.md` zero hit. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
