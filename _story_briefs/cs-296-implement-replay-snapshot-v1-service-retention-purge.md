# CS-296 — Implement replay_snapshot_v1 Service Retention And Purge

## Résumé

Créer le service applicatif interne de gestion `replay_snapshot_v1`, incluant création, lecture contrôlée, purge automatique et purge manuelle audit-ready.

## Contexte

Après CS-295, le stockage approuvé existe. Il faut centraliser la logique métier dans un service unique plutôt que disperser la création, la lecture et la purge dans des routeurs ou jobs.

## Objectif

Ajouter un service `ReplaySnapshotV1Service` ou étendre le service existant canonique pour gérer la durée de vie des replay snapshots.

## Préalable obligatoire

Relire les services existants avant création :

- `backend/app/services/llm_observability/**`
- `backend/app/ops/llm/**`
- `backend/app/services/ops/audit_service.py`
- `backend/app/domain/audit/safe_details.py`
- modèle/migration livré par CS-295

## Périmètre inclus

1. Créer ou étendre un service applicatif unique.
2. Ajouter `create_snapshot`.
3. Ajouter `get_snapshot_metadata`.
4. Ajouter `purge_expired`.
5. Ajouter `purge_snapshot`.
6. Appliquer la rétention 30 jours.
7. Produire des résultats métier contrôlés : succès, introuvable, expiré, déjà purgé.
8. Préparer les hooks d'audit sans créer de route API.

## Hors périmètre

- Ajouter les endpoints admin.
- Ajouter un replay effectif LLM.
- Ajouter des jobs planifiés globaux si aucun mécanisme existant n'est disponible.
- Ajouter une UI ou un client généré.

## Critères d'acceptation

1. La logique de création/lecture/purge est centralisée dans un service unique.
2. Les snapshots expirés ne sont pas utilisables.
3. La purge manuelle écrit un état tombstone ou supprime selon la politique approuvée.
4. Les diagnostics et `narrative_answer_audit_v1` ne sont pas supprimés en cascade.
5. Les tests couvrent création, expiration, purge automatique et purge manuelle.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests\unit tests\integration --tb=short
```

## Dépendances

- CS-295 stockage et redaction.
- `AuditService` existant.

## Risques

Le risque principal est de mélanger purge replay, diagnostics et audit narratif. Le service ne doit supprimer que le replay snapshot et ses références payload.
