# Architecture theme astral prompt contract v1

<!-- Commentaire global: ce rapport fixe les decisions d'architecture produit pour le contrat theme_astral_llm_input_v1 et le payload provider theme astral. -->

## Executive summary

- `decision`: adopter un seul contrat cible `theme_astral_llm_input_v1` pour la feature theme astral, expose au LLM via le squelette stable `runtime_contract`, `safety_contract`, `astrologer_voice`, `feature_context`, `delivery_profile`, `input_data`, `output_contract` (CS-361 SC-001, F-001/F-002, E-004/E-005/E-006; CS-362 SC-001/SC-003, F-001/F-003, E-004/E-005).
- `decision`: les plans `free`, `basic`, `premium` partagent les memes cles; seuls les valeurs, quantites, budgets, selections et profondeur varient via `delivery_profile` (CS-362 F-003, E-004/E-005).
- `decision`: `feature`, `plan` et `astrologer_id` restent des entrees backend; le plan commercial est `backend-only` et ne doit pas etre prompt-visible (CS-362 F-001, E-004/E-005).
- `decision`: `astrologer_voice` influence style, ton, vocabulaire et emphases; il ne modifie jamais la verite astrologique ni les faits issus du moteur (brief CS-363; CS-361 F-001/F-003, E-004/E-005).
- `decision`: `interpretation_material` vient des tables, repositories, catalogues statiques controles et sorties moteur; aucun prompt builder ne doit inventer de matiere interpretative (CS-361 F-001/F-002/F-003, E-004/E-005/E-006).
- `decision`: `output_contract` est versionne et relie aux owners existants `llm_output_schemas`, `llm_assembly_configs`, `llm_prompt_versions`, `llm_personas` et release/observability LLM, sans creer de migration dans CS-363 (story CS-363 Evidence 8/9; source scan CS-363).
- `decision`: la transition est bigbang: pas de double runtime durable, pas de fallback prompt carrier, pas de compatibilite cachee (CS-361 SC-004/SC-005; CS-362 SC-002/SC-004).
- `blocker`: si le product owner exige d'exposer `free/basic/premium` au LLM, l'implementation CS-366 doit s'arreter et obtenir une decision explicite (CS-362 SC-001 blocker).
- `blocker`: si le owner persistance refuse la reutilisation des mecanismes LLM existants, CS-364 doit remapper le schema avant CS-365/CS-366.

## Executive architecture decision summary

| Type | Summary | Sources |
|---|---|---|
| observed | Le runtime actuel envoie surtout `facts`, `signals`, `limits`, `shaping`; les textes riches de tables ne sont pas prouves provider-visible. | CS-361 `00-audit-report.md`, F-001/F-002, E-004/E-005/E-006 |
| observed | Les JSON provider actuels ont des familles de cles stables, mais `messages`, volumes, carrier duplique et plan visible divergent. | CS-362 `00-audit-report.md`, F-001/F-002/F-003/F-004/F-005, E-004/E-005/E-006/E-007/E-008 |
| inferred | La bonne cible n'est pas une egalisation des donnees entre plans, mais une stabilisation de squelette et d'ownership. | CS-362 F-003, E-004/E-005 |
| decision | Le contrat cible s'appelle `theme_astral_llm_input_v1`; il remplace le carrier prompt-visible actuel `llm_astrology_input_v1` pour la feature theme astral lors des stories d'implementation. | CS-361 SC-001, CS-362 SC-003 |
| decision | La persistance doit reutiliser les concepts existants d'assembly, prompt version, output schema, persona, release, call log et replay snapshot. | `backend/app/infra/db/models/llm/**`; migrations LLM existantes; story CS-363 Evidence 8/9 |
| blocker | Contradiction de carrier: les donnees sont presentes dans developer et user; CS-366 doit choisir un seul carrier provider-visible. | CS-362 F-002, E-004/E-006 |
| open question | Faut-il creer un owner explicite de contrat d'entree LLM en DB ou encoder le contrat d'entree dans les registres existants? Defaut propose: commencer par registre domaine + `input_schema` de use case, puis migrer seulement si necessaire. | CS-361 F-003; `LlmUseCaseConfigModel.input_schema` observe via source scan |

## Audit source map

| Audit | Scope | Closure status | Key architecture inputs | Evidence IDs | Findings used | Blockers | Deferred context | Used for |
|---|---|---|---|---|---|---|---|---|
| CS-361 `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1152/` | Usage tables/textes interpretation et reach runtime/LLM/provider | `open`; audit complete, remediation routee CS-363..CS-368 | Sources interpretatives, current builder chain, absence de prose riche provider-visible, story candidates SC-001..SC-006 | E-001..E-010 | F-001, F-002, F-003, F-004 | Missing exact rich-material owner until CS-363; future reachability guard missing | Frontend, auth, migrations, provider calls, UI | `interpretation_material`, owners, roadmap CS-364..CS-368 |
| CS-362 `_condamad/audits/theme-astral-prompt-contract/2026-05-28-1203/` | Contrat JSON provider actuel free/basic/premium | `open`; audit complete, remediation routee CS-363/CS-366 | Stable key families, message/count divergence, plan visible, duplication developer/user, metadata backend-only visible, premium in basic | E-001..E-013 | F-001, F-002, F-003, F-004, F-005 | Product decision if commercial plan must be prompt-visible; unresolved carrier owner | Backend edits, JSON regeneration, prompt seeds, frontend, DB migrations | `delivery_profile`, skeleton stable, backend-only split, guards |

Story label caveats: the audits already name CS-363 through CS-368 as downstream candidates. This report preserves those IDs because the CS-363 story contract explicitly requires proposals CS-364 to CS-368 and no tracker conflict/remap was observed in the supplied CS-363 story. If the tracker later remaps IDs, source labels must remain provenance, not authority.

## Capability matrix

| Capability / family | Inputs | Objects required | Canonical contracts required | Surfaces required | Status | Blockers | Sources |
|---|---|---|---|---|---|---|---|
| Feature context | backend `feature`, subfeature, locale, use case | `feature_context` | `theme_astral_prompt_v1`, `theme_astral_llm_input_v1` | internal, automation_or_llm, data_storage | partial | none | CS-362 F-003, E-004/E-005 |
| Delivery profile | backend `plan`, entitlements, length/budget/depth rules | `delivery_profile` | delivery profile registry v1 | internal, automation_or_llm, observability | implicit | PO decision if plan labels must be prompt-visible | CS-362 F-001/F-003/F-005, E-004/E-005/E-008 |
| Astrologer voice | backend `astrologer_id`, persona config | `astrologer_voice`, `llm_personas` | persona/voice registry v1 | internal, automation_or_llm, data_storage | partial | style/truth boundary must be guarded | CS-362 F-003, E-004/E-006; `llm_personas` |
| Interpretation material | engine facts, table rows, selected themes, delivery profile | `interpretation_material`, source families signs/planets/houses/aspects/dignities/dominants/conditions | interpretation material registry v1 | internal, automation_or_llm, data_storage | missing | source-family owner selection must be closed in CS-365 | CS-361 F-001/F-002/F-003, E-004/E-005/E-006 |
| Output contract | feature, schema name/version, plan-derived section depth | `output_contract`, `llm_output_schemas` | output contract registry v1 | automation_or_llm, data_storage, observability | partial | schema owner must be explicit in CS-364 | CS-362 F-003, E-004; source scan `llm_output_schemas` |
| Provider payload | target contract, prompt assembly, runtime safety | provider skeleton, runtime envelope | provider payload policy v1 | automation_or_llm, observability | conflicting | duplicate developer/user carrier must be removed | CS-362 F-002/F-004, E-004/E-006/E-007 |
| Bigbang cleanup | old carrier scans, tests, examples | legacy deletion register | no-legacy transition contract | internal, automation_or_llm, observability | blocked | cannot start before CS-366 provider builder evidence | CS-361 SC-005, CS-362 SC-002/SC-004 |

## Surface matrix

| Surface | Current contract | Expected contract | Capabilities exposed | Consumers | Risks | Blockers | Required changes | Sources |
|---|---|---|---|---|---|---|---|---|
| internal | `llm_astrology_input_v1` builders and gateway filtering | domain-owned `theme_astral_llm_input_v1` builder/factories/resolver | feature context, material selection, delivery profile | backend services, tests | duplicate selection logic | CS-365 blocked by CS-363/CS-364 | add domain contract and factories in later story | CS-361 F-001/F-002/F-003 |
| public_api | no CS-363 API change | unchanged; no plan leakage decision exposed | none in CS-363 | API clients | accidental contract drift if API starts mirroring provider payload | none | no change in CS-363 | story CS-363 non-goals |
| admin_debug | audit evidence, examples, logs | debug can inspect trace, but not become source of truth | source reachability, validation | developers, reviewers | audit exclusion list entering provider payload | CS-366 must remove provider artifact metadata | keep debug fields backend-only | CS-362 F-004, E-007 |
| automation_or_llm | current provider payload with `llm_astrology_input_v1:` user content | one provider-visible carrier with target skeleton | LLM generation | LLM provider | commercial plan leakage, duplicated chart material | carrier decision in CS-366 | replace prompt-visible plan with `delivery_profile` | CS-362 F-001/F-002 |
| frontend | out of scope | unchanged | none | users | none for CS-363 | none | no change | story CS-363 non-goals |
| data_storage | `llm_assembly_configs`, `llm_prompt_versions`, `llm_output_schemas`, `llm_personas`, releases/logs exist | versioned prompt, output, voice and execution metadata reused; input contract owner decided | persistence/versioning | backend runtime, replay, audits | new duplicate registry | CS-364 persistence owner decision | decide reuse vs new table before migration | source scan; CS-361 F-003 |
| observability | LLM call logs/replay snapshots exist | trace contract version, delivery profile id, output schema id, assembly/prompt/persona ids | trace, replay, invalidation proof | reviewers, operators | replay incompatibility if input identity unversioned | CS-364 | record contract version and hashes in backend-only trace | source scan `llm_call_logs`, `llm_replay_snapshots` |

## Decisions d'architecture

1. `decision`: `theme_astral_prompt_v1` is the provider skeleton name; `theme_astral_llm_input_v1` is the internal feature input contract. They are related but not identical: the internal contract can carry backend-only trace; the provider skeleton cannot.
2. `decision`: use empty arrays or empty objects for absent optional data; key removal is forbidden for plan variation.
3. `decision`: `runtime_contract` and `safety_contract` are stable top-level provider-visible blocks, but backend runtime metadata such as provider, model, `provider_parameters`, hashes, provenance, replay snapshot, `chart_json`, `natal_data`, `provider_response` stays backend-only.
4. `decision`: `delivery_profile` replaces visible `plan`, `editorial_depth_profile`, `precision_level` and mixed commercial wording with non-commercial depth, budget, selection and output-length semantics.
5. `decision`: `input_data.birth_context` contains only normalized LLM-needed birth context; calculation engine metadata moves to backend trace.
6. `decision`: `input_data.interpretation_material` is selected before LLM handoff from declared source owners; prompt prose may render or reference it, not invent it.
7. `decision`: `output_contract` references a versioned schema owner and response obligations; prompt text cannot be the only owner of output structure.
8. `decision`: the bigbang sequence must remove provider-capable legacy carriers after the stable provider builder lands.

## Non-goals

- `observed`: CS-363 forbids application code, migration, prompt seed, provider JSON example, frontend, backend test and runtime behavior changes.
- `decision`: no real provider call, no prompt final prose rewrite, no new dependency, no guardrail registry update.
- `decision`: no durable fallback, compatibility runtime path, or parallel prompt contract outside the bigbang transition.
- `decision`: no frontend/API generated contract impact in CS-363.

## Squelette provider cible

```json
{
  "runtime_contract": {},
  "safety_contract": {},
  "astrologer_voice": {},
  "feature_context": {},
  "delivery_profile": {},
  "input_data": {
    "birth_context": {},
    "astrological_facts": {},
    "interpretation_material": {},
    "selected_themes": {},
    "limits": {}
  },
  "output_contract": {}
}
```

Rules:

- `decision`: every plan emits every key above.
- `decision`: absent fields are `{}` or `[]`, never removed.
- `decision`: `free`, `basic`, `premium` can change cardinality and values only through `delivery_profile`, selected facts/material and output limits.
- `blocker`: if an implementation story needs plan-specific keys, it must stop and request architecture owner approval.

## Contrat theme_astral_llm_input_v1

| Block | Status | Owner | Decision | Sources |
|---|---|---|---|---|
| `runtime_contract` | decision | LLM runtime/config owner | backend-known metadata for contract id/version, feature key, prompt/assembly/output/persona refs; provider-visible subset excludes commercial plan and debug/audit fields | CS-362 F-004; source scan gateway/contracts |
| `safety_contract` | decision | LLM runtime/security owner | non-invention, source-only material, missing-data, no medical/legal certainty, no hidden plan label | CS-361 F-001/F-002; CS-362 F-001 |
| `feature_context` | decision | canonical use case registry owner | feature/subfeature/locale/use-case semantics, no commercial `plan` | CS-362 F-001/F-003; `canonical_use_case_registry.py` |
| `delivery_profile` | decision | product + backend owner | non-commercial depth, budgets, selected groups, section counts, verbosity, reasoning/output constraints | CS-362 F-001/F-003/F-005 |
| `astrologer_voice` | decision | persona owner | style, tone, vocabulary, emphases only | CS-362 F-003; `llm_personas` |
| `input_data.birth_context` | decision | astrology domain owner | normalized user birth context needed by the LLM; engine metadata excluded | CS-362 F-004 |
| `input_data.astrological_facts` | decision | astrology engine/domain owner | calculated facts, stable projections, no prose invention | CS-361 E-005 |
| `input_data.interpretation_material` | decision | interpretation material builder owner | selected table/engine-derived material with source ids | CS-361 F-001/F-002/F-003 |
| `input_data.selected_themes` | decision | feature + delivery resolver owner | selected topics/sections derived from feature and delivery profile | CS-362 E-005 |
| `input_data.limits` | decision | domain/runtime owner | missing data, unavailable sections, uncertainty notes | CS-361 E-005/E-008 |
| `output_contract` | decision | output schema owner | schema id/name/version and response obligations | CS-362 E-004; `llm_output_schemas` |

## Bloc interpretation_material

`observed`: CS-361 proves rich source material exists across sign, house, planet, aspect, dignity, rulership, dominance, advanced conditions and adapter/reference sources, but provider reach is not proven for rich prose (CS-361 F-001/F-002/F-003, E-004/E-005/E-006).

`decision`: `interpretation_material` is a derived object selected by one canonical builder in CS-365. It must include source family, source owner, source id/version where available, selected text/keywords/signals, applicability reason, and delivery-profile visibility.

`decision`: docs under `docs/recherches astro/**` remain reference-only unless a later owner promotes them through a repository-backed source. Prompt builders cannot copy prose from docs or seeds directly.

`blocker`: CS-365 cannot implement material selection until CS-364 or the architecture owner confirms whether source-owner metadata is persisted in existing LLM/config tables or only in domain contract code.

## Bloc astrologer_voice

`observed`: persona/developer message behavior is divergent today: absent for `free`, present for `basic/premium`, and `basic` can inherit premium-oriented language (CS-362 F-005, E-008).

`decision`: `astrologer_voice` is a value object resolved before provider handoff from `astrologer_id`/persona owner. It may set style, ton, vocabulaire, emphases, formatting preferences and caution phrasing. It cannot change astrological facts, source material, allowed sections, or output schema truth.

`decision`: if no astrologer persona applies, emit `{}` for `astrologer_voice` rather than removing the key.

## Bloc delivery_profile

`observed`: current plan variation changes fact counts, house/aspect/dominant counts, section codes, token budgets, reasoning/verbosity and prompt volume (CS-362 E-005).

`decision`: backend resolves commercial `plan` to `delivery_profile` before LLM handoff. The LLM receives profile semantics such as `depth`, `precision`, `allowed_fact_groups`, `section_codes`, `material_budget`, `max_output_tokens_policy`, `verbosity_target`, not `plan=free/basic/premium`.

`decision`: `delivery_profile` participates in cache, replay and invalidation because it changes selected inputs and expected output.

`blocker`: product owner approval is required if business insists that the commercial package name is itself content.

## Bloc output_contract

`observed`: current provider payloads share `response_format` property families (`title`, `summary`, `sections`, `highlights`, `advice`, `evidence`) while prompt prose also carries output obligations (CS-362 E-004).

`decision`: `output_contract` is a top-level block with schema name/version, required sections, allowed evidence style, length bounds and compatibility policy. It must map to `llm_output_schemas` and assembly output schema references.

`decision`: output schema changes that alter required fields, semantics, ordering, replay compatibility or public/persisted shape require a new version suffix.

## Persistence DB et versioning

| Concern | Decision | Owner | Versioning | Compatibility | Trace/deprecation |
|---|---|---|---|---|---|
| Prompt text | reuse `llm_prompt_versions` | prompt owner | prompt version | bigbang for provider-capable old prompt | trace `prompt_version_id`; archive/deprecate old prompt carriers |
| Assembly | reuse `llm_assembly_configs` | assembly resolver owner | assembly publish state/version refs | one active target per feature/profile | trace `assembly_id`; no fallback assembly |
| Output schema | reuse `llm_output_schemas` | schema owner | schema `name/version` | schema compatibility by version | trace `output_schema_id` |
| Persona/voice | reuse `llm_personas` | persona owner | persona row/version policy if added later | voice cannot affect truth | trace `persona_id`; disable/deprecate via enabled/status |
| Execution profile | reuse `llm_execution_profiles` where applicable | runtime owner | execution profile refs | provider/model/budget backend-only | trace execution profile and token policy |
| Release/replay | reuse `llm_release_snapshots`, `llm_call_logs`, `llm_replay_snapshots` | ops/runtime owner | release snapshot | replay tied to contract ids | trace contract version, delivery profile id, material source versions |
| Input contract | adopt domain registry now; decide DB owner in CS-364 | architecture/data owner | `theme_astral_llm_input_v1` | no parallel durable input contract | blocker if DB persistence is required before builder work |

## Integration avec assembly/prompt registry existants

- `observed`: `canonical_use_case_registry.py` declares canonical use case contracts, required placeholders and input schemas for modern natal use cases.
- `observed`: `use_cases_seed.py` seeds output schemas and use cases from canonical contracts.
- `observed`: `seed_66_20_taxonomy.py` links assembly configs to prompt versions, personas, output schemas and execution profiles.
- `observed`: DB models include `llm_assembly_configs`, `llm_prompt_versions`, `llm_use_case_configs`, `llm_output_schemas`, `llm_personas`, `llm_execution_profiles`, `llm_release_snapshots`, `llm_call_logs`, `llm_replay_snapshots`.
- `decision`: CS-364 must prefer extending canonical contracts/input schema metadata over creating a separate prompt-contract registry. A new table is allowed only if existing owners cannot represent input contract version, material source versions, trace and deprecation.
- `decision`: prompt text receives the target contract as a rendered input placeholder or provider carrier, but does not own the contract schema.

## Canonical registry decisions

### theme_astral_contract_registry

Decision: adopt
Owner: architecture owner + domain LLM owner

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
|---|---|---|---|---|---|---|---|
| `theme_astral_llm_input` | `v1` | feature, birth context, engine facts, material, delivery profile, voice | `theme_astral_llm_input_v1` | breaking field/semantic changes create v2 | legacy `llm_astrology_input_v1` provider-capable usage removed in CS-367 | contract_id, contract_version, assembly_id, prompt_version_id, output_schema_id | CS-361 SC-001; CS-362 SC-003 |

### delivery_profile_registry

Decision: adopt
Owner: product owner + backend runtime owner

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
|---|---|---|---|---|---|---|---|
| `theme_astral_delivery_profile` | `v1` | backend plan, feature, entitlement/rules | non-commercial profile | profile changes that alter selection/cache create version bump | old prompt-visible `plan` forbidden | delivery_profile_id, delivery_profile_version, resolved_from_plan backend-only | CS-362 F-001/F-003/F-005 |

### interpretation_material_registry

Decision: adopt
Owner: astrology interpretation domain owner

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
|---|---|---|---|---|---|---|---|
| `theme_astral_interpretation_material` | `v1` | tables, repositories, engine outputs, selected themes | source-attributed material block | source family additions require explicit compatibility review | dormant docs/seeds stay excluded unless promoted | source_family, source_owner, source_id/version, material_builder_version | CS-361 F-001/F-002/F-003 |

### output_contract_registry

Decision: adopt
Owner: LLM schema owner

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
|---|---|---|---|---|---|---|---|
| `theme_astral_output_contract` | `v1` | feature, delivery profile, schema | output schema and section obligations | schema shape/semantics changes create new version | old unversioned prompt-only obligations rejected | output_schema_id, output_contract_version | CS-362 E-004; `llm_output_schemas` |

## Object/entity decisions

| Object | Kind | Lifecycle owner | Persistence | Serialization | Versioning | Surfaces | Decision | Sources |
|---|---|---|---|---|---|---|---|---|
| `theme_astral_llm_input_v1` | value_object | domain LLM owner | not necessarily persisted as row; trace version in logs/replay | JSON stable skeleton | explicit v1 suffix | internal, automation_or_llm, observability | adopt | CS-361 SC-001; CS-362 SC-003 |
| `theme_astral_prompt_v1` | derived_object | prompt/runtime owner | prompt/assembly refs | provider JSON skeleton | v1 | automation_or_llm | adopt | CS-363 brief |
| `delivery_profile` | value_object | product/backend owner | backend config or canonical rules; trace resolved id | JSON object | v1 | internal, automation_or_llm, observability | adopt; plan backend-only | CS-362 F-001 |
| `astrologer_voice` | value_object | persona owner | `llm_personas` | JSON object | persona/version policy | internal, automation_or_llm, data_storage | adopt; style only | CS-362 F-005 |
| `interpretation_material` | derived_object | interpretation material builder owner | source refs persisted/traced; material generated per request | JSON object/arrays | builder/source versions | internal, automation_or_llm, replay | adopt | CS-361 F-001/F-002/F-003 |
| `output_contract` | value_object | schema owner | `llm_output_schemas` + assembly ref | JSON object | schema version | automation_or_llm, data_storage | adopt | CS-362 E-004 |
| legacy `llm_astrology_input_v1` provider carrier | debug_artifact after migration | runtime owner | retained only for non-provider compatibility if explicitly classified | none provider-visible | deprecated | internal/test-only | replace for theme astral provider path | CS-361 SC-005; CS-362 F-002 |

## Operational rules

| Rule area | Rule | Applies to | Invalidated by | Trace requirement | Owner | Sources |
|---|---|---|---|---|---|---|
| Versioning | Contract ids use explicit suffixes; shape/semantic/cache/replay changes create new version. | input, prompt skeleton, material, output | required fields, semantics, ordering, material source rules | contract_id/version | architecture owner | decision-rules; CS-361 F-001 |
| Trace | Backend trace records plan, delivery profile, assembly, prompt, schema, persona, material builder/source versions; provider payload excludes backend-only trace. | logs, replay, provider assembly | any resolved owner/version change | call log + replay snapshot refs | runtime/ops owner | CS-362 F-004 |
| Cache | Cache identity includes contract version, birth/facts identity, delivery profile, material source versions, output contract, voice id when style affects text. | generated output cache | source data, delivery profile, output schema, prompt/persona change | cache key material recorded backend-only | runtime owner | CS-361 F-003; CS-362 F-003 |
| Replay | Replay uses the exact contract, delivery profile, material refs, prompt/assembly/schema/persona refs and provider params from backend trace. | replay snapshots | missing versions or deleted material source | replay snapshot must be self-describing | ops/runtime owner | source scan `llm_replay_snapshots` |
| Invalidation | Changes to tables/material selection, engine fact semantics, delivery profile, output schema, persona voice, prompt version invalidate affected outputs. | generated interpretations | any source owner version bump | invalidation reason linked to owner version | data/runtime owner | CS-361 F-001/F-003 |
| Migration | Bigbang replaces provider-capable old carriers; no durable double runtime, fallback or compatibility branch. | CS-364..CS-368 | stable builder absent or old provider path retained | negative scans and deletion register | architecture/runtime owner | CS-361 SC-005; CS-362 SC-002 |
| Observability | Observability proves chosen carrier, absence of plan leakage and material source reach without exposing debug/audit fields to the LLM. | validation, logs, audits | trace/debug fields become provider-visible | report/test evidence + backend logs | ops/review owner | CS-361 F-004; CS-362 F-004 |

## Blockers and decision owners

| Blocker / open decision | Type | Owner | Blocks | Required resolution | Sources |
|---|---|---|---|---|---|
| Commercial plan prompt visibility | blocker | product owner | CS-366 | approve backend-only plan and non-commercial delivery profile | CS-362 F-001, SC-001 |
| Single provider-visible carrier | blocker | architecture + runtime owner | CS-366/CS-367 | choose user payload as canonical carrier or explicit alternative; remove developer/user duplication | CS-362 F-002 |
| Input contract persistence owner | open question | data/architecture owner | CS-364/CS-365 if DB metadata is required | decide reuse of `input_schema`/assembly/release refs vs new table | CS-361 F-003 |
| Material source promotion | blocker | astrology domain/data owner | CS-365 | decide which source families are selected, excluded, or owner-blocked | CS-361 F-001/F-003 |
| Basic premium wording guard | blocker | prompt owner | CS-366 | add guard against premium-only wording in basic rendered payload | CS-362 F-005 |
| Backend-only metadata split | blocker | runtime/observability owner | CS-366 | remove exclusion registry/calculation metadata from provider payload while preserving backend trace | CS-362 F-004 |

## Bigbang migration plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| CS-363 | undecided target contract | architecture report | none | report scans | `rg` report check | missing CS-361/CS-362 evidence |
| CS-364 | unowned prompt/input persistence | versioned contract persistence decision | DB/config owners | migration/contract tests if implemented | owner decision artifact | persistence owner unresolved |
| CS-365 | facts/codes without rich material owner | `interpretation_material` builder | domain factories | unit/source reach tests | no duplicate material builder scan | source-family decision unresolved |
| CS-366 | plan-shaped duplicated provider payload | stable provider payload builder | gateway/runtime | free/basic/premium payload tests | no plan leakage, no duplicate carrier | carrier or delivery profile unresolved |
| CS-367 | provider-capable legacy carriers | single target runtime | runtime callers/examples | integration/boundary tests | old path negative scans | provider-capable old path remains |
| CS-368 | open validation gaps | closure audit and permanent guards | review process | full targeted suite | reachability matrix + no-legacy proof | evidence missing |

Stop condition: no provider-capable theme astral runtime uses a parallel prompt carrier after CS-367, and CS-368 proves source existence, projection reach, LLM input reach and provider reach.

## Legacy a supprimer

- `decision`: prompt-visible commercial `plan` and `shaping.plan` for theme astral provider payloads.
- `decision`: developer/user duplication of full chart or input data.
- `decision`: provider artifact exposure of `audit_excluded_from_prompt`.
- `decision`: provider-visible `source_metadata` calculation/runtime details; keep only normalized `birth_context`.
- `decision`: premium-only wording in basic prompt material.
- `decision`: provider-capable use of `chart_json`, `natal_data`, hashes, provenance, provider response, observability, replay snapshot, debug/trace fields.
- `decision`: any fallback or compatibility prompt carrier that remains provider-capable after bigbang.

## Ordered implementation roadmap

### Story 1: Define versioned persistence owner

Story ID: CS-364
Source label: CS-361 SC-002
Goal: decide how `theme_astral_llm_input_v1`, material source refs and `output_contract` versions are persisted/traced using existing LLM owners.
Source audits: CS-361, CS-362.
Source findings: CS-361 F-003; CS-362 F-004.
Scope: owner decision, migration impact statement, schema/config mapping, rejected alternatives.
Out of scope: runtime builder, provider payload, prompt prose.
Dependencies: CS-363.
Acceptance criteria:
- Existing owners `llm_assembly_configs`, `llm_prompt_versions`, `llm_output_schemas`, `llm_personas`, releases/logs/replay are mapped.
- New table is either rejected or justified by a missing owner.
- Contract version, material source versions and output schema refs are traceable.
Validation evidence:
- targeted `rg` over owners and report.
- migration impact statement.
Blockers / decisions:
- data owner must approve persistence route.
Stop condition: one persistence owner path is approved before CS-365/CS-366.

### Story 2: Implement interpretation material builder

Story ID: CS-365
Source label: CS-361 SC-003
Goal: build one canonical domain material builder for selected table/engine-derived interpretation material.
Source audits: CS-361.
Source findings: F-001, F-002, F-003.
Scope: domain builder, source family selection matrix, tests for sourced material and absent material.
Out of scope: provider payload assembly, prompt final prose.
Dependencies: CS-363, CS-364 owner decision.
Acceptance criteria:
- signs, planets, houses, aspects, dignity/rulership, dominance and advanced conditions are each selected, excluded, or blocked with evidence.
- prompt builders do not embed source prose selection.
- empty arrays/objects are emitted for absent material.
Validation evidence:
- unit tests.
- negative scans for duplicate builders and inline prompt prose.
Blockers / decisions:
- source-family owner must approve promoted material.
Stop condition: `interpretation_material` is reproducible from declared owners.

### Story 3: Implement stable provider payload builder

Story ID: CS-366
Source label: CS-362 SC-002/SC-004/SC-005
Goal: emit the target provider skeleton with one canonical data carrier and no plan/backend-only leakage.
Source audits: CS-361, CS-362.
Source findings: CS-362 F-001/F-002/F-003/F-004/F-005; CS-361 F-002.
Scope: runtime payload builder/gateway boundary, payload examples, boundary tests, prompt-visible filtering.
Out of scope: material source implementation if CS-365 incomplete, DB migration.
Dependencies: CS-364, CS-365.
Acceptance criteria:
- `free/basic/premium` share skeleton keys.
- provider-visible payload omits commercial `plan`, audit exclusion registry, hashes, provenance, `chart_json`, `natal_data`, provider response, debug/trace.
- one carrier owns input data.
- `basic` rendered payload lacks premium-only labels.
Validation evidence:
- parsed provider payload comparisons.
- scans for forbidden symbols and duplicate carrier.
Blockers / decisions:
- product owner plan visibility decision.
- runtime owner carrier decision.
Stop condition: target payload examples and tests prove stable shape and no leakage.

### Story 4: Bigbang legacy removal

Story ID: CS-367
Source label: CS-361 SC-005
Goal: remove provider-capable legacy carrier surfaces and prevent durable double runtime.
Source audits: CS-361, CS-362.
Source findings: CS-361 F-002; CS-362 F-002/F-004.
Scope: old carrier scans, replacement in nominal runtime, deletion/classification register, tests/examples.
Out of scope: new architecture beyond CS-363 decisions.
Dependencies: CS-366.
Acceptance criteria:
- no fallback prompt carrier.
- no compatibility branch preserving old semantics under new names.
- retained legacy references are classified test-only/public/exported/blocked.
Validation evidence:
- negative scans for old carrier names in provider path.
- passing boundary/integration tests.
Blockers / decisions:
- stop if any old public/exported surface lacks owner decision.
Stop condition: no provider-capable parallel runtime remains.

### Story 5: Closure audit and permanent guards

Story ID: CS-368
Source label: CS-361 SC-006
Goal: prove the migration closed CS-361/CS-362 findings and install durable evidence/guards.
Source audits: CS-361, CS-362.
Source findings: CS-361 F-004 plus all residual CS-362 findings.
Scope: closure audit bundle, reachability matrix, no-legacy scans, full targeted validation.
Out of scope: implementing missing runtime behavior.
Dependencies: CS-364, CS-365, CS-366, CS-367.
Acceptance criteria:
- every CS-361 source family has source existence, projection reach, LLM input reach and provider reach classification.
- no commercial plan or backend-only metadata is provider-visible.
- permanent guards distinguish source existence from provider visibility.
Validation evidence:
- audit bundle under `_condamad/audits/theme-astral-prompt-contract/`.
- tests, scans, provider example comparisons.
Blockers / decisions:
- any incomplete prior phase remains blocker, not backlog.
Stop condition: architecture findings are closed or explicitly owner-blocked.

## Tests et guardrails

- Required report scans:
  - `rg -n "Executive summary|Decisions d'architecture|Bigbang migration plan" _condamad/architecture/theme-astral-prompt-contract`
  - `rg -n "runtime_contract|safety_contract|astrologer_voice|feature_context|delivery_profile" _condamad/architecture/theme-astral-prompt-contract`
  - `rg -n "birth_context|astrological_facts|interpretation_material|selected_themes|limits|output_contract" _condamad/architecture/theme-astral-prompt-contract`
  - `rg -n "plan commercial|backend-only|delivery_profile|free|basic|premium" _condamad/architecture/theme-astral-prompt-contract`
  - `rg -n "CS-364|CS-365|CS-366|CS-367|CS-368" _condamad/architecture/theme-astral-prompt-contract`
- Python validation must run only after `.\.venv\Scripts\Activate.ps1`.
- CS-363 does not require application tests to pass for changed code because no application code changed; targeted pytest/ruff commands may still be run as repository health checks if time permits.
- Permanent future guards must cover: no prompt-visible commercial plan, stable skeleton keys, empty object/array behavior, source-attributed interpretation material, style-only voice, output contract version, no legacy provider carrier.

## Risques et decisions ouvertes

| Question | Why it matters | Owner | Blocks | Suggested default | Sources |
|---|---|---|---|---|---|
| Should commercial `plan` ever be prompt-visible? | It is currently visible and high risk. | product owner | CS-366 | No; use `delivery_profile`. | CS-362 F-001 |
| Where is input contract metadata persisted? | Cache/replay/invalidation need a versioned identity. | data/architecture owner | CS-364/CS-365 | Reuse canonical use case input schema + assembly/release/log refs first. | CS-361 F-003 |
| Which source families enter `interpretation_material` v1? | Prevents ad hoc prompt builder prose. | astrology domain/data owner | CS-365 | Include runtime-backed table/engine families; keep docs reference-only. | CS-361 F-001/F-003 |
| Which provider carrier is canonical? | Current developer/user duplication creates drift. | runtime/architecture owner | CS-366 | User payload owns data; developer prompt owns instructions only. | CS-362 F-002 |
| How strict is basic-not-premium vocabulary? | Prevents product tier confusion without exposing plan. | prompt/product owner | CS-366 | Ban commercial labels; allow non-commercial depth terms. | CS-362 F-005 |

## Validation plan

1. Confirm source audits and report path exist.
2. Scan mandatory headings and target skeleton keys.
3. Scan backend-only plan, `delivery_profile`, `interpretation_material`, `output_contract`, owner table names and CS-364..CS-368 references.
4. Verify no forbidden application surfaces changed: `backend/app`, `backend/tests`, `frontend/src`, `backend/migrations`.
5. Persist validation output under the CS-363 evidence folder.

