# CS-294 — Reevaluate Admin Answer Audit Access Logs After Runtime

## Résumé

Réévaluer et compléter CS-268 maintenant que le runtime admin de revue des réponses rejetées existe.

## Contexte

CS-268 avait été bloquée parce que la surface protégée de consultation `admin_answer_audit_v1` n'existait pas encore. Le runtime a depuis évolué : `/v1/admin/answer-audits/rejected`, `/v1/admin/answer-audits/rejected/{answer_id}` et `/v1/admin/answer-audits/rejected/{answer_id}/review` existent.

Les consultations réussies du workflow de réponses rejetées sont journalisées via `AuditService`, mais il faut vérifier si cela couvre tout le contrat CS-268 ou seulement un sous-cas. Les refus `401/403` sont testés, mais leur journalisation doit être explicitement décidée et prouvée.

## Objectif

Clore ou reclasser CS-268 avec une preuve runtime actuelle, en garantissant que chaque consultation admin pertinente d'un audit de réponse IA est journalisée sans fuite de données sensibles.

## Préalable obligatoire

Avant toute création de contrat, builder, service, modèle, route ou test, vérifier s'il existe déjà dans le backend un élément qui couvre le sujet totalement, partiellement ou différemment. Si un élément pertinent existe, repartir de cet élément et le modifier ou l'étendre plutôt que de créer une implémentation parallèle.

## Périmètre inclus

1. Inventorier les routes admin `answer-audits` actuellement exposées.
2. Vérifier les événements d'audit produits pour liste, détail et changement de statut.
3. Vérifier la présence de `actor_user_id`, `target_id`, `action`, `status`, timestamp et `contract_id`.
4. Vérifier que les détails journalisés n'incluent aucun prompt complet, secret, donnée de naissance brute ou réponse rejetée brute.
5. Décider et documenter le comportement attendu pour les refus `401/403`.
6. Produire une preuve finale CS-268 actualisée ou une story de suivi strictement bornée si un écart reste ouvert.

## Hors périmètre

- Créer un second store d'audit.
- Ajouter une surface client, support ou replay.
- Implémenter `replay_snapshot_v1`.
- Exposer des prompts complets ou réponses rejetées brutes dans les logs.

## Critères d'acceptation

1. Chaque consultation admin réussie du workflow `admin_answer_audit_v1` est journalisée.
2. Les refus d'accès sont soit journalisés, soit explicitement documentés comme hors périmètre avec justification de sécurité.
3. Les tests prouvent que `raw_rejected_answer`, prompts complets, secrets et données sensibles ne sont pas dans les détails d'audit.
4. Les logs contiennent l'identité admin, l'objet consulté, l'action, le statut et un timestamp.
5. La capsule CS-268 possède une preuve finale actualisée qui ne dépend plus du blocker CS-288 historique.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
python -B -m pytest -q backend\tests\api\admin\test_rejected_answer_review_workflow.py backend\tests\unit\test_sensitive_data_non_leakage.py --tb=short
python -B -c "from app.main import app; paths={getattr(r,'path','') for r in app.routes}; assert '/v1/admin/answer-audits/rejected' in paths"
```

## Dépendances

- CS-267 pour le contrat admin answer audit.
- CS-268 pour la story bloquée à réévaluer.
- CS-288 pour la persistance narrative.
- CS-290 pour le workflow de réponse rejetée.

## Risques

Le risque principal est de fermer CS-268 sur le seul cas des réponses rejetées alors que le contrat demande toutes les consultations admin d'audit IA. La story doit nommer clairement le périmètre réellement couvert.
