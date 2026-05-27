# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Modern natal use cases require the new key. | `canonical_use_case_registry.py` exposes `NATAL_LLM_ASTROLOGY_INPUT_SCHEMA` and `list_modern_natal_use_case_contracts()`; all modern natal contracts require `llm_astrology_input_v1`. | `python -B -m pytest -q tests/unit/test_natal_llm_use_case_input_contract.py --tb=short` PASS. | PASS |
| AC2 | Modern natal schemas declare `llm_astrology_input_v1`. | Modern natal contracts share `NATAL_LLM_ASTROLOGY_INPUT_SCHEMA` with required `llm_astrology_input_v1`. | Unit contract test PASS; `evidence/natal-use-cases-after.json` persisted. | PASS |
| AC3 | Modern natal placeholders exclude the old key. | Unit guard rejects `chart_json`/`natal_data` in modern natal placeholders and schema properties; assembly nominal payload uses `llm_astrology_input_v1`. | Unit contract test PASS; targeted forbidden scan `chart_json_v2|natal_data_v2|{{*|shim|compatibility wrapper|fallback prompt branch` returned no matches. | PASS |
| AC4 | Rendered prompts consume the modern payload. | Renderer tests assert final prompt material contains `llm_astrology_input_v1` payload details and excludes `chart_json`/`natal_data`. | `python -B -m pytest -q tests/llm_orchestration/test_prompt_renderer.py --tb=short` PASS. | PASS |
| AC5 | Residual old carriers are classified. | Runtime gateway names `_NATAL_TRANSITION_PROMPT_CARRIERS`; transition comments bound `chart_json`/`natal_data`; tests assert modern payload wins over carriers. | `python -B -m pytest -q --long tests/integration/test_llm_runtime_suppression.py --tb=short` PASS; `evidence/prompt-key-scan-after.txt` persisted. | PASS |
| AC6 | Prompt wording delta is limited to input keys. | No editorial prompt files changed; code delta limited to registry helper, assembly preview key, runtime transition labels and tests. | `git diff --stat` reviewed; before/after use-case snapshot is semantically unchanged because registry had already been migrated in the dirty worktree. | PASS |
| AC7 | Public API surface remains unchanged. | No `backend/app/api/**` changes; OpenAPI/routes snapshots regenerated after implementation. | `python -B -c "from app.main import app; assert app.routes; assert app.openapi()['paths']"` PASS; OpenAPI/routes before-after JSON semantic equality PASS. | PASS |
| AC8 | Story evidence artifacts are persisted. | Evidence directory contains before/after use-case, prompt scan, OpenAPI and route artifacts plus validation summary. | `condamad_validate.py` PASS before evidence completion; final validation rerun recorded in `10-final-evidence.md`. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
