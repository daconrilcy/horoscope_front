# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `ApplicationError` vit hors API, dans `backend/app/core/exceptions.py`. | `backend/app/core/exceptions.py`, auth dependency errors. | Targeted unit tests and imports. | PASS |
| AC2 | Le catalogue HTTP typé a codes uniques, statuts valides et messages non vides. | `backend/app/api/errors/catalog.py`. | `test_http_error_catalog_is_unique_and_valid`. | PASS |
| AC3 | Les routes ne lèvent plus `HTTPException` métier/applicative. | Architecture guard without allowlist. | `test_api_http_exception_usage_is_removed`. | PASS |
| AC4 | Les helpers locaux d'erreur disparaissent des routeurs. | `_error_response` and `_create_error_response` removed/renamed. | Negative `rg` scan and router architecture tests. | PASS |
| AC5 | Les services ne construisent plus de réponse HTTP. | Services now raise `ApplicationError`; no `JSONResponse`/`api_error_response`. | Negative service scan and architecture tests. | PASS |
| AC6 | Toutes les sous-classes d'`ApplicationError` auditées ont mapping ou fallback testé. | Central handler in `app.api.errors.handlers`. | Unit/integration fallback tests. | PASS |
| AC7 | Le JSON d'erreur conserve l'enveloppe `error.code/message/details/request_id`. | `build_error_response` and `application_error_handler`. | Contract and integration tests. | PASS |
| AC8 | OpenAPI ne perd aucun path/method, expose les statuts d'erreur déclarés et ne duplique pas les schémas d'erreur. | OpenAPI smoke tests. | Path/method coverage, declared error status coverage, `ErrorEnvelope` `$ref`, no duplicate canonical schemas. | PASS |
| AC9 | Tests, lint et scans d'architecture passent dans le venv Python activé. | Tests/scans/lint. | Ruff, targeted tests, scans pass; full pytest reported green by user. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
