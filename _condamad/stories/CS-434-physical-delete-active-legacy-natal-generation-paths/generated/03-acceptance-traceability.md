# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Public generation cannot use `natal_interpretation_short`. | `users.py` closes public generators; `interpret()` rejects short generation before gateway; prompt catalog and bootstrap no longer publish it. | `app.routes`/`app.openapi()` checks PASS; architecture guard PASS; targeted `rg` allowlist only. | PASS |
| AC2 | Public generation cannot use `natal_long_free`. | `PROMPT_RUNTIME_DATA` no longer contains `natal_long_free`; `_generate_free_short` was deleted; adapter rejects the key. | Catalog runtime check PASS; `llm_orchestration` full PASS; service branch scan zero-hit. | PASS |
| AC3 | Basic generation does not route through `natal_interpretation`. | `interpretation_service.py` raises `legacy_basic_natal_generation_disabled`; `adapter.py` rejects `plan=basic` with `natal_interpretation`; seed 66.20 no longer publishes Basic legacy assembly. | Product-action API tests PASS; `test_runtime_convergence.py` asserts no Basic legacy assembly. | PASS |
| AC4 | Premium prompts do not receive `basic_natal_prompt_payload`. | `NatalExecutionInput` no longer exposes the field; `adapter.py` and `gateway.py` no longer forward or remap it into legacy execution. | Architecture guard PASS; negative `rg` for `basic_natal_prompt_payload.*natal_interpretation` PASS. | PASS |
| AC5 | Public natal fallback configs contain no generator key. | `catalog.py` removes `natal_interpretation_short` and `natal_long_free` runtime entries; registry fallback target to short removed. | Python catalog check PASS; `test_llm_legacy_extinction.py` PASS. | PASS |
| AC6 | Obsolete natal seeds are deleted or classified. | `seed_29_prompts.py`, `seed_66_20_taxonomy.py`, and `main.py` stop seeding/requiring short/free/basic legacy; removal audit classifies residual scripts. | `removal-audit.md` present; `llm_orchestration` PASS; scan after persisted. | PASS |
| AC7 | Legacy nominal tests stop preserving public generation. | Updated `test_context_quality.py`, `test_resolved_execution_plan.py`, `test_runtime_convergence.py`, `test_ai_engine_adapter.py` from nominal legacy to fixture/guard behavior. | `backend/tests/llm_orchestration` PASS; adapter unit tests PASS. | PASS |
| AC8 | Readonly legacy compatibility cannot call a provider. | Public readonly routes keep list/get/delete formatting only; generation endpoints return 410 before service/provider; adapter rejects deleted keys. | TestClient product-action tests PASS and mocks assert legacy service not called. | PASS |
| AC9 | Historical residual hits are allowlisted. | `evidence/legacy-allowlist.md` classifies readonly, test-guard, bootstrap-classified, admin-only hits. | Artifact check PASS; scan after persisted for reviewer comparison. | PASS |
| AC10 | Deleted generator paths cannot reappear. | Architecture guards inspect public routes, runtime OpenAPI, adapter method, DTO fields, and catalog absence. | `test_llm_legacy_extinction.py` PASS; runtime route/OpenAPI/catalog commands PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
