# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Visible projection wording is inventoried. | `evidence/wording-inventory-before.md` and `evidence/wording-inventory-after.md` list the visible app-owned projection panel, card, state, and disclaimer-adjacent copy. | PASS `python -B -c ...` evidence artifact check. | PASS |
| AC2 | Projection titles distinguish both reading levels. | `frontend/src/i18n/natalChart.ts` now owns `Résumé découverte` and `Interprétation client` plus distinct descriptions; `NatalInterpretationContent.tsx` renders them per projection type. | PASS targeted Vitest `natalInterpretation astrology-i18n natalChartApi`. | PASS |
| AC3 | App-owned disclaimers stay visible. | `NatalInterpretationContent.tsx` still renders `legalNoticeLines` from `natalChartTranslations`; payload disclaimer test remains negative. | PASS targeted Vitest disclaimer assertions; PASS `rg` payload disclaimer ownership scan with no matches. | PASS |
| AC4 | Projection state messages use plain wording. | Loading, entitlement, error, empty, degraded, and card-empty messages moved to `natalChart.ts` as plain client-facing copy. | PASS targeted Vitest state assertions. | PASS |
| AC5 | Regulated-advice wording is absent. | New projection copy avoids medical, legal, financial, diagnostic, treatment, guarantee, and deterministic wording; refused wording records rejected deterministic phrasing. | PASS_WITH_LIMITATIONS global `rg` returns existing disclaimers/unrelated copy only; no new projection wording hit. | PASS_WITH_LIMITATIONS |
| AC6 | Backend projection runtime remains unchanged. | No backend file modified; projection API transport remains centralized. | PASS `git diff --name-only -- backend frontend ...` shows frontend/capsule only; PASS direct transport scan. | PASS |
| AC7 | Frontend validation commands pass. | Tests updated in `frontend/src/tests/natalInterpretation.test.tsx`; style added in existing CSS owner. | PASS `pnpm lint`; PASS targeted Vitest; PASS full Vitest. | PASS |
| AC8 | Final wording decisions are persisted. | `evidence/refused-wording.md`, `evidence/validation.txt`, and this traceability file document decisions and validation. | PASS capsule validation after evidence update. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
