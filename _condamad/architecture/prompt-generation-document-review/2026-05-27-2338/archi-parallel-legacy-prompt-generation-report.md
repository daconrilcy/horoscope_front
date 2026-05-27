<!-- Commentaire global: rapport d'architecture produit CS-354 qui decide le statut des processus paralleles, legacy et non nominaux de generation des prompts LLM. -->

# archi-parallel-legacy-prompt-generation-report - CS-354

## Executive architecture summary

Executive architecture decision summary:

- observed: CS-353 confirme des processus provider-capable hors flux natal moderne: Guidance, Guidance contextuelle, Chat public, Horoscope daily narration, Admin manual execution, Repair prompts et fallbacks bornes. Sources: CS-353 `03-parallel-legacy-processes-audit.md`, E-011 a E-017, F-001, F-003.
- decision: le flux nominal de reference reste le flux natal moderne `llm_astrology_input_v1` avec `facts`, `signals`, `limits`, `shaping` comme blocs prompt-visible. Sources: CS-350, CS-351 F-001/F-002, CS-352 E-007 a E-012, CS-348 `prompt_input_registry`.
- decision: Guidance, Guidance contextuelle, Chat public et Horoscope daily narration sont des flux paralleles supportes, provider-capable, non-natals modernes; ils doivent etre documentes comme actifs sans les convertir en sous-cas du carrier natal. Sources: CS-353 E-011/E-012/E-013, F-001.
- decision: Repair prompts, fallback catalog, no-assembly bootstrap fallback et provider unsupported fallback restent non nominaux; ils ne sont pas runtime truth produit. Sources: CS-353 E-015/E-016, F-001/F-004; CS-348 recovery decision.
- decision: Guidance bootstrap seeds, Horoscope narrator bootstrap seed, Admin sample payload CRUD, tests et mentions CS-350/prior audits sont respectivement seed-only, admin-only, test-only ou archival/non runtime truth. Sources: CS-353 E-014/E-017/E-018.
- blocker: `event_guidance` est provider-capable seulement si invoque par adapter/gateway, mais aucun trigger public audite n'a ete trouve; il garde `chart_json` dans seed/contract et requiert une decision product/architecture: migrer, supprimer ou retenir comme dette explicite. Sources: CS-353 F-002, E-014/E-015/E-018.
- blocker: Admin manual execution est admin-only mais provider-capable et peut transmettre des sample payloads incluant `chart_json`; une decision owner est requise pour sa documentation/politique. Sources: CS-353 F-003, E-017/E-018.
- decision: CS-350 doit recevoir une correction documentaire actionnable, mais ce rapport ne modifie pas CS-350. Sources: CS-351 F-001/F-002, CS-352 F-001/F-002, CS-353 SC-001.
- decision: les guardrails exacts pour classification parallele doivent attendre l'acceptation de la matrice documentaire; ne pas ajouter de guardrail avant SC-001 ou decision equivalente. Sources: CS-353 F-004, SC-002.

## Source map

Audit source map for CS-354 synthesis:

| Audit | Scope | Closure status | Key architecture inputs | Evidence IDs | Findings used | Blockers | Deferred context | Used for |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CS-351 adversarial document review | Revue adversariale de CS-350 | acceptable with corrections | Nuance `evidence_refs`; wording provider-only metadata; guardrail exact absent | E-003, E-004, E-006, E-007, E-008, E-009, E-010, E-011 | F-001, F-002, F-003 | Aucun blocker runtime; corrections documentaires seulement | Future documentation/guardrail story | CS-350 impacts, boundary wording |
| CS-352 code-document concordance | Concordance CS-350 avec code executable | acceptable with documentation-only corrections | Flux nominal confirme; provider metadata non prompt-visible; validation/audit dual role | E-005, E-007, E-008, E-009, E-010, E-011, E-012 | F-001, F-002, F-003 | Exact code-document guardrail absent | Pas de code change ni provider call | Nominal flow, provider handoff, tests existants |
| CS-353 parallel legacy process audit | Inventaire process paralleles, legacy, bootstrap, test, admin | parallel processes confirmed; documentation correction required | Process actifs non-natals, fallbacks, repairs, seeds, admin, tests, archive, `event_guidance` | E-001 a E-018 | F-001, F-002, F-003, F-004, F-005; SC-001, SC-002 | `event_guidance`; admin manual execution policy | Story candidates are provenance labels | Matrice decisionnelle, roadmap, blockers |
| CS-350 final documentation | Cartographie actuelle de generation prompt LLM | exists, but needs corrections from CS-351/352/353 | Flux natal nominal, non-nominal paths, tests/guardrails | Source path only | Impacts from CS-351/352/353 | Must not be edited by CS-354 | Documentation correction story | Impact section |
| CS-348 architecture | Architecture produit prompt generation | delivered | Registries, object decisions, output schema/semantic blockers | CS-343 a CS-347 refs | Architecture blockers and registries | Output schema owner split; semantic grounding bounded | Upstream broader architecture | Registry and operational rules |
| CS-349 delivery report | Synthesis CS-343 a CS-350 | delivered with residual risks | Evidence chain and residual risks | report sections 8-13 | residual risks | CS-350 was downstream at CS-349 time | Current CS-350 now exists | Context and limitations |

Story label caveats: `SC-001` and `SC-002` in CS-353 are provenance labels only. This report does not transform them into definitive tracker IDs. Roadmap stories use `next-available-id` or `needs-tracker-remap`.

## Capability Matrix

| Capability / family | Inputs | Objects required | Canonical contracts required | Surfaces required | Status | Blockers | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Modern natal prompt generation | canonical use case, assembly, rendered prompt, `llm_astrology_input_v1` | `facts`, `signals`, `limits`, `shaping`, `messages` | `llm_astrology_input_v1_v1`, provider messages v1 | internal, automation_or_llm, data_storage, observability | implemented | output schema owner split remains broader blocker | CS-350; CS-352 E-007/E-012; CS-348 |
| Guidance and contextual guidance | route/service context, textual natal summary, situation/objective/time horizon | guidance request context, `natal_chart_summary` | parallel_process_classification_v1, provider messages v1 | public_api, internal, automation_or_llm, observability | partial | needs CS-350 matrix correction | CS-353 E-011, F-001 |
| Public chat | user message, chat history, persona, optional natal hint | chat context, textual `build_chat_natal_hint` | parallel_process_classification_v1, chat messages v1 | public_api, internal, automation_or_llm, observability | partial | needs CS-350 matrix correction | CS-353 E-012, F-001 |
| Horoscope daily narration | daily prediction context, variant plan, narration question | daily narration request | parallel_process_classification_v1, structured messages v1 | public_api, internal, automation_or_llm, observability | partial | legacy route marker must stay non nominal | CS-353 E-013/E-014, F-001 |
| Fallback and repair recovery | invalid output, fallback config, missing assembly/provider fallback | repair request, fallback config | recovery_classification_v1 | internal, automation_or_llm, observability | implicit | must not become runtime truth | CS-353 E-015/E-016, F-004 |
| Bootstrap and seeds | seed scripts, static prompts/profiles/assemblies | prompt versions, assemblies | provisioning_registry_v1 | data_storage, internal | implicit | seed/runtime truth confusion | CS-353 E-014 |
| Admin manual execution and samples | admin sample payload, manifest entry, execution context | sample payload, admin execution request | admin_execution_policy_v1 | admin_debug, internal, automation_or_llm, observability | blocked | product/architecture decision required | CS-353 E-017/E-018, F-003 |
| Legacy carrier governance | `chart_json`, `natal_data`, `event_guidance` | legacy carrier references | legacy_carrier_registry_v1 | internal, admin_debug, test, data_storage | blocked | `event_guidance` decision required | CS-353 E-014/E-018, F-002/F-005 |

## Surface Matrix

| Surface | Current contract | Expected contract | Capabilities exposed | Consumers | Risks | Blockers | Required changes | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| internal | Services, adapters, gateway, builders and seed scripts route prompt work | Owner-routed process classification with nominal/parallel/recovery/admin/seed labels | all capabilities | backend services | non-natal flows hidden behind generic gateway wording | `event_guidance`, admin policy | add architecture-backed CS-350 process matrix | CS-352; CS-353 F-001/F-002/F-003 |
| public_api | `/v1/guidance`, `/v1/guidance/contextual`, `/v1/chat`, prediction services can trigger provider paths | public triggers documented separately from prompt carriers | guidance, chat, horoscope daily | frontend/API clients | treating modern natal as only provider path | none for active public flows | document active non-natal provider-capable flows | CS-353 E-011/E-013 |
| admin_debug | admin samples and manual execution exist; manual execution can call gateway | admin-only provider-capable policy with sample-payload boundaries | admin samples, manual execution, observability | operators/admin users | admin sample `chart_json` mistaken for public runtime | admin owner decision | classify or restrict through follow-up story | CS-353 E-017/E-018, F-003 |
| automation_or_llm | Provider receives messages from nominal, parallel, repair, fallback and admin paths | provider-capability must be explicitly classified per process | provider handoff, repair, fallback | provider runtime manager | non-nominal paths reintroduced as prompt-visible truth | event/admin decisions | maintain provider-capable decision matrix | CS-353 provider-capable table |
| frontend | no direct prompt ownership evidenced | no frontend prompt contract; consume public API only | user workflows indirectly | users | UI could infer unsupported correctness if docs overclaim | none in this story | no frontend change | CS-354 story non-goals |
| data_storage | prompts, assemblies, seeds, samples, audit/log records | storage role separated as runtime config, provisioning, audit or sample | config, seeds, samples, audit | backend/admin | seed/sample rows mistaken for runtime truth | `event_guidance` debt | registry decisions and CS-350 correction | CS-348; CS-353 E-014/E-017 |
| observability | logs, traces, request ids, validation/recovery metadata | audit-only investigation surface, not semantic proof | all provider-capable paths | operators/developers | trace data overclaimed as correctness | semantic grounding bounded from CS-348 | preserve provider-only metadata wording | CS-351 F-002; CS-352 F-002; CS-348 |

## Canonical Registry Decisions

### process_classification_registry

Decision: adopt
Owner: architecture owner

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| prompt_process_classification | v1 | CS-353 process inventory, CS-350 owner map | Category, provider capability, runtime truth status, decision, guardrail | Additive rows allowed; category changes require architecture owner approval | Deprecated processes remain mapped to source finding IDs until deleted by story | process, category, provider_capability, evidence_ids, finding_ids | CS-353 F-001/F-004 |

### prompt_input_registry

Decision: adopt
Owner: domain architecture owner

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| llm_astrology_input_v1 | v1 | structured natal facts and approved projections | prompt-visible `facts`, `signals`, `limits`, `shaping`; validation/audit blocks excluded | Prompt-visible block changes require version/hash review | `chart_json` and `natal_data` remain forbidden for modern natal prompt material | request_id, trace_id, projection_hash, llm_input_hash, evidence_refs | CS-350; CS-352 E-009/E-012; CS-348 |

### parallel_provider_registry

Decision: adopt
Owner: runtime gateway owner + product owner

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| guidance_provider_flow | v1 | guidance request, textual natal summary, context | active non-natal provider-capable flow | Compatible if public trigger and prompt-visible input family remain classified | Deprecate only with product decision and route/story evidence | route, use_case, request_id, trace_id | CS-353 E-011, F-001 |
| chat_provider_flow | v1 | message, chat history, persona, optional natal hint | active chat-mode provider-capable flow | Compatible if chat message shape remains classified | Deprecate only with product decision and route/story evidence | route, use_case, request_id, trace_id | CS-353 E-012, F-001 |
| horoscope_daily_provider_flow | v1 | daily prediction context, variant plan | active daily narration provider-capable flow; legacy marker non nominal | Variant semantics changes require classification update | Legacy route marker can be deprecated after follow-up story | variant_code, use_case, request_id, trace_id | CS-353 E-013/E-014, F-001 |

### recovery_registry

Decision: adopt
Owner: runtime owner

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| repair_prompt_flow | v1 | invalid provider output, validation errors, schema | recovery-only provider-capable second call | Any promotion to first-call behavior requires product/architecture decision | Remove only when validation strategy changes and tests prove no repair path | repair_attempted, validation_status, request_id, trace_id | CS-353 E-016 |
| fallback_prompt_flow | v1 | missing assembly, fallback catalog, unsupported provider profile | bounded non-nominal fallback path | Fallback rows are not public contract unless product approves | Deprecated fallback paths must retain evidence until removed | fallback_kind, use_case, provider_profile | CS-353 E-015, F-004 |

### legacy_carrier_registry

Decision: adopt with blocker
Owner: architecture owner + product owner

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| chart_json_natal_data | v1 | seeds, admin samples, tests, legacy/debt contexts | excluded from modern natal prompt when `llm_astrology_input_v1` exists | Existing non-modern contexts must be classified before reuse | Remove or keep only through explicit story | carrier_name, process, evidence_ids | CS-353 E-014/E-018, F-005 |
| event_guidance | needs-owner-decision | guidance seed and canonical contract using `chart_json` | debt unless product chooses migrate/delete/retain | No compatibility promise until owner decision | blocker: migrate, delete or retain as explicit debt | use_case, seed_path, carrier_name | CS-353 F-002 |

## Object / Entity Decisions

| Object | Kind | Lifecycle owner | Persistence | Serialization | Versioning | Surfaces | Decision | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `llm_astrology_input_v1` | value_object | natal domain owner | may feed audit persistence; prompt projection filtered | canonical JSON/hash material plus prompt-visible projection | v1 | internal, automation_or_llm, data_storage | canonical nominal natal input | CS-350; CS-352; CS-348 |
| `messages` | derived_object | gateway owner | logged under observability policy | ordered provider message list | provider messages v1 | automation_or_llm, observability | last gateway-owned payload before provider | CS-352 E-008/E-011 |
| `natal_chart_summary` / `build_chat_natal_hint` | derived_object | guidance/chat service owners | runtime only unless logged | textual prompt context | parallel provider flow v1 | public_api, internal, automation_or_llm | supported non-natal textual carrier | CS-353 E-011/E-012 |
| daily narration question/context | derived_object | horoscope daily owner | runtime/audit as configured | structured message context | horoscope daily provider flow v1 | public_api, internal, automation_or_llm | supported non-natal daily carrier | CS-353 E-013 |
| repair prompt | derived_object | runtime owner | recovery metadata/logs | repair prompt from invalid output/errors/schema | recovery v1 | internal, automation_or_llm, observability | recovery-only, not nominal | CS-353 E-016 |
| fallback config | value_object | runtime/config owner | catalog/config storage | fallback use-case config | recovery v1 | internal, automation_or_llm | non-nominal bounded fallback | CS-353 E-015 |
| seed prompt/assembly rows | core_entity | configuration owner | DB/provisioning | prompt/profile/assembly seed records | provisioning v1 | data_storage, internal | seed-only unless runtime loads accepted rows | CS-353 E-014 |
| admin sample payload | debug_artifact | admin owner | admin sample storage | sample payload fields, may include `chart_json` | admin policy v1 pending | admin_debug | admin-only; provider handoff only through manual execution | CS-353 E-017/F-003 |
| `chart_json` / `natal_data` | value_object | legacy/data owner | tests, samples, seeds, debt contexts | legacy carrier payload | legacy carrier v1 | test, admin_debug, data_storage | forbidden in modern natal prompt; bounded elsewhere | CS-353 E-014/E-018/F-005 |
| `event_guidance` | core_entity | product + architecture owner | seed/contract context | prompt context with `chart_json` | needs-owner-decision | internal, data_storage | blocker: decide migrate/delete/retain debt | CS-353 F-002 |

## Taxonomy des chemins de prompt generation

| Category | Definition | Provider-capable posture | Decision vocabulary | Sources |
| --- | --- | --- | --- | --- |
| nominal | flux natal moderne `llm_astrology_input_v1` | yes, supported | conserver/documenter | CS-350; CS-352 |
| parallele supporte | runtime actif hors carrier natal moderne | yes, supported if explicitly classified | documenter/conserver | CS-353 F-001 |
| legacy tolere | legacy/debt still present but not nominal | unknown or conditional | migrer/deprecier/supprimer/conserver as debt | CS-353 F-002 |
| fallback | bounded non-nominal recovery/config fallback | conditional | documenter as non nominal/deprecier if unneeded | CS-353 E-015 |
| repair | post-provider recovery after invalid output | yes, second call only | documenter as recovery/tester | CS-353 E-016 |
| bootstrap | seed/provisioning input | not by itself | documenter as seed-only | CS-353 E-014 |
| test | fixtures and guard tests | no real provider | conserver as guard evidence | CS-353 E-018 |
| admin | admin sample/manual execution | manual execution yes; samples alone no | decision owner/documenter/restrict | CS-353 F-003 |
| archive | docs and prior audits only | no | cite as source context only | CS-353 E-004 a E-010 |
| non runtime truth | any seed, sample, test, archive or audit-only artifact | no unless separate trigger proves handoff | exclude from runtime truth | CS-348; CS-353 |

## Matrice nominal/parallele/legacy/fallback/bootstrap/test/admin

| Process | Category | Provider capability | Runtime truth status | Decision | CS-350 impact | Guardrail | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Modern natal `llm_astrology_input_v1` | nominal | provider-capable | supported | conserver | keep as reference; add wording corrections from CS-351/352 | existing carrier boundary tests | documentation correction only |
| Guidance | parallele supporte | provider-capable | supported non-natal | documenter/conserver | add row in CS-350 matrix | future parallel-process classification scan | SC-001 / next-available-id |
| Guidance contextuelle | parallele supporte | provider-capable | supported non-natal | documenter/conserver | add row in CS-350 matrix | future parallel-process classification scan | SC-001 / next-available-id |
| Chat public | parallele supporte | provider-capable | supported chat-mode | documenter/conserver | add row in CS-350 matrix | future chat/provider classification scan | SC-001 / next-available-id |
| Chat public helper | parallele supporte | not provider-capable itself | helper only | documenter as helper | avoid naming it prompt owner | scan keeps helper separate from service | SC-001 / next-available-id |
| Shared natal textual context | parallele supporte | not provider-capable by itself | runtime helper | documenter as textual carrier | add non-natal carrier note | scan for `natal_chart_summary` classification | SC-001 / next-available-id |
| Horoscope daily narration | parallele supporte | provider-capable | supported non-natal | documenter/conserver | add separate daily narration row | future daily provider classification scan | SC-001 / next-available-id |
| Legacy daily prediction route marker | legacy tolere | provider-capable via daily path | non nominal marker | deprecier/documenter | state marker is not nominal | scan for legacy marker wording | follow-up under SC-001 or separate story |
| Fallback catalog | fallback | conditional provider-capable | runtime non nominal | documenter as non nominal | keep out of runtime truth | guard fallback terms and provider-capable status | SC-001; SC-002 after matrix |
| No-assembly bootstrap fallback | fallback/bootstrap | conditional provider-capable | bounded bootstrap/non-production | documenter as non nominal | clarify blank DB behavior | guard no-assembly is not production truth | SC-001 |
| Provider unsupported fallback | fallback | conditional provider-capable | non nominal/test-fallback | documenter as non nominal | clarify not provider policy | guard fallback classification | SC-001 |
| Repair prompts | repair | provider-capable after invalid output | recovery-only | documenter/tester | state not initial prompt source | guard repair as recovery-only | SC-001 |
| Guidance bootstrap seeds | bootstrap | seed-only unless runtime loads rows | provisioning | documenter seed-only | avoid runtime truth wording | seed/runtime truth scan | SC-001 |
| Horoscope narrator bootstrap seed | bootstrap | seed-only unless runtime loads rows | provisioning | documenter seed-only | avoid runtime truth wording | seed/runtime truth scan | SC-001 |
| Admin sample payloads | admin | not provider-capable by itself | admin artifact | documenter/restrict after owner decision | add admin-only classification if approved | admin sample != public runtime scan | blocker: admin owner decision |
| Admin manual execution | admin | provider-capable | admin-only | decision owner: document/restrict/decommission | open policy impact | guard admin-only provider-capable classification | blocker: product/architecture/admin owner |
| Legacy carriers in modern natal tests | test | not provider-capable in tests | test-only guard | conserver as guard evidence | cite tests | existing tests + scan | no new story |
| Historical/admin/test `chart_json` samples | test/admin | not public provider-capable | sample/test-only | document bounded contexts | classify separately from nominal | scan for carrier context | SC-001 |
| CS-350 narrative mentions | archive | not provider-capable | archival/source context | cite only | no runtime claim | source-context wording | no new story |
| `event_guidance` | legacy tolere/debt | conditional provider-capable if invoked | debt/unknown trigger | blocker: migrate/delete/retain | decision required before CS-350 final claim | guard against nominal promotion | needs-owner-decision |

## Decision par processus

| Process | observed | inferred | decision | blocker | open question | Sources |
| --- | --- | --- | --- | --- | --- | --- |
| Modern natal `llm_astrology_input_v1` | CS-352 confirms gateway, rich input and tests | stable as nominal reference | conserver as nominal | output schema owner split is broader blocker | none for process classification | CS-352 E-007/E-012; CS-348 |
| Guidance | public route to service to adapter/gateway | active non-natal prompt path | documenter/conserver as parallel supported | none | none | CS-353 E-011, F-001 |
| Guidance contextuelle | contextual route to service to adapter/gateway | active non-natal prompt path | documenter/conserver as parallel supported | none | none | CS-353 E-011, F-001 |
| Chat public | route/service/adapter/gateway | active chat-mode provider path | documenter/conserver as parallel supported | none | none | CS-353 E-012, F-001 |
| Chat public helper | response mapping helper | not prompt owner | documenter as helper only | none | none | CS-353 inventory |
| Shared natal textual context | summary/hint helper for guidance/chat | prompt-visible textual carrier in callers | documenter as carrier, not provider handoff | none | none | CS-353 inventory |
| Horoscope daily narration | direct gateway call from narration service | active daily provider path | documenter/conserver as parallel supported | legacy marker must stay non nominal | none | CS-353 E-013/E-014, F-001 |
| Legacy daily prediction route marker | `variant_code is None` marker | provider path but non nominal | deprecier or document as tolerated marker | owner needed if deletion desired | should marker be removed? | CS-353 inventory |
| Fallback catalog | synthetic fallback configs | can execute only in bounded fallback | documenter as fallback non nominal | none | product support status if promoted | CS-353 E-015 |
| No-assembly bootstrap fallback | bounded no-assembly condition | local/bootstrap behavior | documenter as bootstrap fallback | none | none | CS-353 E-015 |
| Provider unsupported fallback | provider fallback branch | non-nominal provider policy | documenter as fallback | none | none | CS-353 E-015 |
| Repair prompts | invalid output recovery | provider-capable second call | documenter/tester as recovery-only | none | none | CS-353 E-016 |
| Guidance bootstrap seeds | static seed rows | provisioning only | documenter seed-only | none | none | CS-353 E-014 |
| Horoscope narrator bootstrap seed | static seed rows | provisioning only | documenter seed-only | none | none | CS-353 E-014 |
| Admin sample payloads | CRUD/sample validation | no provider handoff alone | documenter admin artifact | admin policy needed when paired with manual execution | Should CS-350 document all sample contracts? | CS-353 E-017/F-003 |
| Admin manual execution | admin route calls gateway | provider-capable admin-only | owner decision required | product/architecture/admin owner | document, restrict or decommission? | CS-353 E-017/E-018/F-003 |
| Legacy carriers in modern natal tests | tests prove exclusion | guard evidence, not runtime | conserve as test guard | none | should long tests be mandatory? | CS-353 E-018/F-005; CS-348 open question |
| Historical/admin/test `chart_json` samples | sample/test contexts | bounded non-modern contexts | document bounded contexts | none | none | CS-353 E-014/E-017/E-018 |
| CS-350 narrative mentions | documentation only | archive/non runtime truth | cite only | none | none | CS-353 inventory |
| `event_guidance` | seed/contract with `chart_json`, no audited public trigger | debt with conditional provider capability if invoked | blocker: migrate/delete/retain | product/architecture owner | Which decision is accepted? | CS-353 E-014/E-015/E-018/F-002 |

## Impacts sur le document final CS-350

| Impact | Type | Action | Sources |
| --- | --- | --- | --- |
| Add one matrix for active non-natal provider-capable flows | documentation correction | rows for Guidance, Guidance contextuelle, Chat public, Horoscope daily narration | CS-353 F-001, SC-001 |
| Clarify `evidence` / `evidence_refs` dual role | documentation correction | validation-owned, excluded from provider prompt material, may feed audit persistence | CS-351 F-001; CS-352 F-001 |
| Replace strict `backend-only runtime` wording | documentation correction | use `runtime/provider-only metadata, not prompt-visible payload` for request/trace/use-case | CS-351 F-002; CS-352 F-002 |
| Keep fallback/repair/bootstrap/test/admin/archive separate | documentation correction | reuse taxonomy above; do not promote to runtime truth | CS-353 E-014/E-018 |
| Record `event_guidance` as blocker, not ordinary backlog | owner decision | migrate/delete/retain explicit debt before final supported claim | CS-353 F-002 |
| Classify admin manual execution | owner decision | document as admin-only provider-capable, restrict, or decommission | CS-353 F-003 |
| Add exact guardrail only after matrix accepted | governance follow-up | SC-002 after durable invariant exists | CS-353 F-004, SC-002 |

## Guardrails requis

| Guardrail | Verification proposal | Owner | Timing | Sources |
| --- | --- | --- | --- | --- |
| Parallel-process documentation invariant | `rg` checks accepted CS-350 matrix contains Guidance, Chat public, Horoscope daily, fallback, repair, bootstrap, admin, `provider-capable` | architecture owner | after CS-350 correction accepted | CS-353 F-001/F-004, SC-001/SC-002 |
| Legacy carrier anti-promotion | static scan ensures `chart_json`/`natal_data` are not described as modern natal prompt-visible | runtime/test owner | immediate in documentation story | CS-353 F-005; CS-352 E-012 |
| Admin-only provider capability classification | scan/admin policy test proves manual execution is labelled admin-only or restricted | admin owner | after F-003 decision | CS-353 F-003 |
| Seed/runtime truth separation | scan for seed/bootstrap rows classified as provisioning/non runtime truth | configuration owner | in CS-350 correction | CS-353 E-014 |
| Provider metadata wording | scan for `runtime/provider-only metadata, not prompt-visible payload` wording | documentation owner | in CS-350 correction | CS-351 F-002; CS-352 F-002 |
| Evidence refs dual role | scan for validation-owned and audit-persistence sentence | documentation owner | in CS-350 correction | CS-351 F-001; CS-352 F-001 |

## Operational Rules

| Rule area | Rule | Applies to | Invalidated by | Trace requirement | Owner | Sources |
| --- | --- | --- | --- | --- | --- | --- |
| Versioning | Version `prompt_process_classification_v1` when a process changes category, provider capability or runtime truth status. | decision matrix, CS-350 correction, guardrails | new public trigger, removed trigger, carrier change, provider handoff change | process, version, evidence IDs, finding IDs | architecture owner | CS-353 F-001/F-004 |
| Trace | Provider-capable rows must cite trigger, owner, handoff and evidence IDs; request/trace/use-case remain provider metadata, not prompt-visible payload. | nominal, parallel, admin, repair, fallback | missing route/owner/handoff evidence | request_id, trace_id, use_case, source evidence | runtime owner | CS-351 F-002; CS-352 F-002; CS-353 |
| Cache | Any future cache for generated output must key on prompt-affecting inputs and classification version, not audit-only fields or samples. | nominal and parallel provider flows | prompt-visible input, prompt version, schema/provider profile, classification version | input hash, prompt version, classification version | data owner | CS-348 cache rule; CS-353 F-001 |
| Replay | Replay/admin execution is investigation/admin surface and cannot prove semantic correctness or public support. | admin/debug, observability, repair/fallback | raw payload exposure, policy change, new public consumer | replay snapshot id, admin actor, trace_id | operations/security owner | CS-348; CS-353 F-003 |
| Invalidation | Documentation and guardrails must be revalidated when a process becomes provider-capable, loses provider capability, or changes category. | all matrix rows | route/gateway changes, seed promotion, admin execution policy change | source audit/story ID, process ID | architecture owner | CS-353 F-004 |
| Migration | Legacy/debt paths require explicit migrate/delete/retain decision before code or doc promotion. | `event_guidance`, legacy marker, `chart_json` contexts | owner decision, deletion, runtime trigger proof | decision owner, story ID, evidence IDs | product + architecture owner | CS-353 F-002 |
| Observability | Observability must report execution/recovery/admin status without turning traces, samples or audit anchors into prompt truth. | logs, admin execution, fallback/repair | new consumer, wording change, redaction change | trace_id, recovery status, provider capability class | operations/data owner | CS-348; CS-351/352 |

## Blockers and decision owners

| Type | Blocker / decision | Owner | Blocks | Required owner decision | Sources |
| --- | --- | --- | --- | --- | --- |
| blocker | `event_guidance` keeps a `chart_json` seed/contract surface with no audited public trigger. | product owner + architecture owner | final CS-350 supported/debt claim; any implementation on event guidance | migrate, delete, or retain as explicit debt | CS-353 F-002, E-014/E-015/E-018 |
| blocker | Admin manual execution is admin-only but provider-capable and may use sample payload contexts. | product owner + architecture owner + admin/security owner | CS-350 admin policy wording; guardrail scope | document as admin-only provider-capable, restrict, or decommission | CS-353 F-003, E-017/E-018 |
| decision | Exact parallel-process guardrail is absent. | architecture owner | SC-002/governance hardening | add after CS-350 matrix is durable, or explicitly defer | CS-353 F-004 |
| decision | CS-350 corrections are required but not in this story. | documentation owner | final doc accuracy | authorize documentation correction story using this report | CS-351 F-001/F-002; CS-352 F-001/F-002; CS-353 SC-001 |
| blocker | Output schema ownership split remains broader architecture blocker. | product owner + architecture owner | stable schema-dependent contracts, cache/replay identity | choose nominal runtime owner | CS-348 blocker |

## Ordered implementation roadmap - Stories candidates ordonnees par risque

### Story 1: Correct CS-350 with the accepted prompt-process matrix

Story ID: next-available-id
Source label: CS-353 SC-001
Goal: Amend CS-350 with the process matrix and taxonomy from this report.
Source audits: CS-351, CS-352, CS-353
Source findings: CS-351 F-001/F-002; CS-352 F-001/F-002; CS-353 F-001/F-005
Scope: documentation-only correction for nominal, parallel, fallback, repair, bootstrap, test, admin, archive and provider-capable rows.
Out of scope: runtime code, provider call, DB migration, frontend.
Dependencies: owner wording for unresolved blockers must stay explicit if not resolved.
Acceptance criteria:
- CS-350 has one process matrix covering every CS-353 process or explicit blocker row.
- `evidence_refs` and provider metadata wording are corrected.
- `chart_json`/`natal_data` are not promoted to modern natal prompt-visible inputs.
Validation evidence:
- `rg` for Guidance, Chat public, Horoscope daily, fallback, repair, bootstrap, admin, provider-capable.
- bounded `git status` proves no app code changed.
Blockers / decisions:
- If admin or `event_guidance` wording implies product support, stop for owner decision.
Stop condition: any proposed wording changes runtime behavior or hides blockers.

### Story 2: Decide `event_guidance` legacy carrier status

Story ID: needs-tracker-remap
Source label: CS-353 Decision item / F-002
Goal: Choose migrate, delete, or retain `event_guidance` as explicit debt.
Source audits: CS-353
Source findings: F-002
Scope: product/architecture decision record, then implementation story only if authorized.
Out of scope: opportunistic route/provider changes.
Dependencies: product owner and architecture owner decision.
Acceptance criteria:
- Decision states final category, provider capability, compatibility and deprecation posture.
- Any follow-up story has exact files/surfaces and guard evidence.
Validation evidence:
- decision artifact cites E-014/E-015/E-018 and bounded scans.
Blockers / decisions:
- Product/architecture owner approval required.
Stop condition: no public trigger proof or owner decision is available.

### Story 3: Decide admin manual execution policy

Story ID: needs-tracker-remap
Source label: CS-353 Decision item / F-003
Goal: Classify admin manual execution as documented admin-only provider-capable, restricted, or decommissioned.
Source audits: CS-353
Source findings: F-003
Scope: policy/documentation decision and possible guardrail requirements.
Out of scope: changing admin execution behavior without explicit authorization.
Dependencies: product, architecture, admin/security owner decision.
Acceptance criteria:
- Admin sample payload CRUD and admin manual execution are distinct in documentation.
- Provider-capable admin execution is guarded by policy wording or follow-up implementation.
Validation evidence:
- scans for admin-only/provider-capable classification; bounded app status.
Blockers / decisions:
- Admin/security owner decision required if restriction/decommission is chosen.
Stop condition: policy cannot be classified without owner input.

### Story 4: Add exact guardrail for parallel prompt process classification

Story ID: next-available-id
Source label: CS-353 SC-002
Goal: Add a durable regression guardrail after CS-350 matrix is accepted.
Source audits: CS-353
Source findings: F-004
Scope: `_condamad/stories/regression-guardrails.md` only, with exact terms and surfaces.
Out of scope: runtime tests or code refactor.
Dependencies: Story 1 accepted or equivalent matrix approved.
Acceptance criteria:
- Guardrail names exact CS-350 matrix or successor artifact.
- Scans prove provider-capable, fallback, repair, bootstrap, admin, test and archival statuses remain classified.
Validation evidence:
- `rg` over CS-350 and regression guardrails.
Blockers / decisions:
- Architecture owner approval.
Stop condition: no durable matrix exists.

### Story 5: Revisit broader schema and semantic blockers from CS-348

Story ID: next-available-id
Source label: CS-348 roadmap
Goal: Keep CS-354 classifications compatible with output schema and bounded semantic grounding decisions.
Source audits: CS-348, CS-349
Source findings: CS-348 blockers
Scope: architecture decision/update only if future implementation depends on schema/cache/replay semantics.
Out of scope: CS-354 documentation correction.
Dependencies: product/data owner decisions.
Acceptance criteria:
- Schema owner and semantic grounding claims are not overclaimed in any prompt-process story.
Validation evidence:
- architecture scans and targeted tests as defined by future story.
Blockers / decisions:
- product/data owner acceptance.
Stop condition: implementation story requires stronger proof than audits provide.

## Open questions produit ou technique

| Question | Why it matters | Owner | Blocks | Suggested default | Sources |
| --- | --- | --- | --- | --- | --- |
| Should `event_guidance` be migrated, deleted or retained as explicit debt? | It uses `chart_json` and could be confused with nominal guidance if provider-capable invocation appears later. | product owner + architecture owner | final CS-350 claim and any event guidance implementation | retain as debt only until explicit decision, with no public support claim | CS-353 F-002 |
| Should admin manual execution be documented as provider-capable admin-only, restricted, or decommissioned? | It can call gateway from admin sample contexts and must not be hidden as non-runtime. | product owner + admin/security owner | CS-350 admin section and guardrail story | document as admin-only provider-capable until policy changes | CS-353 F-003 |
| Should exact parallel-process guardrail be added after documentation correction? | Prevents future agents from collapsing non-natal/fallback/admin paths into nominal prompt generation. | architecture owner | governance hardening | add after CS-350 matrix is accepted | CS-353 F-004/SC-002 |
| Are long legacy carrier tests mandatory in CI? | Affects confidence that `chart_json`/`natal_data` remain excluded from modern natal prompts. | test owner | validation policy | keep long-run guard unless CI policy changes | CS-353 F-005; CS-348 open question |
| Which component owns output schema identity for cache/replay compatibility? | Broader architecture dependency for stable generated output contracts. | product owner + architecture owner | future schema/cache/replay stories | use CS-348 suggested nominal resolver until decided | CS-348 |

## Validation plan

- Check report exists under `_condamad/architecture/prompt-generation-document-review/2026-05-27-2338/archi-parallel-legacy-prompt-generation-report.md`.
- Run `rg` for required headings: `Executive architecture summary`, `Source map`, `Taxonomy`, `Decision par processus`, `Guardrails`, `Open questions produit ou technique`.
- Run `rg` for taxonomy/process terms: `nominal`, `parallele`, `legacy`, `fallback`, `repair`, `bootstrap`, `test`, `admin`, `provider-capable`.
- Run `rg` for source references and gaps: `CS-350`, `CS-351`, `CS-352`, `CS-353`, `Evidence gap`, `Open question`.
- Run bounded `git status --short -- backend/app backend/tests frontend/src backend/migrations _condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md` to prove no app or CS-350 edit.

## Missing Evidence

- Evidence gap: no direct tracker remap was provided for CS-353 `SC-001` or `SC-002`; this report keeps them as source labels.
- Evidence gap: no owner decision was supplied for `event_guidance`; classified as blocker.
- Evidence gap: no owner decision was supplied for admin manual execution policy; classified as blocker.
- Evidence gap: no real provider call is introduced or required by CS-354; provider capability relies on audited source evidence from CS-353.
