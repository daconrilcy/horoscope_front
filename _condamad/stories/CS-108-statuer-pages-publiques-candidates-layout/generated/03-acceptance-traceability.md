# Acceptance Traceability - CS-108

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le baseline liste les cinq residus. | `page-decisions-before.md` liste les cinq fichiers et l'etat CS-107 initial. | `rg -n "PrivacyPolicyPage|BillingSuccessPage" page-decisions-before.md` PASS. | PASS |
| AC2 | Chaque residu a une decision sourcee. | `page-architecture-allowlist.ts` et `page-decisions-after.md` portent owner, `decisionSource`, `expiresOn` ou `removalStory` pour les cinq residus. | `npm run test -- page-architecture layout` PASS; scan des cinq symboles PASS. | PASS |
| AC3 | Aucune page `needs-user-decision` n'est routee sans decision. | `routes.tsx` reste sans ces symboles; guard conserve le blocage de routage. | `npm run test -- page-architecture layout` PASS; scan `routes.tsx` zero-hit PASS. | PASS |
| AC4 | Toute route ajoutee a un owner explicite. | Aucune route ajoutee; aucune entree privacy/billing routee. | `npm run test -- page-architecture layout` PASS; diff de `routes.tsx` absent. | PASS |
| AC5 | Le registre executable reste aligne avec CS-107. | `page-layout-owner-after.md` aligne les cinq decisions avec l'allowlist. | `rg -n "HomePage" page-layout-owner-after.md` PASS; `npm run test -- page-architecture layout` PASS. | PASS |
| AC6 | Tout retrait execute est decide `delete`. | Aucun retrait physique execute; `HomePage` n'est plus re-exportee par le barrel runtime et les decisions de retrait futur restent en story dediee. | `git diff --stat` montre aucune suppression de page; `npm run test -- page-architecture layout` PASS; scan `src/pages/index.ts` zero-hit pour `HomePage`. | PASS |
| AC7 | Les validations frontend restent vertes. | Changement limite au registre et au guard frontend. | `npm run lint` PASS; `npm run test -- App router BillingSuccessPage` PASS. | PASS |
