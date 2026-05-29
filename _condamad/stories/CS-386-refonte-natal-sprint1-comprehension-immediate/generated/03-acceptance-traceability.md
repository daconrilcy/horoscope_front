# CS-386 Acceptance Traceability

| AC | Evidence |
| --- | --- |
| AC1 comprehension immediate | `NatalProfileHero` renders Soleil / Lune / Ascendant; covered by `NatalChartPage.test.tsx`. |
| AC2 ADN astrologique public | `NatalAstrologicalDna.test.tsx` validates dominant payload usage. |
| AC3 domaines de vie | `NatalLifeDomains.test.tsx` validates six public domains from placements/houses. |
| AC4 no technical noise by default | `NatalTechnicalDetails` is rendered inside `NatalAstrologerMode`; page tests open the toggle before raw assertions. |
| AC5 no local astrology calculator | Forbidden constants scan returned no public-section match. |
| AC6 no inline style | `Select-String` scan for `style=` returned no match. |
| AC7 regression guardrails | `evidence/validation.txt` classifies RG-047, RG-052, RG-071, RG-073, RG-129, RG-150. |
| AC8 tests | Targeted Vitest command passed, 123 tests. |
| AC9 build/lint | `npm run lint` and `npm run build` passed. |
