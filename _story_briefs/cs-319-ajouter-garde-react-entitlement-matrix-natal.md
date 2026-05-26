# CS-319 — Ajouter Une Garde Anti-Matrice Entitlement React Pour /natal

## Résumé

Ajouter une garde ciblée pour empêcher l'apparition d'une matrice locale free/basic/premium dans le frontend `/natal`. Cette story formalise le follow-up optionnel du rapport CS-312-CS-316.

## Contexte

Le rapport `_condamad/reports/CS-312-CS-316-delivery-report.md` recommande de promouvoir la garde anti-drift React si le sign-off produit CS-315 est accepté. CS-315 documente que :

- le backend reste source d'autorisation ;
- React rend les success/403 backend ;
- aucune matrice locale d'entitlement ne doit apparaître dans `frontend/src`.

## Objectif

Créer une garde automatisée, ciblée et maintenable qui échoue si une politique locale free/basic/premium est ajoutée dans les surfaces React de projection `/natal`.

## Préalable obligatoire

Relire :

- `_condamad/reports/CS-312-CS-316-delivery-report.md`
- `docs/architecture/natal-projection-plan-matrix-product-decision.md`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/tests/component-architecture-guards.test.ts`
- `frontend/src/tests/natalInterpretation.test.tsx`

## Périmètre inclus

1. Identifier la garde frontend existante la plus proche.
2. Ajouter un test ou scan ciblé interdisant une matrice locale free/basic/premium dans les owners `/natal`.
3. Autoriser les fixtures de tests backend-shaped existantes seulement si elles ne deviennent pas source de politique.
4. Documenter les patterns interdits et les exceptions acceptées.
5. Vérifier que les tests CS-309/CS-315 continuent de prouver le rendu backend-sourced.

## Hors périmètre

- Modifier l'entitlement backend.
- Modifier la matrice produit.
- Changer l'UI ou les textes d'upgrade.
- Ajouter un script global fragile si un test existant suffit.

## Critères d'acceptation

1. Une garde automatisée existe dans les tests frontend ou un script déjà utilisé.
2. La garde cible les surfaces `/natal` et les composants de projection pertinents.
3. Les fixtures de test restent autorisées quand elles simulent des réponses backend.
4. Une tentative de matrice locale dans React serait détectée.
5. `pnpm lint` et les tests ciblés passent.
6. Aucun code backend ni document produit n'est modifié sauf référence de preuve.

## Validation attendue

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards natalInterpretation NatalChartPage natalChartApi
```

Scan de contrôle :

```powershell
rg -n "free.*basic.*premium|accepted_matrix|entitlement matrix|plan_code.*===" frontend/src/features/natal-chart frontend/src/components/natal-interpretation frontend/src/pages frontend/src/tests
```

## Risques

Le risque principal est une garde trop large qui bloque des fixtures légitimes. La garde doit distinguer fixture backend-shaped et politique active dans React.
