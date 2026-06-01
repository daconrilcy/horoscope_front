# CS-433 - Frontend Remove LLM Technical Generation Controls

<!-- Commentaire global: ce brief cadre la suppression frontend des controles techniques LLM au profit d'actions produit. -->

## Resume

Adapter le frontend pour qu'il n'envoie plus de niveau/use case/variant technique. Le composant
natal demande des actions produit backend et ne declenche plus de generation courte automatique
apres upgrade Basic.

## Perimetre Inclus

1. Supprimer `shouldRefreshShortAfterBasicUpgrade`.
2. Supprimer l'envoi frontend de:
   - `use_case_level`;
   - `variant_code`;
   - `forceRefresh` pour generation LLM;
   - `plan` technique;
   - `use_case` technique.
3. Ajouter un client API product-action.
4. Adapter CTA:
   - preview;
   - generate_full;
   - regenerate;
   - download.
5. Adapter etats UI:
   - existing accepted;
   - generating;
   - failed_retriable;
   - locked/paywall;
   - rejected controlled state.
6. Supprimer ou deplacer en compat readonly explicitement non generatrice les anciennes fonctions du
   client API qui exposent la generation natale legacy.
7. Supprimer des types TypeScript publics de generation natale:
   - `useCaseLevel`;
   - `variantCode`;
   - `forceRefresh`;
   - `useCase`;
   - `plan`.
8. Tests frontend de non-regression.

## Hors Perimetre

- Redesign visuel large.
- Changement CSS non necessaire.
- Provider/backend runtime.
- Suppression backend legacy.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-432-public-api-cutover-product-actions.md`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-071` - `NatalInterpretation` ne doit pas redevenir monolithique non classe.
  - `RG-073` - orchestration interpretation reste sous feature natal-chart.
  - `RG-153` - composition publique `/natal` en couches.
  - `RG-154` - denylist DOM lecture publique.
  - `RG-158` - accordeons/actions modernes.
  - `RG-170` - sources/mentions Basic dedupliquees.
- Required regression evidence:
  - Tests Vitest `natalInterpretation`.
  - Scans zero-hit des controles techniques.
- Allowed differences:
  - Le client API natal utilise les actions produit.
  - La generation short automatique post-upgrade disparait.

## Criteres D'acceptation

1. Aucun composant frontend n'envoie `use_case_level`.
2. Aucun composant frontend n'envoie `variant_code`.
3. Aucun effet React ne genere une lecture apres upgrade sans action utilisateur explicite.
4. Le CTA complet envoie `action=generate_full`.
5. Le frontend gere les slots `accepted/generating/failed_retriable/rejected`.
6. Le rendu Basic consomme uniquement le schema public.
7. Les mentions legales restent dedupliquees.
8. Les types API publics de generation natale n'exposent plus les champs techniques legacy.
9. Les anciennes fonctions client generateurs sont supprimees ou marquees compat readonly non
   generatrice.

## Commandes De Validation Minimales

Frontend:

```powershell
pnpm --dir frontend test -- natalInterpretation NatalChartPage
pnpm --dir frontend lint
```

Scans:

```powershell
rg -n "shouldRefreshShortAfterBasicUpgrade|use_case_level|variant_code|forceRefresh" frontend/src
rg -n "useCaseLevel|variantCode|forceRefresh|useCase|plan" frontend/src/api frontend/src/features/natal-chart frontend/src/tests
rg -n "action:\\s*['\"]generate_full|ThemeNatalReadingAction|theme-natal/readings" frontend/src
rg -n "style=" frontend/src/features/natal-chart frontend/src/components/natal-interpretation
```

## Dependances

- CS-432.

## Risques

Le risque est de garder un effet React qui reproduit la generation parasite. Cette story transforme
le frontend en demandeur d'intention metier uniquement.
