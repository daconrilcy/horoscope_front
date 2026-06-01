# Dev Log CS-434

- Preflight: `.git` present; initial dirty file observed: `_condamad/run-state.json`.
- Capsule: generated files were missing; ran `condamad_prepare.py` with explicit story key, then `condamad_validate.py` PASS.
- Implementation: closed public `/users` generation paths with 410, removed old request DTO, removed short/free runtime catalog entries, removed fallback targets, blocked Basic via legacy `natal_interpretation`, removed legacy Basic carrier from `NatalExecutionInput`, adapter and gateway.
- Tests: converted nominal legacy tests to fixture or anti-return behavior; added public route, OpenAPI, adapter and DTO guards.
- Review fix: removed the remaining `_generate_free_short` branch and changed non-cached short/free-short legacy calls to fail before gateway.
- Review fix tests: updated `test_natal_interpretation_service_v2.py` and `test_llm_legacy_extinction.py` so reintroducing the branch fails.
- Evidence: persisted OpenAPI before/after, legacy scans before/after, removal audit, allowlist, validation summary.
- Propagation: no-propagation; changes are story-local and covered by new guards.
