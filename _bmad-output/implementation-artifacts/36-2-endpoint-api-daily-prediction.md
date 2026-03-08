# Story 36.2 : Endpoint API GET /v1/predictions/daily

Status: done

## Story

As a développeur frontend ou consommateur API,
I want un endpoint REST authentifié `GET /v1/predictions/daily` qui retourne la prédiction astrologique complète du jour pour l'utilisateur connecté,
so that l'interface utilisateur peut afficher toutes les sections de la prédiction (résumé, catégories, timeline, points de bascule) à partir d'un seul appel API structuré.

## Acceptance Criteria

### AC1 — Structure de réponse toujours complète

L'endpoint retourne toujours les cinq blocs (`meta`, `summary`, `categories`, `timeline`, `turning_points`), même si certaines sous-sections sont vides (listes vides `[]`, champs `null`).

### AC2 — Catégories triées par rank ascendant

Le tableau `categories[]` est trié par `rank` ascendant (rang 1 en premier).

### AC3 — Timeline triée chronologiquement

Le tableau `timeline[]` est trié par `start_local` croissant.

### AC4 — Heures retournées en local ISO

Tous les champs d'heure (`computed_at`, `start_local`, `end_local`, `occurred_at_local`) sont des chaînes ISO 8601 représentant l'heure locale (sans conversion UTC forcée dans la réponse).

### AC5 — Codes d'erreur métier explicites

- `404` avec `{"code": "natal_missing", "message": "..."}` si le natal est absent.
- `422` avec le code d'erreur métier approprié pour tout autre `DailyPredictionServiceError` (timezone manquante, localisation invalide, etc.).

### AC6 — Query param `date` optionnel

Le paramètre `?date=YYYY-MM-DD` est optionnel. Quand absent, la date utilisée est "aujourd'hui" dans le fuseau horaire de l'utilisateur (délégué au `DailyPredictionService`).

### AC7 — `was_reused` dans `meta`

Le champ `meta.was_reused` indique si le run retourné était déjà calculé (`True`) ou vient d'être calculé (`False`).

### AC8 — Délégation au `DailyPredictionService` en mode `compute_if_missing`

L'endpoint appelle `DailyPredictionService.get_or_compute()` avec `mode=ComputeMode.compute_if_missing`. Il ne contient aucune logique de calcul astrologique.

## Tasks / Subtasks

### T1 — Créer le router `predictions.py` avec `GET /v1/predictions/daily` (AC1–AC8)

- [x] Créer `backend/app/api/v1/routers/predictions.py`
  - [x] Déclarer `router = APIRouter(prefix="/v1/predictions", tags=["predictions"])`
  - [x] Schémas Pydantic de réponse :
    - [x] `DailyPredictionMeta`
    - [x] `DailyPredictionCategory`
    - [x] `DailyPredictionTurningPoint`
    - [x] `DailyPredictionTimeBlock`
    - [x] `DailyPredictionSummary`
    - [x] `DailyPredictionResponse`
  - [x] Handler `GET /daily` :
    - [x] Paramètre `date` optionnel
    - [x] Parser la date si fournie
    - [x] Injecter `DailyPredictionService` via `Depends()` et appeler `get_or_compute()`
    - [x] Mapper `ServiceResult` → `DailyPredictionResponse`
    - [x] Gestion des erreurs `DailyPredictionServiceError` → `HTTPException`

### T2 — Enregistrer le router (AC8)

- [x] Ajouter dans `backend/app/api/v1/routers/__init__.py`
- [x] Ajouter dans `backend/app/main.py`

### T3 — Tests d'intégration (AC1–AC8)

- [x] Créer `backend/app/tests/integration/test_daily_prediction_api.py`
  - [x] `test_daily_prediction_200_nominal`
  - [x] `test_daily_prediction_404_no_natal`
  - [x] `test_daily_prediction_422_for_non_natal_service_error`
  - [x] `test_daily_prediction_categories_sorted_by_rank`
  - [x] `test_daily_prediction_timeline_chronological`
  - [x] `test_daily_prediction_date_param`
  - [x] `test_daily_prediction_returns_500_on_malformed_json_payload`
  - [x] `test_daily_prediction_meta_uses_run_reference_version_and_house_system_effective`
  - [x] `test_daily_prediction_401_unauthenticated`

## Dev Notes

### Structure payload V1

```
meta: { date_local, timezone, computed_at, reference_version, ruleset_version, was_reused, house_system_effective }
summary: { overall_tone, overall_summary, top_categories, bottom_categories, best_window, main_turning_point }
categories[]: { code, note_20, raw_score, power, volatility, rank, summary }
timeline[]: { start_local, end_local, tone_code, dominant_categories, summary, turning_point: bool }
turning_points[]: { occurred_at_local, severity, summary, drivers: list }
```

### Dev Agent Record

### Agent Model Used

gemini-2.0-flash-thinking-exp

### Debug Log References

- Fixed `AttributeError: 'Settings' object has no attribute 'active_ruleset_version'` by using `ruleset_version`.
- Fixed linting issues (line too long, unused imports) in both router and test files.
- Fixed post-review issues on turning-point mapping, JSON payload robustness, DI, and metadata fidelity.

### Completion Notes List

- Implemented `GET /v1/predictions/daily` endpoint.
- Structured response according to ACs with 5 distinct blocks.
- Guaranteed sorting for categories (rank) and timeline (chronological).
- Implemented robust mapping from `ServiceResult` and `full_run` DB data.
- Added coverage for non-natal `422`, malformed persisted JSON, turning-point overlap, and metadata fidelity.
- Persisted `house_system_effective` on daily prediction runs so reused runs return the effective house system.
- Verified fixes with `ruff check .` and targeted backend test suites in the venv.

### File List

- `backend/app/api/v1/routers/predictions.py`
- `backend/app/api/v1/routers/__init__.py` (modified)
- `backend/app/main.py` (modified)
- `backend/app/tests/integration/test_daily_prediction_api.py`
- `backend/app/infra/db/models/daily_prediction.py`
- `backend/app/infra/db/repositories/daily_prediction_repository.py`
- `backend/app/prediction/persistence_service.py`
- `backend/app/tests/integration/test_prediction_persistence.py`
- `backend/app/tests/integration/test_migration_c_daily_prediction.py`
- `backend/migrations/versions/20260308_0038_add_house_system_effective_to_daily_prediction_runs.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)

## Change Log

- 2026-03-08: Story créée pour l'Epic 36 — Productisation V1.
- 2026-03-08: Implémentation de l'endpoint API et des tests d'intégration.
- 2026-03-08: Correctifs post-review appliqués et validés, story passée à done.
