# CS-270 — Define Internal Role Model: ADMIN, MARKETER, TECHNO, ASTRO_EXPERT

## Résumé

Définir le modèle de rôles internes cible : `ADMIN`, `MARKETER`, `TECHNO`, `ASTRO_EXPERT`.

## Contexte

Aujourd'hui, seul `ADMIN` est actif avec accès complet. Les futurs rôles internes doivent être anticipés pour éviter que toutes les surfaces admin restent indistinctes.

`MARKETER`, `TECHNO` et `ASTRO_EXPERT` sont des rôles cibles, non actifs tant qu'aucun RBAC n'est implémenté.

## Objectif

Documenter le modèle de rôles internes sans l'implémenter immédiatement si ce n'est pas nécessaire.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir chaque rôle et son intention métier.
2. Distinguer rôles internes et clients B2C/B2B.
3. Identifier les surfaces concernées.
4. Définir l'état actuel : `ADMIN` seul actif.
5. Définir les implications futures sur permissions.
6. Préciser que les rôles futurs ne sont pas opérationnels.

## Hors périmètre

- Implémenter RBAC complet.
- Créer des comptes ou migrations.
- Modifier l'authentification.
- Ouvrir des accès réels à de nouveaux rôles.

## Critères d'acceptation

1. Les quatre rôles internes sont documentés.
2. `ADMIN` est explicitement le seul rôle actif actuel.
3. Les clients B2C ne sont pas confondus avec les rôles internes.
4. Les rôles futurs ne donnent aucun accès tant qu'ils ne sont pas implémentés.
5. `ADMIN` reste le seul rôle opérationnel tant qu'aucun RBAC n'est implémenté.
6. Les dépendances vers la matrice de permissions sont listées.

## Validation attendue

```powershell
rg -n "ADMIN|MARKETER|TECHNO|ASTRO_EXPERT|rôle interne|B2C|B2B" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-255 pour les surfaces produit.
- CS-267 pour la première surface admin d'audit.

## Risques

Le risque principal est de documenter des rôles comme déjà disponibles. Le brief doit distinguer cible et état réel.



