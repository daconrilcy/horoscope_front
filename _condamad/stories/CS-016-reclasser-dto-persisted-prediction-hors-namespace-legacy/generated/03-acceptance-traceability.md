# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Chaque DTO persisted est classe avec un owner canonique. | `persisted-dto-classification.md`, `persisted-dto-before.md`, `persisted-dto-after.md`. | `pytest -q app/tests/integration/test_v3_persistence.py app/tests/integration/test_relative_scoring_service.py` PASS. | PASS |
| AC2 | Les repositories DB n'importent plus les DTO legacy. | Repositories inspectés; guard `test_prediction_repositories_do_not_import_legacy_persisted_dtos` ajouté. | Scan repositories zero-hit; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` PASS. | PASS |
| AC3 | Aucun shim ou double DTO actif ne remplace la migration. | Owner unique `app.domain.prediction`; `backend/app/prediction` absent. | Scan imports legacy zero-hit; `rg --files app/prediction` confirme le path absent. | PASS |
| AC4 | Les tests persistence restent passants. | Aucun changement schema; DTO canoniques inchangés. | `pytest -q app/tests/integration/test_v3_persistence.py app/tests/integration/test_relative_scoring_service.py` PASS. | PASS |
| AC5 | L'API daily reste compatible avec les snapshots persisted. | Aucun changement payload; snapshots importés depuis owner canonique. | `pytest -q app/tests/integration/test_daily_prediction_api.py` PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
