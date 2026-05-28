# 01-audit-usage-tables-textes-interpretation

## Executive summary

CS-361 audits the current use of interpretive astrology texts before the LLM/provider boundary. The current path is controlled and fact-rich, but no evidence proves that rich table, seed, or reference prose reaches the provider payload. The visible handoff is mostly `facts`, compact `signals`, `limits`, `shaping`, and short `interpretation_hints` in examples.

The detailed CONDAMAD evidence, finding register, risk matrix and candidate contracts are maintained in the sibling files of this audit folder. This file is the specialized CS-361 deliverable requested by the story and repeats the required decision matrix so the expected path is self-contained.

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

1. `backend/app/services/llm_generation/natal/interpretation_service.py` builds the LLM astrology input through `StructuredFactsV1Builder`, `AINarrativeInputBuilder`, `ClientInterpretationProjectionV1Builder` and `LLMAstrologyInputV1Builder` (E-005).
2. `StructuredFactsV1Builder` emits factual and signal-oriented material such as positions, houses, aspects, dominants, interpretive signals, missing data and sign profile balances (E-005).
3. `AINarrativeInputBuilder` keeps structural facts and signal code collections; it does not prove long interpretation prose handoff (E-005).
4. `LLMAstrologyInputV1Builder` exposes only `facts`, `signals`, `limits` and `shaping` while excluding runtime/audit-only carriers (E-005, E-008).
5. `LLMGateway.build_user_payload` serializes the prompt-visible contract and removes excluded audit/runtime fields before provider handoff (E-005, E-008).

## Comparaison avec les JSON provider actuels

The `1974-04-24-1100-paris` examples include `free`, `basic` and `premium` provider payloads with `provider_call_performed=false`. The payloads show local facts, compact signals, limits and shaping. The `premium` payload includes `interpretation_hints`, but those hints are short synthesized strings, not controlled citations of rich table rows or reference profiles. The `1973-04-24-paris` examples also show `llm_astrology_input_v1` user content, confirming the filtered provider handoff shape (E-006).

## Tables/textes utilises

- Chart object facts, aspects, house positions, dignities, rulerships, dominants and advanced condition codes are used before provider handoff (E-005).
- `AstralSignProfileModel` contributes structured balance categories, not rich sign prose (E-004, E-005).
- Dignity, dominance, advanced condition and interpretation adapter reference rows are used as calculable rule or signal material (E-004, E-007).
- Provider examples are used only as evidence of final handoff shape (E-006).

## Tables/textes non utilises

- House, planet and aspect interpretation profile text/keyword seeds are not proven to reach `llm_astrology_input_v1` provider payloads (E-004, E-005, E-006).
- Translation seed tables for house, planet and aspect interpretation profiles remain seed/admin/reference material for this audited path unless a future story wires them into a stable material builder (E-004).
- `docs/recherches astro/**` is reference-only in this audit and is not runtime-loaded (E-004).

## Gaps et risques

| Gap | Severity | Evidence | Risk |
|---|---|---|---|
| Rich interpretive table material exists but the provider handoff mostly receives facts and compact codes. | High | E-004, E-005, E-006 | LLM output quality depends on model priors rather than controlled business text. |
| The target prompt contract for `interpretation_material` is not yet defined in implemented artifacts. | High | E-001, E-002 | Implementation stories may choose incompatible carriers. |
| Seed/admin/reference materials lack a single runtime ownership decision for prompt-visible use. | Medium | E-004 | Future code could duplicate selection logic or promote dormant tables ad hoc. |
| Guardrails protect adjacent prompt and astrology runtime surfaces but no exact CS-361 invariant exists. | Medium | E-001, E-007 | Regressions could conflate existence of text with provider visibility. |

## Story candidates

- CS-363: define the target `theme_astral_llm_input_v1` architecture and the `interpretation_material` contract from F-001.
- CS-364: define versioned persistence and ownership decisions from F-003.
- CS-365: implement the canonical interpretation material builder from F-001.
- CS-366: implement the stable provider payload builder from F-002.
- CS-367: replace legacy prompt contract surfaces after the stable builder exists from F-002.
- CS-368: audit closure and reachability guardrails from F-004.
