# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Free short renders its primary public reading. | `NatalInterpretationContent.tsx` renders free public title and summary for short and free complete branches. | `pnpm --dir frontend test -- natalInterpretation natalPublicDomGuard NatalChartPage natalNarrativeReading`; full test rerun classified in validation evidence. | PASS |
| AC2 | Free short renders its supporting public blocks. | Free public sections, highlights, advice and payload disclaimers render with `ni-public-*` classes in `NatalInterpretationContent.tsx` and CSS. | Same targeted Vitest command; `natalInterpretation.test.tsx` asserts short payload disclaimers and public sections. | PASS |
| AC3 | Free short never renders the regeneration message. | Branch selection excludes the missing-narrative note for `natal_long_free`. | `natalInterpretation.test.tsx` and `natalPublicDomGuard.test.tsx` assert no `Lecture complète à régénérer`. | PASS |
| AC4 | Frontend types expose Basic V2 on interpretation data. | `BasicNatalInterpretationV2` is added to `frontend/src/api/natal-chart/index.ts`; `basic_natal_interpretation_v2` is carried in API result and view data. | `pnpm --dir frontend build`; `pnpm --dir frontend lint`. | PASS |
| AC5 | Basic V2 renders its public reading structure. | `BasicV2Reading` renders Basic title, introduction, themes, conclusion, limitations and disclaimers. | `natalInterpretation.test.tsx` covers Basic V2 public rendering. | PASS |
| AC6 | Basic V2 evidence renders only public labels. | `PublicEvidenceList` merges `interpretation.public_evidence` and root evidence, then renders only `label` and `meaning`. | `natalPublicDomGuard.test.tsx`; scan for forbidden public technical markers. | PASS |
| AC7 | Complete legacy keeps the regeneration message. | Complete readings without narrative v1 or Basic V2 still use `ni-content-card--missing-narrative`. | Existing and updated `natalPublicDomGuard.test.tsx` assertions. | PASS |
| AC8 | Narrative v1 keeps accessible accordions. | `NatalInterpretation.tsx` injects the existing `NatalNarrativeReading` and `NatalReadingSources`; no duplicate narrative renderer added. | `pnpm --dir frontend test -- natalNarrativeReading NatalChartPage`; scan for `natal-narrative-reading__toggle`. | PASS |
| AC9 | Public DOM excludes technical markers. | Legacy evidence/legacy body components deleted; public render surfaces avoid forbidden fields/classes. | `natalPublicDomGuard`; targeted `rg` scans for markers, legacy symbols and `.ni-evidence-tags`/`.ni-projections`. | PASS |
| AC10 | Touched TSX surfaces do not add inline styles. | Styling added only in `NatalInterpretation.css`; no inline style props added. | `rg -n "style=\\{"` on touched natal TSX surfaces returns no matches. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
