# Evidence Log - prompt-generation - 2026-05-02-1452

| ID | Evidence type | Command / Source | Result | Notes |
|---|---|---|---|---|
| E-001 | source | Read previous audit baseline: `_condamad/audits/prompt-generation/2026-04-30-1810/{00,02,03}*.md` | PASS | Baseline findings F-001 a F-004 used as re-audit targets. |
| E-002 | targeted_forbidden_symbol_scan | `rg` scan for LLMNarrator instantiation, legacy import, chat completions create, and openai AsyncOpenAI under `backend/app backend/tests` | PASS | Exit 1 / zero hits for executable legacy narrator and direct OpenAI provider patterns. |
| E-003 | targeted_forbidden_symbol_scan | `rg` scan for fallback catalog symbols and supported prompt keys under `backend/app/domain/llm/prompting backend/tests/llm_orchestration` | PASS | Forbidden keys are present in tests as guards and in runtime metadata, but absent as `PROMPT_FALLBACK_CONFIGS` entries. |
| E-004 | source | Inspected `PROMPT_FALLBACK_CONFIGS` and guard tests in catalog and LLM orchestration tests | FAIL | The explicit forbidden keys are guarded, but fallback prompt exceptions remain exact and executable. |
| E-005 | targeted_forbidden_symbol_scan | `rg` scan for forbidden durable narration phrases under daily builder and its guard test | PASS | Hits exist only in the guard test; application builder has no hits. |
| E-006 | source | Inspected daily builder and assembly seed | PASS | Builder contains context payload only; seed owns durable JSON/style/length instructions. |
| E-007 | targeted_forbidden_symbol_scan | `rg` scan for consultation family drift, consultation contextual use case, prompt_content to developer_prompt, and fallback catalog symbols | PASS | Hits are documentation and governance tests; no runtime consultation family or `developer_prompt` from `prompt_content` found. |
| E-008 | source | Inspected `_condamad/stories/formalize-consultation-guidance-prompt-ownership/consultation-routing-after.md` | PASS | Consultation is documented as `guidance_contextual`; precheck refusal remains before GuidanceService call. |
| E-009 | dependency_direction_scan | `rg` scan for `app.api`, `HTTPException`, and `JSONResponse` under prompt generation layers | PASS | Exit 1 / zero forbidden API or FastAPI hits. |
| E-010 | test_coverage_inventory | `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py tests/llm_orchestration/test_narrator_migration.py tests/llm_orchestration/test_llm_legacy_extinction.py tests/llm_orchestration/test_prompt_governance_registry.py tests/unit/prediction/test_astrologer_prompt_builder.py app/tests/unit/test_seed_horoscope_narrator_assembly.py app/tests/unit/test_guidance_service.py app/tests/unit/test_consultation_generation_service.py` | PASS | `75 passed in 11.64s`; venv was activated before pytest. |
| E-011 | source | Inspected story evidence artifacts under `_condamad/stories/*` | PASS | Story evidence exists; some story validation plan paths were stale and required path correction during audit. |
| E-012 | limitation | First attempted targeted pytest command with story-listed paths | LIMITATION | Two story-listed paths were invalid: `tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py` and `tests/unit/test_guidance_service.py`; actual files are under `app/tests/unit`. |

## Evidence notes

- Static scans are used as supporting evidence; E-010 provides executable guard evidence.
- Application code was not modified.
- The audit did not run the full backend test suite or full Ruff check because this was a read-only domain audit; targeted guards passed.
