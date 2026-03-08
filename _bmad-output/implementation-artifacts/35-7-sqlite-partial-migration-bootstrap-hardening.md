# Story 35.7 : SQLite partial-migration bootstrap hardening

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want un bootstrap SQLite local capable de remettre à `head` une base existante mais partiellement migrée,
so that le runtime local soit robuste même en présence d'un schéma intermédiaire ou d'un drift Alembic.

## Acceptance Criteria

### AC1 — Détection du drift de révision

Le bootstrap ne doit pas seulement vérifier l'absence des tables auth, mais aussi comparer la révision courante à la révision `head`.

### AC2 — Upgrade d'une DB existante non vide

Une base SQLite locale déjà créée, avec données présentes et révision intermédiaire, peut être remontée à `head`.

### AC3 — Conservation des données

Les données existantes survivent à l'upgrade.

### AC4 — Compatibilité avec le cas ciblé 0037

Le scénario de drift autour de la migration `20260308_0037` reste couvert et idempotent.

## Tasks / Subtasks

### T1 — Durcir le bootstrap local

- [x] Modifier `backend/app/infra/db/bootstrap.py`
  - [x] Lire la révision courante depuis `alembic_version`
  - [x] Lire la révision `head` via `ScriptDirectory`
  - [x] Déclencher `command.upgrade(..., "head")` si tables auth manquantes ou révision non à `head`

### T2 — Couvrir la base partiellement migrée

- [x] Créer `backend/app/tests/integration/test_db_bootstrap_partial_upgrade.py`
  - [x] Base montée à `20260307_0036`
  - [x] Insertion de données utilisateur
  - [x] Bootstrap local
  - [x] Vérification passage à `head` + conservation données

### T3 — Conserver les couvertures existantes

- [x] Garder `backend/app/tests/integration/test_db_bootstrap.py`
- [x] Garder `backend/app/tests/integration/test_migration_0037_add_contributors_json.py`

## Completion Notes List

- Le bootstrap local SQLite ne dépend plus uniquement de la présence des tables auth.
- Le mécanisme couvre maintenant le cas réaliste d'une base existante avec `alembic_version` intermédiaire.
- La conservation des données existantes est validée pendant l'upgrade.
- Le drift spécifique autour de `20260308_0037` reste couvert séparément par un test d'idempotence dédié.

## Validation

- `pytest -q app/tests/integration/test_db_bootstrap.py app/tests/integration/test_db_bootstrap_partial_upgrade.py app/tests/integration/test_migration_0037_add_contributors_json.py`
- inclus dans la validation consolidée :
  - `pytest -q app/tests/unit/test_engine_orchestrator.py app/tests/integration/test_prediction_persistence.py app/tests/integration/test_engine_persistence_e2e.py app/tests/integration/test_intraday_refinement_integration.py app/tests/integration/test_db_bootstrap.py app/tests/integration/test_db_bootstrap_partial_upgrade.py app/tests/regression/test_engine_non_regression.py`
- résultat consolidé : `64 passed`

## File List

- `backend/app/infra/db/bootstrap.py`
- `backend/app/tests/integration/test_db_bootstrap.py`
- `backend/app/tests/integration/test_db_bootstrap_partial_upgrade.py`
- `backend/app/tests/integration/test_migration_0037_add_contributors_json.py`
