# CS-271 — Define Permission Matrix For Business, Technical, Astrology And Debug Data

## Résumé

Définir la matrice de permissions pour les données business, techniques, astrologiques et debug.

## Contexte

`ADMIN` peut tout voir aujourd'hui, mais les futures surfaces doivent séparer marketer, techno et expert astro. Les permissions doivent empêcher l'exposition accidentelle des données techniques ou personnelles.

La matrice décrit une cible. Tant qu'aucun RBAC n'est implémenté, `ADMIN` reste le seul rôle opérationnel et les rôles futurs ne donnent aucun accès réel.

## Objectif

Créer une matrice de permissions cible utilisable par les futures stories d'API admin.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Classer les données par domaine.
2. Définir les droits par rôle interne.
3. Définir les règles de masquage.
4. Définir les actions : lire, rechercher, exporter, rejouer, corriger.
5. Identifier les permissions non décidées.
6. Marquer `MARKETER`, `TECHNO` et `ASTRO_EXPERT` comme rôles cibles non actifs.

## Hors périmètre

- Implémenter le contrôle d'accès.
- Créer un back-office.
- Modifier les clients B2C.
- Décider la rétention RGPD finale.

## Critères d'acceptation

1. Une matrice rôle x domaine existe.
2. Les données de naissance sont traitées comme sensibles.
3. Les traces, prompts et replay sont classés séparément.
4. Les accès client B2C sont exclus de la matrice admin.
5. Les rôles futurs sont explicitement non actifs sans RBAC.
6. Les permissions incertaines sont marquées comme décisions ouvertes.

## Validation attendue

```powershell
rg -n "matrice|permission|business|technical|astrology|debug|données de naissance|replay" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-270 pour les rôles.

## Risques

Le risque principal est d'accorder par défaut des accès trop larges aux futurs rôles. La matrice doit être restrictive hors `ADMIN`.



