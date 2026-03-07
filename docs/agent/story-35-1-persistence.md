# Story 35-1 — Persistance du run calculé

## Contexte & Périmètre

**Epic 35 / Story 35-1**
**Chapitre 35** — Persistance, explicabilité et audit

Cette story branche le moteur de calcul sur les repositories DB existants. Elle prend la sortie complète de `EngineOutput` (après épics 33 et 34) et la persiste de manière transactionnelle dans les tables `daily_prediction_runs`, `daily_prediction_category_scores`, `daily_prediction_turning_points` et `daily_prediction_time_blocks`.

---

## Hypothèses & Dépendances

- **Dépend de 34-5** : `EngineOutput` complet avec scores, pivots, blocs disponibles
- `DailyPredictionRepository` est stable et opérationnel (`backend/app/infra/db/repositories/daily_prediction_repository.py`)
- Les modèles DB sont stables :
  - `DailyPredictionRunModel` (table `daily_prediction_runs`)
  - `DailyPredictionCategoryScoreModel` (table `daily_prediction_category_scores`)
  - `DailyPredictionTurningPointModel` (table `daily_prediction_turning_points`)
  - `DailyPredictionTimeBlockModel` (table `daily_prediction_time_blocks`)
- La politique `input_hash` est figée : si un run avec le même hash existe en DB → le retourner sans recalcul

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Créer `PredictionPersistenceService.save(engine_output, db)` → `DailyPredictionRunModel`
- Implémenter la vérification `input_hash` avant création
- Persister les scores par catégorie avec tous les champs requis
- Persister les pivots et blocs en transaction unique

**Non-Objectifs :**
- Pas de recalcul dans ce service
- Pas d'API endpoint (c'est ultérieur)
- Pas de cache Redis

---

## Acceptance Criteria

### AC1 — Politique `input_hash` : réutilisation
Si un `DailyPredictionRunModel` avec le même `input_hash`, `user_id` et `local_date` existe déjà en DB :
- Le service le retourne tel quel
- Aucune écriture n'est effectuée
- Un flag `was_reused=True` est retourné avec le modèle

### AC2 — Création d'un run neuf
Si aucun run avec ce hash n'existe, un nouveau `DailyPredictionRunModel` est créé avec :
- `user_id`, `local_date`, `timezone`, `reference_version_id`, `ruleset_id`, `input_hash`
- `computed_at` = maintenant (UTC)
- `overall_tone` dérivé du ton global de l'`EngineOutput` si disponible

### AC3 — Scores par catégorie
Pour chaque catégorie active, un `DailyPredictionCategoryScoreModel` est créé avec :
- `run_id`, `category_id`
- `raw_score` = `raw_day` de `CategoryAggregation`
- `normalized_score` = valeur intermédiaire entre `raw_day` et la note calibrée (si disponible)
- `note_20` = note entière 1–20 calibrée
- `power` = `Power(c)`
- `volatility` = `Vol(c)`
- `rank` = classement de la catégorie par note décroissante (1 = meilleure)
- En cas d'égalité de note, le rang est attribué selon `category.sort_order`

### AC4 — Pivots persistés
Pour chaque `TurningPoint` de l'`EngineOutput`, un `DailyPredictionTurningPointModel` est créé avec :
- `run_id`, `occurred_at_local`, `severity`
- `event_type_id` : FK vers `ruleset_event_types` si l'événement déclencheur est identifiable
- `driver_json` : JSON sérialisé du `TurningPoint.driver_events` (top contributeurs du pivot)

### AC5 — Blocs persistés
Pour chaque `TimeBlock` de l'`EngineOutput`, un `DailyPredictionTimeBlockModel` est créé avec :
- `run_id`, `block_index`, `start_at_local`, `end_at_local`
- `tone_code`
- `dominant_categories_json` : JSON sérialisé de `TimeBlock.dominant_categories`

### AC6 — Transaction unique
Toutes les écritures (run + scores + pivots + blocs) sont dans une seule session SQLAlchemy. En cas d'erreur sur une écriture enfant, toute la transaction est rollback.

### AC7 — Idempotence sur hash identique
Appeler `save()` deux fois avec le même `EngineOutput` (même hash) produit le même résultat en DB sans doublon.

---

## Spécification technique

### Structure des fichiers

```
backend/app/prediction/
└── persistence_service.py    ← PredictionPersistenceService, SaveResult
```

### `persistence_service.py` — extraits clés

```python
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.prediction.schemas import EngineOutput
from app.infra.db.models.daily_prediction import DailyPredictionRunModel
from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository

@dataclass
class SaveResult:
    run: DailyPredictionRunModel
    was_reused: bool

class PredictionPersistenceService:
    def save(
        self,
        engine_output: EngineOutput,
        user_id: int,
        reference_version_id: int,
        ruleset_id: int,
        db: Session,
    ) -> SaveResult:
        repo = DailyPredictionRepository(db)
        input_hash = engine_output.effective_context.input_hash

        # Vérification hash existant
        existing = repo.get_run_by_hash(user_id, input_hash)
        if existing:
            return SaveResult(run=existing, was_reused=True)

        # Création transactionnelle
        with db.begin_nested():  # savepoint
            run = repo.create_run(...)
            self._save_scores(run, engine_output, db)
            self._save_turning_points(run, engine_output, db)
            self._save_time_blocks(run, engine_output, db)
        db.flush()

        return SaveResult(run=run, was_reused=False)
```

---

## Tests

### Fichier : `backend/app/tests/integration/test_prediction_persistence.py`

| Test | Description |
|------|-------------|
| `test_create_new_run` | Premier save → run créé, `was_reused=False` |
| `test_reuse_existing_hash` | Second save avec même hash → `was_reused=True`, pas de doublon |
| `test_recalculate_after_hash_change` | Hash différent → nouveau run créé |
| `test_all_category_scores_persisted` | Autant de `DailyPredictionCategoryScoreModel` que de catégories actives |
| `test_rank_correct` | Catégorie avec note 18 → rank=1, note 5 → rank le plus bas |
| `test_rank_tiebreak_by_sort_order` | Deux catégories à même note → rang selon `sort_order` |
| `test_turning_points_persisted` | Pivots de l'`EngineOutput` → autant de `DailyPredictionTurningPointModel` |
| `test_time_blocks_persisted` | Blocs de l'`EngineOutput` → autant de `DailyPredictionTimeBlockModel` |
| `test_transaction_rollback_on_error` | Erreur sur un score → run non créé, DB propre |
| `test_idempotent_double_save` | Double save → un seul run en DB |

Ces tests nécessitent une DB de test (SQLite en mémoire avec les migrations).

---

## Nouveaux fichiers

- `backend/app/prediction/persistence_service.py` ← CRÉER
- `backend/app/tests/integration/test_prediction_persistence.py` ← CRÉER

## Fichiers existants à modifier

- `backend/app/infra/db/repositories/daily_prediction_repository.py` ← MODIFIER : ajouter `get_run_by_hash(user_id, input_hash)`

## Fichiers existants à consulter (lecture seule)

- `backend/app/infra/db/models/daily_prediction.py` — tous les modèles DB
- `backend/app/infra/db/repositories/daily_prediction_repository.py` — `DailyPredictionRepository`
- `backend/app/prediction/schemas.py` — `EngineOutput`, `EffectiveContext`

---

## Checklist de validation

- [ ] Run créé avec tous les champs requis
- [ ] Réutilisation correcte si hash identique (`was_reused=True`)
- [ ] Nouveau run si hash différent
- [ ] Scores par catégorie avec `raw_score`, `note_20`, `power`, `volatility`, `rank`
- [ ] Rang correct avec tiebreak par `sort_order`
- [ ] Pivots et blocs persistés
- [ ] Transaction rollback en cas d'erreur
- [ ] Idempotence sur double save
- [ ] Tous les tests d'intégration passent
