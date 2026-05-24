# CS-288 — Implement narrative_answer_audit_v1 Persistence

## Résumé

Implémenter la persistance de `narrative_answer_audit_v1`.

## Contexte

CS-259 définit le contrat d'audit. Avant les APIs admin, les réponses narratives auditées doivent être stockées avec leurs versions, hashes, provider, modèle et catégorie.

## Objectif

Créer ou adapter la persistance de l'audit des réponses IA.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Repartir du stockage existant identifié par CS-262.
2. Stocker `answer_id`, `answer_type`, `chart_id`, `user_id`, `plan`.
3. Stocker versions, hashes, prompt, provider, model et `grounding_status`.
4. Ajouter les tests de création et lecture.
5. Préparer le lien avec `evidence_refs`.

## Hors périmètre

- Créer une UI admin.
- Implémenter la validation complète des preuves.
- Exposer l'audit au client.
- Décider la rétention RGPD finale si elle reste ouverte.

## Critères d'acceptation

1. Les audits de réponses sont persistés.
2. Les champs obligatoires de CS-259 sont couverts.
3. `answer_type` distingue basic, premium, long, sensitive et free_short.
4. Les tests évitent la création d'un stockage doublon si l'existant convient.
5. Les données sensibles sont masquées ou isolées selon la politique existante.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

## Dépendances

- CS-259 pour le contrat.
- CS-262 pour l'audit de l'existant.

## Risques

Le risque principal est d'ajouter une deuxième table ou un deuxième modèle alors qu'un stockage de réponses IA existe déjà. La story doit adapter l'existant quand c'est possible.



