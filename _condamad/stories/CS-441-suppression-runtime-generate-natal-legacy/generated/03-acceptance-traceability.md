# Acceptance Traceability - CS-441

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Removed adapter method absent from `backend/app`. | `backend/app/domain/llm/runtime/adapter.py` deletes `AIEngineAdapter.generate_natal_interpretation`; `backend/tests/architecture/test_llm_legacy_extinction.py::test_natal_adapter_entry_point_is_removed`. | `rg -n "generate_natal_interpretation" backend/app` -> `PASS: no matches`; targeted pytest `64 passed`. | PASS |
| AC2 | Service cannot call removed method. | `backend/app/services/llm_generation/natal/interpretation_service.py` raises `legacy_natal_generation_disabled`; service tests assert no gateway call. | AST/source guard in `test_natal_legacy_service_does_not_build_runtime_input`; targeted pytest `64 passed`. | PASS |
| AC3 | Natal service no longer builds `NatalExecutionInput`. | Import and construction removed from `interpretation_service.py`. | `rg -n "NatalExecutionInput\|use_case_key\s*=\s*['\"]natal_interpretation" backend/app/services/llm_generation/natal` -> `PASS: no matches`. | PASS |
| AC4 | Old runtime use case is not executable. | Legacy `interpret` path now rejects before provider request construction. | `backend/tests/architecture/test_llm_legacy_extinction.py`; `backend/app/tests/unit/test_natal_interpretation_service*.py`; targeted pytest `64 passed`. | PASS |
| AC5 | `level` no longer selects a provider runtime. | `level`/`variant_code` only control readonly cache lookup and rejection metadata in the removed path. | Bounded scans of natal service and adapter -> no `NatalExecutionInput` or removed adapter call; targeted pytest `64 passed`. | PASS |
| AC6 | Positive tests no longer mock removed adapter method. | Positive provider mocks removed or converted to absence/rejection assertions in backend tests. | `rg -n "generate_natal_interpretation" backend/tests backend/app/tests` -> `PASS: no matches`. | PASS |
| AC7 | Historical readonly rows remain readable without provider access. | Readonly deserialization/list/get code retained in `interpretation_service.py`. | `python -B -m pytest -q --tb=short backend/tests/integration/test_theme_natal_public_reads.py` included in targeted run. | PASS |
| AC8 | Basic runtime uses `theme_natal` slots. | `ThemeNatalBasicFullReadingRuntime` tests retained; legacy Basic assertions now reject provider route. | `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py` included in targeted run. | PASS |
| AC9 | CS-440 CR-4 adapter blocker resolved. | Adapter method deleted and architecture guard expanded for removed entry point. | AST guard + bounded zero-hit scans + targeted pytest `64 passed`. | PASS |
| AC10 | Zero-hit evidence artifacts persisted. | Evidence files under `evidence/` include before/after scans and OpenAPI snapshots. | `runtime-generate-natal-after.txt`, `positive-mocks-after.txt`, `openapi-after.json`, `route-openapi-after-check.txt`; artifact paths present. | PASS |
| AC11 | Public routes do not preserve removed runtime path. | No public route added; runtime `app.routes`/`app.openapi()` check persisted. | `route-openapi-after-check.txt`: `PASS: no public route/openapi legacy runtime hits`. | PASS |

## Validation limitations

Full `python -B -m pytest -q --tb=short` was executed and remains red:
`9 failed, 3552 passed, 2 skipped, 1284 deselected`. The 9 failures are outside CS-441 scope:
API router architecture debt, LLM DB model namespace debt, and prompt catalogue/seed expectations explicitly owned outside this story (CS-442 for catalogues/seeds). Targeted CS-441 validations pass.
