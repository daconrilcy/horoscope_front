# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Missing `hayz` no longer crashes the panel. | `NatalExpertPanel.tsx` narrows each runtime `traditional_conditions` entry before reading `hayz`. | `evidence/partial-before.txt` fails before fix; `evidence/partial-after.txt` and `pnpm --dir frontend test -- NatalExpertPanel` pass. | PASS |
| AC2 | A partial traditional entry shows localized degraded copy. | `NatalExpertPanel.tsx` renders `Contrat expert partiel` and `NatalExpertPanel.css` styles the drift state. | Focused Vitest assertion on partial `alpha` entry passes. | PASS |
| AC3 | Valid neighboring traditional entries remain visible. | Rendering branch is per planet entry; complete `beta` still renders full facts. | Focused Vitest asserts `beta` keeps `hayz.is_hayz` and `rejoicing.rejoicing_house`. | PASS |
| AC4 | Complete expert rendering still proves hayz fields. | Complete rendering branch preserves existing `FactRow` labels and values. | Existing complete-payload Vitest test passes. | PASS |
| AC5 | Nominal API types keep required traditional blocks. | `frontend/src/api/natal-chart/index.ts` unchanged; `hayz` and `rejoicing` remain required. | AST guard `rg -n "hayz: TraditionalHayzCondition|rejoicing: TraditionalRejoicingCondition" frontend/src/api/natal-chart/index.ts`; `pnpm --dir frontend build` pass. | PASS |
| AC6 | React adds no astrology derivation. | New guard only checks object presence and never computes hayz, sect, joy, scores, or doctrine. | Diff scan for added `calculate|score|infer|derive|doctrine|fallback` returns no matches. | PASS |
| AC7 | No inline style is introduced. | New visual state is CSS-only in `NatalExpertPanel.css`. | Touched-file scan `rg -n "style=" NatalExpertPanel.tsx NatalExpertPanel.test.tsx` returns no matches. | PASS |
| AC8 | Story evidence artifacts are persisted. | `evidence/partial-before.txt`, `partial-after.txt`, `validation.txt`, and generated capsule files are present. | Capsule validation `python -B ... condamad_validate.py ...` passes with all required generated files present. | PASS |
| AC9 | Trace decision non-sensitive. | No trace/logging added for this local drift state. | Touched-file scan `rg -n "trackEvent|console\\." NatalExpertPanel.tsx NatalExpertPanel.test.tsx` returns no matches. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
