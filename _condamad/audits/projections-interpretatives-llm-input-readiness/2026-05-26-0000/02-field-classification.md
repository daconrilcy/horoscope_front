# Field Classification

| contract | field | classification | hashable | current-llm-use | readiness | rationale |
|---|---|---|---|---|---|---|
| `structured_facts_v1` | `projection_id`, `contract_version` | audit | yes | available-not-injected | ready | Stable identity for projection and hash input. |
| `structured_facts_v1` | `source_versions` | audit | yes | available-not-injected | ready | Provenance owner for runtime/input/reference versions. |
| `structured_facts_v1` | `structural_facts.positions` | factuel | yes | available-not-injected | ready | Calculated positions with code, type, longitude, sign, house and source. |
| `structured_facts_v1` | `structural_facts.houses` | factuel | yes | available-not-injected | ready | House position facts when birth time supports them. |
| `structured_facts_v1` | `structural_facts.major_aspects` | factuel | yes | available-not-injected | ready | Major aspect facts with participants, angle, orb and strength level. |
| `structured_facts_v1` | `interpretive_signals.*_codes` | signal interpretatif | yes | available-not-injected | ready | Pre-narrative identifiers, not prose. |
| `structured_facts_v1` | `dominants` | signal interpretatif | yes | available-not-injected | ready | Calculated dominance summary with scores/ranks; useful but should remain bounded. |
| `structured_facts_v1` | `missing_data` | audit | yes | available-not-injected | ready | Explicit incompleteness and empty collections. |
| `structured_facts_v1` | `excluded_surfaces` | exclusion | no | available-not-injected | ready | Names raw/debug/provider/prompt surfaces intentionally absent. |
| `structured_facts_v1` | `hash_input` | audit | yes | available-not-injected | ready | Canonical digest boundary. |
| `beginner_summary_v1` | `allowed_fields`, `audience`, `state` | shaping editorial | partial | product-only | partial | Public display contract and audience gates. |
| `beginner_summary_v1` | `main_signs`, `ascendant`, `dominant_house` | signal interpretatif | partial | product-only | partial | Reduced B2C fields derived from facts. |
| `beginner_summary_v1` | `display_messages`, `summary_items`, `dominant_themes` | shaping editorial | partial | product-only | missing | Client wording/labels, not factual prompt source. |
| `beginner_summary_v1` | `excluded_surfaces` | exclusion | no | product-only | ready | Excludes audit, debug, evidence_refs, full facts and technical scores. |
| `client_interpretation_projection_v1` | `llm_input_selection` | shaping editorial | partial | product-only | partial | Product selection hints, not canonical prompt payload. |
| `client_interpretation_projection_v1` | `editorial_depth_profile`, `precision_level` | shaping editorial | partial | product-only | partial | Plan/depth control, not fact. |
| `client_interpretation_projection_v1` | `frontend_visibility_rules` | shaping editorial | partial | product-only | missing | UI visibility, not LLM injection data. |
| `client_interpretation_projection_v1` | `sections`, `support_elements` | signal interpretatif | partial | product-only | partial | Labels and section skeletons only. |
| `client_interpretation_projection_v1` | `audit_input`, `excluded_audit_surfaces` | audit | partial | product-only | partial | Audit-oriented section ids and excluded audit internals. |
| `client_interpretation_projection_v1` | `excluded_surfaces` | exclusion | no | product-only | ready | Excludes raw runtime, provider responses and prompt payloads. |
| `AINarrativeInputContract` | `structural_facts` | factuel | partial | available-not-injected | ready | Compact factual identifiers from interpretation input. |
| `AINarrativeInputContract` | `interpretive_signals` | signal interpretatif | partial | available-not-injected | ready | Pre-narrative signal code groups. |
| `AINarrativeInputContract` | `readiness_flags` | audit | no | available-not-injected | ready | Builder-local completeness booleans. |
| `AINarrativeInputContract` | `source_versions` | audit | partial | available-not-injected | ready | Provenance of runtime, graph, governance and reference versions. |
| `AINarrativeInputContract` | `masking_policy` | exclusion | no | available-not-injected | ready | Redaction/PII exclusion policy. |
| `AINarrativeInputContract` | `public_projection_links` | audit | partial | available-not-injected | ready | Links projection identity without embedding public payload. |
| `AINarrativeInputContract` | `debug_context` | debug | no | available-not-injected | partial | Bounded counters only; not narrative substance. |
| `narrative_answer_audit_v1` | `projection_hash`, `llm_input_hash` | audit | yes | audit-only | ready | Digest anchors for projection/input evidence. |
| `narrative_answer_audit_v1` | `prompt_version`, `prompt_ref`, `prompt_snapshot_ref`, `provider`, `model` | audit | no | audit-only | ready | Operational metadata, not prompt text. |
| `narrative_answer_audit_v1` | `evidence_refs`, `grounding_status` | audit | partial | audit-only | ready | Grounding evidence and validation status. |
| `narrative_answer_audit_v1` | `raw provider responses`, `prompt payloads` | exclusion | no | audit-only | ready | Explicitly absent/forbidden by sensitive data policy and audit tests. |

