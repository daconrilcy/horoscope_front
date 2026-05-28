# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Theme astral path is unique. | `LLMGateway.build_user_payload` now requires `theme_astral_llm_input_v1` for `use_case="theme_astral"`; `ThemeAstralProviderPayloadBuilder` remains the single provider payload owner. | `python -B -m pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py tests/architecture/test_theme_astral_prompt_contract_guard.py --tb=short`; full `python -B -m pytest -q tests --tb=short`. | PASS |
| AC2 | `chart_json` cannot feed theme astral. | Gateway raises `InputValidationError` when `theme_astral` lacks the canonical payload, even if `chart_json` is present. | Bigbang integration test; `evidence/legacy-scan-after.txt` interpreted for scoped owners and examples. | PASS |
| AC3 | `natal_data` cannot feed theme astral. | Same explicit gateway rejection path blocks `natal_data` as replacement input. | Bigbang integration test; `evidence/legacy-scan-after.txt`. | PASS |
| AC4 | Old plan prompts are inactive. | Prompt contract id is `theme_astral_prompt_v1`; theme astral seed template no longer names `theme_astral_prompt_contract_v1`; old natal prompt constants are not used by theme astral owners. | `python -B -m pytest -q tests/architecture/test_theme_astral_prompt_contract_guard.py --tb=short`; targeted scan evidence. | PASS |
| AC5 | Commercial plan is hidden from LLM. | Provider payload receives only non-commercial `delivery_profile`; tests assert no JSON key `plan` and no string values `free/basic/premium`. | Bigbang integration test; example JSON shape check. | PASS |
| AC6 | Example payload shapes are stable. | Six example provider payload JSON files regenerated from `ThemeAstralProviderPayloadBuilder` with identical top-level and `input_data` keys. | `python -B -c <example shape check>` => PASS. | PASS |
| AC7 | Old tests are replaced. | Added CS-367 integration and architecture tests for the canonical contract; existing CS-366 builder/handoff tests remain green. | `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/integration/llm/test_theme_astral_provider_payload_handoff.py ... --tb=short`. | PASS |
| AC8 | Reintroduction guard fails old path. | `backend/tests/architecture/test_theme_astral_prompt_contract_guard.py` blocks old carriers and old prompt id in theme astral owners. | Architecture guard pytest PASS. | PASS |
| AC9 | Public API routes are unchanged. | No API/router files changed; loaded app route/OpenAPI hashes captured after implementation. | `python -B -c <app.routes/app.openapi hash>` => routes `3c0dfb...`, OpenAPI `201582...`. | PASS |
| AC10 | Story evidence is persisted. | `generated/*`, `evidence/legacy-scan-before.txt`, `evidence/legacy-scan-after.txt`, this traceability file, and final evidence updated. | `condamad_validate.py` final PASS. | PASS |
| AC11 | Local startup command is exact. | Exact command verified: `python -B -m uvicorn app.main:app --host 127.0.0.1 --port 8000`. | PowerShell `Start-Process` startup proof => PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
