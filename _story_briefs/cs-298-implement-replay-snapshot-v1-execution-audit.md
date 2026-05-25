# CS-298 — Implement replay_snapshot_v1 Execution And Audit

## Résumé

Implémenter la tentative de replay contrôlée et journaliser chaque lecture, replay, export éventuel et purge via des événements d'audit sûrs.

## Contexte

Après stockage, service et API admin, il faut brancher l'exécution de replay sans réintroduire de prompt brut, payload modèle brut ou données sensibles. Le replay doit documenter ses limites déterministes.

## Objectif

Ajouter l'orchestration de replay interne et ses audit logs obligatoires.

## Préalable obligatoire

Relire les owners existants avant implémentation :

- `backend/app/services/llm_observability/**`
- `backend/app/ops/llm/replay_service.py` si présent
- `backend/app/domain/llm/runtime/**`
- `backend/app/services/ops/audit_service.py`
- `backend/app/domain/audit/safe_details.py`

## Périmètre inclus

1. Ajouter une tentative de replay contrôlée à partir du snapshot approuvé.
2. Refuser replay si snapshot expiré, purgé ou incomplet.
3. Journaliser lecture metadata.
4. Journaliser tentative replay succès/échec.
5. Journaliser purge succès/échec.
6. Documenter les limites déterministes/non déterministes.
7. Ajouter tests de non-fuite dans les audit logs.

## Hors périmètre

- Rejouer des prompts bruts.
- Exposer la sortie brute provider.
- Ajouter de l'entraînement modèle.
- Ajouter export massif.
- Modifier les prompts LLM.

## Critères d'acceptation

1. Chaque lecture admin du snapshot est auditée.
2. Chaque tentative de replay est auditée.
3. Chaque purge est auditée.
4. Les logs ne contiennent ni prompts bruts, ni birth data, ni secrets, ni payload modèle brut.
5. Les limites de reproductibilité sont documentées.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests\unit tests\integration tests\api\admin --tb=short
```

## Dépendances

- CS-295 stockage.
- CS-296 service.
- CS-297 API admin interne.

## Risques

Le risque principal est de faire du replay une exécution LLM libre ou non reproductible sans trace. Toute tentative doit être bornée, auditée et refusable.
