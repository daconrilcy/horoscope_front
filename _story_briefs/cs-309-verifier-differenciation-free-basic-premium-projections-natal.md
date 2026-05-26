# CS-309 — Vérifier Différenciation free/basic/premium Sur Les Projections /natal

## Résumé

Vérifier que l'expérience `/natal` différencie correctement les plans free, basic et premium pour les projections B2C, avec messages d'accès, états verrouillés et contenus disponibles cohérents.

## Contexte

CS-302 a prouvé côté backend la matrice de plans pour `POST /v1/astrology/projections`. CS-303 a branché le frontend sur ces projections. Il faut maintenant vérifier que l'utilisateur comprend ce qui est disponible selon son plan et que l'UI ne promet pas un contenu non autorisé.

## Objectif

Prouver, par tests et QA, que `/natal` affiche correctement les contenus et restrictions free/basic/premium pour `beginner_summary_v1` et `client_interpretation_projection_v1`.

## Préalable obligatoire

Relire :

- `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/generated/10-final-evidence.md`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`
- `backend/tests/api/test_projection_authorization.py`
- `frontend/src/api/astrologyProjections.ts`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/tests/natalInterpretation.test.tsx`

## Périmètre inclus

1. Définir la matrice attendue free/basic/premium pour les deux projections affichées sur `/natal`.
2. Vérifier les états autorisé, verrouillé, upgrade, erreur 403 et contenu partiel.
3. Vérifier que le frontend ne décide pas localement des droits à la place du backend.
4. Ajouter ou renforcer les tests frontend pour les trois plans.
5. Rejouer les tests backend d'autorisation projection pertinents.
6. Capturer une preuve QA ou un ledger montrant les différences visibles par plan.
7. Documenter toute ambiguïté produit sur la valeur livrée par plan.

## Hors périmètre

- Modifier la politique commerciale des plans sans décision produit.
- Modifier le modèle d'entitlement backend sauf bug prouvé.
- Ajouter un paiement, une page pricing ou un flow Stripe.
- Contourner un 403 côté frontend.
- Introduire une matrice de droits dupliquée en React.

## Critères d'acceptation

1. La matrice free/basic/premium attendue est documentée.
2. Chaque plan a une preuve frontend ciblée.
3. Les refus backend 403 sont affichés comme restriction de plan compréhensible.
4. Le frontend reste consommateur du contrat backend et ne reconstruit pas la politique d'entitlement.
5. Les CTAs d'upgrade, s'ils existent, pointent vers les chemins déjà supportés.
6. Les tests backend projection authorization passent avec venv actif.
7. Aucun contenu premium n'est rendu comme disponible pour un plan non autorisé.

## Validation attendue

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run
```

Pour le backend :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q tests\api\test_projection_authorization.py tests\api\test_projection_endpoint.py --tb=short
```

## Dépendances

- CS-302.
- CS-303.

## Risques

Le risque principal est de dupliquer la logique d'entitlement côté frontend. L'UI peut expliquer et présenter les états, mais la décision d'accès doit rester pilotée par le backend.
