# CS-439 - Supprimer Les Adaptateurs Front Legacy D'Interpretation Natale

<!-- Commentaire global: ce brief cadre le retrait des DTO et heuristiques front issus des anciennes interpretations natales. -->

## Resume

Supprimer du frontend les adaptateurs qui convertissent encore les payloads
historiques `NatalInterpretationResult`/`use_case` en rendu moderne. Le front doit
consommer un contrat public `theme_natal` directement, avec des etats produits
explicites, sans heuristique `natal_long_free`, `natal_interpretation_short`,
`use_case`, `level` ou `variant_code` pour piloter la lecture.

## Perimetre Inclus

1. Remplacer `mapProductActionDataToInterpretation(...)` par un mapping vers un
   type public `ThemeNatalReadingPublicPayload` ou equivalent.
2. Retirer les tests et branches qui detectent:
   - `item.use_case === "natal_long_free"`;
   - `useCase === "natal_long_free"`;
   - `use_case === "natal_interpretation_short"`.
3. Supprimer les dependances UI au contrat historique
   `NatalInterpretationResult` pour la lecture moderne.
4. Conserver `variant_code` uniquement dans les surfaces entitlement non-natales ou
   dans l'affichage de droits, jamais comme commande de generation.
5. Adapter `NatalInterpretationContent` pour rendre directement les schemas publics
   `theme_natal`.
6. Supprimer les boutons/actions qui appellent les routes historiques si CS-438 les
   retire, ou les brancher sur les endpoints modernes.
7. Renforcer le DOM guard pour refuser les symboles legacy dans la lecture publique.
8. Supprimer les types front qui ne servent plus qu'a accepter les anciennes
   enveloppes `NatalInterpretationResult` dans le flux theme natal moderne.

## Hors Perimetre

- Redesign visuel complet de la page `/natal`.
- Changer les couleurs/styles hors besoins fonctionnels.
- Modifier les contrats backend.
- Supprimer `variant_code` de l'entitlement global billing/admin/daily horoscope.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `frontend/src/api/natal-chart/index.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-153` - la composition publique `/natal` reste narrative et non legacy.
  - `RG-154` - denylist DOM lecture publique.
  - `RG-155` - pas de padding semantique ou sources vides.
  - `RG-158` - accordeons modernes conserves.
  - `RG-170` - sources et mentions legales Basic dedupliquees.
  - `RG-173` - pas de raw old use_case dans generation publique.
- Required regression evidence:
  - Tests component/API front.
  - Scan zero-hit des anciens use cases dans les composants publics.
  - Screenshot ou test DOM si la story touche le rendu principal.
- Allowed differences:
  - Suppression de compatibilite UI avec payloads historiques.
  - Retrait d'actions front sans endpoint moderne disponible, si documente.

## Criteres D'acceptation

1. `frontend/src/features/natal-chart/NatalInterpretation.tsx` ne contient plus
   `natal_long_free` ni `natal_interpretation_short`.
2. `NatalInterpretationContent` ne decide plus son rendu a partir d'un ancien
   `use_case`.
3. Le client front des lectures modernes n'expose plus `NatalInterpretationResult`
   comme type cible principal, ni comme enveloppe de compatibilite silencieuse.
4. Les bodies envoyes au backend contiennent uniquement:
   `chart_id`, `action`, `persona_profile_id`, `locale`, `client_request_id`.
5. `variant_code` peut rester dans `NatalChartPage` seulement pour affichage/gate
   entitlement, pas pour construire une requete LLM.
6. Les tests front prouvent que les anciens champs techniques ne sont pas envoyes.
7. Les tests DOM prouvent que les symboles legacy ne sont pas visibles dans la
   lecture publique.
8. Aucun style inline n'est introduit.
9. Les tests ne gardent pas de fixtures positives construites avec
   `natal_long_free` ou `natal_interpretation_short`.

## Commandes De Validation Minimales

Frontend:

```powershell
pnpm --dir frontend test -- natalChartApi.test.tsx natalInterpretation.test.tsx natalPublicDomGuard.test.tsx NatalChartPage.test.tsx
pnpm --dir frontend lint
```

Scans:

```powershell
rg -n "natal_long_free|natal_interpretation_short|use_case_level|forceRefresh|force_refresh|shouldRefreshShortAfterBasicUpgrade" frontend/src
rg -n "variant_code|variantCode" frontend/src/features/natal-chart frontend/src/components/natal-interpretation frontend/src/api/natal-chart frontend/src/pages/NatalChartPage.tsx
rg -n "style=\\{\\{" frontend/src/features/natal-chart frontend/src/components/natal-interpretation frontend/src/pages/NatalChartPage.tsx
```

## Dependances

- CS-438 si les routes historiques sont supprimees.
- Peut commencer avant CS-438 pour retirer les heuristiques use case, tant que les
  tests documentent les endpoints encore appeles.

## Risques

Le front peut encore recevoir d'anciennes lignes en environnement de dev. Comme
l'application n'est pas en production, la strategie privilegiee est de ne pas
conserver une compat UI historique complexe: afficher une regeneration moderne ou
une absence de lecture plutot que remapper les anciens use cases.
