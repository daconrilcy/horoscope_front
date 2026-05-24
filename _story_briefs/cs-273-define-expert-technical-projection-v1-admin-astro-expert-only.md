# CS-273 — Define expert_technical_projection_v1 For ADMIN / ASTRO_EXPERT Only

## Résumé

Reclasser et définir `expert_technical_projection_v1` comme projection interne admin/futur expert astro, non destinée au client B2C.

## Contexte

La projection technique expert n'est pas client-safe. Elle peut être riche et astrologiquement complète parce qu'elle vise un usage interne ou expert, avec permissions et logs adaptés.

## Objectif

Spécifier le contrat d'une projection technique expert sans exposition client.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir les consommateurs autorisés : `ADMIN`, futur `ASTRO_EXPERT`.
2. Définir les familles de données astrologiques autorisées.
3. Définir les liens vers faits structurés, signaux et preuves.
4. Définir les exclusions techno/debug.
5. Définir les logs d'accès nécessaires.

## Hors périmètre

- Exposer la projection au client B2C.
- Implémenter `ASTRO_EXPERT`.
- Ajouter fixed stars publiques.
- Ajouter replay complet.

## Critères d'acceptation

1. `expert_technical_projection_v1` est explicitement interne.
2. Le client B2C ne peut pas y accéder.
3. La projection n'inclut pas de traces runtime brutes non nécessaires.
4. Les permissions se rattachent à la matrice interne.
5. Les usages admin/expert sont documentés.

## Validation attendue

```powershell
rg -n "expert_technical_projection_v1|ADMIN|ASTRO_EXPERT|non client|interne|B2C" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-270 pour les rôles.
- CS-271 pour la matrice de permissions.
- CS-256 pour le socle factuel.

## Risques

Le risque principal est de raviver l'ambiguïté `client-safe`. Le brief doit dire clairement que cette projection n'est pas une surface B2C.



