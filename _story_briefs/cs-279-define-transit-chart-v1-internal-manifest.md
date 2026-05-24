# CS-279 — Define transit_chart_v1 Internal Manifest

## Résumé

Définir le manifest interne de `transit_chart_v1` sans exposition publique.

## Contexte

`transit_chart_v1` est sélectionné mais non public. Aucune route client, frontend ou promesse produit ne doit être ajoutée tant que projection, preuve et doctrine ne sont pas fermées.

## Objectif

Spécifier le manifest interne des transits pour préparer le runtime sans engagement public.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir les inputs et outputs internes.
2. Définir les dépendances à la preuve astronomique.
3. Définir les limites doctrinales.
4. Définir les traces nécessaires.
5. Marquer l'exposition publique comme bloquée.

## Hors périmètre

- Implémenter une route client.
- Modifier le frontend.
- Ajouter une projection client transits.
- Promettre une fonctionnalité commerciale.

## Critères d'acceptation

1. `transit_chart_v1` a un manifest interne documenté.
2. L'exposition publique est explicitement interdite.
3. Les prérequis preuve/doctrine sont listés.
4. Les inputs/outputs restent internes.
5. Les futures stories runtime sont identifiées.

## Validation attendue

```powershell
rg -n "transit_chart_v1|manifest|interne|non public|preuve|doctrine" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-250 pour la preuve avant runtime temporel public.
- CS-252 pour la gouvernance doctrinale.

## Risques

Le risque principal est de créer une attente produit prématurée. Cette story doit rester interne.



