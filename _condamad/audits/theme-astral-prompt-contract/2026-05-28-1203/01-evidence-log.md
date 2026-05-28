# Evidence Log

| ID | Evidence type | Command / Source | Inspected path / surface | Result | Limitation |
|---|---|---|---|---|---|
| E-001 | source-read | `Get-Content -Raw` on CS-362 story and source brief | `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/00-story.md`; `_story_briefs/cs-362-audit-contrats-prompt-theme-astral-json-provider-actuels.md` | PASS | Read-only story/brief evidence. |
| E-002 | guardrail-read | `Get-Content -Raw _condamad/stories/regression-guardrails.md` | `_condamad/stories/regression-guardrails.md` | PASS | Registry is large; relevant RG-002/RG-149 and registry gap were used. |
| E-003 | prior-history-scan | `Get-Content` prior audit files; `rg` scan for theme-astral prompt contract and CS-362 through CS-368 | prior same-domain audit and downstream stories | PASS | CS-361 findings remain adjacent active context; this audit does not close them. |
| E-004 | json-contract-shape | Venv command: Python parsed the three provider JSON files and compared top-level keys, `messages`, user payload root, `llm_astrology_input_v1`, `facts`, `signals`, `limits`, `shaping`, `response_format`, `provider_parameters` | `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/*-provider-payload.json` | PASS | User message is a prefixed JSON string (`llm_astrology_input_v1:`), so parsing stripped that prefix. |
| E-005 | quantity-comparison | Venv command: Python counted message roles/chars and nested array lengths for the three payloads | same provider payload files | PASS | Character counts prove relative volume, not token counts. |
| E-006 | runtime-doc-scan | `rg` scan for llm_astrology_input_v1, commercial, plan, provider_parameters, response_format, developer, user, premium, basic | prompt construction doc, gateway, seed prompts | PASS | Source scan only; no runtime provider call. |
| E-007 | targeted-forbidden-symbol-scan | `rg` scan for premium, plan, source_metadata, projection_hash, llm_input_hash, provider_response, provenance, evidence, trace, debug, audit, response_format, provider_parameters | provider payload examples | PASS | `trace` and `debug` direct fields were not observed; `evidence` also appears as output schema property, not only audit data. |
| E-008 | premium-in-basic-scan | `rg` scan for theme natal premium, premium, PREMIUM, profondeur, Exigence, sections, summary plus provider payload scan | prompt seed files and basic provider payload | PASS | Direct payload line is long because JSON is minified in message content. |
| E-009 | test-guard-inventory | `rg --files` inventory filtered to the three LLM astrology input boundary test names | backend prompt boundary tests | PASS | Inventory only until targeted tests are executed. |
| E-010 | json-validity | Venv command: `python -m json.tool` for `free-provider-payload.json`, `basic-provider-payload.json`, `premium-provider-payload.json` | provider payload examples | PASS | Validates outer JSON files; user content JSON was separately parsed in E-004. |
| E-011 | status-baseline | `git status --short` before artifact creation | repository root | PASS | Pre-existing untracked `_condamad/run-state.json`; no app source delta observed before audit writing. |
| E-012 | persistent-story-evidence | Review-created evidence files under `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/evidence/` | source availability, JSON validity, structure comparison, report shape, validation evidence | PASS | Evidence is persisted as story governance artifacts; no application source was changed. |
| E-013 | domain-audit-validation | Venv commands: `condamad_domain_audit_validate.py` and `condamad_domain_audit_lint.py` on this audit folder | `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1203` | PASS | `--explain-audit` was not needed because validation and lint passed. |

## Reproducible E-004/E-005 summary

```text
free: messages=3; roles=['system', 'developer', 'user']; chars={system:197, developer_total:6068, user:3599}
free: facts counts positions=2, houses=0, aspects=3, dominants=1, angles=1
free: signals hints=2, codes=3; allowed_fact_groups=3; section_codes=4
free: provider_params={'temperature': 0.7, 'max_output_tokens': 4000, 'reasoning_effort': None, 'verbosity': None}; shaping_plan=free; depth=free_short; precision=orientation
basic: messages=4; roles=['system', 'developer', 'developer', 'user']; chars={system:197, developer_total:12070, user:7192}
basic: facts counts positions=7, houses=4, aspects=8, dominants=2, angles=2
basic: signals hints=3, codes=3; allowed_fact_groups=7; section_codes=5
basic: provider_params={'temperature': 0.55, 'max_output_tokens': 16000, 'reasoning_effort': None, 'verbosity': None}; shaping_plan=basic; depth=basic_contextual; precision=contextual
premium: messages=4; roles=['system', 'developer', 'developer', 'user']; chars={system:197, developer_total:29881, user:11183}
premium: facts counts positions=11, houses=12, aspects=14, dominants=3, angles=2
premium: signals hints=4, codes=5; allowed_fact_groups=8; section_codes=9
premium: provider_params={'temperature': 0.5, 'max_output_tokens': 32000, 'reasoning_effort': 'low', 'verbosity': 'high'}; shaping_plan=premium; depth=premium_deep; precision=detailed
```
