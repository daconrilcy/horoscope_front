# CS-303 — Connect B2C Frontend To Astrology Projections

## Résumé

Brancher le frontend B2C React sur `POST /v1/astrology/projections` pour afficher `beginner_summary_v1` et `client_interpretation_projection_v1`.

## Contexte

Le backend projection est prêt et la prochaine étape produit est la consommation B2C. Le frontend doit utiliser le client API central, gérer les états de chargement/erreur/vide et respecter les disclaimers définis côté produit.

## Objectif

Créer une expérience B2C exploitable qui consomme les projections sans dupliquer la logique métier backend.

## Préalable obligatoire

Relire :

- `frontend/src/**` pour identifier les pages et clients API existants.
- `backend/app/services/api_contracts/public/projections.py`.
- `docs/architecture/astrology-disclaimer-projection-policy.md`.
- `_condamad/reports/CS-256-CS-291-delivery-report.md`.

## Périmètre inclus

1. Identifier la page B2C cible existante.
2. Ajouter ou étendre le client API central pour `POST /v1/astrology/projections`.
3. Consommer `beginner_summary_v1`.
4. Consommer `client_interpretation_projection_v1`.
5. Gérer loading, error, empty, forbidden/entitlement et degraded mode.
6. Afficher les disclaimers en dur depuis l'app, pas depuis le LLM.
7. Ajouter tests frontend ciblés.

## Hors périmètre

- Modifier le backend projection sauf bug bloquant découvert.
- Ajouter replay admin.
- Ajouter audit admin.
- Ajouter une landing page marketing.
- Inventer des disclaimers côté LLM.

## Critères d'acceptation

1. Le frontend appelle le endpoint via le client API central.
2. Les deux projections B2C sont affichées clairement.
3. Les erreurs et restrictions de plan sont compréhensibles côté utilisateur.
4. Les disclaimers sont présents selon la politique produit.
5. Aucun secret, prompt, payload replay ou donnée admin n'est exposé au frontend.
6. Les tests frontend critiques passent.

## Validation attendue

```powershell
cd frontend
pnpm lint
pnpm test
```

Si le projet frontend utilise une commande différente, documenter la commande réelle dans la preuve finale.

## Dépendances

- CS-302.
- CS-291.
- CS-284.

## Risques

Le risque principal est de réimplémenter la logique de projection dans React. Le frontend doit rester consommateur du contrat API et ne pas reconstruire les projections localement.
