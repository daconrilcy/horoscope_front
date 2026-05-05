<!-- Traceabilite des criteres d'acceptation CS-047. -->

# CS-047 Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Retirer anciennes assertions typo litterales | `visual-smoke.test.tsx` | scan `18px|12px|font-weight.*500` | Passed |
| AC2 | Verifier le contrat tokenise | `visual-smoke.test.tsx` | `npm run test -- visual-smoke` | Passed |
| AC3 | Conserver les assertions d'opacite | aucun retrait opacity | scan `opacity` + test | Passed |
| AC4 | Vitest complet ne casse plus | tests frontend | `npm run test` | Passed |
| AC5 | Guards design-system passent | aucun code produit | guards cibles | Passed |

