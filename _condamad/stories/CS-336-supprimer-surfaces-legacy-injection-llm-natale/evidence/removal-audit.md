# Removal audit - CS-336

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `chart_json` natal LLM carrier | field/placeholder | historical-facade | `NatalExecutionInput`, natal adapter, gateway natal payload validation, natal prompt governance, active natal seeds | `llm_astrology_input_v1` | delete | Runtime diff, `test_llm_legacy_extinction.py`, `test_natal_llm_use_case_input_contract.py`, scan after | prompt owner drift |
| `natal_data` natal LLM carrier | field/placeholder | historical-facade | `NatalExecutionInput`, natal adapter, gateway natal payload validation, natal prompt governance | `llm_astrology_input_v1` | delete | Runtime diff, `test_gateway_input_validation_payload.py`, `test_llm_astrology_input_boundaries.py`, scan after | duplicate prompt input |
| chart-derived `evidence_catalog` prompt carrier | runtime flag | historical-facade | Natal adapter handoff and chart-derived evidence catalog build | modern `evidence_refs` in `llm_astrology_input_v1` | delete | Service diff, adapter diff, architecture guard, payload-boundary tests | false grounding |
| `chart_json` in event guidance and public chart projection | public/non-natal owner | canonical-active | `event_guidance`, chart JSON builder, public projection tests | none in this story | keep | `legacy-carrier-scan-after.txt`; no API/router diff | deleting would exceed story scope |
| `evidence_catalog` in output validator | validation owner | canonical-active outside natal prompt input | output validation tests and sanitizer | none in this story | keep | `legacy-carrier-scan-after.txt`; no natal adapter handoff remains | over-deletion could weaken validation |
| Old-key strings in tests/guards | guard evidence | canonical-active guard | negative assertions and architecture tests | none | keep | `test_llm_legacy_extinction.py`, `test_natal_llm_use_case_input_contract.py` | none |
