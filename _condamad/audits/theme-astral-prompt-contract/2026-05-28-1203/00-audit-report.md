# Audit theme-astral-prompt-contract - CS-362

## Domain Closure Status

Status: `open`.

The audited domain is the read-only contract shape of the current natal provider JSON payloads for plans `free`, `basic`, and `premium`. No provider JSON, backend runtime, backend tests, frontend files, migrations, prompt docs, or prompt seeds were changed.

## Prior Audit And Story History Consulted

| Item | Status | Evidence | Current classification |
|---|---|---|---|
| `_condamad/stories/CS-362-audit-contrats-prompt-theme-astral-json-provider-actuels/00-story.md` | current source story | E-001 | active scope |
| `_story_briefs/cs-362-audit-contrats-prompt-theme-astral-json-provider-actuels.md` | source brief | E-001 | active scope |
| `_condamad/stories/regression-guardrails.md` | guardrail registry, including RG-002 and RG-149 | E-002 | relevant invariants consulted |
| `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1152/` | latest same-domain audit, CS-361 | E-003 | still-active adjacent findings; this audit adds provider JSON contract evidence for CS-363 |
| `_condamad/stories/CS-363-*` through `_condamad/stories/CS-368-*` | downstream target stories | E-003 | ready-to-dev follow-up context; not implemented here |

## Closure Analysis

- Active findings remain: F-001, F-002, F-003, F-004 and F-005.
- Closed findings from CS-361: none. CS-361 remains active because this CS-362 audit supplies a different prerequisite: current provider JSON contract comparison.
- Complete active implementation surface: none in CS-362. Follow-up implementation/architecture surfaces are routed to CS-363 through CS-368.
- Governance/test surfaces: audit files under `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1203/`.
- Deferred non-domain context: backend runtime edits, provider JSON regeneration, prompt seed edits, frontend, DB migrations, real provider calls, auth and UI behavior are out of scope.

## Executive summary

The broad claim that top-level and nested provider structures are not stable across plans is only partially valid. Top-level keys are stable across `free`, `basic`, and `premium`; the user payload always carries `llm_astrology_input_v1` with the same four top-level blocks `facts`, `limits`, `shaping`, and `signals`; `response_format` and `provider_parameters` keep the same key families. However, the message envelope is not stable because `free` has three messages while `basic` and `premium` have four, and the plan-specific quantity of facts, hints, developer text, user payload text and provider parameters diverges materially.

The plan commercial is visible twice in the current provider payload family: as top-level `plan` metadata in every example and as prompt-visible `shaping.plan` inside the user message. Runtime/audit-only families such as `audit_excluded_from_prompt`, `projection_hash`, `llm_input_hash`, `provider_response`, `provenance`, `chart_json`, and `natal_data` are listed as excluded, but that exclusion list itself is present in the provider payload artifact. `source_metadata` is inside prompt-visible `facts` and exposes birth/context/calculation metadata, including fields that should be reviewed as backend-only for the future contract.

The current `basic` payload confirms the brief risk: its first developer message contains premium-oriented instructions inherited from seed prompt material. The payload also duplicates material: the rendered developer prompt embeds the same `llm_astrology_input_v1` data that is also sent as the user message. These are contract-shape and payload-hygiene findings for CS-363/CS-366, not code changes for CS-362.

## Tableau comparatif free/basic/premium

| Plan | Structure status | Value status | LLM visibility | Evidence | CS-363 recommendation |
|---|---|---|---|---|---|
| `free` | top-level stable; message envelope has 3 messages | `use_case=natal_interpretation_short`, model `gpt-4o-mini`, max tokens 4000 | prompt-visible `shaping.plan=free`; no persona developer message | E-004, E-005 | keep stable skeleton; replace plan-visible labels with backend-owned delivery profile |
| `basic` | top-level stable; message envelope has 4 messages | `use_case=natal_interpretation`, model `gpt-4o-mini`, max tokens 16000 | prompt-visible `shaping.plan=basic`; persona present; first developer message contains premium language | E-004, E-005, E-008 | keep skeleton; replace commercial plan; remove premium-oriented basic instructions |
| `premium` | top-level stable; message envelope has 4 messages | `use_case=natal_interpretation`, model `gpt-5`, max tokens 32000, reasoning/verbosity set | prompt-visible `shaping.plan=premium`; persona present | E-004, E-005 | keep skeleton; express depth through backend-owned profile, not commercial plan string |

## Divergences structurelles

| Surface | Structure status | Evidence | Conclusion |
|---|---|---|---|
| Top-level provider payload keys | stable | E-004 | Same keys for `use_case`, `plan`, `mode`, `provider_call_performed`, `generation_kind`, `model`, `messages`, `response_format`, `provider_parameters`, `audit_excluded_from_prompt`. |
| `messages` role sequence | divergent | E-004 | `free` has `system/developer/user`; `basic` and `premium` have `system/developer/developer/user`. |
| User payload root | stable | E-004 | User content starts with `llm_astrology_input_v1:` and parses to the same root blocks. |
| `llm_astrology_input_v1` blocks | stable | E-004 | All plans have `facts`, `limits`, `shaping`, and `signals`. |
| `facts`, `signals`, `limits`, `shaping` key families | stable by key, divergent by cardinality | E-004, E-005 | Key families match; array counts and selected data differ by plan. |
| `response_format` schema property keys | stable | E-004 | All plans expose `title`, `summary`, `sections`, `highlights`, `advice`, `evidence`. |
| `provider_parameters` key family | stable | E-004 | All plans expose `temperature`, `max_output_tokens`, `reasoning_effort`, `verbosity`; values differ. |

## Divergences de quantite de donnees

| Quantity axis | free | basic | premium | Evidence | Contract reading |
|---|---:|---:|---:|---|---|
| Message count | 3 | 4 | 4 | E-005 | Structural divergence caused by persona/developer message. |
| Developer total chars | 6068 | 12070 | 29881 | E-005 | Volume divergence by plan; expected as product depth, but should not duplicate full user payload. |
| User message chars | 3599 | 7192 | 11183 | E-005 | Volume divergence by plan; expected if fact selection is intentional. |
| `facts.positions` | 2 | 7 | 11 | E-005 | Plan-specific variability. |
| `facts.houses` | 0 | 4 | 12 | E-005 | Plan-specific variability; `free` lacks house list despite birth time metadata. |
| `facts.major_aspects` | 3 | 8 | 14 | E-005 | Plan-specific variability. |
| `facts.dominants` | 1 | 2 | 3 | E-005 | Plan-specific variability. |
| `signals.interpretation_hints` | 2 | 3 | 4 | E-005 | Plan-specific variability. |
| `signals.interpretive_signal_codes` | 3 | 3 | 5 | E-005 | Premium adds extra signal codes. |
| `shaping.llm_input_selection.allowed_fact_groups` | 3 | 7 | 8 | E-005 | Delivery selection grows by plan. |
| `shaping.llm_input_selection.section_codes` | 4 | 5 | 9 | E-005 | Output section contract grows by plan. |

## Donnees inutiles ou backend-only

| Data family | Current location | LLM visibility | Matrix outcome | Evidence | Rationale |
|---|---|---|---|---|---|
| Commercial plan | top-level `plan`; prompt-visible `shaping.plan` | visible | move backend-only / replace | E-004, E-005 | The LLM needs delivery depth, not commercial package labels. |
| Runtime metadata | top-level `use_case`, `mode`, `generation_kind`, `model`, `provider_call_performed`; `provider_parameters` | provider artifact metadata | move backend-only | E-004, E-005 | Provider call assembly needs it; prompt text should not. |
| Audit exclusion list | top-level `audit_excluded_from_prompt` | provider artifact metadata | move backend-only | E-007 | It lists hidden fields but should not be in the future provider payload contract. |
| Hashes | `audit_excluded_from_prompt` entries `projection_hash`, `llm_input_hash` | listed only, not user block value | move backend-only | E-007 | Good exclusion intent; future contract should not send the exclusion registry. |
| Provenance/provider response | `audit_excluded_from_prompt` entries | listed only, not user block value | move backend-only | E-007 | Validation/audit owner only. |
| `chart_json` and `natal_data` | `audit_excluded_from_prompt` entries | listed only, not prompt-visible carrier | drop-from-provider-payload | E-007 | Must remain absent from provider prompt payload. |
| Source metadata | `facts.source_metadata` inside user message | prompt-visible | replace / move backend-only | E-004, E-005 | Birth context may be needed in normalized form; calculation engine, Julian day, SwissEph version and timezone details are backend-only unless a target contract justifies them. |
| Trace/debug | no direct hit in current examples | absent | keep absent | E-007 | No trace/debug payload observed in the three files. |

## Donnees manquantes pour la redaction

| Needed family | Current state | LLM visibility | Matrix outcome | Evidence | CS-363 recommendation |
|---|---|---|---|---|---|
| Delivery profile | encoded as `editorial_depth_profile`, `precision_level`, `output_expectations`, and section/fact selection | visible but mixed with commercial plan | replace | E-005 | Define a non-commercial `delivery_profile` contract. |
| Feature context | encoded as `module=natal_theme`, `use_case`, and prompt prose | partial | replace | E-004, E-006 | Define explicit `feature_context` independent from runtime use case names. |
| Astrologer voice | persona developer message exists in `basic/premium`, absent in `free` | divergent | keep / replace | E-004, E-006 | Keep as a controlled `astrologer_voice` block when required; avoid plan leakage. |
| Interpretation material | facts and short `interpretation_hints`, no table-derived material block | partial | replace | E-003, E-005 | CS-363/CS-365 should define `interpretation_material`. |
| Output contract | `response_format` schema plus prompt instructions | split | keep / replace | E-004, E-008 | Keep schema, move durable output obligations into a versioned contract. |

## Incoherences de prompt

| Incoherence | Current state | Evidence | Impact | Recommendation |
|---|---|---|---|---|
| Basic carries premium-oriented instructions | `basic` developer message contains premium language; seed files contain premium sections used by current prompt material. | E-008 | The basic provider may be instructed toward premium density/depth. | Remove commercial/premium labels from basic prompt path; express depth through backend-owned delivery profile. |
| Developer/user duplication | Developer prompt embeds rendered `llm_astrology_input_v1` data, and the user message sends `llm_astrology_input_v1:` again. | E-004, E-006 | Payload volume grows and creates two possible sources for the same data. | Pick one canonical data carrier in CS-363/CS-366. |
| Plan-specific values can look like structure drift | Keys are stable but counts and values differ heavily. | E-004, E-005 | Future stories may overcorrect by forcing identical content instead of stable shape. | Preserve intended variability, stabilize key shape and ownership labels. |

## Matrice keep / move backend-only / replace / drop-from-provider-payload

| Surface | Current status | Recommendation | Evidence |
|---|---|---|---|
| Stable provider skeleton keys | Same across plans | keep | E-004 |
| `messages` as final provider carrier | Active, role count differs | keep with explicit role policy | E-004 |
| Prompt-visible `facts`, `signals`, `limits`, `shaping` root | Same across plans | keep as compatibility input to CS-363; replace with target `theme_astral_llm_input_v1` when defined | E-004 |
| Commercial `plan` label | Visible top-level and prompt-visible in `shaping.plan` | move backend-only / replace | E-004, E-005 |
| `editorial_depth_profile`, `precision_level`, `output_expectations` | Prompt-visible delivery signals | replace with non-commercial delivery profile | E-005 |
| `llm_input_selection.allowed_fact_groups` and `section_codes` | Prompt-visible plan variability | keep / preserve variability | E-005 |
| `source_metadata` | Prompt-visible fact metadata | replace: split birth context from backend-only calculation metadata | E-005 |
| `audit_excluded_from_prompt` | Top-level provider artifact metadata | move backend-only | E-007 |
| `projection_hash`, `llm_input_hash`, `provider_response`, `provenance`, `observability`, `replay_snapshot` | Exclusion-list entries | drop-from-provider-payload while preserving backend audit ownership | E-007 |
| `chart_json`, `natal_data` | Exclusion-list entries | drop-from-provider-payload | E-007 |
| Trace/debug fields | Not observed | keep absent | E-007 |
| Basic premium instructions | Present in basic prompt material | drop-from-provider-payload / replace with basic delivery profile | E-008 |
| `response_format` JSON schema | Stable | keep, version as output contract | E-004 |
| `provider_parameters` | Stable keys, plan-specific values | move backend-only | E-004, E-005 |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1203/02-audit-json-provider-theme-astral-actuels.md` | used | E-001 | Explicit CS-362 deliverable. | New audit artifact. |
| `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/free-provider-payload.json` | used | E-004, E-005 | Required provider payload evidence for free plan. | Existing file inspected only. |
| `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/basic-provider-payload.json` | used | E-004, E-005, E-008 | Required provider payload evidence for basic plan and premium-in-basic finding. | Existing file inspected only. |
| `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/premium-provider-payload.json` | used | E-004, E-005 | Required provider payload evidence for premium plan. | Existing file inspected only. |
| `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/intermediate-data.json` | used | E-001 | Required context source for generation scenario. | Not deeply revalidated beyond availability in this audit. |
| `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` | used | E-006 | Documents current prompt construction and backend-only exclusions. | Documentation evidence, not runtime proof by itself. |
| `backend/app/domain/llm/runtime/gateway.py` `_prompt_visible_llm_astrology_input`, `_without_prompt_excluded_keys`, `build_user_payload`, `_call_provider` | used | E-006 | Runtime owner for prompt-visible filtering and provider handoff. | Source scan only; no provider call. |
| `backend/app/ops/llm/bootstrap/seed_29_prompts.py` | used | E-008 | Seed prompt evidence for current premium-oriented prompt text. | Bootstrap source, not direct DB row inspection. |
| `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py` | used | E-008 | Seed prompt evidence for premium-density instructions. | Bootstrap source, not direct DB row inspection. |
| `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | test-only | E-009 | Existing boundary test for prompt-visible input. | Execution targeted separately. |
| `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` | test-only | E-009 | Existing architecture guard for payload boundaries. | Execution targeted separately. |
| `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` | test-only | E-009 | Existing unit guard for LLM input contract. | Execution targeted separately. |
| `_condamad/stories/regression-guardrails.md` | used | E-002 | Guardrail registry required by domain auditor. | No guardrail update authorized by CS-362. |

## Findings Summary

- High: F-001, F-002.
- Medium: F-003, F-004, F-005.
- Critical/Low/Info: none.

## Recommandations pour CS-363

1. Define `theme_astral_llm_input_v1` with stable top-level/nested keys, while preserving explicit plan-specific value variability.
2. Replace prompt-visible commercial `plan` with backend-owned `delivery_profile`, `feature_context`, `astrologer_voice`, `interpretation_material`, and `output_contract` decisions.
3. Split birth context from calculation/runtime metadata; only LLM-needed context should remain prompt-visible.
4. Choose one canonical carrier for chart data. The current developer/user duplication should not survive the target contract.
5. Keep `response_format` semantics, but version output contract ownership so prompt prose and JSON schema cannot drift independently.
6. Preserve absence of trace/debug and keep audit hashes/provenance/provider response outside provider payloads.
7. Add specific guards for basic-not-premium prompt instructions and for absence of commercial plan strings in prompt-visible user payload.

## Validation Plan

Python validation commands must run after `.\.venv\Scripts\Activate.ps1`. This audit validated the JSON examples, executed the domain-auditor validation/lint scripts, and ran targeted scans listed in `01-evidence-log.md`.
