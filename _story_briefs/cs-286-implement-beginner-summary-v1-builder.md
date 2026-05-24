# CS-286 — Implement beginner_summary_v1 Builder

## Résumé

Implémenter le builder `beginner_summary_v1` pour produire une projection B2C simple et déterministe.

## Contexte

CS-257 définit la projection débutant. Elle doit devenir calculable depuis `structured_facts_v1` sans exposer de runtime technique.

## Objectif

Créer ou adapter le builder qui produit `beginner_summary_v1`.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Rechercher les synthèses client existantes.
2. Construire la projection depuis `structured_facts_v1`.
3. Gérer les états normal, empty, degraded et unavailable.
4. Ajouter les tests sans heure de naissance.
5. Garantir l'absence de données techniques internes.

## Hors périmètre

- Ajouter une UI frontend.
- Ajouter une narration LLM longue.
- Implémenter les projections premium.
- Exposer les preuves techniques.

## Critères d'acceptation

1. `beginner_summary_v1` est généré par un builder testé.
2. Les cas sans heure de naissance produisent un mode dégradé contrôlé.
3. Les primitives internes ne sont pas exposées.
4. Les messages sont déterministes et non LLM.
5. Le builder réutilise `structured_facts_v1`.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

## Dépendances

- CS-257 pour le contrat.
- CS-285 pour `structured_facts_v1`.
- CS-284 pour les disclaimers applicables.

## Risques

Le risque principal est de créer une projection débutant indépendante du socle factuel. Le builder doit dériver de `structured_facts_v1`.



