# UX Audit Before — CS-307

Date: 2026-05-26
Route: `/natal`

| Finding | Evidence | Decision |
|---|---|---|
| Projection hierarchy after CS-303/CS-306 wiring needed real browser proof. | `browser-qa-ledger.json`, desktop/tablet/mobile screenshots | acceptable |
| Projection state messages needed verification beyond unit tests. | mobile degraded, entitlement, error, and empty screenshots | acceptable |
| Legal disclaimer visibility needed ownership and placement proof. | `NatalInterpretationContent.tsx`, `frontend/src/i18n/natalChart.ts`, screenshots | acceptable |
| Inline styles and direct projection HTTP calls must stay absent. | negative `rg` scans recorded in `validation.txt` | acceptable |

No UI defect requiring a React or CSS correction was demonstrated by the browser audit.

