# Story 31.2 : Migration B — Ruleset, paramètres du moteur et table de calibrations percentiles

Status: done

## Story

As a développeur du moteur de prédiction quotidienne,
I want que la base de données dispose d'une table de ruleset versionnée, de ses paramètres clé/valeur, des types d'événements astrologiques et d'une table de calibrations percentiles par catégorie,
so that tous les réglages du moteur de scoring (orbes actifs, multiplicateurs, seuils, formule de normalisation) sont lisibles en DB et modifiables sans redéploiement.

## Contexte métier

Un moteur de prédiction ne se réduit pas à ses données symboliques : il dépend aussi de ses paramètres de calcul (orbe d'activation, multiplicateur applying/exact/separating, taille du pas temporel, seuil de bascule). Ces paramètres constituent une version de règles (`prediction_ruleset`) distincte de la version du référentiel symbolique (`reference_version`). Cette séparation permet de changer la méthode de calcul sans toucher à la sémantique astrologique.

Cette story couvre **Migration B** : création des tables `prediction_rulesets`, `ruleset_event_types`, `ruleset_parameters` et `category_calibrations`. Ces tables sont indépendantes des tables créées en Migration A, mais préparent le terrain pour le seed (story 31.3).

## Acceptance Criteria

### AC1 — Table `prediction_rulesets`

La table `prediction_rulesets` est créée avec :
- `id` PK autoincrement
- `version` VARCHAR(32) UNIQUE NOT NULL
- `reference_version_id` FK → `reference_versions.id`, NOT NULL, indexé
- `zodiac_type` VARCHAR(16) NOT NULL DEFAULT `'tropical'`
- `coordinate_mode` VARCHAR(16) NOT NULL DEFAULT `'geocentric'`
- `house_system` VARCHAR(16) NOT NULL DEFAULT `'placidus'`
- `time_step_minutes` INTEGER NOT NULL DEFAULT 30
- `description` TEXT nullable
- `is_locked` BOOLEAN NOT NULL DEFAULT FALSE
- `created_at` DATETIME WITH TIMEZONE NOT NULL DEFAULT utcnow

### AC2 — Table `ruleset_event_types`

La table `ruleset_event_types` est créée avec :
- `id` PK autoincrement
- `ruleset_id` FK → `prediction_rulesets.id`, NOT NULL, indexé
- `code` VARCHAR(64) NOT NULL
- `name` VARCHAR(128) NOT NULL
- `event_group` VARCHAR(64) nullable
- `priority` INTEGER NOT NULL DEFAULT 0
- `base_weight` FLOAT NOT NULL DEFAULT 1.0
- `description` TEXT nullable
- Contrainte UNIQUE `(ruleset_id, code)`

### AC3 — Table `ruleset_parameters`

La table `ruleset_parameters` est créée avec :
- `id` PK autoincrement
- `ruleset_id` FK → `prediction_rulesets.id`, NOT NULL, indexé
- `param_key` VARCHAR(64) NOT NULL
- `param_value` TEXT NOT NULL
- `data_type` VARCHAR(16) NOT NULL DEFAULT `'string'` — valeurs : `string`, `float`, `int`, `bool`, `json`
- Contrainte UNIQUE `(ruleset_id, param_key)`

### AC4 — Table `category_calibrations`

La table `category_calibrations` est créée avec :
- `id` PK autoincrement
- `ruleset_id` FK → `prediction_rulesets.id`, NOT NULL
- `category_id` FK → `prediction_categories.id`, NOT NULL (table créée en story 31.1)
- `p05` FLOAT nullable — percentile 5
- `p25` FLOAT nullable — percentile 25
- `p50` FLOAT nullable — percentile 50 (médiane)
- `p75` FLOAT nullable — percentile 75
- `p95` FLOAT nullable — percentile 95
- `sample_size` INTEGER nullable
- `valid_from` DATE NOT NULL
- `valid_to` DATE nullable
- Contrainte UNIQUE `(ruleset_id, category_id, valid_from)`

### AC5 — Migration Alembic idempotente

Une migration Alembic unique (numéro de séquence `0033`) est créée. Elle crée les 4 tables dans cet ordre :
1. `prediction_rulesets` (dépend de `reference_versions`)
2. `ruleset_event_types` (dépend de `prediction_rulesets`)
3. `ruleset_parameters` (dépend de `prediction_rulesets`)
4. `category_calibrations` (dépend de `prediction_rulesets`, `prediction_categories`)

Le `downgrade()` supprime dans l'ordre inverse.

### AC6 — Modèles SQLAlchemy

Les 4 modèles SQLAlchemy sont créés dans `backend/app/infra/db/models/prediction_ruleset.py` :
- `PredictionRulesetModel`
- `RulesetEventTypeModel`
- `RulesetParameterModel`
- `CategoryCalibrationModel`

Chaque modèle a les bons `__table_args__` avec contraintes UNIQUE et les `relationship()` vers les entités parentes.

### AC7 — Aucun seed dans cette story

Les tables sont créées vides. Le seed (création du ruleset `1.0.0`, paramètres, event types) est effectué en story 31.3.

### AC8 — Tests de migration

Un test d'intégration vérifie que :
- Les 4 tables existent après migration
- La contrainte UNIQUE `(ruleset_id, param_key)` est active
- La contrainte UNIQUE `(ruleset_id, code)` sur `ruleset_event_types` est active
- La contrainte UNIQUE `(ruleset_id, category_id, valid_from)` sur `category_calibrations` est active

## Tasks / Subtasks

### T1 — Migration Alembic (AC5)

- [x] Créer `backend/migrations/versions/20260307_0033_migration_b_prediction_ruleset_tables.py`
  - [x] Créer `prediction_rulesets` : colonnes + UNIQUE version
  - [x] Créer `ruleset_event_types` : colonnes + UNIQUE `(ruleset_id, code)`
  - [x] Créer `ruleset_parameters` : colonnes + UNIQUE `(ruleset_id, param_key)`
  - [x] Créer `category_calibrations` : colonnes + UNIQUE `(ruleset_id, category_id, valid_from)`
  - [x] `downgrade()` dans l'ordre inverse

### T2 — Modèles SQLAlchemy (AC6)

- [x] Créer `backend/app/infra/db/models/prediction_ruleset.py`
  - [x] `PredictionRulesetModel` avec tous les champs (AC1)
  - [x] `RulesetEventTypeModel` avec tous les champs (AC2)
  - [x] `RulesetParameterModel` avec tous les champs (AC3)
  - [x] `CategoryCalibrationModel` avec tous les champs (AC4) — FK vers `prediction_categories`
- [x] Importer ces modèles dans le point d'entrée Alembic

### T3 — Tests (AC8)

- [x] Créer `backend/app/tests/integration/test_migration_b_ruleset_tables.py`
  - [x] Test : les 4 tables existent
  - [x] Test : doublon dans `ruleset_parameters` → IntegrityError
  - [x] Test : doublon dans `ruleset_event_types` → IntegrityError
  - [x] Test : doublon dans `category_calibrations` → IntegrityError

## Dev Notes

### Paramètres clés attendus dans `ruleset_parameters` (seed story 31.3)

Ces clés seront créées lors du seed (pas dans cette story, mais à garder en tête pour la modélisation) :

| param_key | data_type | valeur typique |
|-----------|-----------|----------------|
| `orb_multiplier_applying` | float | `1.2` |
| `orb_multiplier_exact` | float | `1.5` |
| `orb_multiplier_separating` | float | `0.8` |
| `turning_point_threshold` | float | `0.7` |
| `score_clamp_min` | float | `0.0` |
| `score_clamp_max` | float | `100.0` |
| `top_turning_points_count` | int | `3` |
| `normalization_method` | string | `'percentile'` |

> `time_step_minutes` est exclu de cette table car il est déjà une colonne canonique de `prediction_rulesets`. Ne pas dupliquer ici.

### Event types attendus dans `ruleset_event_types` (seed story 31.3)

| code | event_group | base_weight |
|------|-------------|-------------|
| `aspect_exact_to_angle` | `aspect` | `2.0` |
| `aspect_exact_to_luminary` | `aspect` | `1.8` |
| `aspect_exact_to_personal` | `aspect` | `1.5` |
| `aspect_enter_orb` | `aspect` | `1.0` |
| `aspect_exit_orb` | `aspect` | `0.5` |
| `moon_sign_ingress` | `ingress` | `1.5` |
| `asc_sign_change` | `ingress` | `2.0` |
| `planetary_hour_change` | `timing` | `0.8` |

### Dépendance FK vers `prediction_categories`

`category_calibrations.category_id` référence `prediction_categories.id`. Cette table est créée en story 31.1 (migration 0032). La migration 0033 doit avoir `0032` en dépendance Alembic (`down_revision`).

### Numéro de migration

La migration A utilise `0032`. La migration B utilise `0033`.

Pattern de nommage : `{YYYYMMDD}_0033_migration_b_prediction_ruleset_tables.py`

### Fichiers à créer / modifier

| Fichier | Action |
|---------|--------|
| `backend/migrations/versions/{date}_0033_migration_b_prediction_ruleset_tables.py` | Créer |
| `backend/app/infra/db/models/prediction_ruleset.py` | Créer |
| `backend/app/infra/db/base.py` (ou équivalent) | Modifier — importer les nouveaux modèles |
| `backend/app/tests/integration/test_migration_b_ruleset_tables.py` | Créer |

### Fichiers à NE PAS toucher

- `backend/app/infra/db/models/reference.py` — pas de changement
- `backend/app/infra/db/models/prediction_reference.py` — créé en story 31.1, pas de modification
- Tout fichier frontend

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Completion Notes List

- Created migration `0033` for Migration B tables.
- Implemented SQLAlchemy models in `prediction_ruleset.py`.
- Registered models in `app/infra/db/models/__init__.py`.
- Added integration tests verifying table creation and unique constraints.
- Verified both new and previous migration tests pass.
- Cleaned up linting issues with `ruff`.

### File List

- `backend/migrations/versions/20260307_0033_migration_b_prediction_ruleset_tables.py`
- `backend/app/infra/db/models/prediction_ruleset.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/base.py`
- `backend/app/tests/integration/test_migration_b_ruleset_tables.py`
