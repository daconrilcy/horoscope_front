# Executive Summary - Configuration Prompts Placeholders Input Schema

The audited LLM natal configuration is not ready to receive a modern structured astrology input contract as a first-class runtime/configuration shape.

Active natal use cases and thematic modules still declare `chart_json` in `input_schema` and prompt placeholders. Runtime assembly currently builds `chart_json`, `natal_data`, `evidence_catalog` and `astro_context`; gateway validation can satisfy `chart_json` from either `natal_data` or `chart_json`. No `llm_astrology_input`, `facts`, `signals`, `limits` or `proofs` contract exists in the scoped LLM configuration/runtime/orchestration paths.

Findings by severity:

- High: 1 (`F-001`)
- Medium: 3 (`F-002`, `F-003`, `F-004`)
- Low/Critical: 0

Story candidates:

- 3 candidates, with one full-closure architecture candidate blocked by the target input schema decision and two dependent blocked follow-ups.

No backend application or test file was changed by this audit.
