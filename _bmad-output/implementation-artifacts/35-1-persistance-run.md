# Story 35.1 : Persistance du run calculé

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want un service `PredictionPersistenceService` qui persiste transactionnellement la sortie complète du moteur dans les tables DB existantes,
so that les prédictions sont stockées une seule fois, réutilisées via `input_hash`, et auditables.

## Acceptance Criteria

### AC1 — Réutilisation si hash identique

Si un `DailyPredictionRunModel` avec le même `user_id` et `input_hash` existe → retourner `SaveResult(run=existing, was_reused=True)`. Aucune écriture.

### AC2 — Création d'un run neuf

Sinon : créer un nouveau `DailyPredictionRunModel` via `DailyPredictionRepository.create_run()`.

### AC3 — Scores par catégorie avec `rank`

Pour chaque catégorie active : `DailyPredictionCategoryScoreModel` avec `raw_score`, `normalized_score`, `note_20`, `power`, `volatility`, `rank`.
- `rank` = classement par note décroissante (1 = meilleure)
- Tiebreak sur `category.sort_order` si même note

### AC4 — Pivots persistés

Pour chaque `TurningPoint` : `DailyPredictionTurningPointModel` avec `occurred_at_local`, `severity`, `driver_json` (JSON sérialisé des drivers).

### AC5 — Blocs persistés

Pour chaque `TimeBlock` : `DailyPredictionTimeBlockModel` avec `block_index`, `start_at_local`, `end_at_local`, `tone_code`, `dominant_categories_json`.

### AC6 — Transaction unique

Toutes les écritures (run + scores + pivots + blocs) dans une seule session SQLAlchemy. Rollback total en cas d'erreur.

### AC7 — Idempotence

Double appel avec même `EngineOutput` (même hash) → un seul run en DB, `was_reused=True` au deuxième appel.

## Tasks / Subtasks

### T1 — Ajouter `get_run_by_hash` au repository (AC1)

- [x] Modifier `backend/app/infra/db/repositories/daily_prediction_repository.py`
  - [x] Ajouter `get_run_by_hash(user_id: int, input_hash: str) -> DailyPredictionRunModel | None`

### T2 — `PredictionPersistenceService` (AC1–AC7)

- [x] Créer `backend/app/prediction/persistence_service.py`
  - [x] Dataclass `SaveResult(run: DailyPredictionRunModel, was_reused: bool)`
  - [x] Classe `PredictionPersistenceService`
  - [x] `save(engine_output, user_id, reference_version_id, ruleset_id, db) -> SaveResult`
    - [x] Vérifier hash existant via `get_run_by_hash()`
    - [x] Si trouvé → retourner `SaveResult(run=existing, was_reused=True)`
    - [x] Sinon : créer run, scores, pivots, blocs dans une session
    - [x] `_save_scores(run, engine_output, ctx, db)` — calcul du rank inclus
    - [x] `_save_turning_points(run, engine_output, db)`
    - [x] `_save_time_blocks(run, engine_output, db)`

### T3 — Tests d'intégration (AC1–AC7)

- [x] Créer `backend/app/tests/integration/test_prediction_persistence.py`
  - [x] Setup : DB SQLite en mémoire avec migrations appliquées
  - [x] `test_create_new_run` — premier save → `was_reused=False`, run en DB
  - [x] `test_reuse_existing_hash` — deuxième save même hash → `was_reused=True`, pas de doublon
  - [x] `test_new_run_on_hash_change` — hash différent → nouveau run
  - [x] `test_scores_persisted` — autant de scores que de catégories actives
  - [x] `test_rank_correct` — catégorie note 18 → rank=1
  - [x] `test_rank_tiebreak_sort_order` — même note → rang selon `sort_order`
  - [x] `test_turning_points_persisted` — pivots de l'`EngineOutput` → en DB
  - [x] `test_time_blocks_persisted` — blocs → en DB
  - [x] `test_transaction_rollback` — erreur injection → DB propre
  - [x] `test_idempotent_double_save` — double save → un seul run

## Dev Notes

### Pattern save transactionnel SQLAlchemy

```python
from sqlalchemy.orm import Session

def save(self, engine_output: EngineOutput, user_id: int, ..., db: Session) -> SaveResult:
    input_hash = engine_output.effective_context.input_hash
    repo = DailyPredictionRepository(db)

    existing = repo.get_run_by_hash(user_id, input_hash)
    if existing:
        return SaveResult(run=existing, was_reused=True)

    # Tout dans un seul flush
    run = repo.create_run(
        user_id=user_id,
        local_date=...,
        timezone=engine_output.effective_context.timezone,
        reference_version_id=reference_version_id,
        ruleset_id=ruleset_id,
        input_hash=input_hash,
    )
    self._save_scores(run, engine_output, db)
    self._save_turning_points(run, engine_output, db)
    self._save_time_blocks(run, engine_output, db)
    db.flush()

    return SaveResult(run=run, was_reused=False)
```

### Calcul du `rank`

```python
sorted_scores = sorted(scores.items(), key=lambda x: (-x[1].note_20, x[1].sort_order))
for rank_idx, (cat_code, score) in enumerate(sorted_scores, start=1):
    score_model.rank = rank_idx
```

### Sérialisation `driver_json`

```python
import json
driver_json = json.dumps([
    {
        "event_type": e.event_type,
        "body": e.body,
        "target": e.target,
        "contribution": contrib,
    }
    for e, contrib in pivot.driver_events
])
```

### `EngineOutput` doit porter `local_date`

Vérifier que `EngineOutput` (défini en 33-1) expose la `local_date` du run. Si elle n'est pas dans la sortie, la passer en paramètre supplémentaire à `save()`.

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/app/prediction/persistence_service.py` | Créer |
| `backend/app/infra/db/repositories/daily_prediction_repository.py` | Modifier (ajouter `get_run_by_hash`) |
| `backend/app/tests/integration/test_prediction_persistence.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/infra/db/models/daily_prediction.py`
- `backend/app/prediction/engine_orchestrator.py`

### Références

- [Source: backend/app/infra/db/repositories/daily_prediction_repository.py — DailyPredictionRepository]
- [Source: backend/app/infra/db/models/daily_prediction.py — DailyPredictionRunModel, DailyPredictionCategoryScoreModel]
- [Source: _bmad-output/implementation-artifacts/32-1-migration-c-tables-persistance-quotidienne-predictions.md — patterns upsert]

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash

### Debug Log References

- Added `get_run_by_hash` to `DailyPredictionRepository`.
- Created `PredictionPersistenceService` with transaction support.
- Implemented score ranking with tiebreak on category `sort_order`.
- Added serialization for `TurningPoint` drivers and `TimeBlock` dominant categories.
- Created comprehensive integration tests.

### Completion Notes List

- All ACs satisfied.
- Tests pass (10/10) after code review fixes.
- Code review fixes applied: field name mapping corrected for real TurningPoint/TimeBlock objects (C2), test_transaction_rollback uses deterministic mock injection (H1), 3 missing tests added (C1), unused Any import removed (L1).

### File List

- `backend/app/infra/db/repositories/daily_prediction_repository.py` (modified)
- `backend/app/prediction/persistence_service.py` (created)
- `backend/app/tests/integration/test_prediction_persistence.py` (created)
- `backend/app/tests/integration/conftest.py` (modified)
