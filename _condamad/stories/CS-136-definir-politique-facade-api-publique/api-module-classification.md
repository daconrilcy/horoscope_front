<!-- Classification des modules API ambigus pour CS-136. -->

# CS-136 - Classification modules API

| Module | Classification | Owner | Preuve | Action autorisee |
|---|---|---|---|---|
| `b2bAstrology.ts` | public-export-retained | B2B astrology API | export `@api`, test `b2bAstrologyApi.test.ts` | conserver l'export; migrations internes autorisees |
| `b2bBilling.ts` | public-export-retained | B2B billing API | export `@api`, test `b2bBillingApi.test.ts` | conserver l'export; migrations internes autorisees |
| `b2bEditorial.ts` | runtime-owned | B2B editorial API | test `b2bEditorialApi.test.ts` | conserver le module et son export |
| `b2bUsage.ts` | public-export-retained | B2B usage API | export `@api`, test `b2bUsageApi.test.ts` | conserver l'export; migrations internes autorisees |
| `guidance.ts` | runtime-owned | Guidance API | test `guidanceApi.test.ts` | conserver le module et son export |
| `opsMonitoring.ts` | external-unknown | Ops monitoring API | export `@api`; pas de consommateur runtime observe dans `src` | ne pas supprimer sans decision utilisateur |

## Decision de conservation

Les modules listes restent presents dans `frontend/src/api/index.ts` pour ne pas
casser la facade publique globale. Toute suppression ou depublication future
devra etre portee par une story dediee avec preuve de non-consommation externe.
