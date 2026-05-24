# CS-264 — Implement Projection Persistence And projection_hash

## Résumé

Implémenter la persistance des projections et le calcul de `projection_hash`.

## Contexte

L'audit IA nécessite de savoir exactement quelle projection a servi à produire une réponse. Les projections doivent pouvoir être persistées avec version, source et hash.

## Objectif

Ajouter une persistance contrôlée des projections calculées à la demande.

Cette story ne doit pas inventer les projections si les builders n'existent pas encore. Elle doit persister des projections déjà produites par des builders validés, ou être bloquée.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir ou ajouter le modèle de persistance.
2. Calculer un hash stable du payload canonique.
3. Stocker type, version, source_versions et date de génération.
4. Ajouter les tests de stabilité du hash.
5. Vérifier le lien avec `narrative_answer_audit_v1`.
6. Bloquer l'implémentation si aucun builder réel n'existe pour la projection ciblée.

## Hors périmètre

- Implémenter toutes les projections.
- Ajouter un back-office.
- Maintenir plusieurs versions historiques longues.
- Exposer les projections internes aux clients.

## Critères d'acceptation

1. Une projection persistée porte `projection_hash`.
2. Le hash est stable pour un payload canonique identique.
3. Les versions source sont conservées.
4. Les tests couvrent stabilité et changement de hash.
5. Les accès restent filtrés par type de projection et rôle.
6. La story ne crée pas de projection fictive pour satisfaire la persistance.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

## Dépendances

- CS-256 pour le contrat `structured_facts_v1`.
- CS-285 pour l'implémentation du builder `structured_facts_v1`.
- CS-286 pour l'implémentation du builder `beginner_summary_v1`.
- CS-287 pour l'implémentation du builder `client_interpretation_projection_v1`.
- CS-263 pour le contrat d'endpoint.
- CS-259 pour les besoins d'audit.

## Risques

Le risque principal est de hasher un JSON non canonique. La sérialisation doit être stable, déterministe et testée.

Un second risque est de livrer le contenant avant le contenu. Si aucune projection réelle n'est produite, la story doit être reportée plutôt que créer une abstraction vide.



