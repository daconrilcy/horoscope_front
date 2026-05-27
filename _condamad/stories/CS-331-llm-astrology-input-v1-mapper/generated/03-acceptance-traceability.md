# Acceptance Traceability

| AC | Requirement | Implementation evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The canonical mapper exists. | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` owns `LLMAstrologyInputV1Builder`. | `python -B -m pytest -q tests/unit/domain/astrology/test_llm_astrology_input_v1.py tests/architecture/test_llm_astrology_input_boundary.py --tb=short` PASS. | PASS |
| AC2 | `facts` maps from `structured_facts_v1`. | `facts` rejects non-`structured_facts_v1` sources and maps positions, houses, aspects, metadata, sign balances and dominants from that payload. | Unit assertions plus AST import guard PASS. | PASS |
| AC3 | `signals` maps from `AINarrativeInputContract`. | `signals` exposes interpretive signal codes, readiness flags, masking policy, source versions and projection links from `AINarrativeInputContract`. | Unit assertions plus AST import guard PASS. | PASS |
| AC4 | `limits` exposes missing data. | `limits` includes structured missing data, readiness-derived unavailable sections, masking policy and excluded calculation surfaces. | Missing-data unit test PASS. | PASS |
| AC5 | `evidence` uses compact refs. | `evidence` validates refs through `evidence_refs_validation.py` and stores compact refs plus grounding status only. | Unit JSON serialization and evidence owner import guard PASS. | PASS |
| AC6 | `shaping` stays separate from facts. | Shaping accepts only `client_interpretation_projection_v1` metadata fields and facts do not contain plan/module/selection. | Non-duplication unit test and targeted scan PASS. | PASS |
| AC7 | Complete natal mapping is covered. | Fixture covers natal object, dignity, house, rulership, aspect, dominance and sign balances. | Complete mapping unit assertions PASS. | PASS |
| AC8 | Missing-data mapping is covered. | Fixture without payloads/chart balance emits empty houses/aspects and prompt-visible missing data. | Missing-data unit test PASS. | PASS |
| AC9 | Field ownership is disjoint. | Facts do not copy signal codes; signals do not copy structural facts; shaping remains metadata-only. | `test_llm_astrology_input_v1_keeps_facts_signals_and_shaping_disjoint` PASS. | PASS |
| AC10 | Raw carriers are not serialized. | Raw carriers are only listed in `exclusions`; facts/signals omit `chart_json`, `natal_data`, provider output and runtime payloads. | Negative unit assertions and targeted scan PASS. | PASS |
| AC11 | Public API surface stays unchanged. | New architecture guard checks app routes/OpenAPI and TestClient smoke. | OpenAPI/routes commands PASS; `test_llm_astrology_input_boundary.py` PASS. | PASS |
| AC12 | Evidence artifacts are persisted. | `evidence/sample-payload.json`, `evidence/validation.txt`, `evidence/public-surface-guard.txt`, `evidence/architecture-guard.txt`. | Capsule validation PASS after evidence update. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
