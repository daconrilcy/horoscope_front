# Acceptance Traceability

| AC | Requirement | Code / artifact evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | A final `event_guidance` decision is persisted. | `evidence/event-guidance-decision.md` records decision `delete`. | Decision artifact exists; before/after scans persisted. | PASS |
| AC2 | Runtime contracts exclude legacy carriers. | `canonical_use_case_registry.py` no longer declares `event_guidance`; integration guard checks `get_canonical_use_case_contract("event_guidance") is None`. | `python -B -m pytest -q --tb=short ... test_llm_legacy_extinction.py`; AST guard PASS. | PASS |
| AC3 | Guidance seeds exclude legacy carriers. | `seed_guidance_prompts.py` no longer seeds `event_guidance`; `seed_66_20_taxonomy.py` no longer maps guidance/event. | Integration guard over `GUIDANCE_PROMPTS_TO_SEED`; `rg` scan after persisted. | PASS |
| AC4 | Prompt governance excludes legacy carriers. | `prompt_governance_registry.json` guidance family no longer allows `chart_json` or `event_description`. | `test_prompt_governance_registry.py` blocks `event_description`; AST/JSON guard PASS. | PASS |
| AC5 | Adapter routing matches the final decision. | `AIEngineAdapter.generate_guidance` no longer special-cases `event_guidance`; `PAID_USE_CASES` and prompt catalog no longer list it. | AST guard and targeted tests PASS. | PASS |
| AC6 | Residual `event_guidance` hits are classified. | `evidence/event-guidance-decision.md` classifies chat intent, guard tests, and CONDAMAD docs as residuals. | `evidence/event-guidance-scan-before.txt` and `evidence/event-guidance-scan-after.txt`. | PASS |
| AC7 | Modern natal legacy carriers stay blocked. | Natal runtime code unchanged; tests retained. | `python -B -m pytest -q --tb=short backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py backend/tests/integration/test_llm_legacy_extinction.py`. | PASS |
| AC8 | CS-350 reflects the final classification. | `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` marks `event_guidance` as deleted by CS-359. | CS-350 `rg` scan persisted in after evidence. | PASS |
| AC9 | Public API route surface is unchanged. | No route/API file changed. | `openapi-before.json` vs `openapi-after.json`: paths equal; `TestClient` `/openapi.json` status 200. | PASS |
| AC10 | Story evidence artifacts are persisted. | `evidence/event-guidance-decision.md`, before/after scan and OpenAPI snapshots. | Capsule validation PASS. | PASS |
| AC11 | RG-149 reflects the final classification. | `_condamad/stories/regression-guardrails.md` classifies `event_guidance` as deleted by CS-359. | RG-149 `rg` scan persisted in after evidence. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
