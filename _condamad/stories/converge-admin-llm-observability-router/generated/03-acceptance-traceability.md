# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Runtime owner is `admin.llm.observability`. | Register `admin.llm.observability.router`; remove duplicate runtime decorators from `prompts.py`. | `route-owners-after.md`; `pytest -q app/tests/unit/test_api_router_architecture.py`; runtime owner script. | PASS |
| AC2 | The four HTTP contracts remain exposed in OpenAPI. | Keep paths/methods/models stable through the canonical router. | `openapi-contract-diff.md`; `pytest -q app/tests/integration/test_admin_llm_config_api.py`. | PASS |
| AC3 | `prompts.py` no longer owns observability route decorators. | Delete four handlers and dead imports from `prompts.py`. | AST guard in `test_api_router_architecture.py`; targeted `rg` returns no hits. | PASS |
| AC4 | `observability.py` delegates to services without forbidden SQL symbols. | Keep HTTP adapter thin; remove `Session` annotation/import from route module. | Architecture guard forbids SQL tokens/imports; targeted `rg` returns no hits. | PASS |
| AC5 | No duplicate active implementation remains for the four endpoints. | One registered APIRoute per method/path; no wrapper or alias. | Architecture runtime cardinality guard; `pytest -q tests/unit/test_story_70_14_transition_guards.py`. | PASS |
| AC6 | Evidence files exist. | Generate before/after OpenAPI, route owners, filtered diff, removal audit. | Persistent evidence check script passed. | PASS |
| AC7 | Runtime contract covers all four endpoints. | Integration OpenAPI coverage includes call-logs, dashboard, replay, purge. | `pytest -q app/tests/integration/test_admin_llm_config_api.py`; runtime OpenAPI script. | PASS |
| AC8 | Runtime route cardinality is exactly one per expected route key. | Runtime guard asserts exact route key set and owner module. | `pytest -q app/tests/unit/test_api_router_architecture.py`; runtime owner script. | PASS |
