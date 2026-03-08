# Story 39.4: Documenter, monitorer et déprécier le ruleset legacy

Status: completed

## Story

As a product operations lead,
I want documenter la transition de versionning et tracer l'usage du ruleset legacy,
So that l'équipe peut piloter la bascule vers le ruleset canonique puis planifier proprement la dépréciation du legacy.

## Acceptance Criteria

- [x] AC1: La documentation backend/calibration/QA explique clairement la relation entre référence `2.0.0`, ruleset canonique and ruleset legacy.
- [x] AC2: Les environnements non prod disposent d'un runbook de transition simple.
- [x] AC3: L'observabilité permet d'identifier si des calculs ou jobs utilisent encore le ruleset legacy.
- [x] AC4: Une stratégie de dépréciation explicite du ruleset legacy est écrite, sans suppression immédiate des données historiques.

## Implementation Details

- Mise à jour de `backend/README.md` avec le runbook de transition.
- Création de `docs/architecture/prediction-versioning-transition.md` (Stratégie et relation entre versions).
- Ajout d'un log de warning `DEPRECATION` dans `DailyPredictionService._resolve_ruleset_id` si le ruleset `1.0.0` est utilisé.
- Ajout du champ `ruleset_version` dans les logs de `prediction.run` via `_log_and_metrics`.
- Centralisation de `LEGACY_RULESET_VERSION` dans `backend/app/core/versions.py`.
- Validation unitaire du log de dépréciation dans `test_daily_prediction_service.py`.

### File List

- `backend/app/core/versions.py`
- `backend/app/services/daily_prediction_service.py`
- `backend/app/tests/unit/test_daily_prediction_service.py`
- `backend/README.md`
- `docs/architecture/prediction-versioning-transition.md`
- `_bmad-output/implementation-artifacts/39-4-documenter-monitorer-et-deprecier-le-ruleset-legacy.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
