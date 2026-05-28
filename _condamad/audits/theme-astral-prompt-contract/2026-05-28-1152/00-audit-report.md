# Audit theme-astral-prompt-contract - CS-361

## Domain Closure Status

Status: `open`.

The audited domain is the read-only prompt contract diagnostic for interpretive astrology material before LLM/provider handoff. The current runtime already carries calculated facts and compact symbolic signal codes, but rich table/reference/seed text is not proven prompt-visible in the provider payloads. No application implementation file was changed.

## Prior Audit And Story History Consulted

| Item | Status | Evidence | Current classification |
|---|---|---|---|
| `_condamad/stories/CS-361-audit-usage-tables-textes-interpretation-moteur-astrologique/00-story.md` | current source story | E-001 | active scope |
| `_story_briefs/cs-361-audit-usage-tables-textes-interpretation-moteur-astrologique.md` | source brief | E-001 | active scope |
| `_condamad/stories/regression-guardrails.md` | guardrail registry, including RG-002, RG-022 and RG-149 | E-001 | relevant invariants consulted |
| `_condamad/audits/astro-calculation-interpretation-boundary/**` | prior nearby audit family | E-002 | non-domain context for this prompt-contract audit |
| `_condamad/audits/projections-interpretatives-llm-input-readiness/**` | prior nearby audit family | E-002 | non-domain context for this prompt-contract audit |
| `_condamad/stories/CS-363-*` through `_condamad/stories/CS-368-*` | downstream target stories | E-002 | ready-to-dev follow-up candidates already exist |

## Closure Analysis

- Active findings remain: F-001, F-002, F-003 and F-004.
- Closed findings: none in this audit run; CS-361 is the first report under `_condamad/audits/theme-astral-prompt-contract/` in this workspace.
- Complete active implementation surface: no CS-361 implementation surface. Follow-up implementation surfaces are routed to CS-363 through CS-368.
- Governance/test surfaces: audit files under `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1152/` and evidence under the CS-361 story folder.
- Deferred non-domain context: frontend, auth, migrations, DB schema mutation, prompt editing, provider calls and UI are out of scope.

## Executive summary

The current natal LLM path is structurally coherent: `interpretation_service._build_llm_astrology_input_v1` builds `StructuredFactsV1Builder`, `AINarrativeInputBuilder`, `ClientInterpretationProjectionV1Builder`, then `LLMAstrologyInputV1Builder`; `LLMGateway.build_user_payload` sends only prompt-visible `facts`, `signals`, `limits` and `shaping`. This proves a controlled handoff, not a rich interpretive text handoff.

Rich interpretive material exists in DB models, seed JSON, reference repositories and documentation: sign profiles, house/planet/aspect interpretation profiles, fixed star keywords, dignity/condition descriptions, interpretation adapter rules, and advanced condition profile catalog entries. The runtime path that reaches provider payloads mostly reduces these to fact lists, signal codes and short `interpretation_hints` examples. That leaves a product gap: provider prompts can be fact-rich yet editorially dependent on the LLM's general knowledge.

## Inventaire des sources de textes

| Source | Family | Owner | Usage status | Runtime path | Evidence | Gap | Story candidate |
|---|---|---|---|---|---|---|---|
| `backend/app/infra/db/models/reference.py` `AstralSignProfileModel` | sign | DB model and runtime reference repository | used | source-to-engine, partial source-to-LLM-input as profile balance codes | E-004, E-005 | rich keywords not provider-visible | CS-365 |
| `docs/db_seeder/astrology/astral_sign_keywords.json` | sign | seed/reference material | seed-only | not active in inspected provider payload | E-004, E-006 | dormant source | CS-365 |
| `backend/app/infra/db/models/interpretation_reference.py` `AstralHouseInterpretationProfileModel` | house | DB model | seed-only | not traced into `llm_astrology_input_v1` provider payload | E-004, E-005 | dormant source | CS-365 |
| `backend/app/infra/db/models/interpretation_reference.py` `AstralPlanetInterpretationProfileModel` | planet | DB model | seed-only | not traced into `llm_astrology_input_v1` provider payload | E-004, E-005 | dormant source | CS-365 |
| `backend/app/infra/db/models/interpretation_reference.py` `AstralAspectInterpretationProfileModel` | aspect | DB model | seed-only | aspect runtime facts reach provider, profile text not proven | E-004, E-005 | lost before LLM | CS-365 |
| `backend/app/infra/db/models/reference.py` `AstralPointInterpretationKeywordModel` | pattern | DB model and repository | used | used by astral point interpretation path, not proven in natal provider examples | E-004, E-005 | unknown prompt reach | CS-363 |
| `backend/app/infra/db/models/dignity_reference.py` dignity tables | dignity | runtime reference repository and dignity calculators | used | source-to-engine, codes/scores reach interpretation facts | E-004, E-005 | text descriptions not provider-visible | CS-365 |
| `backend/app/infra/db/models/dignity_reference.py` `AstralInterpretationAdapterRuleModel` | pattern | runtime reference repository | used | interpretation adapter signals exist in domain tests and repository | E-004, E-007 | signal labels/codes, not rich text | CS-363 |
| `backend/app/domain/astrology/interpretation/advanced_conditions/advanced_condition_profile_catalog.py` | advanced condition | static domain catalog | used | resolved as symbolic profiles, no final prose handoff proven | E-004, E-005 | text-like profiles not selected into provider payload | CS-365 |
| `docs/recherches astro/**` | mixed | reference documents | unused | not runtime-loaded by inspected path | E-004 | reference-only material | CS-363 |
| `_condamad/examples/prompt-generation-cartography/*/*provider-payload.json` | provider JSON | prompt cartography examples | used | provider-payload evidence only | E-006 | shows short hints, not rich tables | CS-366 |
| `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` | prompt contract | documentation owner | used | documents provider handoff rules | E-006 | needs target contract alignment | CS-363 |

## Matrice source -> owner -> usage runtime

| Source family | Canonical owner | Runtime owner observed | Projection reach | LLM input reach | Provider payload reach | Status |
|---|---|---|---|---|---|---|
| signs | `AstralSignProfileModel`, sign seed JSON | `AstrologyRuntimeReferenceRepository`, chart balance | yes, via `sign_profile_balances` | partial facts | partial fact/profile-balance data only | used |
| planets | `AstralPlanetInterpretationProfileModel`, translation seeds | seed services and DB models | not proven in nominal natal LLM input | no rich profile text | no rich profile text | seed-only |
| houses | `AstralHouseInterpretationProfileModel`, translation seeds | seed services and DB models | not proven in nominal natal LLM input | no rich profile text | no rich profile text | seed-only |
| aspects | `AstralAspectInterpretationProfileModel`, aspect runtime | `ChartInterpretationInputBuilder._project_aspects` | yes as aspect facts | yes as facts/codes | yes as aspect facts only | used |
| dominance | dominance reference tables and `DominantPlanetsResult` | chart dominance projection | yes | yes as dominants and signal codes | yes as compact dominant facts | used |
| dignity and rulership | dignity DB tables, `HouseRulerResolver`, dignity calculators | chart object runtime payloads | yes | yes as codes | yes as compact signals/facts | used |
| advanced conditions | DB tables and profile catalog | advanced condition runtime/profile resolver | yes | yes as condition codes | no rich text proven | used |
| docs/reference prose | `docs/recherches astro/**` | documentation only | no | no | no | unused |
| provider examples | prompt-generation cartography examples | generated audit examples | yes, as evidence | yes, as evidence | yes, final handoff samples | used |

## Trace d'appel vers projections et LLM

1. `backend/app/services/llm_generation/natal/interpretation_service.py` imports and calls `StructuredFactsV1Builder`, `AINarrativeInputBuilder`, `ClientInterpretationProjectionV1Builder` and `LLMAstrologyInputV1Builder` in `_build_llm_astrology_input_v1` (E-005).
2. `StructuredFactsV1Builder` calls `ChartInterpretationInputBuilder`, then emits `positions`, `houses`, `major_aspects`, `dominants`, `interpretive_signals`, `missing_data` and `sign_profile_balances` (E-005).
3. `AINarrativeInputBuilder` adapts `ChartInterpretationInputRuntimeData` into structural facts and signal code collections; it does not carry long interpretation prose (E-005).
4. `LLMAstrologyInputV1Builder` declares prompt-visible blocks as `facts`, `signals`, `limits`, `shaping`, with runtime/audit-only exclusions for `chart_json`, `natal_data`, `provider_response`, hashes and provenance (E-005, E-008).
5. `LLMGateway.build_user_payload` serializes only `_prompt_visible_llm_astrology_input` into `llm_astrology_input_v1`, then removes excluded audit fields recursively (E-005, E-008).

## Comparaison avec les JSON provider actuels

The `1974-04-24-1100-paris` examples include `free`, `basic` and `premium` provider payloads with `provider_call_performed=false`. Their payloads contain local facts, compact signals, limits and shaping. The `premium` payload includes `interpretation_hints`, but they are short synthesized hint strings such as dominant sign/angle/aspect summaries, not citations of controlled table rows or rich source profiles. The older `1973-04-24-paris` examples also show `llm_astrology_input_v1` provider user content, reinforcing that final handoff is a filtered contract rather than a dump of DB/reference texts (E-006).

## Tables/textes utilises

- Runtime fact owners: chart object runtime, aspects, house positions, dignities, rulerships, dominants and advanced condition codes are used before provider handoff (E-005).
- `AstralSignProfileModel` contributes structured sign profile balance categories, but not rich sign prose (E-004, E-005).
- Dignity, dominance, advanced condition and interpretation adapter reference rows are used by calculators/repositories/tests as calculable rule and signal material (E-004, E-007).
- Provider examples are used as evidence of final handoff shape (E-006).

## Tables/textes non utilises

- House, planet and aspect interpretation profile text/keyword seeds are not proven to reach `llm_astrology_input_v1` provider payloads (E-004, E-005, E-006).
- Translation seed tables for house/planet/aspect interpretation profiles remain seed/admin/reference material for this audited path unless a future story wires them into a stable material builder (E-004).
- `docs/recherches astro/**` is reference-only in this audit and is not runtime-loaded (E-004).

## Gaps et risques

| Gap | Severity | Evidence | Risk |
|---|---|---|---|
| Rich interpretive table material exists but the provider handoff mostly receives facts and compact codes. | High | E-004, E-005, E-006 | LLM output quality depends on model priors rather than controlled business text. |
| The target prompt contract for `interpretation_material` is not yet defined in implemented artifacts. | High | E-001, E-002 | Implementation stories may choose incompatible carriers. |
| Seed/admin/reference materials lack a single runtime ownership decision for prompt-visible use. | Medium | E-004 | Future code could duplicate selection logic or promote dormant tables ad hoc. |
| Guardrails protect adjacent prompt and astrology runtime surfaces but no exact CS-361 invariant exists. | Medium | E-001, E-007 | Regressions could conflate existence of text with provider visibility. |

## File Usage Classification

| Surface | Classification | Evidence | Rationale | Limitation |
|---|---|---|---|---|
| `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1152/01-audit-usage-tables-textes-interpretation.md` | used | E-001 | Explicit story deliverable. | New audit artifact. |
| `backend/app/services/llm_generation/natal/interpretation_service.py` `_build_llm_astrology_input_v1` | used | E-005 | Canonical natal LLM orchestration path calls the builders. | Source inspection, no provider call. |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` `LLMAstrologyInputV1Builder` | used | E-005, E-008 | Canonical internal LLM input contract and prompt-visible role owner. | Source inspection. |
| `backend/app/domain/llm/runtime/gateway.py` `LLMGateway.build_user_payload` | used | E-005, E-008 | Final prompt-visible filtering before provider messages. | Source inspection. |
| `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` | used | E-005 | Builds factual projection consumed by LLM input. | Source inspection. |
| `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` | used | E-005 | Builds compact pre-narrative signal contract. | Source inspection. |
| `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` | used | E-005 | Builds plan-shaped client projection and shaping. | Source inspection. |
| `backend/app/infra/db/models/interpretation_reference.py` | used | E-004 | DB owner for interpretation profile tables and translations. | Runtime provider reach not proven. |
| `backend/app/infra/db/models/reference.py` | used | E-004 | DB owner for reference/sign/fixed-star/point profile material. | Runtime provider reach partial. |
| `backend/app/infra/db/models/dignity_reference.py` | used | E-004 | DB owner for dignity/condition/adapter reference material. | Text description handoff not proven. |
| `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` | used | E-004, E-005 | Runtime loads reference material for calculations/signals. | Does not prove final prompt prose. |
| `backend/app/services/reference_data/*_seed_service.py` | used | E-004 | Admin/seed owners for reference rows. | Classified as used repository surface, individual rows may be seed-only. |
| `docs/db_seeder/astrology/**` | used | E-004 | Source seed data for reference/import flows. | No runtime provider handoff by itself. |
| `docs/recherches astro/**` | out-of-domain | E-004 | Reference material inspected to bound audit. | Not runtime-loaded by audited path. |
| `_condamad/examples/prompt-generation-cartography/**` | used | E-006 | Provider payload examples are required evidence. | Existing files are already modified/untracked before this audit. |
| `backend/tests/unit/domain/astrology/test_llm_astrology_input_v1.py` | test-only | E-007 | Unit guard for LLM input payload shape. | Test execution targeted separately. |
| `backend/tests/llm_orchestration/test_llm_astrology_input_boundaries.py` | test-only | E-007 | Boundary guard for prompt-visible payload filtering. | Test execution targeted separately. |

## Findings Summary

- High: F-001, F-002.
- Medium: F-003, F-004.
- Critical/Low/Info: none.

## Validation Plan

Validation commands and outputs are persisted in the CS-361 story evidence folder. Python commands must be executed only after `.\.venv\Scripts\Activate.ps1`.
