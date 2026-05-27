<!-- Commentaire global: audit bloc par bloc des sources astrologiques natales envoyees au prompt LLM moderne. -->

# CS-346 - Natal Astrology Input Audit

## Executive Summary

`llm_astrology_input_v1` has a traceable runtime source chain:

```text
NatalInterpretationService
  -> StructuredFactsV1Builder
  -> AINarrativeInputBuilder
  -> ClientInterpretationProjectionV1Builder
  -> LLMAstrologyInputV1Builder
  -> AIEngineAdapter.generate_natal_interpretation
  -> LLMGateway prompt-visible projection
```

No application code was changed. The audited source shows a single canonical LLM input builder, stable role buckets, and existing tests for shape, hash, evidence, prompt boundary, and legacy carrier extinction.

## Builder Source Map

| Owner | Source input | Output | Runtime role | Evidence | Gap |
|---|---|---|---|---|---|
| `StructuredFactsV1Builder` | `NatalResult` and chart metadata | `structured_facts_v1` | prompt-visible source for `facts` | E-005, E-007, E-014 | no gap |
| `AINarrativeInputBuilder` | `NatalResult` interpretation-ready signals | `AINarrativeInputContract` | prompt-visible source for `signals` | E-006, E-014 | no gap |
| `ClientInterpretationProjectionV1Builder` | `structured_facts_v1` plus plan | `client_interpretation_projection_v1` | shaping-only input | E-007, E-014 | no gap |
| `LLMAstrologyInputV1Builder` | facts, narrative contract, client projection | `llm_astrology_input_v1` | full runtime object | E-004, E-005, E-014 | no gap |
| `projection_hash.py` | JSONable projection payloads | canonical SHA-256 hashes | hash helper | E-007, E-011 | no gap |
| `NatalInterpretationService` | natal calculation result and user plan | `NatalExecutionInput` with rich input | runtime assembly and audit owner | E-008, E-010 | no gap |
| `AIEngineAdapter` | `NatalExecutionInput` | `LLMExecutionRequest` context | runtime handoff | E-009, E-010 | no gap |
| `LLMGateway` | execution context | prompt-visible payload | prompt boundary owner | E-009, E-012 | no gap |

## Block-By-Block Ownership Matrix

| block | owner | source input | runtime role | prompt visibility | hash impact | evidence | gap |
|---|---|---|---|---|---|---|---|
| facts | `LLMAstrologyInputV1Builder._facts_block` | `structured_facts_v1.structural_facts` and dominants | prompt-visible | visible | included in `llm_input_hash` | E-005, E-014 | no gap |
| signals | `LLMAstrologyInputV1Builder._signals_block` | `AINarrativeInputContract` | prompt-visible | visible | included in `llm_input_hash` | E-006, E-014 | no gap |
| limits | `LLMAstrologyInputV1Builder._limits_block` | missing data and readiness flags | prompt-visible | visible | included in `llm_input_hash` | E-005, E-014 | no gap |
| shaping | `LLMAstrologyInputV1Builder._shaping_block` | `client_interpretation_projection_v1` | prompt-visible | visible | included in `llm_input_hash` | E-007, E-014 | no gap |
| evidence | `LLMAstrologyInputV1Builder._evidence_block` | compact `evidence_refs` and validation result | validation-only | not visible | excluded from `llm_input_hash` | E-005, E-011, E-012 | no gap |
| provenance | `LLMAstrologyInputV1Builder._provenance_block` | source versions, hashes, prompt ref | audit-only | not visible | contains `projection_hash` and `llm_input_hash`; not prompt material | E-005, E-011, E-012 | no gap |
| exclusions | `LLMAstrologyInputV1Builder` | `EXCLUDED_SURFACES` constant | audit-only classification | not visible | excluded from `llm_input_hash` | E-004, E-014 | no gap |
| data_roles | `LLM_ASTROLOGY_INPUT_DATA_ROLES` | role constants | validation contract | not visible | excluded from `llm_input_hash` | E-004, E-012 | no gap |

## Prompt-Visible Versus Backend-Only Classification

| Surface | Classification | Owner | Evidence | Notes |
|---|---|---|---|---|
| `facts` | prompt-visible | `llm_astrology_input_v1.py` | E-004, E-005 | Source is `structured_facts_v1`, not client projection. |
| `signals` | prompt-visible | `llm_astrology_input_v1.py` | E-006 | Source is `AINarrativeInputContract`. |
| `limits` | prompt-visible | `llm_astrology_input_v1.py` | E-005, E-014 | Missing data remains visible without raw carriers. |
| `shaping` | prompt-visible | `llm_astrology_input_v1.py` | E-007 | Source is client projection metadata only. |
| `request_id`, `trace_id` | runtime-only | runtime request | E-004 | Not part of prompt-visible hash material. |
| `chart_json`, `natal_data` | forbidden carrier | runtime legacy fields | E-004, E-009, E-013 | Runtime-only/excluded for modern natal prompt. |
| `evidence`, `grounding_status`, `validation_owner` | validation-only | evidence validation owner | E-004, E-011, E-012 | Kept for backend validation and audit. |
| `projection_hash`, `llm_input_hash` | audit-only | provenance/hash helpers | E-008, E-011 | Persisted/read by service audit helpers. |
| `provider_response`, `persisted_answer` | audit-only | runtime/persistence | E-004 | Classified by role contract, not prompt material. |

## Hash Policy

`PROMPT_INFLUENCING_BLOCKS` is `("facts", "signals", "limits", "shaping")`. `build_llm_input_hash_material` serializes only those blocks, and `compute_projection_hash` applies canonical JSON plus SHA-256. `projection_hash` is derived from `structured_facts_v1` unless supplied; `llm_input_hash` is derived from the prompt-visible material. Evidence E-004, E-007, E-008, E-011, and E-014 prove the current policy.

## Evidence Policy

`_evidence_block` validates compact `evidence_refs` through `validate_evidence_refs_by_section`. The full object keeps `evidence_refs`, `grounding_status`, and `validation_owner`; gateway prompt projection excludes these fields. `NatalInterpretationService` persists evidence refs and grounding status from the full `llm_astrology_input_v1`, not from prompt material. Evidence E-005, E-008, E-011, and E-012 prove the boundary.

## Runtime Branch Points

| Step | Owner | Symbol | Evidence | Classification |
|---|---|---|---|---|
| rich input assembly | natal service | `_build_llm_astrology_input_v1` | E-008, E-010 | used |
| execution input construction | natal service | `NatalExecutionInput` with `llm_astrology_input_v1` | E-008 | used |
| adapter handoff | runtime adapter | `generate_natal_interpretation` | E-009, E-010 | used |
| prompt filtering | gateway | `_prompt_visible_llm_astrology_input` | E-009, E-012 | used |
| nested audit-key removal | gateway | `_without_prompt_excluded_keys` | E-009, E-012 | used |

## Legacy Carrier Classification

`chart_json` and `natal_data` are forbidden legacy carriers for the modern natal prompt. They still exist in non-domain contexts such as legacy/runtime context, admin samples, tests, and non-modern paths, but the audited modern natal flow classifies them as runtime-only or excluded. Evidence E-004, E-009, E-012, and E-013 prove they are not prompt-visible when `llm_astrology_input_v1` exists.

## Existing Tests And Gaps

| Test | Result | Proves | Gap |
|---|---|---|---|
| `tests/unit/domain/astrology/test_llm_astrology_input_v1.py` | PASS, 9 passed | shape, owners, disjoint blocks, exclusions, public API absence | no gap |
| `tests/unit/domain/astrology/test_llm_astrology_input_hash.py` | PASS, included in 5 passed | hash stability and prompt-visible invalidation | no gap |
| `tests/unit/domain/astrology/test_llm_astrology_input_evidence.py` | PASS, included in 5 passed | evidence refs and grounding status policy | no gap |
| `tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | PASS, included in 10 passed | prompt payload and local provider handoff boundary | no external provider call by design |
| `tests/architecture/test_llm_astrology_input_payload_boundaries.py` | PASS, included in 10 passed | AST role reuse and audit-only exclusions | no gap |
| `tests/integration/test_llm_legacy_extinction.py` | PASS, 7 passed with `--long` | modern contracts reject legacy carriers | default fast run deselects integration tests |

## Gap Classification

No implementation gap remains for the audited domain. The only operational caveat is validation ergonomics: integration legacy guards require `pytest --long`, which is repository policy rather than a CS-346 implementation defect.
