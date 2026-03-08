# Story 39.2: Basculer la configuration runtime et centraliser les versions actives

Status: completed

## Story

As a backend maintainer,
I want centraliser les versions actives de prédiction et basculer la configuration par défaut vers le ruleset canonique,
So that les environnements local/dev/test n'utilisent plus de paire de versions ambiguë ou implicite.

## Acceptance Criteria

- [x] AC1: La configuration active de prédiction est centralisée dans un point unique réutilisable par les services, jobs et tests.
- [x] AC2: `backend/.env.example` et la documentation runtime exposent explicitement la paire active supportée.
- [x] AC3: Les services de prédiction quotidienne, de calibration et de QA consomment la source de vérité centrale plutôt que des strings dispersées.
- [x] AC4: Une incohérence runtime entre ruleset actif et référence active est détectable explicitement.

## Implementation Details

- Basculement de `ACTIVE_RULESET_VERSION` à `2.0.0` dans `backend/app/core/versions.py`.
- Mise à jour de `DailyPredictionService.get_or_compute` pour utiliser `settings.active_ruleset_version` par défaut.
- Ajout d'un check de cohérence dans `DailyPredictionService._resolve_ruleset_id` pour vérifier que le ruleset est rattaché à la bonne référence.
- Mise à jour de `backend/.env.example` et `backend/README.md`.
- Mise à jour des tests d'intégration QA pour utiliser `2.0.0`.
- Création d'un test unitaire `backend/app/tests/unit/test_daily_prediction_version_consistency.py` pour valider AC4.

### File List

- `backend/app/core/versions.py`
- `backend/app/services/daily_prediction_service.py`
- `backend/.env.example`
- `backend/README.md`
- `backend/app/tests/integration/test_daily_prediction_qa.py`
- `backend/app/tests/unit/test_daily_prediction_version_consistency.py`
- `backend/app/tests/unit/test_calibration_runtime.py`
- `_bmad-output/implementation-artifacts/39-2-basculer-la-configuration-runtime-et-centraliser-les-versions-actives.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
