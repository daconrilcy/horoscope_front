# Story 32.1 : Migration C — Tables de persistance quotidienne des prédictions (runs, scores par catégorie, turning points, blocs horaires)

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want que la base de données dispose de tables normalisées pour stocker les résultats de chaque run de prédiction quotidienne (scores par catégorie, points de bascule, blocs horaires),
so that les prédictions sont persistées et consultables sans recalcul, l'évolution jour par jour est traçable, et une UI riche peut être construite ultérieurement.

## Contexte métier

Le moteur de prédiction produit pour chaque utilisateur et chaque date locale :
- un run de calcul global (`daily_prediction_runs`) avec métadonnées (timezone, ruleset, hash d'input)
- des scores normalisés pour chaque catégorie (`daily_prediction_category_scores`)
- les points de bascule détectés dans la journée (`daily_prediction_turning_points`)
- une segmentation en blocs horaires avec tonalité (`daily_prediction_time_blocks`)

Stocker ces données en DB évite de recalculer, permet le suivi longitudinal des notes 1–20, et prépare la livraison d'une UI de prédiction détaillée (sprint suivant).

Cette story couvre **Migration C** : création des 4 tables de persistance. Aucun service, aucune API, aucun frontend dans cette story — uniquement la couche DB.

## Acceptance Criteria

### AC1 — Table `daily_prediction_runs`

La table `daily_prediction_runs` est créée avec :
- `id` PK autoincrement
- `user_id` FK → `users.id`, NOT NULL, indexé
- `local_date` DATE NOT NULL
- `timezone` VARCHAR(64) NOT NULL — IANA timezone string
- `reference_version_id` FK → `reference_versions.id`, NOT NULL
- `ruleset_id` FK → `prediction_rulesets.id`, NOT NULL
- `input_hash` VARCHAR(64) nullable — hash SHA256 des inputs (thème natal + params)
- `computed_at` DATETIME WITH TIMEZONE NOT NULL DEFAULT utcnow
- `overall_summary` TEXT nullable — résumé en prose du run
- `overall_tone` VARCHAR(16) nullable — valeurs : `positive`, `mixed`, `challenging`
- `main_turning_point_at` DATETIME WITH TIMEZONE nullable — timestamp du turning point principal
- Contrainte UNIQUE `(user_id, local_date, reference_version_id, ruleset_id)`
- Index composite sur `(user_id, local_date)` pour les requêtes fréquentes

### AC2 — Table `daily_prediction_category_scores`

La table `daily_prediction_category_scores` est créée avec :
- `id` PK autoincrement
- `run_id` FK → `daily_prediction_runs.id`, NOT NULL, indexé (avec CASCADE DELETE)
- `category_id` FK → `prediction_categories.id`, NOT NULL
- `raw_score` FLOAT nullable — score avant normalisation
- `normalized_score` FLOAT nullable — score normalisé (0–100)
- `note_20` INTEGER nullable — note sur 20 (1–20)
- `power` FLOAT nullable — amplitude/intensité du signal
- `volatility` FLOAT nullable — variance sur la journée
- `rank` INTEGER nullable — classement de la catégorie pour ce run (1 = la plus forte)
- `summary` TEXT nullable — résumé en prose de la catégorie
- Contrainte UNIQUE `(run_id, category_id)`

### AC3 — Table `daily_prediction_turning_points`

La table `daily_prediction_turning_points` est créée avec :
- `id` PK autoincrement
- `run_id` FK → `daily_prediction_runs.id`, NOT NULL, indexé (avec CASCADE DELETE)
- `occurred_at_local` DATETIME nullable — heure locale du point de bascule
- `event_type_id` FK → `ruleset_event_types.id`, nullable
- `severity` FLOAT nullable — score de sévérité (0–1)
- `driver_json` TEXT nullable — JSON décrivant les facteurs astrologiques déclencheurs
- `summary` TEXT nullable — description lisible du turning point

### AC4 — Table `daily_prediction_time_blocks`

La table `daily_prediction_time_blocks` est créée avec :
- `id` PK autoincrement
- `run_id` FK → `daily_prediction_runs.id`, NOT NULL, indexé (avec CASCADE DELETE)
- `block_index` INTEGER NOT NULL — index du bloc dans la journée (0, 1, 2…)
- `start_at_local` DATETIME nullable — début du bloc en heure locale
- `end_at_local` DATETIME nullable — fin du bloc en heure locale
- `tone_code` VARCHAR(16) nullable — valeurs : `positive`, `mixed`, `challenging`, `neutral`
- `dominant_categories_json` TEXT nullable — JSON liste des catégories dominantes du bloc
- `summary` TEXT nullable
- Contrainte UNIQUE `(run_id, block_index)`

### AC5 — Migration Alembic idempotente

Une migration Alembic unique (numéro de séquence `0034`) est créée. Elle crée les 4 tables dans cet ordre :
1. `daily_prediction_runs` (dépend de `users`, `reference_versions`, `prediction_rulesets`)
2. `daily_prediction_category_scores` (dépend de `daily_prediction_runs`, `prediction_categories`)
3. `daily_prediction_turning_points` (dépend de `daily_prediction_runs`, `ruleset_event_types`)
4. `daily_prediction_time_blocks` (dépend de `daily_prediction_runs`)

Le `downgrade()` supprime dans l'ordre inverse. Les CASCADE DELETE sur les tables filles garantissent la suppression en cascade lors du `downgrade`.

### AC6 — Modèles SQLAlchemy

Les 4 modèles sont créés dans `backend/app/infra/db/models/daily_prediction.py` :
- `DailyPredictionRunModel`
- `DailyPredictionCategoryScoreModel`
- `DailyPredictionTurningPointModel`
- `DailyPredictionTimeBlockModel`

Chaque modèle a les `__table_args__` avec contraintes UNIQUE et les `relationship()` vers les entités parentes.

### AC7 — Repository basique `DailyPredictionRepository`

Un repository minimal est créé dans `backend/app/infra/db/repositories/daily_prediction_repository.py` avec les méthodes CRUD de base :

#### `create_run(user_id, local_date, timezone, reference_version_id, ruleset_id, ...) -> DailyPredictionRunModel`

Crée un nouveau run. Lève une exception si la contrainte UNIQUE est violée (le run existe déjà).

#### `get_run(user_id, local_date, reference_version_id, ruleset_id) -> DailyPredictionRunModel | None`

Retourne le run existant, ou `None`.

#### `get_or_create_run(..., input_hash: str | None = None) -> tuple[DailyPredictionRunModel, bool]`

Retourne `(run, created)` selon la politique suivante :

- **Run inexistant** → crée et retourne `(run, True)`.
- **Run existant, même `input_hash`** → retourne `(run, False)` sans toucher aux données filles.
- **Run existant, `input_hash` différent** → supprime les enregistrements filles (`category_scores`, `turning_points`, `time_blocks`) via DELETE, met à jour `input_hash` et `computed_at` sur le run parent, retourne `(run, False)` avec `run.needs_recompute = True` (flag transient Python, pas en DB). Le caller est responsable de re-seeder les données filles.
- **`input_hash` is None** → comparaison ignorée, comportement identique à "même hash".

Cette politique garantit qu'un changement de thème natal ou de ruleset invalide les prédictions mises en cache sans laisser de données obsolètes orphelines.

#### `upsert_category_scores(run_id, scores: list[dict]) -> None`

Insère ou met à jour les scores de catégories pour un run.

#### `upsert_turning_points(run_id, turning_points: list[dict]) -> None`

Insère les turning points (remplace les existants pour ce run).

#### `upsert_time_blocks(run_id, blocks: list[dict]) -> None`

Insère les blocs horaires (remplace les existants pour ce run).

#### `get_full_run(run_id) -> dict`

Retourne le run complet avec ses scores, turning points et blocs horaires, sérialisé en dict.

#### `get_user_history(user_id, from_date, to_date) -> list[DailyPredictionRunModel]`

Retourne les runs d'un utilisateur sur une plage de dates.

### AC8 — Aucun service ni API dans cette story

Cette story ne crée aucun service FastAPI, aucun router, aucun schéma Pydantic exposé en API. Les tables et le repository sont des fondations pour le sprint moteur de calcul (Epic 33+).

### AC9 — Tests

Un test d'intégration vérifie :
- Les 4 tables existent après migration
- `create_run()` crée un run
- `get_or_create_run()` retourne `created=False` au second appel
- La contrainte UNIQUE sur `daily_prediction_category_scores` est active (doublon `run_id, category_id` → IntegrityError)
- `upsert_category_scores()` fonctionne en update (pas de doublon)
- `upsert_turning_points()` supprime et recrée les turning points
- `get_full_run()` retourne toutes les données

## Tasks / Subtasks

### T1 — Migration Alembic (AC5)

- [x] Créer `backend/migrations/versions/{date}_0034_migration_c_daily_prediction_tables.py`
  - [x] Créer `daily_prediction_runs` avec index composite `(user_id, local_date)` et UNIQUE `(user_id, local_date, reference_version_id, ruleset_id)`
  - [x] Créer `daily_prediction_category_scores` avec UNIQUE `(run_id, category_id)` et CASCADE DELETE
  - [x] Créer `daily_prediction_turning_points` avec CASCADE DELETE
  - [x] Créer `daily_prediction_time_blocks` avec UNIQUE `(run_id, block_index)` et CASCADE DELETE
  - [x] `downgrade()` dans l'ordre inverse

### T2 — Modèles SQLAlchemy (AC6)

- [x] Créer `backend/app/infra/db/models/daily_prediction.py`
  - [x] `DailyPredictionRunModel` avec tous les champs (AC1) et relationships vers les tables filles
  - [x] `DailyPredictionCategoryScoreModel` avec tous les champs (AC2) et `ondelete="CASCADE"`
  - [x] `DailyPredictionTurningPointModel` avec tous les champs (AC3) et `ondelete="CASCADE"`
  - [x] `DailyPredictionTimeBlockModel` avec tous les champs (AC4) et `ondelete="CASCADE"`
- [x] Importer ces modèles dans le point d'entrée Alembic

### T3 — Repository (AC7)

- [x] Créer `backend/app/infra/db/repositories/daily_prediction_repository.py`
  - [x] `create_run()` — INSERT + flush + return model
  - [x] `get_run()` — SELECT avec filtre 4 colonnes
  - [x] `get_or_create_run()` — implémenter la politique à 3 cas (inexistant / même hash / hash différent) décrite en AC7
  - [x] `upsert_category_scores()` — DELETE existants + INSERT (ou INSERT ON CONFLICT UPDATE)
  - [x] `upsert_turning_points()` — DELETE existants pour `run_id` + INSERT
  - [x] `upsert_time_blocks()` — DELETE existants pour `run_id` + INSERT
  - [x] `get_full_run()` — SELECT avec eager loading des relations
  - [x] `get_user_history()` — SELECT avec filtre `user_id`, `local_date BETWEEN from_date AND to_date`

### T4 — Tests (AC9)

- [x] Créer `backend/app/tests/integration/test_migration_c_daily_prediction.py`
  - [x] Test : les 4 tables existent
  - [x] Test : `create_run()` → run créé
  - [x] Test : `get_or_create_run()` × 2 avec même hash → `created=False` au 2ème appel, données filles intactes
  - [x] Test : `get_or_create_run()` avec hash différent → `created=False`, données filles supprimées
  - [x] Test : doublon `(run_id, category_id)` → IntegrityError
  - [x] Test : `upsert_category_scores()` → update sans doublon (appel double, vérification anti-doublon)
  - [x] Test : `upsert_turning_points()` → remplace les existants (appel double, vérification remplacement)
  - [x] Test : `get_full_run()` → dict complet avec scores, turning_points, time_blocks
  - [x] Test : `get_full_run()` → None pour run inexistant
  - [x] Test : `get_user_history()` → filtre par plage de dates, ordre chronologique

## Dev Notes

### Dépendances FK inter-sprints

`daily_prediction_runs` référence `prediction_rulesets.id` créé en story 31.2 (migration `0033`). La migration `0034` doit avoir `0033` en `down_revision`.

`daily_prediction_category_scores` référence `prediction_categories.id` créé en story 31.1 (migration `0032`).

`daily_prediction_turning_points` référence `ruleset_event_types.id` créé en story 31.2 (migration `0033`).

### Pattern CASCADE DELETE dans SQLAlchemy + Alembic

```python
# Dans la migration Alembic :
op.create_table(
    "daily_prediction_category_scores",
    sa.Column("run_id", sa.Integer(),
              sa.ForeignKey("daily_prediction_runs.id", ondelete="CASCADE"),
              nullable=False),
    ...
)

# Dans le modèle SQLAlchemy :
class DailyPredictionCategoryScoreModel(Base):
    run_id: Mapped[int] = mapped_column(
        ForeignKey("daily_prediction_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
```

### Pattern `upsert_category_scores()`

Approche simple : DELETE + INSERT dans la même transaction :
```python
def upsert_category_scores(self, run_id: int, scores: list[dict]) -> None:
    self.db.execute(
        delete(DailyPredictionCategoryScoreModel).where(
            DailyPredictionCategoryScoreModel.run_id == run_id
        )
    )
    self.db.add_all([
        DailyPredictionCategoryScoreModel(run_id=run_id, **score)
        for score in scores
    ])
    self.db.flush()
```

Alternativement, utiliser `INSERT ... ON CONFLICT DO UPDATE` (SQLite/PostgreSQL) si les performances l'exigent.

### Sérialisation dans `get_full_run()`

```python
def get_full_run(self, run_id: int) -> dict:
    run = self.db.scalar(
        select(DailyPredictionRunModel)
        .options(
            selectinload(DailyPredictionRunModel.category_scores),
            selectinload(DailyPredictionRunModel.turning_points),
            selectinload(DailyPredictionRunModel.time_blocks),
        )
        .where(DailyPredictionRunModel.id == run_id)
    )
    if run is None:
        return {}
    return {
        "id": run.id,
        "local_date": run.local_date.isoformat(),
        "overall_tone": run.overall_tone,
        "overall_summary": run.overall_summary,
        "category_scores": [
            {
                "category_id": s.category_id,
                "note_20": s.note_20,
                "normalized_score": s.normalized_score,
                "rank": s.rank,
                "summary": s.summary,
            }
            for s in run.category_scores
        ],
        "turning_points": [
            {
                "occurred_at_local": tp.occurred_at_local,
                "severity": tp.severity,
                "summary": tp.summary,
            }
            for tp in run.turning_points
        ],
        "time_blocks": [
            {
                "block_index": b.block_index,
                "tone_code": b.tone_code,
                "summary": b.summary,
            }
            for b in sorted(run.time_blocks, key=lambda x: x.block_index)
        ],
    }
```

### Numéro de migration

Pattern : `{YYYYMMDD}_0034_migration_c_daily_prediction_tables.py`

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/migrations/versions/{date}_0034_migration_c_daily_prediction_tables.py` | Créer |
| `backend/app/infra/db/models/daily_prediction.py` | Créer |
| `backend/app/infra/db/base.py` (ou équivalent) | Modifier — importer les nouveaux modèles |
| `backend/app/infra/db/repositories/daily_prediction_repository.py` | Créer |
| `backend/app/tests/integration/test_migration_c_daily_prediction.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/models/prediction_ruleset.py`
- Tout fichier frontend, API router, ou service applicatif

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Completion Notes List

- Création de la migration Alembic 0034 avec les 4 tables de persistance quotidienne.
- Implémentation des modèles SQLAlchemy avec cascades de suppression (CASCADE DELETE).
- Développement du repository `DailyPredictionRepository` avec gestion intelligente du cache (invalidation par `input_hash`).
- Couverture de tests d'intégration complète (migration, repository, contraintes).
- Validation ruff et formatage du code.

### File List

- `backend/migrations/versions/20260307_0034_migration_c_daily_prediction_tables.py`
- `backend/app/infra/db/models/daily_prediction.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/repositories/daily_prediction_repository.py`
- `backend/app/tests/integration/test_migration_c_daily_prediction.py`
