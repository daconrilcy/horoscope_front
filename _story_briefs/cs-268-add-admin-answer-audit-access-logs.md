# CS-268 — Add Admin Answer Audit Access Logs

## Résumé

Journaliser chaque consultation admin des audits de réponses IA.

## Contexte

L'accès admin est complet mais doit être tracé. Chaque consultation d'audit contenant des preuves, prompts ou données sensibles doit générer un journal d'accès.

## Objectif

Ajouter une traçabilité d'accès pour `admin_answer_audit_v1`.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Définir l'événement d'accès audit.
2. Capturer admin, date, objet consulté, action et justification si disponible.
3. Masquer les données sensibles dans les logs.
4. Ajouter les tests d'écriture de log.
5. Documenter la rétention attendue ou l'incertitude RGPD.

## Hors périmètre

- Décider la politique RGPD finale.
- Implémenter tous les logs admin du back-office.
- Ajouter du replay.
- Exposer les logs aux clients.

## Critères d'acceptation

1. Chaque consultation admin d'audit IA est journalisée.
2. Les logs ne contiennent pas de secrets ni données de naissance brutes.
3. Les tests couvrent succès et refus.
4. Les erreurs de logging sont gérées.
5. La rétention est documentée comme dépendante de la politique RGPD si non tranchée.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q
```

## Dépendances

- CS-267 pour l'API admin d'audit.
- CS-288 pour disposer de données d'audit réellement persistées.

## Risques

Le risque principal est de créer une surface admin puissante sans traçabilité. Le log doit être minimal mais systématique.



