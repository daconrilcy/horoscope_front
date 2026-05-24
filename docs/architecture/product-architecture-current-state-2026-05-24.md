<!-- Commentaire global: ce document synthetise l'architecture produit actuellement livree sans exposer les surfaces runtime internes comme API publiques. -->

# Product Architecture Current State - CS-255

## Résumé exécutif

### Executive architecture decision summary

| Type | Synthese | Sources |
| --- | --- | --- |
| observed | CS-237 a CS-254 sont livres comme chaine audit -> architecture -> primitives backend/documentation. Le delivery report est la source primaire de l'etat livre. | `_condamad/reports/astro-canonical-runtime-transition-CS237-CS254-delivery-report.md`; CS-246..CS-254 `generated/10-final-evidence.md` |
| decision | `ChartObjectRuntimeData` et `CalculationGraph` sont des primitives canoniques internes; elles ne deviennent pas des contrats API publics. | CS-245 `05-executive-summary.md`; CS-238 F-001/E-005..E-008; CS-244 F-001/E-004/E-008/E-009/E-010/E-019 |
| decision | La direction autorisee est `calcul -> faits -> signaux -> narration/projection`; les prompts, textes narratifs et providers AI ne sont pas source de verite astrologique. | CS-243 F-001..F-003/E-006..E-014; CS-254 final evidence |
| observed | `natal_chart_v1` est le seul runtime de famille livre; `transit_chart_v1` est le chemin temporel selectionne, mais aucune exposition publique temporelle n'est livree. | CS-245 summary; CS-246 final evidence; CS-253 final evidence |
| decision | Les primitives produit publiques sont des projections nommees: `structured_facts`, `beginner_summary`, `expert_technical_projection`; `fixed_star_contacts` et `astrologer_debug_data` restent `needs-user-decision`; `llm_input` reste LLM-only. | `docs/architecture/official-product-primitives-public-projections.md`; CS-251 final evidence |
| blocker | `fixed_star_contacts`, `astrologer_debug_data`, preuve ephemeris externe, gouvernance doctrine et runtime temporel public restent bloques par decisions produit, securite, data ou doctrine. | Delivery report sections 9/11; CS-238 F-002/F-003; CS-240 F-001..F-006; CS-250 final evidence |
| blocker | Les contradictions visibles ne sont pas lissees: runtime interne utile mais public interdit, cache local mais cache durable non autorise, DB/Python tous deux proprietaires de regles, fixed stars seulement en conjonctions zodiacales. | CS-245 `02-gap-register.md`; CS-245 `04-risk-matrix.md` |

Dependencies les plus risquees: registry/manifest avant familles non natales, projections publiques avant API/frontend, preuve astronomique avant runtime temporel public, gouvernance doctrine avant extension traditionnelle, trace/cache/replay avant support durable.

## Architecture produit en place

Etat courant observe: CS-237..CS-244 ont produit les audits source; CS-245 a produit l'architecture de transition; CS-246..CS-254 ont livre les primitives internes et contrats de garde. Cette synthese est un capstone: elle ne refait pas les audits et ne modifie aucun backend, frontend, test, migration, route, serializer ou contrat OpenAPI.

Decision produit centrale: le systeme possede une architecture runtime canonique interne, mais la valeur produit doit sortir par des projections explicites. `ChartObjectRuntimeData`, `chart_objects`, raw calculation graph payloads et traces brutes sont des surfaces internes, admin/debug protegees ou LLM-only selon le cas; elles ne sont pas des API publiques.

## Sources obligatoires citées

Cette section verrouille la tracabilite demandee par CS-255: les assertions
d'etat livre doivent pointer vers ces sources plutot que vers une deduction non
sourcee.

| Source obligatoire | Role dans ce rapport |
| --- | --- |
| `_condamad/reports/astro-canonical-runtime-transition-CS237-CS254-delivery-report.md` | Source primaire de l'etat livre CS-237..CS-254 et des risques residuels. |
| `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/05-executive-summary.md` | Decisions CS-245: primitives internes, rejet du raw public, blockers et gates. |
| `_condamad/architecture/astro-canonical-runtime-transition/2026-05-23-2155/03-story-candidates.md` | Remap `SC-ARCH-*` vers CS-246..CS-254 et ordre de dependance. |
| `docs/architecture/official-product-primitives-public-projections.md` | Primitives produit publiques, surfaces interdites, statuts `needs-user-decision`. |
| `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/generated/10-final-evidence.md` | Preuve livree du registry de familles de graphes. |
| `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/generated/10-final-evidence.md` | Preuve livree du manifest et du contrat node IO. |
| `_condamad/stories/CS-248-calculation-graph-execution-trace-contract/generated/10-final-evidence.md` | Preuve livree du contrat de trace d'execution redigee/masquee. |
| `_condamad/stories/CS-249-chart-object-capability-taxonomy-matrix/generated/10-final-evidence.md` | Preuve livree de la taxonomie/capability matrix des objets astrologiques. |
| `_condamad/stories/CS-250-astronomical-proof-before-public-temporal-runtime/generated/10-final-evidence.md` | Preuve livree du gate de preuve astronomique avant runtime temporel public. |
| `_condamad/stories/CS-251-official-product-primitives-public-projection-roadmap/generated/10-final-evidence.md` | Preuve livree des primitives publiques officielles et exclusions raw runtime. |
| `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/generated/10-final-evidence.md` | Preuve livree de la gouvernance doctrine/source ownership. |
| `_condamad/stories/CS-253-first-temporal-technique-implementation-path/generated/10-final-evidence.md` | Preuve livree du chemin `transit_chart_v1` selectionne sans exposition publique. |
| `_condamad/stories/CS-254-ai-scoring-narrative-input-contract/generated/10-final-evidence.md` | Preuve livree du contrat `llm_input` et de la frontiere narration. |

## Audit source map

| Audit | Scope | Closure status | Key architecture inputs | Evidence IDs | Findings used | Blockers | Deferred context | Used for |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CS-237 feature coverage | Couverture des techniques astrologiques. | delivered audit | Natal solide; predictif/non-planetaire absent ou reference-only. | E-005, E-006, E-010, E-014, E-015 | F-001..F-005 | Predictive runtime owner, lots/Chiron/asteroids/midpoints. | Parans, directions symboliques, firdaria. | capability matrix, roadmap |
| CS-238 runtime surface exposure | Exposition runtime/public/admin. | delivered audit | Raw `chart_objects` unsafe; projections controlees requises. | E-005..E-008, E-011, E-012, E-014 | F-001..F-005 | Admin/debug authz, fixed-star projection policy. | Guard exact de vocabulaire d'exposition. | surface matrix, registry decisions |
| CS-239 chart object capability payload | Capabilities et payloads objets. | delivered audit | Matrice capability/taxonomy necessaire. | E-005..E-019 | F-001..F-006 | Derived point taxonomy, angle/cusp aspectability, node category. | Validation centralisee phase-aware. | object/entity decisions |
| CS-240 reference governance | Gouvernance DB/Python/doctrine. | delivered audit | Source ownership split sur seuils, poids, profils. | E-007..E-019 | F-001..F-006 | Doctrine/data owner decisions. | Migration de sources de regles. | operational rules |
| CS-241 astronomical accuracy | Precision astronomique. | delivered audit | SwissEph/proof/golden/ephemeris gates. | E-005..E-016 | F-001..F-005 | External ephemeris references/tolerances. | Exact guard apres hardening. | validation plan, blockers |
| CS-242 calculation graph readiness | Readiness multi-graph. | delivered audit | Registry, manifest, trace, cache/invalidation requis. | E-006..E-016 | F-001..F-006 | Durable cache owner, replay policy. | Tracker label remap. | canonical registry decisions |
| CS-243 calculation/interpretation boundary | Frontiere calcul/interpretation. | delivered audit | Split internal/public/LLM; readiness; narrative guard. | E-006..E-014, E-017, E-018 | F-001..F-004 | Public/LLM subshape ownership. | Historical namespace caveats. | AI/LLM rules |
| CS-244 product data needs | Besoins expert/beginner/AI/PDF/debug. | delivered audit | Expert/beginner/fixed-star projections; debug decision. | E-004..E-021 | F-001..F-005 | `astrologer_debug_data` audience/auth/retention. | Product-data audit guardrail. | public projections roadmap |
| CS-245 architecture transition | Synthese audits -> stories CS-246..CS-254. | PASS after correction | Internal primitives adopted; raw public exposure rejected; remap applied. | PA-E-001..PA-E-014 | GAP-001..GAP-016; R-001..R-011 | Owner decisions and remap caveats. | none | capstone baseline |
| CS-246..CS-254 final evidence | Primitives backend/docs livrees. | PASS per story evidence | Registry, manifest, trace, taxonomy, proof, projections, doctrine, temporal selection, AI input. | story final evidence files | SC-ARCH-001..SC-ARCH-008 | Remaining product/security/data decisions. | Frontend/API implementation future. | delivered-state proof |

Story label caveats: CS-245 noted that source labels such as CS-243, CS-244 and CS-245 were already allocated and had to be remapped. The delivered mapping in `03-story-candidates.md` maps `SC-ARCH-001`..`SC-ARCH-008` to CS-246..CS-254. Future roadmap items below keep audit/story candidate IDs as provenance and use `next-available-id` or `needs-user-decision`, not recycled source labels.

## Primitives canoniques internes

### Capability matrix

| Capability / family | Inputs | Objects required | Canonical contracts required | Surfaces required | Status | Blockers | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `natal_chart_v1` | birth data, house/zodiac options, reference data | planets, luminaires, angles, cusps, supported astral points | graph family registry, natal manifest, redacted trace, taxonomy | internal, public_api via existing natal projections, frontend existing, observability | implemented | none for current natal runtime | CS-237 F-001; CS-246..CS-249 evidence |
| `transit_chart_v1` | natal chart, transit date/time/location, ephemeris proof | natal objects, transiting objects, relationships | family registry, manifest template, proof gate, temporal selection | internal now; public_api blocked | partial | public runtime and API exposure not delivered | CS-253 evidence; CS-250 evidence; CS-242 F-001/F-005 |
| Other temporal families | multi-chart inputs | synastry/return/progression/composite/profection objects | registry entries and future manifests | internal only until selected | blocked | product choice, proof, doctrine | CS-237 F-001; CS-246 evidence; CS-253 evidence |
| Chart object taxonomy | chart object runtime payloads | planets, luminaires, angles, cusps, fixed stars, lots, calculated points | capability taxonomy matrix | internal, observability | partial | lots/Chiron/asteroids/midpoints and angle/node policies | CS-239 F-001..F-006; CS-249 evidence |
| Expert public projection | stable technical fields only | structured public facts | `expert_technical_projection` | public_api future, frontend future | framed | exact field list and raw exclusions per API story | CS-244 F-001; CS-251 evidence |
| Beginner summary | compact translated safe facts | structured facts, labels, masking | `beginner_summary` | public_api future, frontend future, AI output | framed | deterministic contract not implemented as API | CS-244 F-002; CS-251 evidence |
| Fixed-star contacts | conjunction contacts, star catalog refs | fixed stars, target objects | `fixed_star_contacts` if approved | blocked public; LLM/internal possible | blocked | `needs-user-decision` public/gated/rejected | CS-237 F-002; CS-238 F-002; CS-251 evidence |
| Astrologer/debug data | traces, audit rows, graph runtime | debug artifacts | protected admin/debug contract | admin_debug blocked | blocked | audience, authz, retention, redaction | CS-238 F-003; CS-244 F-004 |
| AI narrative input | interpretation input, structural facts, signals, source versions | narrative structural facts/signals | `llm_input`, AI narrative input contract | automation_or_llm | implemented internal/LLM-only | scoring/public masking policy future | CS-243 F-001..F-003; CS-254 evidence |

## Surfaces produit et niveaux d'exposition

### Surface matrix

| Surface | Current contract | Expected contract | Capabilities exposed | Consumers | Risks | Blockers | Required changes | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| internal | `ChartObjectRuntimeData`, `CalculationGraph`, registry, manifest, trace, taxonomy | Versioned internal contracts with owners and redaction | natal runtime, selected temporal path, AI input assembly | backend runtime/services | accidental public coupling | none for internal use; owner decisions for extensions | keep canonical modules as owners | CS-245 summary; CS-246..CS-254 evidence |
| public_api | Existing natal public payloads; no raw graph/object/traces | explicit projections: `structured_facts`, `expert_technical_projection`, `beginner_summary` | stable facts only | frontend, public users, PDF | raw runtime leak, OpenAPI drift | fixed-star policy, debug exclusion | future API contract stories before frontend work | CS-238 F-001; CS-244 F-001/F-002; CS-251 |
| admin_debug | No protected graph/debug product surface evidenced | protected, authorized, redacted trace/debug artifact if approved | traces, audit rows, diagnostic facts | support/admin/astrologer if approved | privacy/security leakage | product/security decision | decide audience/auth/retention first | CS-238 F-003; CS-244 F-004 |
| automation_or_llm | AI narrative input contract; no provider integration | LLM-only input from facts/signals/source versions | `llm_input`, readiness, projection links | AI narration/scoring services | prompt becomes source of truth | scoring/masking policy | keep provider-neutral contract | CS-243 F-001..F-003; CS-254 |
| frontend | Existing natal simple/expert surfaces only | consume public projections after API contract | current natal display, future expert/beginner | React app | fields inferred by availability | API contracts not delivered for new projections | no frontend before API contract | CS-244 F-001/F-002; CS-251 |
| data_storage | DB/Python rule sources, no durable graph replay/cache owner | governed source ownership, no durable cache without keys | doctrine/rules, evidence, future cache | backend/data owners | stale cache, divergent rules | data/product doctrine owner | classify thresholds/weights/profiles; define cache keys | CS-240 F-001..F-006; CS-242 F-005; CS-252 |
| observability | redacted execution trace contract internal; ephemeris proof evidence | trace != provenance != replay; reproducible proof metadata | runtime diagnostics, proof | backend/support | replay inferred from trace | replay/storage policy, external ephemeris proof | keep redaction; add replay only by decision | CS-248; CS-250; CS-242 F-003/F-005 |

## Canonical registry decisions

### Graph family registry

Decision: adopt
Owner: architecture/backend astrology

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `natal_chart_v1` | v1 | natal birth/options | graph definition + manifest | backward-compatible manifest comparison | no alias without registry decision | graph_code, graph_version, run_id | CS-246, CS-247, CS-248 |
| `transit_chart_v1` | v1 | natal + transit datetime/options | selected path contract, not public runtime | public compatibility deferred | rejected alternatives stay closed | selected_family, gate_state | CS-253; CS-250 |
| other family codes | v1 reserved | family-specific | blocked registry metadata | no runtime until owner/manifest/proof | rejected/closed status explicit | blocker/status/user_decisions | CS-246; CS-253 |

### Public projection registry

Decision: adopt for roadmap, defer API implementation
Owner: product/API/frontend

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `structured_facts` | v1 | stable natal public data | public structured facts | OpenAPI-ready once implemented | deprecate only with API version | source primitive, source version | CS-251; CS-244 F-001 |
| `expert_technical_projection` | v1 | selected technical fields | expert projection | explicit field compatibility | no raw fallback | source fields, exclusion proof | CS-251; CS-244 F-001 |
| `beginner_summary` | v1 | compact facts, labels, masking | beginner projection | deterministic summary contract | no raw score exposure | masking policy, evidence refs | CS-251; CS-244 F-002 |
| `fixed_star_contacts` | v1 candidate | contacts + policy | blocked public/gated/rejected | none until decision | rejected/gated/public explicit | decision owner, source rule | CS-251; CS-238 F-002 |
| `astrologer_debug_data` | v1 candidate | traces/audit rows | blocked protected surface | none until authz | no public fallback | retention, redaction, actor | CS-251; CS-244 F-004 |
| `llm_input` | v1 | facts/signals/source versions | LLM-only, not public API | provider-neutral | no frontend exposure | source_versions, masking | CS-254; CS-243 F-001 |

### Doctrine and proof registry

Decision: adopt internal governance, defer owner policy choices
Owner: product astrology/data/security

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| doctrine governance | v1 | thresholds, weights, profiles, sources | owner/status registry | owner changes require explicit transition | no silent threshold replacement | rule_family, source_owner, doctrine_status | CS-240 F-001..F-006; CS-252 |
| astronomical proof | v1 | golden cases, ephemeris mode/hash/path | proof manifest | tolerance changes are versioned | no public temporal proof downgrade | engine, path_version, path_hash, tolerance | CS-241 F-001..F-004; CS-250 |

## Object / entity decisions

| Object | Kind | Lifecycle owner | Persistence | Serialization | Versioning | Surfaces | Decision | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ChartObjectRuntimeData` | derived_object | backend astrology runtime | runtime/internal only | forbidden as public schema | internal payload version via runtime contracts | internal, LLM-derived refs only | decision: internal canonical, not API public | CS-238 F-001; CS-239 F-006; CS-245 |
| `chart_objects` | derived_object | backend astrology runtime | internal calculation result | excluded from public JSON dump | tied to runtime version | internal | decision: never public raw surface | CS-238 F-001; CS-251 |
| `CalculationGraph` | derived_object | backend architecture | runtime graph definition | manifest/schema, not raw public payload | graph_code + graph_version | internal, observability | decision: orchestration primitive | CS-242 F-001..F-004; CS-247 |
| Execution trace | debug_artifact | backend/observability/security | internal evidence only unless approved | redacted keys/status/durations/errors | trace contract version | internal, observability, admin_debug blocked | decision: trace != replay != provenance | CS-242 F-003; CS-248 |
| Ephemeris proof | debug_artifact | backend/data | evidence/proof manifest | proof JSON/trace metadata | proof/tolerance version | observability, validation | decision: gate public temporal claims | CS-241; CS-250 |
| Doctrine rule source | external_reference | product astrology/data | DB/Python/docs as classified | governance registry | owner transitions versioned | internal, data_storage | decision: no unclassified thresholds/weights | CS-240; CS-252 |
| Public projection | presentation_model | product/API/frontend | future API contract | stable OpenAPI shape when implemented | projection_id_v1 | public_api, frontend | decision: only projection leaves runtime | CS-244; CS-251 |
| AI narrative input | value_object | interpretation/product | internal service contract | provider-neutral structured sections | contract_version | automation_or_llm | decision: LLM-only input, no provider source of truth | CS-243; CS-254 |

## Frontières calcul / interprétation / narration

Decision: le calcul produit des faits structures; l'interprétation produit des signaux pre-narratifs; la narration/projection consomme ces faits et signaux. Le sens autorise est exactement `calcul -> faits -> signaux -> narration/projection`.

| Layer | Allowed responsibility | Forbidden shortcut | Sources |
| --- | --- | --- | --- |
| calcul | Construire objets, graphes, preuves, traces redigees/masquees. | importer provider AI, texte final utilisateur, prompt comme regle. | CS-243 F-003; CS-254 evidence |
| faits | Stabiliser `structured_facts`, manifest, taxonomy, proof metadata. | exposer `ChartObjectRuntimeData` ou raw calculation graph payloads. | CS-238 F-001; CS-251 |
| signaux | Produire readiness et signaux interpretatifs depuis faits. | recalculer le runtime ou ignorer gouvernance doctrine. | CS-243 F-001/F-002; CS-254 |
| narration/projection | Rendre un resume, projection expert, ou input LLM provider-neutral. | devenir source de verite astrologique ou API raw. | CS-244 F-002; CS-254 |

## Familles astrologiques et statut produit

| Family | Runtime status | Selected path | Public exposure | Decision status | Sources |
| --- | --- | --- | --- | --- | --- |
| `natal_chart_v1` | implemented | current canonical natal graph | existing public natal projections only; raw internals excluded | delivered | CS-237; CS-246..CS-249 |
| `transit_chart_v1` | selected, non-public | chemin sélectionné par CS-253 apres preuve CS-250 | exposition publique absente | selected / blocked for public API | CS-250; CS-253 |
| synastry/returns/progressions/composite/profection/forecasting | not implemented or closed candidates | none | none | blocked/closed until product and proof decisions | CS-237 F-001; CS-253 |
| fixed stars | conjunction contacts internal/LLM-ready | no public path selected | `fixed_star_contacts` blocked | needs-user-decision | CS-237 F-002; CS-251 |
| lots/asteroids/Chiron/midpoints | no runtime owner | none | none | needs-user-decision | CS-237 F-004; CS-239 F-003 |
| nodes/angles/cusps | partial current behavior | natal policy only | public projection depends on stable capability choices | partial / needs-user-decision | CS-239 F-004/F-005; CS-249 |

## Operational rules

| Rule area | Rule | Applies to | Invalidated by | Trace requirement | Owner | Sources |
| --- | --- | --- | --- | --- | --- | --- |
| Versioning | Every graph/projection/LLM/proof contract uses explicit v1 identity. | graph families, projections, AI input, proof | inputs, output shape, semantics, ordering, replay/cache identity | contract_version or graph_version | architecture/backend/product | CS-242 F-002/F-004; CS-254 |
| Trace | Trace is redacted and separate from provenance and replay. | calculation graph execution | node schema, error kind, redaction policy | run_id, graph_code, graph_version, node status, input/output keys | backend/security | CS-242 F-003; CS-248 |
| Cache | Runner-local cache is allowed; durable cache is blocked until keys exist. | graph runtime, future app cache | graph version, input fingerprint, reference version, ephemeris source | cache hit state without cached value | data/architecture | CS-242 F-005; CS-248 |
| Replay | Replay is not inferred from trace; it needs explicit storage/input/version policy. | support/admin/debug | missing retention/auth/storage decision | replay snapshot owner and retention if approved | security/product/data | CS-238 F-003; CS-242 F-003 |
| Invalidation | Public/runtime outputs invalidate on graph, doctrine, ephemeris, projection contract or masking changes. | projections, temporal runtime, AI input | graph/manifest/proof/doctrine/projection changes | source_versions and proof metadata | backend/data/product | CS-240; CS-250; CS-254 |
| Migration | Rule ownership transitions require explicit source owner and doctrine status. | thresholds, weights, profiles | DB/Python ownership change or duplicate active source | rule_family/source_owner/doctrine_status | product astrology/data | CS-240 F-001..F-006; CS-252 |
| Observability | Proof and trace evidence must be reviewable without exposing raw runtime publicly. | proof, trace, admin/debug | missing ephemeris/hash/tolerance or raw leak | path_version/path_hash/tolerance/redaction | backend/security/data | CS-241; CS-248; CS-250 |
| Backward compatibility | Public projections need stronger compatibility than internal runtime objects. | public_api/frontend | renamed field, semantic change, removed masking | projection_id, source evidence | product/API/frontend | CS-244; CS-251 |

## Garde-fous et validations

Garde-fous observes:

- CS-246..CS-254 final evidence cite des validations sous venv, lint/tests et controles `app.openapi()`/`app.routes` selon les stories.
- CS-251 prouve que `chart_objects`, `ChartObjectRuntimeData`, raw calculation graph payloads et `interpretation_input` restent hors API publique.
- CS-253 prouve que `transit_chart_v1` est selectionne sans route, schema OpenAPI, frontend ou migration publique.
- CS-254 prouve que l'AI narrative input est provider-neutral et consomme des faits/signaux, pas des artefacts de generation texte.

Plan de validation CS-255:

| Check | Purpose |
| --- | --- |
| `Test-Path docs/architecture/product-architecture-current-state.md` | AC1 document present |
| `rg` source/primitive/surface/blocker scans | AC2..AC9 content shape |
| Python path assertions after `.\\.venv\\Scripts\\Activate.ps1` | evidence artifact presence |
| `git status --short -- frontend/src backend/app backend/tests backend/app/tests backend/migrations` | AC10 application roots unchanged by CS-255 |

## Limites et décisions ouvertes

## Blockers and decision owners

| Type | Item | Why it matters | Owner | Blocks | Sources |
| --- | --- | --- | --- | --- | --- |
| blocker | `fixed_star_contacts` policy | Contacts exist, but public/gated/rejected status is undecided. | product/API/security | CS-257-style public fixed-star projection | CS-238 F-002; CS-251 |
| blocker | `astrologer_debug_data` | Debug/astrologer surface needs audience, authz, retention and masking; c'est une décision sécurité et produit. | product/security | admin_debug API/frontend | CS-238 F-003; CS-244 F-004 |
| blocker | Temporal public runtime | `transit_chart_v1` selected but no public route/OpenAPI/frontend delivered. | product/backend/API | public transit chart | CS-253; CS-250 |
| blocker | Ephemeris proof deployment | Moshier integrated proof is recorded; external `.se1` deployment hash/path policy remains a risk. | data/backend | stronger public accuracy claims | CS-250 remaining risk; CS-241 F-003/F-004 |
| blocker | Doctrine governance policy | DB/Python rule sources still need owner decisions for broad expansion. | product astrology/data | doctrine-heavy temporal/traditional features | CS-240 F-001..F-006; CS-252 |
| open question | Exact expert fields | Public expert projection needs field selection. | product/API | `expert_technical_projection` API story | CS-244 F-001; CS-251 |
| open question | Beginner masking policy | Beginner projection needs deterministic masking/labels. | product/API | `beginner_summary` API story | CS-244 F-002; CS-251 |

## Prochaines stories recommandées

## Ordered implementation roadmap

### Story 1: Define expert technical public projection contract

Story ID: next-available-id
Source label: CS-251 roadmap `expert_technical_projection`; CS-244 SC candidate provenance
Goal: create a public API contract for expert technical fields without exposing `ChartObjectRuntimeData`, `chart_objects`, raw dominance/dignity payloads or `interpretation_input`.
Source audits: CS-238, CS-244, CS-251.
Source findings: CS-238 F-001/F-005; CS-244 F-001; CS-251 final evidence.
Scope: API contract only, field list, exclusions, OpenAPI tests, frontend client story split.
Out of scope: frontend UI, raw runtime exposure, temporal runtime.
Dependencies: current CS-251 roadmap.
Acceptance criteria:
- `expert_technical_projection_v1` schema exists with explicit field allowlist.
- OpenAPI and tests prove forbidden raw runtime names absent.
- `calcul -> faits -> signaux -> narration/projection` remains unchanged.
Validation evidence:
- OpenAPI diff, route/schema tests, negative `rg` scans.
Blockers / decisions:
- Product/API owner approves exact expert fields.
Stop condition: no raw runtime name is public.

### Story 2: Define beginner summary public projection contract

Story ID: next-available-id
Source label: CS-251 roadmap `beginner_summary`
Goal: create deterministic beginner summary facts, labels and masking policy.
Source audits: CS-244, CS-243, CS-251.
Source findings: CS-244 F-002; CS-243 F-002; CS-251 final evidence.
Scope: API contract, masking, translated label strategy, no raw score/degree/orb leak unless approved.
Out of scope: provider prompt copy, UI component.
Dependencies: projection registry terms from CS-251.
Acceptance criteria:
- `beginner_summary_v1` has deterministic inputs and masked output rules.
- Evidence IDs are references, not final-user narrative source of truth.
Validation evidence:
- contract tests, negative raw-runtime scans.
Blockers / decisions:
- Product owner approves masking defaults.
Stop condition: beginner projection can be consumed without reading runtime internals.

### Story 3: Decide fixed-star public/gated/rejected policy

Story ID: needs-user-decision
Source label: CS-251 roadmap `fixed_star_contacts`; CS-238 F-002
Goal: decide whether fixed-star contacts become public, gated, or rejected.
Source audits: CS-237, CS-238, CS-244, CS-251.
Source findings: CS-237 F-002; CS-238 F-002; CS-244 F-003.
Scope: product/security decision record and, only after approval, contract story.
Out of scope: new parans/aspects/heliacal calculators.
Dependencies: product owner decision.
Acceptance criteria:
- Decision is explicit: `public`, `gated`, or `rejected`.
- If public/gated, reduced fields are named; raw catalog/conjunction payloads remain internal.
Validation evidence:
- decision doc, negative raw payload scans.
Blockers / decisions:
- Product and security owner approval.
Stop condition: no CS-257 implementation starts while status is `needs-user-decision`.

### Story 4: Decide protected astrologer/debug surface

Story ID: needs-user-decision
Source label: CS-238 SC-003 / CS-244 F-004 provenance
Goal: decide whether a protected admin/debug or astrologer surface exists.
Source audits: CS-238, CS-242, CS-244.
Source findings: CS-238 F-003; CS-242 F-003; CS-244 F-004.
Scope: audience, authz, retention, redaction, allowed trace/debug fields.
Out of scope: unauthenticated public endpoint, frontend before auth decision.
Dependencies: security/product owner decision.
Acceptance criteria:
- Decision states allowed actors, retention, masking and trace/replay separation.
- If rejected, roadmap records no debug API/frontend story.
Validation evidence:
- security decision record, route/OpenAPI negative checks until approved.
Blockers / decisions:
- Security/product approval.
Stop condition: trace is not mistaken for replay or public payload.

### Story 5: Harden temporal public runtime readiness

Story ID: next-available-id after owner decisions
Source label: CS-253 selected path; CS-250 proof gate
Goal: prepare public `transit_chart_v1` only after proof, manifest, projection and doctrine gates are accepted.
Source audits: CS-237, CS-241, CS-242, CS-253.
Source findings: CS-237 F-001; CS-241 F-001..F-004; CS-242 F-001/F-005.
Scope: public runtime readiness checklist, manifest/projection shape, proof evidence, no frontend until API.
Out of scope: batch implementation of all temporal families.
Dependencies: CS-250 proof accepted, doctrine owners clear, projection contract selected.
Acceptance criteria:
- `transit_chart_v1` public contract exists or remains blocked with explicit reason.
- No simplified/public temporal shortcut is added.
Validation evidence:
- proof tests, route/OpenAPI checks, temporal family guard.
Blockers / decisions:
- Data/backend approval for ephemeris proof posture.
Stop condition: transit API cannot ship without proof metadata and projection contract.

### Story 6: Govern doctrine and object taxonomy expansion

Story ID: next-available-id
Source label: CS-252 governance; CS-249 taxonomy
Goal: close owner decisions for rule families and non-planetary objects before calculators/projections expand.
Source audits: CS-239, CS-240, CS-249, CS-252.
Source findings: CS-239 F-003/F-004/F-005; CS-240 F-001..F-006.
Scope: decisions for lots, Chiron, asteroids, midpoints, node/angle/cusp policy, DB/Python rule ownership.
Out of scope: calculator implementation before taxonomy acceptance.
Dependencies: product astrology/data owner.
Acceptance criteria:
- Every object/rule family is classified as active, blocked, rejected, or migration candidate.
- Guards prevent unclassified thresholds/weights/object families.
Validation evidence:
- taxonomy/governance tests and negative scans.
Blockers / decisions:
- Product doctrine and data owner approval.
Stop condition: no new object calculator lands without canonical taxonomy.

## Open questions and validation plan

| Question | Why it matters | Owner | Blocks | Suggested default | Sources |
| --- | --- | --- | --- | --- | --- |
| Should `fixed_star_contacts` be public, gated or rejected? | Prevents accidental exposure of raw fixed-star payloads. | product/security | fixed-star projection/API/UI | keep `needs-user-decision` | CS-251; CS-238 F-002 |
| Who may see `astrologer_debug_data`? | Trace/debug payloads may reveal internals and require retention policy. | product/security | admin_debug surface | no public surface | CS-238 F-003; CS-244 F-004 |
| What external ephemeris proof posture is required? | Public temporal accuracy claims depend on reproducible proof metadata. | backend/data | public temporal runtime | keep Moshier proof caveat until external path/hash decided | CS-250; CS-241 F-003 |
| Which doctrine owner controls thresholds and weights? | DB/Python divergence can change astrology semantics. | product astrology/data | traditional/temporal expansion | classify every family before migration | CS-240; CS-252 |
| What exact fields belong to expert and beginner projections? | Frontend/API must not infer from available internals. | product/API | first public projection stories | start with explicit allowlist | CS-244 F-001/F-002; CS-251 |

Validation plan:

- Run required document scans for source citations, primitive coverage, exposure levels, raw-runtime exclusions, dependency direction, family statuses and open decisions.
- Run Python path assertions only after `.\\.venv\\Scripts\\Activate.ps1`.
- Run `git status --short -- frontend/src backend/app backend/tests backend/app/tests backend/migrations` and persist output to prove CS-255 did not modify application roots.
- Do not run broad backend/frontend tests for this documentation-only story unless a validation command itself reveals an application delta; no application code is modified here.
