# CS-389 Acceptance Traceability

| AC | Evidence |
| --- | --- |
| AC1 mode ferme par defaut | `NatalAstrologerMode.test.tsx` validates hidden technical content before toggle. |
| AC2 ouverture accessible | `NatalAstrologerMode.test.tsx` validates `aria-expanded` after click. |
| AC3 reuse expert panel | `NatalChartPage.tsx` keeps `NatalExpertPanel` and wraps it in `NatalAstrologerMode`. |
| AC4 details techniques extraits | `NatalTechnicalDetails` owns the previous raw planets/houses/aspects rendering. |
| AC5 free-short gate | `NatalAstrologerMode.test.tsx` validates upgrade CTA for `free_short`. |
| AC6 CS-380 partial payload non-regression | `NatalChartPage.test.tsx` still passes with partial payload scenarios. |
| AC7 no inline style | Inline style scan returned no match. |
| AC8 tests | Targeted Vitest command passed, 123 tests. |
| AC9 build/lint | `npm run lint` and `npm run build` passed. |
