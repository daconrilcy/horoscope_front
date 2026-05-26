# Legacy Fallbacks - CS-327

| Surface | Class | Evidence | Injection impact | Required decision |
|---|---|---|---|---|
| `chart_json` in canonical natal `input_schema` | `legacy fallback` | E-007, E-008 | Blocks first-class validation of `llm_astrology_input`; current readiness remains tied to one object field. | Decide whether `chart_json` is replaced, wrapped, or kept as compatibility-only. |
| `chart_json` in bootstrap prompts | `legacy fallback` | E-010, E-011 | Prompt copy treats `chart_json` as the source unique/exclusive; adding new blocks without prompt governance would be ad hoc. | Defer prompt rewrite until contract owner exists. |
| `natal_data` to `chart_json` validation substitution | `legacy fallback` | E-012, E-013, E-016 | Runtime can prove schema validity through a carrier alias, not through a named structured input. | Align validation payload after schema decision. |
| `astro_context` | `partiel` | E-012, E-013 | Carries astral-point context, but not a complete facts/signals/limits/proofs contract. | Keep as data context only unless target contract explicitly includes it. |
| `fallback_target_key="natal_interpretation_short"` | `legacy fallback` | E-007, E-008, E-022 | Output fallback is blocked for supported features, but config fallback target can obscure readiness analysis. | Keep separate from target input compatibility. |
| `PROMPT_FALLBACK_CONFIGS` | `compatible` | E-021 | Catalog fallback configs are limited to `test_natal` and `test_guidance`, not active natal production configs. | No implementation story from this audit. |

Evidence keywords: `chart_json`, `natal_data`, `astro_context`, `llm_astrology_input`.
