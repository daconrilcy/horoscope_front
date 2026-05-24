# CS-281 — Define Transit Client Projection By Plan

## Résumé

Définir une future projection client des transits par plan B2C, sans exposition immédiate.

## Contexte

Les transits ne sont pas publics. Avant toute exposition, il faut définir ce que free, basic et premium pourraient voir, avec preuves et doctrine fermées.

## Objectif

Spécifier le contrat cible d'une projection client transits segmentée par plan.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir les contenus free/basic/premium.
2. Définir les états dégradés et indisponibles.
3. Définir les preuves nécessaires.
4. Définir le rôle éventuel du LLM rédacteur.
5. Définir les exclusions techniques.

## Hors périmètre

- Implémenter la projection.
- Exposer une route client.
- Modifier le frontend.
- Ajouter une promesse produit.

## Critères d'acceptation

1. La projection client transits est documentée comme cible future.
2. Les plans se différencient par narration et richesse, pas par debug.
3. L'exposition reste bloquée tant que le proof gate n'est pas validé.
4. Les preuves et limites doctrinales sont obligatoires.
5. Les clients ne voient pas le runtime brut.

## Validation attendue

```powershell
rg -n "transit|free|basic|premium|proof gate|non public|LLM" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-280 pour le runtime interne.
- CS-258 pour le modèle de projection client par plan.

## Risques

Le risque principal est de spécifier une UX plus vite que la preuve astrologique. La story doit maintenir le blocage d'exposition.



