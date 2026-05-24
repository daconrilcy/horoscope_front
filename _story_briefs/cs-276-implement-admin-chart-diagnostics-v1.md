# CS-276 — Implement admin_chart_diagnostics_v1

## Résumé

Implémenter `admin_chart_diagnostics_v1` pour diagnostiquer les calculs astrologiques côté admin.

## Contexte

Le support technique et l'expertise astro auront besoin d'une surface de diagnostic calcul, distincte de l'audit des réponses IA et du replay complet.

## Objectif

Ajouter une projection admin protégée de diagnostic calcul avec redaction, logs et tests.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Implémenter le contrat de diagnostic validé.
2. Appliquer les règles de masquage.
3. Journaliser les consultations.
4. Ajouter tests permissions, redaction et erreurs.
5. Documenter les limites par rapport au replay.

## Hors périmètre

- Implémenter `replay_snapshot_v1`.
- Exposer au client B2C.
- Ajouter fixed stars publiques.
- Fusionner avec l'audit IA.

## Critères d'acceptation

1. `admin_chart_diagnostics_v1` est accessible uniquement à admin autorisé.
2. Les données sensibles sont masquées selon politique.
3. Chaque consultation est journalisée.
4. Les tests couvrent accès autorisé et refusé.
5. La projection reste distincte de l'audit de réponse IA.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

## Dépendances

- CS-275 pour la politique diagnostic/replay.
- CS-272 pour la séparation d'endpoints admin.

## Risques

Le risque principal est d'exposer trop de données brutes sous prétexte d'admin. L'implémentation doit respecter redaction et logs.



