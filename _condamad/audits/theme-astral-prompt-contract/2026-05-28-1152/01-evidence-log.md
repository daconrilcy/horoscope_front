# Evidence Log

| ID | Evidence type | Command / Source | Inspected path / surface | Result | Limitation |
|---|---|---|---|---|---|
| E-001 | source-contract | `Get-Content` story, brief and guardrails | `_condamad/stories/CS-361-*/00-story.md`, `_story_briefs/cs-361-*.md`, `_condamad/stories/regression-guardrails.md` | PASS | Guardrail registry is long; only relevant IDs and prompt/astrology invariants were mapped. |
| E-002 | prior-history-scan | `rg -n "CS-36[3-8]\|theme-astral-prompt-contract\|interpretation_hints" _condamad/stories _condamad/audits -g "*.md"` and audit folder listing | `_condamad/stories`, `_condamad/audits` | PASS | No prior `theme-astral-prompt-contract` audit folder existed before this run. |
| E-003 | source-availability | `rg --files` over story-mandated roots | backend astrology/services/db/ops/migrations/tests, docs, prompt examples | PASS | Large inventory summarized by selected owner surfaces. |
| E-004 | interpretive-source-scan | `rg -n "interpret\|keyword\|texte\|description\|meaning\|profile\|dignit\|rulership\|condition\|aspect\|dominant" backend/app docs backend/migrations -g "*.py" -g "*.md"` plus seed JSON scan | DB models, repositories, seeds, docs | PASS | Some docs paths contain spaces; one raw scan had a quoting limitation, then was bounded by file inventory and direct source inspections. |
| E-005 | call-trace-source | `Get-Content` targeted owners and `rg -n "LLMAstrologyInputV1Builder\|ClientInterpretationProjectionV1Builder\|LLMGateway\|interpretive_signal_codes"` | `interpretation_service.py`, `llm_astrology_input_v1.py`, `structured_facts_v1_builder.py`, `ai_narrative_input_builder.py`, `gateway.py` | PASS | Source trace, not a live provider call. |
| E-006 | provider-payload-comparison | `rg -n "free\|basic\|premium\|provider payload\|interpretation_hints\|developer\|user\|response_format\|provider_parameters" _condamad/examples/prompt-generation-cartography _condamad/docs/prompt-generation-cartography -g "*.json" -g "*.md"` | `1974-04-24-1100-paris` and `1973-04-24-paris` examples | PASS | Existing example files were already modified/untracked before this audit. |
| E-007 | test-guard-inventory | `rg -n "interpretation_hints\|interpretive_signal_codes\|signals" backend/tests backend/app/domain/astrology/interpretation backend/app/domain/llm/runtime/gateway.py -g "*.py"` | LLM input unit and architecture tests | PASS | Targeted inventory only; full suite handled separately by story validation plan if needed. |
| E-008 | no-legacy-dry-scan | Source inspection of `LLM_ASTROLOGY_INPUT_DATA_ROLES`, `EXCLUDED_SURFACES`, `_prompt_visible_llm_astrology_input`, `build_user_payload` | `llm_astrology_input_v1.py`, `gateway.py` | PASS | Proves current carrier filtering, not future target adequacy. |
| E-009 | runtime-limitation | No provider call and no DB mutation by CS-361 contract | Provider runtime, DB migrations, application code | LIMITATION | Audit intentionally stays read-only and does not execute real LLM provider calls. |
| E-010 | app-diff-guard | `git diff --quiet -- backend/app backend/tests frontend/src backend/migrations` | forbidden application/runtime surfaces | PASS | Existing pre-audit changes in `_condamad/docs` and `_condamad/examples` were not claimed clean; they were inspected as evidence only. |

## Evidence Notes

All Python validation commands for audit scripts were run after verifying and activating `.venv`.
