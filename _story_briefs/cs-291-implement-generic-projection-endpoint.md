# CS-291 — Implement Generic Projection Endpoint

## Résumé

Implémenter `POST /v1/astrology/projections` en orchestrant calcul, projection, persistance optionnelle et autorisation.

## Contexte

CS-263 définit le contrat de l'endpoint. L'implémentation doit arriver après les builders, la politique d'entitlements, la persistance et les garde-fous OpenAPI.

## Objectif

Créer la route générique de projection sans exposer les projections internes aux clients.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Implémenter `POST /v1/astrology/projections`.
2. Orchestrer `chart_id` existant vs `birth_input`.
3. Appeler le service de calcul si nécessaire.
4. Appeler le builder de projection demandé.
5. Appliquer persistance optionnelle, entitlements et interdictions internes.
6. Ajouter tests d'autorisation, erreurs et OpenAPI.

## Hors périmètre

- Implémenter une API B2B.
- Ajouter une UI frontend.
- Exposer les projections admin/expert.
- Créer des builders non livrés par les stories précédentes.

## Critères d'acceptation

1. La route fonctionne avec `chart_id` ou `birth_input`.
2. Les projections internes sont refusées côté client.
3. Les plans free/basic/premium sont contrôlés.
4. La persistance optionnelle réutilise CS-264.
5. Les tests OpenAPI confirment l'absence de surfaces interdites.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

## Dépendances

- CS-263 pour le contrat.
- CS-264 pour la persistance.
- CS-266 pour les garde-fous OpenAPI.
- CS-283 pour les entitlements.
- CS-285 à CS-287 pour les builders de projection.

## Risques

Le risque principal est de faire de l'endpoint une façade qui crée des projections inexistantes ou expose des surfaces internes. La route doit refuser toute projection sans builder validé.



