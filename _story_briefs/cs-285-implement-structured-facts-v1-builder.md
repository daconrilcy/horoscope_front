# CS-285 — Implement structured_facts_v1 Builder

## Résumé

Implémenter le builder `structured_facts_v1` à partir du runtime canonique existant.

## Contexte

CS-256 définit le contrat de faits structurés, mais la persistance et l'audit IA ont besoin d'une projection réelle, calculable et hashable.

## Objectif

Créer ou adapter le builder qui produit `structured_facts_v1`.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Rechercher les adaptateurs/projections existants et repartir de l'existant.
2. Produire un payload canonique stable.
3. Séparer faits structurés, signaux interprétatifs et narration.
4. Ajouter les tests de structure et stabilité.
5. Vérifier que les primitives internes ne sont pas exposées publiquement.

## Hors périmètre

- Ajouter une route API publique.
- Ajouter une narration LLM.
- Implémenter `beginner_summary_v1`.
- Modifier le frontend.

## Critères d'acceptation

1. `structured_facts_v1` est généré par un builder testé.
2. Le payload est stable et prêt pour hash canonique.
3. Les champs narratifs sont absents.
4. Les tests couvrent les cas nominaux et données manquantes.
5. Le builder réutilise les composants backend existants plutôt qu'un pipeline parallèle.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

## Dépendances

- CS-256 pour le contrat.

## Risques

Le risque principal est de dupliquer une logique de transformation déjà présente dans le backend. La story doit d'abord auditer l'existant et modifier l'élément le plus proche.



