# Executive Summary - Pipeline Prompt LLM Natal

The current natal LLM pipeline carries rich runtime context into `LLMGateway`, but only `chart_json` is prompt-visible by default. If the rendered developer prompt contains `{{chart_json}}`, that placeholder owns injection; otherwise the gateway appends `Technical Data: {chart_json}` to the user data block.

`natal_data`, `astro_context`, `plan`, `level`, `module` and `variant_code` are runtime-only for the audited `build_user_payload` path. `evidence_catalog` is validation-only in current evidence: it is passed through flags and consumed by `validate_output`, not by message composition.

The main risk is architectural: recent canonical interpretation owners are absent from this prompt path, while `/users`, `free_short`, schema compatibility and fallback guardrails remain active. Recommended next action is to choose the canonical LLM input owner before implementing prompt or runtime changes.

