# CS-305 Failure Ledger

| test_file | test_name | initial_failure_symptom | classification | changed_owner | validation_command | final_status |
|---|---|---|---|---|---|---|
| `frontend/src/tests/ShortcutCard.test.tsx` | English dashboard shortcuts | English labels expected while French labels rendered after suite state leakage. | corrected-test-fixture | `frontend/src/tests/ShortcutCard.test.tsx`, `frontend/src/tests/setup.ts` | `node .\scripts\run-vite-logged.mjs vitest vitest run` | pass |
| `frontend/src/tests/DashboardPage.test.tsx` | English dashboard labels | English labels expected while French labels rendered; one dashboard summary wait was flaky in full suite. | corrected-test-fixture | `frontend/src/tests/DashboardPage.test.tsx`, `frontend/src/tests/setup.ts` | `node .\scripts\run-vite-logged.mjs vitest vitest run` | pass |
| `frontend/src/tests/DailyHoroscopePage.test.tsx` | English labels and section titles | English strings expected while French labels/titles rendered because fixtures only set `localStorage.lang`. | corrected-test-fixture | `frontend/src/tests/DailyHoroscopePage.test.tsx`, `frontend/src/tests/setup.ts` | `node .\scripts\run-vite-logged.mjs vitest vitest run` | pass |
| `frontend/src/tests/ConsultationsPage.test.tsx` | Consultation catalogue and wizard localization group | English consultation strings expected while French strings rendered after language state leakage. | corrected-test-fixture | `frontend/src/tests/ConsultationsPage.test.tsx`, `frontend/src/tests/setup.ts` | `node .\scripts\run-vite-logged.mjs vitest vitest run` | pass |
| `frontend/src/tests/ConsultationsPage.test.tsx` | Consultation wizard back-to-overview label | Raw `back_to_overview` key rendered instead of localized text. | corrected-mock-or-translation | `frontend/src/i18n/consultations.ts` | `node .\scripts\run-vite-logged.mjs vitest vitest run ConsultationsPage` and full suite | pass |

## Summary

- Initial full suite: 4 failed files, 18 failed tests, 1253 passed, 8 skipped.
- Final full suite: 116 passed files, 1271 passed tests, 8 skipped.
- No tests were skipped, deleted, renamed, or narrowed to obtain the green full-suite result.
