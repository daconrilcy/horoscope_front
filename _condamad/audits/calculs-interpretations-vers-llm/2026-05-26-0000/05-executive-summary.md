# Executive Summary - Calculs Interpretations Vers LLM

The audit found one High finding, two Medium findings and one Low finding.

Current natal LLM execution input is assembled from `chart_json`, `natal_data`, `evidence_catalog` and `astro_context`. The first three are tied to the public/historical chart JSON owner; `astro_context` is a transition astral-point context.

Recent owners are present and tested or source-backed: `ChartObjectRuntimeData`, `CalculationGraph`, `ChartInterpretationInputBuilder`, `structured_facts_v1`, `client_interpretation_projection_v1` and `AINarrativeInputContract`. They are not currently invoked in the scoped natal LLM path.

Recommended next action: a story-writer pass should choose the canonical LLM input owner, preferably around `AINarrativeInputContract` or an explicit derivative, then map every `NatalExecutionInput` field and guard against raw runtime exposure.
