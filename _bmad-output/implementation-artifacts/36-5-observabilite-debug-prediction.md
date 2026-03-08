# Story 36.5 : Observabilité interne "prediction debug view"

Status: done

## Story

As a développeur backend ou administrateur technique,
I want un endpoint admin `GET /v1/predictions/daily/debug` qui expose les détails internes d'un run de prédiction (contributeurs, drivers pivots, versions, hash),
so that je peux inspecter les entrailles d'un calcul sans déclencher de recalcul et sans modifier les données existantes.

## Acceptance Criteria

### AC1 — Contributeurs par catégorie visibles

La réponse JSON inclut, pour chaque catégorie, la liste des contributeurs parsée depuis le champ `contributors_json` stocké en DB (`DailyPredictionCategoryScoreModel`). Si `contributors_json` est null ou absent, retourner une liste vide `[]`.

### AC2 — Drivers par pivot visibles

La réponse JSON inclut, pour chaque turning point, la liste des drivers parsée depuis le champ `driver_json` stocké en DB (`DailyPredictionTurningPointModel`). Si `driver_json` est null ou absent, retourner `[]`.

### AC3 — Métadonnées de versions exposées

La réponse inclut `input_hash`, `reference_version_id`, `ruleset_id` et, si disponible, `is_provisional_calibration` depuis le run complet.

### AC4 — Mode read-only strict

Aucun recalcul n'est déclenché. Le service est appelé exclusivement en mode `read_only`. Si aucun run n'existe pour le jour demandé, retourner 404 immédiatement.

### AC5 — Accès admin uniquement, `target_user_id` obligatoire

L'endpoint vérifie `current_user.role == "admin"` avant tout traitement. Retourner 403 avec `{"code": "forbidden", "message": "Admin only"}` pour tout autre rôle.

Le query param `target_user_id: int` est **obligatoire** : un admin inspecte la prédiction d'un utilisateur cible, pas la sienne. Sans ce param, l'endpoint est peu utile en support réel.

### AC6 — 404 si run absent

Si le service retourne `None` (aucun run persisté pour ce jour), l'endpoint retourne HTTP 404 avec `{"code": "not_found", "message": "Aucun run trouvé pour ce jour"}`.

## Tasks / Subtasks

### T1 — Ajouter `GET /v1/predictions/daily/debug` dans `predictions.py` (AC1–AC6)

- [x] Déclarer `DailyPredictionDebugContributor` (utilisé via `list[dict[str, Any]]`)
- [x] Déclarer `DailyPredictionDebugCategory` (Pydantic) :
  - Champs standards : `code`, `note_20`, `raw_score`, `power`, `volatility`, `rank`
  - Champ enrichi : `contributors: list[dict[str, Any]]`
- [x] Déclarer `DailyPredictionDebugDriver` (utilisé via `list[dict[str, Any]]`)
- [x] Déclarer `DailyPredictionDebugTurningPoint` (Pydantic) :
  - Champs standards : `occurred_at_local`, `severity`, `summary`
  - Champ enrichi : `drivers: list[dict[str, Any]]`
- [x] Déclarer `DailyPredictionDebugResponse` (Pydantic) :
  - `meta`: réutiliser le schéma de réponse standard
  - `input_hash: str | None`
  - `reference_version_id: int`
  - `ruleset_id: int`
  - `is_provisional_calibration: bool | None`
  - `categories: list[DailyPredictionDebugCategory]`
  - `turning_points: list[DailyPredictionDebugTurningPoint]`
- [x] Ajouter `target_user_id: int = Query(...)` comme query param **obligatoire**
- [x] Implémenter le handler `debug_daily_prediction()` :
  - [x] Vérifier `current_user.role != "admin"` → `HTTPException(403, ...)`
  - [x] Utiliser `target_user_id`
  - [x] Appeler `DailyPredictionService.get_or_compute(user_id=target_user_id, ..., mode=ComputeMode.read_only)`
  - [x] Si `None` → `HTTPException(404, ...)`
  - [x] Appeler `DailyPredictionRepository.get_full_run(run.id)`
  - [x] Parser `contributors_json` et `driver_json` via `_load_json_list`
  - [x] Construire et retourner `DailyPredictionDebugResponse`

### T2 — Tests dans `test_daily_prediction_api.py` (AC1–AC6)

- [x] `test_debug_200_admin` : utilisateur admin + run existant → 200 avec structure complète
- [x] `test_debug_403_non_admin` : utilisateur non-admin → 403 avec `code: "forbidden"`
- [x] `test_debug_404_no_run` : admin mais aucun run persisté pour ce jour → 404
- [x] `test_debug_contributors_present` (inclus dans nominal)
- [x] `test_debug_no_recompute` : vérifier que le service est bien appelé avec `mode=ComputeMode.read_only`
- [x] `test_debug_422_when_target_user_id_missing` : paramètre obligatoire validé par FastAPI
- [x] `test_debug_422_when_target_profile_missing` : erreur service convertie en réponse HTTP contrôlée
- [x] `test_debug_returns_empty_lists_when_json_fields_are_absent` : fallback `[]` pour `contributors_json` / `driver_json` absents

### T3 — Alignement persistence / repository / migration après review (AC1, AC3)

- [x] Ajouter la colonne `is_provisional_calibration` sur `DailyPredictionRunModel`
- [x] Persister `is_provisional_calibration` depuis `engine_output.run_metadata`
- [x] Exposer `contributors_json` dans `DailyPredictionRepository.get_full_run()`
- [x] Exposer `is_provisional_calibration` dans `DailyPredictionRepository.get_full_run()`
- [x] Ajouter une migration Alembic idempotente `20260308_0039_add_is_provisional_calibration_to_daily_prediction_runs.py`
- [x] Ajouter les tests d'intégration de migration et de persistance associés

## Dev Notes

### Project Structure Notes

- Fichier modifié : `backend/app/api/v1/routers/predictions.py`
- Fichier de tests modifié : `backend/app/tests/integration/test_daily_prediction_api.py`
- Fichier modifié : `backend/app/infra/db/models/daily_prediction.py`
- Fichier modifié : `backend/app/infra/db/repositories/daily_prediction_repository.py`
- Fichier modifié : `backend/app/prediction/persistence_service.py`
- Fichier de tests modifié : `backend/app/tests/integration/test_engine_persistence_e2e.py`
- Fichier de tests modifié : `backend/app/tests/integration/test_migration_c_daily_prediction.py`
- Fichier de tests ajouté : `backend/app/tests/integration/test_migration_0039_add_is_provisional_calibration.py`
- Fichier ajouté : `backend/migrations/versions/20260308_0039_add_is_provisional_calibration_to_daily_prediction_runs.py`

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-thinking-exp

### Debug Log References

- Fixed `TypeError: string indices must be integers, not 'str'` in tests by ensuring 404 responses return a dict with `detail` object.
- Verified `mode=ComputeMode.read_only` is correctly passed to the service.
- Fixed post-review gaps where `contributors_json` and `is_provisional_calibration` were not actually exposed by the repository / persistence layer.
- Added HTTP error translation for `DailyPredictionServiceError` on the debug endpoint.
- Verified lint and targeted integration suite after corrections.
- Targeted checks pass: `ruff check` OK, `pytest` OK (36 tests).

### Completion Notes List

- Implemented `GET /v1/predictions/daily/debug` restricted to admin role.
- Mandatory `target_user_id` parameter implemented for admin inspection.
- Full exposure of internal prediction details: contributors (JSON), drivers (JSON), input hash, and version IDs.
- Guaranteed read-only mode (no recompute) as per AC4.
- Persisted and exposed `is_provisional_calibration` from `daily_prediction_runs`.
- Aligned `DailyPredictionRepository.get_full_run()` with the debug contract by returning `contributors_json`.
- Hardened the endpoint by converting `DailyPredictionServiceError` into controlled HTTP responses.
- Added migration coverage and persistence checks for the new run metadata flag.
- Expanded the debug endpoint integration coverage to cover required query params, service errors, and empty JSON fallbacks.

### File List

- `backend/app/api/v1/routers/predictions.py`
- `backend/app/infra/db/models/daily_prediction.py`
- `backend/app/infra/db/repositories/daily_prediction_repository.py`
- `backend/app/prediction/persistence_service.py`
- `backend/app/tests/integration/test_daily_prediction_api.py`
- `backend/app/tests/integration/test_engine_persistence_e2e.py`
- `backend/app/tests/integration/test_migration_c_daily_prediction.py`
- `backend/app/tests/integration/test_migration_0039_add_is_provisional_calibration.py`
- `backend/migrations/versions/20260308_0039_add_is_provisional_calibration_to_daily_prediction_runs.py`

## Change Log

- 2026-03-08: Story créée pour l'Epic 36 — Productisation V1.
- 2026-03-08: Implémentation complète de l'endpoint de debug admin et des tests associés.
- 2026-03-08: Corrections post-review sur la persistance / exposition de `contributors_json` et `is_provisional_calibration`, ajout d'une migration Alembic et renforcement des tests.
