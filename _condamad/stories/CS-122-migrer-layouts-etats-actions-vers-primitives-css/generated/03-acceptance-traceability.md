# Acceptance Traceability — CS-122

| AC | Requirement | Expected code impact | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Inventaire before structurel. | `app-structure-before.md` | Artefact before | PASS |
| AC2 | Layouts migrent vers CS-121. | `App.css` + consumers TSX | `npm run test -- ... App router` | PASS |
| AC3 | Aucun ancien nom migre ne reste comme alias. | Suppression selectors/consumers obsoletes | No Legacy scan App.css zero hit | PASS |
| AC4 | Tests runtime cibles passent. | Pages/routes touchees | `npm run test -- App router ...` PASS | PASS |
| AC5 | Guards design-system verts. | `design-system-guards.test.ts` | `npm run test -- design-system visual-smoke` PASS | PASS |
