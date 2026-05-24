# CS-287 — Implement client_interpretation_projection_v1 Builder By Plan

## Résumé

Implémenter le builder `client_interpretation_projection_v1` par plan B2C.

## Contexte

CS-258 définit l'interprétation client par plan. La projection doit préparer des sections, signaux et contraintes exploitables par la narration, sans laisser le LLM inventer les faits.

## Objectif

Créer ou adapter le builder qui prépare les projections d'interprétation client free/basic/premium.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Rechercher les services de narration/interprétation existants.
2. Construire les sections par plan depuis faits et signaux autorisés.
3. Appliquer la politique d'entitlements.
4. Attacher les disclaimers applicables.
5. Ajouter les tests par plan et par erreur d'accès.

## Hors périmètre

- Intégrer un provider LLM.
- Écrire des prompts définitifs.
- Exposer les projections expert.
- Ajouter une UI.

## Critères d'acceptation

1. Le builder produit des projections distinctes par plan.
2. Les plans se différencient par profondeur et sections, pas par runtime brut.
3. Les projections basic/premium sont prêtes à alimenter l'audit IA.
4. Les erreurs plan insuffisant sont testées.
5. Le builder réutilise les services existants plutôt que de créer un pipeline parallèle.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

## Dépendances

- CS-258 pour le contrat.
- CS-283 pour les entitlements.
- CS-284 pour les disclaimers.
- CS-285 pour `structured_facts_v1`.

## Risques

Le risque principal est de mélanger construction de projection et génération LLM. La projection prépare l'entrée, elle ne devient pas provider narratif.



