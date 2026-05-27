# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Gateway projection uses canonical roles. | `backend/app/domain/llm/runtime/gateway.py` imports `LLM_ASTROLOGY_INPUT_DATA_ROLES` and derives `LLM_ASTROLOGY_INPUT_V1_PROMPT_BLOCKS` from `["prompt_visible"]`. | `python -B -m pytest -q tests\architecture\test_llm_astrology_input_payload_boundaries.py tests\integration\test_llm_legacy_extinction.py --tb=short` PASS. | PASS |
| AC2 | Rendered prompt keeps prompt-visible blocks. | `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` expects the rendered payload keys from canonical `prompt_visible`. | `python -B -m pytest -q tests\unit\domain\astrology\test_llm_astrology_input_evidence.py tests\llm_orchestration\test_llm_astrology_input_boundaries.py --tb=short` PASS. | PASS |
| AC3 | Rendered prompt excludes audit-only keys. | Runtime tests now reject `provenance`, `projection_hash`, `llm_input_hash`, `provider_response`, and `persisted_answer` anywhere in the rendered prompt payload. | Same orchestration test command PASS; `evidence/prompt-payload-after.json` contains only `facts`, `signals`, `limits`, `evidence`, `shaping`. | PASS |
| AC4 | Audit persistence still receives hash metadata. | Audit path remains unchanged and integration test asserts model hashes/version/grounding/evidence refs from complete `llm_astrology_input_v1`. | `python -B -m pytest -q tests\integration\llm\test_natal_llm_astrology_input_audit.py --long --tb=short` PASS. | PASS |
| AC5 | Existing hash behavior remains stable. | Hash contract owner remains `llm_astrology_input_v1`; gateway only changes prompt projection. | `python -B -m pytest -q tests\unit\domain\astrology\test_llm_astrology_input_v1.py tests\unit\domain\astrology\test_llm_astrology_input_hash.py --tb=short` PASS. | PASS |
| AC6 | Legacy natal LLM guards still pass. | No `chart_json`/`natal_data` prompt fallback was added; gateway legacy guard remains active. | `python -B -m pytest -q tests\architecture\test_llm_astrology_input_payload_boundaries.py tests\integration\test_llm_legacy_extinction.py --tb=short` PASS. | PASS |
| AC7 | Evidence artifacts are persisted. | `evidence/prompt-payload-before.json`, `evidence/prompt-payload-after.json`, and `evidence/validation.txt` were written. | `python -B -c "from pathlib import Path; ..."` PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
