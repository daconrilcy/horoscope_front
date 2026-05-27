# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Payload role classes are tested. | `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` asserts prompt-visible blocks only; `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` guards the gateway projection. | `python -B -m pytest -q tests\llm_orchestration\test_llm_astrology_input_boundaries.py --tb=short` => 4 passed; architecture payload guard => 3 passed. | PASS |
| AC2 | Representative prompt contains rich blocks. | `LLMGateway.build_user_payload` now projects `facts`, `signals`, `limits`, `evidence`, `shaping`, `provenance` before JSON serialization. | Orchestration test `test_gateway_payload_projects_prompt_visible_role_blocks_only`; after snapshot `evidence/payload-boundary-after.json`. | PASS |
| AC3 | Missing-data limits are prompt-visible. | Missing-data payload is rendered through the gateway and decoded from the final user payload. | Orchestration test `test_gateway_payload_makes_missing_data_limits_prompt_visible`. | PASS |
| AC4 | Raw surfaces stay out. | Gateway prompt projection excludes `exclusions`, `data_roles`, `chart_json`, `natal_data` and raw runtime metadata from prompt material. | Orchestration test `test_gateway_payload_does_not_promote_raw_or_legacy_prompt_owners`; scan persisted in `evidence/payload-boundary-scan.txt`. | PASS |
| AC5 | No `chart_json` prompt owner. | `llm_astrology_input_v1` branch is selected before legacy carriers and serializes only projected blocks. | Orchestration handoff test with mocked provider client; full backend regression passed. | PASS |
| AC6 | Duplication guard exists. | Existing domain test keeps facts, signals and shaping disjoint and verifies canonical owners. | `python -B -m pytest -q tests\unit\domain\astrology\test_llm_astrology_input_v1.py --tb=short` => 9 passed. | PASS |
| AC7 | Tests avoid external LLM provider calls. | Provider handoff test uses `MagicMock`/`AsyncMock`; no real provider is constructed by the boundary evidence. | `test_gateway_provider_handoff_uses_local_double_and_prompt_boundary` passed. | PASS |
| AC8 | Guard evidence artifacts are persisted. | `evidence/payload-boundary-before.json`, `payload-boundary-after.json`, `validation.txt`, `payload-boundary-scan.txt` created. | Python existence check passed; capsule validation passed. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
