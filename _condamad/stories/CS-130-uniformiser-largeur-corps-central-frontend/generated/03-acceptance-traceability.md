# CS-130 - Acceptance traceability

| AC | Status | Code evidence | Validation evidence |
|---|---|---|---|
| AC1 | PASS | `--layout-page-max-width` devient le token canonique non-admin; `.app-bg-container` et `.page-layout` le consomment. | `npm run test -- design-system page-architecture layout` PASS; `layout-width-after.md` |
| AC2 | PASS | `PageLayout.css`, `backgrounds.css`, `AppBgStyles.test.ts`, `design-system-guards.test.ts`. | `npm run test -- AppShell visual-smoke` PASS |
| AC3 | PASS | Suppression des `--layout-max-width`, `max-width: none !important`, bypass chat, caps locaux non-admin, cap actif `.page-layout.people-page` et cap wrapper billing-return. | scan cible PASS avec hits restants classes landing/media queries et cartes internes; `npx playwright test e2e/layout-width-cs130.spec.ts` PASS |
| AC4 | PASS | `AdminLayout.css`, `.app-bg-container--admin`, `--layout-admin-max-width` inchanges. | scan admin PASS |
| AC5 | PASS | Nouveau guard CS-130 dans `design-system-guards.test.ts`, etendu aux modules CSS actifs de `App.css`. | `npm run test -- design-system page-architecture layout` PASS |
| AC6 | PASS | Aucun style inline ajoute; suppression overflow masque profile/chat page-level. | scan `style=` PASS zero-hit sur surfaces ciblees; tests inline-style via design-system PASS |
| AC7 | PASS | TypeScript/lint inchanges hors tests CSS. | `npm run lint` PASS |
| AC8 | PASS | AppShell, visual-smoke et E2E CS-130 couvrent shell/profil/layout. | `npm run test -- AppShell visual-smoke` PASS; `npx playwright test e2e/layout-width-cs130.spec.ts` PASS |
