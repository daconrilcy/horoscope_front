# CS-258 — Define client_interpretation_projection_v1 By Plan

## Résumé

Définir la projection d'interprétation client par plan B2C : free, basic et premium.

## Contexte

La valeur client est portée par l'interprétation rédigée et vulgarisée, pas par l'exposition de données techniques. Les plans doivent différer par profondeur de narration, personnalisation, sections, prédictions et richesse explicative.

## Objectif

Spécifier `client_interpretation_projection_v1` et ses variantes de profondeur par plan sans exposer de runtime interne.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir les sections free, basic et premium.
2. Définir les règles de profondeur narrative.
3. Définir les éléments d'appui vulgarisés possibles.
4. Définir les exclusions techniques client.
5. Définir le lien avec `structured_facts_v1`, signaux interprétatifs et LLM.

## Hors périmètre

- Implémenter le provider LLM.
- Créer des prompts définitifs.
- Exposer `expert_technical_projection_v1`.
- Définir les rôles admin.

## Critères d'acceptation

1. Les plans free/basic/premium sont distingués par profondeur produit.
2. Aucun plan ne reçoit plus de runtime technique brut.
3. Les preuves techniques restent internes.
4. Les éléments d'appui client sont vulgarisés.
5. Le LLM est décrit comme rédacteur, pas calculateur.

## Validation attendue

```powershell
rg -n "client_interpretation|free|basic|premium|LLM|rédacteur|runtime technique" .\docs .\_story_briefs
git status --short -- backend/app frontend/src
```

## Dépendances

- CS-256 pour le socle factuel.
- CS-257 pour la projection débutant.

## Risques

Le risque principal est de faire varier les plans en exposant davantage de technique. La différenciation doit rester narrative et fonctionnelle.



