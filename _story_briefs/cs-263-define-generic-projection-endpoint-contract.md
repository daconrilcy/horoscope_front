# CS-263 — Define Generic Projection Endpoint Contract

## Résumé

Définir le contrat d'un endpoint générique de projection pouvant consolider calcul de thème et construction de projection.

## Contexte

Le backend doit garder deux étapes séparées : calcul du thème puis construction de projection. L'API peut néanmoins offrir une commande consolidée pour simplifier l'usage.

## Objectif

Spécifier `POST /v1/astrology/projections` et ses règles de sécurité sans implémentation.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir le payload avec `chart_id`, `birth_input`, `projection_type`, `projection_version`, `persist`.
2. Définir la règle `chart_id` existant vs `birth_input`.
3. Définir les erreurs contrôlées.
4. Définir les accès par type de projection.
5. Définir les projections internes non accessibles client.
6. Graver que l'API B2B est hors scope de ce chantier.

## Hors périmètre

- Implémenter la route.
- Modifier OpenAPI.
- Ajouter une persistance.
- Ajouter des écrans frontend.
- Définir ou exposer une API B2B.

## Critères d'acceptation

1. Le contrat d'endpoint est documenté.
2. Les services calcul et projection restent conceptuellement séparés.
3. Les projections techniques internes sont interdites aux clients B2C.
4. La version de projection est obligatoire.
5. Les indisponibilités sont bloquantes et loguées.
6. Le B2B API est explicitement hors scope.

## Validation attendue

```powershell
rg -n "/v1/astrology/projections|projection_type|projection_version|birth_input|chart_id|persist" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-256 à CS-258 pour les projections initiales.
- CS-259 pour l'audit des réponses narratives.

## Risques

Le risque principal est de laisser l'endpoint devenir une porte d'accès aux projections internes. Le contrat doit porter les règles d'autorisation dès le départ.



