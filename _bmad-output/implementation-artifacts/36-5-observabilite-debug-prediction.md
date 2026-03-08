# Story 36.5 : Observabilité interne "prediction debug view"

Status: ready-for-dev

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

- [ ] Déclarer `DailyPredictionDebugContributor` (Pydantic) avec les champs extraits du JSON contributeurs
- [ ] Déclarer `DailyPredictionDebugCategory` (Pydantic) :
  - Champs standards : `code`, `note_20`, `raw_score`, `power`, `volatility`, `rank`
  - Champ enrichi : `contributors: list[Any]`
- [ ] Déclarer `DailyPredictionDebugDriver` (Pydantic) avec les champs extraits du JSON drivers
- [ ] Déclarer `DailyPredictionDebugTurningPoint` (Pydantic) :
  - Champs standards : `occurred_at_local`, `severity`, `summary`
  - Champ enrichi : `drivers: list[Any]`
- [ ] Déclarer `DailyPredictionDebugResponse` (Pydantic) :
  - `meta`: réutiliser le schéma de réponse standard ou en créer un dédié
  - `input_hash: str | None`
  - `reference_version_id: int`
  - `ruleset_id: int`
  - `is_provisional_calibration: bool | None`
  - `categories: list[DailyPredictionDebugCategory]`
  - `turning_points: list[DailyPredictionDebugTurningPoint]`
- [ ] Ajouter `target_user_id: int = Query(...)` comme query param **obligatoire** (inspection d'un autre utilisateur par l'admin)
- [ ] Implémenter le handler `debug_daily_prediction()` :
  - Vérifier `current_user.role != "admin"` → `HTTPException(403, ...)`
  - Utiliser `target_user_id` (pas `current_user.id`) pour toutes les opérations
  - Appeler `DailyPredictionService.get_or_compute(user_id=target_user_id, ..., mode=ComputeMode.read_only)`
  - Si `None` → `HTTPException(404, ...)`
  - Appeler `DailyPredictionRepository.get_full_run(run.id)` pour charger catégories et pivots avec champs JSON
  - Parser `contributors_json` et `driver_json` depuis JSON string
  - Construire et retourner `DailyPredictionDebugResponse`

### T2 — Tests dans `test_daily_prediction_api.py` (AC1–AC6)

- [ ] `test_debug_200_admin` : utilisateur admin + run existant → 200 avec structure complète
- [ ] `test_debug_403_non_admin` : utilisateur non-admin → 403 avec `code: "forbidden"`
- [ ] `test_debug_404_no_run` : admin mais aucun run persisté pour ce jour → 404
- [ ] `test_debug_contributors_present` : vérifier que `categories[*].contributors` est parsé et non vide
- [ ] `test_debug_no_recompute` : vérifier que le service est bien appelé avec `mode=ComputeMode.read_only` (mock + assert_called_with)

## Dev Notes

### Parser les JSON internes

```python
import json

# Contributeurs d'un DailyPredictionCategoryScoreModel
contributors = json.loads(score.contributors_json) if score.contributors_json else []

# Drivers d'un DailyPredictionTurningPointModel
drivers = json.loads(tp.driver_json) if tp.driver_json else []
```

### Vérification rôle admin

```python
from fastapi import HTTPException

if current_user.role != "admin":
    raise HTTPException(
        status_code=403,
        detail={"code": "forbidden", "message": "Admin only"},
    )
```

### Appel service en mode read_only

```python
from app.services.daily_prediction_service import DailyPredictionService, ComputeMode

result = daily_prediction_service.get_or_compute(
    user_id=target_user_id,  # ← obligatoire : admin inspecte l'utilisateur cible, pas lui-même
    db=db,
    date_local=date_local,   # None = aujourd'hui
    mode=ComputeMode.read_only,
    ruleset_version=settings.active_ruleset_version,
)
if result is None:
    raise HTTPException(
        status_code=404,
        detail={"code": "not_found", "message": "Aucun run trouvé pour ce jour"},
    )
```

### Chargement du run complet

Le run retourné par le service peut ne pas avoir les relations chargées. Utiliser `DailyPredictionRepository.get_full_run()` pour obtenir les objets avec `category_scores` et `turning_points` :

```python
from app.infra.db.repositories.daily_prediction_repository import DailyPredictionRepository

repo = DailyPredictionRepository(db)
full_run = repo.get_full_run(result.run.id)
```

### Construire la réponse debug

```python
debug_categories = [
    DailyPredictionDebugCategory(
        code=score.category_code,
        note_20=score.note_20,
        raw_score=score.raw_score,
        power=score.power,
        volatility=score.volatility,
        rank=score.rank,
        contributors=json.loads(score.contributors_json) if score.contributors_json else [],
    )
    for score in full_run.category_scores
]

debug_turning_points = [
    DailyPredictionDebugTurningPoint(
        occurred_at_local=tp.occurred_at_local,
        severity=tp.severity,
        summary=tp.summary,
        drivers=json.loads(tp.driver_json) if tp.driver_json else [],
    )
    for tp in full_run.turning_points
]

return DailyPredictionDebugResponse(
    input_hash=full_run.input_hash,
    reference_version_id=full_run.reference_version_id,
    ruleset_id=full_run.ruleset_id,
    is_provisional_calibration=getattr(full_run, 'is_provisional_calibration', None),
    categories=debug_categories,
    turning_points=debug_turning_points,
)
```

### Route FastAPI à ajouter

```python
@router.get("/daily/debug", response_model=DailyPredictionDebugResponse)
def debug_daily_prediction(
    date: str | None = Query(default=None),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    daily_prediction_service: DailyPredictionService = Depends(get_daily_prediction_service),
) -> DailyPredictionDebugResponse:
    ...
```

Ajouter cette route **avant** la route `GET /daily` dans le fichier `predictions.py` pour éviter un conflit de routing FastAPI (le segment `debug` serait sinon interprété comme un paramètre de path).

### Project Structure Notes

- Fichier à modifier : `backend/app/api/v1/predictions.py`
- Fichier de tests à modifier : `backend/app/tests/api/test_daily_prediction_api.py`
- `DailyPredictionRepository.get_full_run()` doit exister — vérifier sa signature dans `backend/app/infra/db/repositories/daily_prediction_repository.py`
- `ComputeMode` est importé depuis `backend/app/services/daily_prediction_service.py`
- **NE PAS toucher** : le moteur, les modèles DB, le service de persistance, les autres endpoints

## References

- [Source: backend/app/api/v1/predictions.py — router existant, dépendances FastAPI]
- [Source: backend/app/services/daily_prediction_service.py — DailyPredictionService, ComputeMode, ServiceResult]
- [Source: backend/app/infra/db/repositories/daily_prediction_repository.py — get_full_run()]
- [Source: backend/app/infra/db/models/daily_prediction.py — DailyPredictionRunModel, DailyPredictionCategoryScoreModel, DailyPredictionTurningPointModel (champs contributors_json, driver_json)]
- [Source: backend/app/core/config.py — settings.active_ruleset_version]
- [Source: _bmad-output/implementation-artifacts/36-1-service-applicatif-daily-prediction.md — ComputeMode.read_only, ServiceResult]
- [Source: _bmad-output/implementation-artifacts/35-2-explicabilite-debug.md — contributeurs et drivers JSON]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `backend/app/api/v1/predictions.py`
- `backend/app/tests/api/test_daily_prediction_api.py`

## Change Log

- 2026-03-08: Story créée pour l'Epic 36 — Productisation V1.
