# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The loaded app registers `POST /v1/theme-natal/readings`. | `backend/app/api/v1/routers/public/theme_natal_readings.py`, `backend/app/api/v1/routers/registry.py`. | `app.routes` command PASS; `evidence/routes-after.txt` contains `POST /v1/theme-natal/readings`. | PASS |
| AC2 | OpenAPI exposes product action fields. | `ThemeNatalReadingCommandRequest` under `backend/app/services/api_contracts/public/theme_natal_readings.py`. | `app.openapi()` command PASS; `evidence/openapi-after.json`. | PASS |
| AC3 | The new route accepts product command fields. | Route delegates `chart_id`, `action`, `persona_profile_id`, `locale`, `client_request_id` through `execute_theme_natal_reading_product_action`. | `python -B -m pytest -q --long tests/integration/test_theme_natal_public_api_product_actions.py --tb=short` PASS. | PASS |
| AC4 | The new route rejects old technical fields. | Pydantic `ConfigDict(extra="forbid")` on the new request schema; no aliases or fallbacks. | Integration test `test_new_route_rejects_legacy_generation_fields` PASS with centralized `invalid_request_payload`. | PASS |
| AC5 | Basic `generate_full` resolves to `basic_full_reading`. | `theme_natal_product_actions.py` calls `ThemeNatalBasicFullReadingRuntime`; runtime decision emits `basic_full_reading`. | Integration test `test_generate_full_accepts_product_command_and_returns_accepted_slot` PASS. | PASS |
| AC6 | Basic `preview` avoids short generation. | Preview branch resolves a product decision and returns `readonly` without calling `ThemeNatalBasicFullReadingRuntime.generate` or old interpretation service. | Integration test `test_preview_returns_controlled_state_without_short_generation` PASS; product-action symbol scan in `evidence/product-action-symbols-after.txt`. | PASS |
| AC7 | Public responses return accepted slots only. | Accepted runtime result is projected to `data`; provider/run internals are not copied. | Integration accepted-slot assertion PASS; response payload excludes `raw_provider_response`. | PASS |
| AC8 | Rejected runs return a controlled state. | Rejection path returns `state="rejected"` plus sanitized `reason_code` details only. | Integration rejected-run assertion PASS; no provider secret in serialized response. | PASS |
| AC9 | The old public endpoint is non-generative. | `POST /v1/natal/interpretation` raises `ApplicationError` code `natal_interpretation_endpoint_gone` before generation code. | `test_old_public_endpoint_is_non_generative` PASS; `evidence/old-endpoint-after.txt`. | PASS |
| AC10 | Public errors use centralized shape. | Error code mapped in `backend/app/api/errors/catalog.py`; FastAPI validation uses the existing error envelope. | 422 and 410 integration assertions PASS. | PASS |
| AC11 | New-route schema excludes old fields. | New schema has no `use_case`, `use_case_level`, `variant_code`, `plan`, or `forceRefresh`; no compatibility aliases. | `app.openapi()` command PASS; targeted `rg` on new route/schema returned `PASS: no matches`. | PASS |
| AC12 | Story evidence artifacts are persisted. | Evidence directory contains before/after OpenAPI, route, scan, old-endpoint, validation artifacts. | `condamad_validate.py <capsule>` PASS before implementation evidence update; final validation rerun recorded in `10-final-evidence.md`. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
