# CS-284 — Audit Existing Astrology Disclaimers And Projection Disclaimer Policy

## Résumé

Auditer les disclaimers astrologiques existants et définir leur rattachement aux projections B2C.

## Contexte

Les disclaimers doivent être contrôlés par l'application, pas inventés ou modifiés par le LLM. Avant d'en créer de nouveaux, il faut vérifier l'existant et décider quels textes sont injectés en dur selon les usages.

## Objectif

Définir une politique de disclaimers pour les projections free/basic/premium.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Rechercher les disclaimers existants dans le backend, frontend et la documentation.
2. Classer les disclaimers par usage : natal, prédiction, IA, mode dégradé, absence d'heure.
3. Décider quels disclaimers sont injectés en dur.
4. Interdire au LLM d'inventer ou modifier ces disclaimers.
5. Rattacher les disclaimers aux projections B2C par plan.

## Hors périmètre

- Créer une nouvelle politique juridique complète.
- Modifier les prompts sans besoin identifié.
- Ajouter une UI dédiée.
- Exposer des disclaimers techniques admin aux clients.

## Critères d'acceptation

1. Les disclaimers existants sont inventoriés.
2. Chaque projection B2C indique les disclaimers applicables.
3. Le LLM ne porte pas la responsabilité de générer les disclaimers.
4. Les cas dégradés et absence d'heure de naissance sont couverts.
5. Les disclaimers créés ou modifiés sont justifiés par un écart identifié.

## Validation attendue

```powershell
rg -n "disclaimer|avertissement|IA|prédiction|heure de naissance|mode dégradé" .\backend .\frontend .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-257 pour la projection débutant.
- CS-258 pour les interprétations par plan.
- CS-283 pour les entitlements B2C.

## Risques

Le risque principal est de laisser le LLM produire une politique produit ou juridique variable. Les disclaimers doivent rester applicatifs et versionnés.



