# CS-306 — Close CS-303 Browser QA And Refresh Delivery Status

## Résumé

Valider visuellement et fonctionnellement `/natal` avec les projections CS-303, puis mettre à jour le rapport CS-302 à CS-304 pour passer le statut final à `Delivered` si toutes les preuves sont réunies.

## Contexte

Le rapport `_condamad/reports/CS-302-CS-304-delivery-report.md` conserve deux limites liées à CS-303 : la suite frontend complète n'était pas verte et aucun démarrage local avec QA navigateur n'était enregistré. CS-305 doit traiter la suite complète. Cette story ferme la preuve navigateur et la preuve de livraison consolidée.

## Objectif

Prouver que l'expérience `/natal` rend correctement les projections `beginner_summary_v1` et `client_interpretation_projection_v1` dans un navigateur réel, sans régression d'état UI, puis rafraîchir les preuves et le rapport de livraison.

## Préalable obligatoire

Relire :

- `_condamad/reports/CS-302-CS-304-delivery-report.md`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-after.md`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/api/astrologyProjections.ts`

## Condition obligatoire

Ne marquer le rapport final `Delivered` que si CS-305 a levé la limitation de suite frontend complète ou si une preuve équivalente et explicite démontre que la suite complète passe désormais.

## Périmètre inclus

1. Démarrer localement le frontend et les services nécessaires selon les scripts du repo.
2. Utiliser l'utilisateur test autorisé si une session authentifiée est nécessaire : `daconrilcy@hotmail.com`.
3. Ouvrir `/natal` dans un navigateur réel et vérifier les états projection utiles : chargement, succès, erreur contrôlée si reproductible, entitlement si reproductible, et mode dégradé si reproductible.
4. Capturer une preuve de rendu ou un log de QA navigateur sous la capsule de story.
5. Vérifier qu'aucun texte ne déborde ou ne masque les contrôles principaux sur desktop et mobile.
6. Rejouer les validations ciblées CS-303 utiles après QA.
7. Rafraîchir `_condamad/reports/CS-302-CS-304-delivery-report.md` pour remplacer `Partially delivered` par `Delivered` uniquement si toutes les limites bloquantes sont fermées.

## Hors périmètre

- Modifier le comportement métier backend.
- Ajouter une nouvelle page ou navigation produit.
- Implémenter les flows admin CS-304.
- Corriger des défauts frontend non nécessaires au rendu `/natal` sauf s'ils bloquent la validation.
- Dégrader ou supprimer des états UI pour simplifier la QA.

## Critères d'acceptation

1. L'application démarre localement ou le blocage de démarrage est documenté avec une cause exploitable.
2. `/natal` est validé dans un navigateur réel avec preuve datée.
3. Les projections B2C s'affichent sans reconstruire la logique backend dans React.
4. Les disclaimers restent app-owned.
5. Aucun champ interne, replay, provider, prompt ou admin n'est exposé.
6. Les validations ciblées CS-303 et la suite complète frontend passée par CS-305 sont référencées.
7. Le rapport CS-302 à CS-304 est rafraîchi avec le statut final correct et les anciens gaps retirés seulement s'ils sont prouvés fermés.

## Validation attendue

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation
node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run
```

Pour les commandes backend de contrat, activer le venv avant toute commande Python :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q tests\api\test_projection_openapi.py tests\api\test_projection_endpoint.py tests\api\test_projection_authorization.py --tb=short
python -B -c "from app.main import app; assert '/v1/astrology/projections' in app.openapi().get('paths', {}); assert '/v1/astrology/projections' in {getattr(r, 'path', '') for r in app.routes}"
```

## Dépendances

- CS-303.
- CS-305.
- Rapport `_condamad/reports/CS-302-CS-304-delivery-report.md`.

## Risques

Le risque principal est de changer le statut du rapport sans preuve navigateur réelle ou sans suite complète frontend verte. Cette story doit fermer les gaps, pas seulement reformuler le rapport.
