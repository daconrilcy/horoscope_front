# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | The internal contract exists. | `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` adds the canonical `LLMAstrologyInputV1Builder` and `llm_astrology_input_v1` constants. | `evidence/validation.txt`: targeted pytest `tests/unit/domain/astrology/test_llm_astrology_input_v1.py` PASS. | PASS |
| AC2 | The seven top-level blocks exist. | Contract payload emits `facts`, `signals`, `limits`, `evidence`, `shaping`, `provenance`, `exclusions` plus id/version. | `test_llm_astrology_input_v1_shape_and_sources_are_stable` PASS; `evidence/sample-payload.json`. | PASS |
| AC3 | `facts` uses `structured_facts_v1`. | `_ensure_structured_facts_source` requires `STRUCTURED_FACTS_V1_PROJECTION_ID`; `facts` block stores `source_projection_id`. | Unit rejection test PASS; `evidence/architecture-guard.txt` source scan. | PASS |
| AC4 | `signals` uses `AINarrativeInputContract`. | Builder requires `AINarrativeInputContract` and exposes prompt-visible signal/readiness blocks from that owner. | AST import guard and source scan PASS in `evidence/architecture-guard.txt`. | PASS |
| AC5 | B2C projections are shaping only. | `client_interpretation_projection_v1` is accepted only by `_shaping_block`; sections/support content are not copied into shaping. | Unit shape assertion PASS; owner guard for B2C builder PASS. | PASS |
| AC6 | Raw chart carriers are not canonical. | Raw carriers are listed only in `exclusions`; facts/signals tests assert `chart_json`, `natal_data`, provider response are absent from canonical blocks. | Unit negative assertions PASS; `evidence/architecture-guard.txt` scan documents allowed exclusion mentions. | PASS |
| AC7 | Hash provenance is deterministic. | `llm_input_hash` is computed through `compute_projection_hash` over every prompt-influencing block. | `test_llm_astrology_input_v1_hash_is_deterministic_and_covers_prompt_blocks` PASS. | PASS |
| AC8 | Prompt wiring stays unchanged. | No files under `backend/app/services/llm_generation/**` changed. | `evidence/architecture-guard.txt`: prompt/provider neutrality scan; `git status` shows no service changes. | PASS |
| AC9 | Public API surface stays unchanged. | No router/OpenAPI change; domain-only contract. | `evidence/public-surface-guard.txt`: OpenAPI, routes and TestClient `/health` PASS. | PASS |
| AC10 | Evidence artifacts are persisted. | `evidence/sample-payload.json`, `validation.txt`, `public-surface-guard.txt`, `architecture-guard.txt` created. | `condamad_validate.py` PASS after evidence update. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
