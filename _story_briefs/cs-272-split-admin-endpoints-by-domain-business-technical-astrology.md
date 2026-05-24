# CS-272 — Split Admin Endpoints By Domain: Business / Technical / Astrology

## Résumé

Définir la séparation des endpoints admin par domaine : business, technique et astrologie.

## Contexte

`ADMIN peut tout voir` ne signifie pas que toutes les données doivent transiter par les mêmes endpoints. Les surfaces doivent être séparées pour simplifier permissions, logs et audit.

## Objectif

Spécifier une architecture d'endpoints admin segmentée par domaine.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir les familles d'endpoints admin.
2. Associer chaque famille aux rôles cibles.
3. Définir les règles de logging.
4. Définir les règles OpenAPI interne.
5. Définir les exclusions client.

## Hors périmètre

- Refactorer tous les endpoints existants.
- Implémenter le RBAC complet.
- Créer les écrans admin.
- Ajouter replay ou diagnostics complets.

## Critères d'acceptation

1. Les domaines admin sont séparés dans la documentation.
2. Les endpoints client ne partagent pas les surfaces debug.
3. Les permissions se rattachent à CS-271.
4. Les logs d'accès sont prévus pour les surfaces sensibles.
5. Les projections internes restent hors exposition publique.

## Validation attendue

```powershell
rg -n "admin|business|technical|astrology|endpoint|OpenAPI interne|client" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-271 pour la matrice de permissions.
- CS-266 pour les garde-fous d'exposition.

## Risques

Le risque principal est une API admin fourre-tout difficile à sécuriser. La séparation par domaine doit être posée avant l'extension du back-office.



