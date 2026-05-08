# CS-104 - Acceptance traceability

| AC | Status | Code evidence | Validation evidence |
|---|---|---|---|
| AC1 | PASS | Route index sous `LandingLayout` dans `routes.tsx` | `npm run test -- App visual-smoke`; guard landing PASS |
| AC2 | PASS | `LandingRedirect.tsx` sans import `LandingLayout.css` | scan cible zero hit |
| AC3 | PASS | `LandingRedirect` conserve token expire / redirect actif | `npm run test -- App router` PASS |
| AC4 | PASS | Seul `LandingLayout.tsx` rend `.landing-layout`; aucun bypass guard | guard landing PASS |
| AC5 | PASS | TypeScript/lint green | `npm run lint` PASS |
