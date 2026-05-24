# CS-280 — Implement Internal Transit Runtime

## Résumé

Implémenter le runtime interne de transits, sans route client ni frontend.

## Contexte

Le manifest interne `transit_chart_v1` prépare la structure. L'implémentation doit rester derrière les garde-fous de preuve, doctrine et non-exposition publique.

## Objectif

Ajouter un runtime interne testable pour les transits.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Implémenter les calculs ou adaptateurs internes validés.
2. Ajouter tests unitaires et tests de preuve.
3. Ajouter traces internes contrôlées.
4. Vérifier l'absence d'exposition client.
5. Documenter les limites astrologiques.

## Hors périmètre

- Ajouter une API client.
- Ajouter un écran frontend.
- Ajouter une interprétation LLM de transit.
- Exposer les fixed stars.

## Critères d'acceptation

1. Le runtime interne passe les tests.
2. Aucune route client n'est ajoutée.
3. Les preuves astronomiques requises sont présentes.
4. Les limites doctrinales sont documentées.
5. Les traces restent internes.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

## Dépendances

- CS-279 pour le manifest interne.

## Risques

Le risque principal est d'implémenter un runtime utilisable publiquement avant la projection client et le proof gate.



