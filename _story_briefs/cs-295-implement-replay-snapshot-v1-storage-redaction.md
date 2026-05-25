# CS-295 — Implement replay_snapshot_v1 Storage And Redaction

## Résumé

Implémenter le stockage interne approuvé de `replay_snapshot_v1` avec redaction stricte, rétention 30 jours et sans données interdites.

## Contexte

CS-278 est maintenant `ready-to-dev` après validation DPO/sécurité `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`. Le modèle de sécurité approuve uniquement un runtime interne, sans exposition publique/client, avec rétention maximale 30 jours, purge obligatoire, chiffrement au repos pour toute référence/payload isolé et interdiction des données brutes sensibles.

## Objectif

Créer ou étendre le propriétaire de persistance canonique des replay snapshots sans introduire de store parallèle.

## Préalable obligatoire

Avant toute création de modèle, migration, service ou test, vérifier les surfaces existantes :

- `backend/app/infra/db/models/llm/llm_observability.py`
- migrations existantes autour de `llm_replay_snapshots`
- `backend/app/core/sensitive_data.py`
- `backend/app/domain/audit/safe_details.py`
- `docs/architecture/replay-snapshot-v1-storage-security-model.md`
- `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md`

Si un owner existe déjà, l'étendre plutôt que créer un second store.

## Périmètre inclus

1. Identifier le propriétaire canonique du stockage replay.
2. Ajouter les champs nécessaires à `replay_snapshot_v1` si absents.
3. Ajouter une migration Alembic si le schéma change.
4. Garantir `expires_at = created_at + 30 jours`.
5. Stocker uniquement des références, hash, versions et métadonnées approuvées.
6. Ajouter/étendre les tests de schéma et redaction.
7. Ajouter des scans anti-données interdites en DB.

## Hors périmètre

- Ajouter une route API.
- Exécuter un replay.
- Ajouter une UI frontend.
- Ajouter une exposition OpenAPI publique.
- Stocker prompts bruts, données de naissance brutes, coordonnées exactes, identifiants directs ou secrets.

## Critères d'acceptation

1. Le stockage `replay_snapshot_v1` existe sur un owner canonique unique.
2. Aucun store parallèle n'est ajouté.
3. La rétention 30 jours est représentée par `expires_at`.
4. Les champs interdits ne sont ni persistés ni exposés.
5. Les tests prouvent la redaction et le schéma.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests\unit\test_replay_snapshot_v1_storage_security_model.py tests\integration --tb=short
```

## Dépendances

- CS-278 approval gate.
- CS-277 storage/security model.
- `DPO-REPLAY-SNAPSHOT-V1-RETENTION-001`.

## Risques

Le risque principal est de dupliquer un stockage replay déjà existant ou de persister une donnée sensible brute. La story doit privilégier l'extension de l'owner existant et des tests de non-fuite.
