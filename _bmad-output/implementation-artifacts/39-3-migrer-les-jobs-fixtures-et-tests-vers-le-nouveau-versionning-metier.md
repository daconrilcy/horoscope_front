# Story 39.3: Migrer les jobs, fixtures et tests vers le nouveau versionning métier

Status: completed

## Story

As a QA and data engineer,
I want réaligner les seeds, fixtures, jobs de calibration et suites de test sur le nouveau ruleset canonique,
So that la validation automatique reflète le contrat métier cible sans dépendre d'une dette de nommage historique.

## Acceptance Criteria

- [x] AC1: Les jobs de calibration et de QA utilisent la source de vérité centrale pour résoudre `reference_version` / `ruleset_version`.
- [x] AC2: Les tests backend et les fixtures critiques n'utilisent plus de strings dispersées quand une constante de version active existe.
- [x] AC3: Les suites ciblées de daily prediction restent vertes après la bascule.
- [x] AC4: Les cas legacy nécessaires continuent à couvrir la lecture de données `1.0.0`.

## Implementation Details

- Migration de `test_daily_prediction_metrics.py` et `test_daily_prediction_guardrails.py` pour utiliser les versions par défaut.
- Refonte complète des mocks dans `test_daily_prediction_service.py` pour assurer la cohérence `ruleset <-> reference`.
- Ajout de tests unitaires pour le cas `ruleset_inconsistent`.
- Mise à jour de `test_daily_prediction_api.py` pour utiliser `settings.active_reference_version`.
- Correction de `test_daily_prediction_qa.py` pour gérer le seeding correct des deux versions et le déverrouillage temporaire nécessaire au script de seed.
- Vérification que les jobs `generate_qa_cases.py` et `natal_profiles.py` utilisent déjà les réglages centralisés.

### File List

- `backend/app/core/versions.py`
- `backend/app/core/config.py`
- `backend/app/tests/unit/test_daily_prediction_metrics.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `backend/app/tests/unit/test_daily_prediction_service.py`
- `backend/app/tests/integration/test_daily_prediction_api.py`
- `backend/app/tests/integration/test_daily_prediction_qa.py`
- `_bmad-output/implementation-artifacts/39-3-migrer-les-jobs-fixtures-et-tests-vers-le-nouveau-versionning-metier.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
