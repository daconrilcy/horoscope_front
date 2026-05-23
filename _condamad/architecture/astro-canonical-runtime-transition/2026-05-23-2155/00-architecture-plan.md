# CS-245 - Canonical Astrology Runtime Transition Architecture

## Executive Architecture Decision Summary

- observed: `natal_chart_v1` est la seule famille runtime implémentée avec preuve de graphe, objets runtime et tests; sources CS-237 F-001/E-006/E-010, CS-242 F-001/E-006/E-016.
- decision: `ChartObjectRuntimeData` devient primitive canonique interne pour les objets astrologiques, mais reste interdit comme payload public brut; sources CS-238 F-001/E-005..E-008, CS-239 F-001/E-005/E-014, CS-244 F-001/E-010/E-019.
- decision: `CalculationGraph` devient le mécanisme cible d'orchestration des familles, sous réserve d'un registre de familles, d'un manifest, de schemas node IO, d'une trace stable et d'une règle cache/replay; sources CS-242 F-001..F-005.
- decision: les surfaces publiques doivent être des projections nommées (`chart_facts`, beginner summary, expert technical, fixed-star display), jamais `chart_objects`; sources CS-238 F-001/F-002, CS-244 F-001..F-003.
- decision: l'entrée LLM est une projection stable issue des faits structurels et de `ChartInterpretationInputRuntimeData`, pas une source de vérité astrologique; sources CS-243 F-001/F-002.
- blocker: transits, progressions, synastrie, returns, composite et profections ne peuvent pas être déclarés implémentés sans runtime + tests; sources CS-237 F-001/F-005.
- blocker: doctrine et ownership de seuils/poids/profils doivent être arbitrés avant extension large; sources CS-240 F-001..F-006.
- blocker: preuve astronomique incomplète pour cas sensibles et mode simplifié encore callable; sources CS-241 F-001..F-004.
- decision: les candidates d'audit CS-243/244/245, CS-246..257 sont des labels source; les futures stories restent bloquées en `needs-tracker-remap` tant que le tracker owner n'a pas assigné de nouveaux IDs concrets.

## Audit Source Map

| Audit | Scope | Closure status | Key architecture inputs | Evidence IDs | Findings used | Blockers | Deferred context | Used for |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CS-237 `_condamad/audits/astro-feature-coverage/2026-05-23-1905` | Couverture runtime astrologie | phased-with-map | Natal implémenté; techniques prédictives reference-only/missing; objets non planétaires sans owner | E-005, E-006, E-010, E-014, E-015 | F-001..F-005 | Choix première technique; guard implemented | API/frontend/DB | Familles runtime, roadmap |
| CS-238 `_condamad/audits/astro-runtime-surface-exposure/2026-05-23-1919` | Surfaces runtime/exposition | phased-with-map | `chart_objects` interne; projection `chart_facts`; admin/debug bloqué | E-005..E-008, E-011..E-015 | F-001..F-005 | Product/security admin/debug | Frontend/auth | Surface matrix, projections |
| CS-239 `_condamad/audits/astro-chart-object-capability-payload/2026-05-23-1928` | Capacités et payloads ChartObject | phased-with-map | Capacités dispersées; validation partielle; taxonomy lots/points ouverte | E-005..E-019, E-021 | F-001..F-006 | Taxonomie et aspectability | Projection publique | Object matrix, registry |
| CS-240 `_condamad/audits/astro-reference-governance/2026-05-23-1939` | Gouvernance références | phased-with-map | Seuils/poids/profils split DB/Python; doctrine index partiel | E-007..E-018 | F-001..F-006 | Owner doctrine/data | Refactor app immédiat | Règles opérationnelles |
| CS-241 `_condamad/audits/astro-astronomical-accuracy/2026-05-23-1950` | Exactitude astronomique | phased-with-map | SwissEph vs simplified; golden coverage incomplète; trace éphémérides | E-005..E-016 | F-001..F-005 | Preuve externe/tolérances | Nouveau calcul | Validation, risques |
| CS-242 `_condamad/audits/astro-calculation-graph-readiness/2026-05-23-2000` | Readiness CalculationGraph | phased-with-map | Registre famille absent; manifest/node IO/trace/cache manquants | E-006..E-016 | F-001..F-006 | Remap labels CS-243/244/245 | API/admin | Registries, roadmap |
| CS-243 `_condamad/audits/astro-calculation-interpretation-boundary/2026-05-23-2013` | Frontière calcul/interprétation | full-closure-ready | Split interne/public/LLM; readiness projection; guard narration | E-006..E-014, E-017, E-018 | F-001..F-004 | Sémantique readiness | Docs historiques | LLM/narration |
| CS-244 `_condamad/audits/astro-product-data-needs/2026-05-23-2024` | Besoins data produit | phased-with-map | Expert, beginner, fixed-star projection; debug astrologique à décider | E-004..E-019, E-021 | F-001..F-005 | Debug/interface astrologue | UI sans contrat | Projections produit |

Story label caveats: CS-242 signale que les labels source `CS-243`, `CS-244` et `CS-245` sont déjà alloués. Le tracker confirme aussi CS-237..CS-245 alloués. Les candidates issues des audits gardent leur provenance (`SC-*`, source label), mais aucune story de mise en oeuvre ne doit être générée avant remapping explicite dans `_condamad/stories/story-status.md`.

## Capability Matrix

| Famille | Statut actuel | Runtime canonique cible | Owner cible | Inputs requis | Graph requis | Objets requis | Surfaces publiques | Surfaces internes | Trace/replay requis | Cache/invalidation | Blockers | Story recommandée |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `natal_chart_v1` | implemented | `ChartObjectRuntimeData` + `CalculationGraph` v1 interne | backend astrology domain | naissance, lieu, ref version, éphémérides | actuel + manifest | planètes, luminaires, angles, points, fixes | Projection chart facts/expert/beginner | chart_objects, provenance, interpretation_input | oui, trace stable | runner local; app cache interdit sans clés | manifest/trace/cache incomplets | SC-Graph-Manifest |
| `transit_chart_v1` | reference-only | famille graphe canonique multi-date | product astrology + backend astrology | natal + date transit + ref/éphémérides | nouveau graphe single-base/multi-date | planètes transit, aspects inter-chart | future projection transit | chart_objects transit, relations | oui | input fingerprint + graph/ref/eph | premier choix produit requis | SC-First-Temporal |
| `synastry_chart_v1` | reference-only | famille graphe multi-chart | product astrology + backend architecture | deux thèmes, relation, orb policy | nouveau graphe multi-chart | deux sets objets + aspects relationnels | projection relationnelle | graph relation trace | oui | deux fingerprints + versions | modèle pair inputs à décider | SC-Graph-Family-Registry |
| `solar_return_v1` | reference-only | famille return chart | product astrology + backend astrology | natal + année + lieu return | nouveau graphe return | objets thème return | projection return | snapshot return | oui | date/lieu/ref/eph | doctrine return/locus à décider | SC-First-Temporal |
| `lunar_return_v1` | reference-only | famille return chart | product astrology + backend astrology | natal + période lunaire + lieu | nouveau graphe return | objets thème return | projection return | snapshot return | oui | date/lieu/ref/eph | priorité produit | SC-First-Temporal |
| `progressed_chart_v1` | reference-only | famille temporal technique | product astrology + doctrine owner | natal + date cible + règle progression | nouveau graphe technique | objets progressés | projection progression | trace règle progression | oui | règle doctrine + date + ref | doctrine progression | SC-First-Temporal |
| `composite_chart_v1` | reference-only | famille multi-chart dérivée | product astrology + object taxonomy owner | deux thèmes + méthode composite | nouveau graphe multi-chart | midpoints/composite objects | projection relationnelle | objets dérivés | oui | pair fingerprint + méthode | midpoints sans owner | SC-Object-Taxonomy |
| `profection_v1` | missing | famille doctrine/time-lord | doctrine owner + product astrology | natal + âge/année + école | nouveau graphe doctrine | signes/maisons/time lord | projection profection | règle doctrine | oui | doctrine version | blocked-by-doctrine-decision | SC-Doctrine-Governance |
| `forecasting_v1` | missing | orchestrateur produit de techniques | product astrology + platform owner | techniques sélectionnées + horizon | graph aggregator futur | sorties transits/progressions/etc. | forecast projection | trace multi-technique | oui | chaque technique + horizon | dépend première technique | SC-First-Temporal |
| `ai_scoring_v1` | blocked-by-product-decision | projection deterministic scoring input | product/commercial owner + interpretation owner | chart facts + readiness + policy | peut consommer graph outputs | objets scorables | score bands si approuvés | scoring facts | oui | policy/version | product/commercial scoring | SC-AI-Narrative-Input |
| `narrative_generation_v1` | partially-ready | LLM input contract non source-of-truth | narration/product owner + interpretation owner | interpretation readiness + evidence | pas graphe de calcul | faits interprétables | texte final | LLM input redacted | trace prompt séparée | invalidation par facts/prompt version | LLM contract split | SC-AI-Narrative-Input |

Sources: CS-237 F-001..F-005; CS-239 F-001..F-005; CS-242 F-001..F-005; CS-243 F-001..F-003; CS-244 F-001..F-004.

## Surface Matrix

| Surface | Owner actuel | Statut cible | Public API | Admin/debug | LLM/input | Frontend | Risque d'exposition brute | Projection requise | Guard requis | Story recommandée |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ChartObjectRuntimeData` | domain runtime | interne canonique | non | résumé protégé seulement | non brut | non | high | `chart_facts` | no raw runtime | SC-Public-Projections |
| `chart_objects` | `NatalResult` exclu | interne | non | trace redacted | non brut | non | high | chart facts | scan API/frontend | SC-Public-Projections |
| `CalculationGraphDefinition` | runtime | registry/manifest | non | oui protégé | non | non | medium | manifest summary | manifest validation | SC-Graph-Manifest |
| `CalculationGraphRunner` | runtime | internal orchestrator | non | diagnostics protégés | non | non | high | trace | auth/admin decision | SC-Trace-Contract |
| `CalculationGraphExecutionResult` | runtime | internal result + trace contract | non | oui redacted | non | non | high | trace DTO | redaction | SC-Trace-Contract |
| provenance | runner local | trace source, pas replay | non | oui protégé | non | non | medium | execution trace | trace/provenance split | SC-Trace-Contract |
| trace d'exécution | missing | contract v1 | non | oui | possible evidence IDs | non | medium | trace redacted | retention/exposure | SC-Trace-Contract |
| replay snapshot | missing | blocked owner | non | décision | non | non | high | replay snapshot v1 | storage/retention | needs-user-decision |
| graph manifest | missing | canonical registry | non | oui | non | non | medium | manifest v1 | schema tests | SC-Graph-Manifest |
| node IO schema | descriptive | schema contract | non | oui | non | non | medium | schema v1 | validator | SC-Graph-Manifest |
| fixed-star contacts | runtime/internal | reduced projection if approved | oui réduit | oui | oui réduit | oui si produit | medium | fixed-star display | no raw payload | SC-Fixed-Star-Projection |
| advanced planetary conditions | mixed | public selected fields + internal details | oui sélectionné | oui | oui selected | oui expert | medium | expert technical | source governance | SC-Expert-Projection |
| dignities | public partial | stable expert contract | oui | oui | oui selected | oui | medium | expert technical | source governance | SC-Expert-Projection |
| dominance | public partial | stable expert contract | oui | oui | oui selected | oui | medium | expert technical | source governance | SC-Expert-Projection |
| aspects structural data | public structural | stable facts | oui | oui | oui selected | oui | low | chart facts | structural/narrative guard | SC-Public-Projections |
| interpretation input | internal/pre-LLM | split internal/public/LLM | non brut | oui | oui stable subset | non brut | high | readiness + LLM input | no prompt in runtime | SC-AI-Narrative-Input |
| chart facts projection | missing | public primitive | oui | oui | oui selected | oui | low | `chart_facts_v1` | no raw runtime | SC-Public-Projections |
| beginner summary projection | missing | public-user primitive | oui | non | non source-of-truth | oui | low | `beginner_summary_v1` | no raw expert/runtime | SC-Beginner-Projection |
| expert technical projection | partial | public expert primitive | oui | non | selected | oui | medium | `expert_technical_v1` | field allowlist | SC-Expert-Projection |

## Mandatory Astrology Object Capability Matrix

Cette matrice complète la section `Object / Entity Decisions` ci-dessous avec le format exigé par la story CS-245 et le brief ASTRO-ARCHI-01. Les valeurs `needs-user-decision` restent des blockers explicites, pas des choix implicites de doctrine.

| Objet | Type canonique proposé | Source calcul/référence | Positionnel | Aspectable | Interprétable | Scorable | Dignité-éligible | Dominance-éligible | Projection publique | Décision requise |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Soleil | `core_entity` luminaire | DB référence + SwissEph/runtime natal | oui | oui | oui | oui | oui | oui | `chart_facts_v1`, `expert_technical_v1`, `beginner_summary_v1` | none; garder version/source en trace |
| Lune | `core_entity` luminaire | DB référence + SwissEph/runtime natal | oui | oui | oui | oui | oui | oui | `chart_facts_v1`, `expert_technical_v1`, `beginner_summary_v1` | none; garder version/source en trace |
| planètes classiques | `core_entity` planet | DB référence + Python/SwissEph runtime | oui | oui | oui | oui | oui | oui | expert/public selected fields | owner doctrine/data pour seuils et poids |
| planètes modernes | `core_entity` planet | DB référence + Python/SwissEph runtime | oui | oui | oui | oui | needs-user-decision | oui | expert/public selected fields | doctrine d'éligibilité dignité moderne |
| ASC/MC/angles | `derived_object` angle | runtime maisons/angles | oui | needs-user-decision | oui | oui | non | oui partiel | expert/public selected fields | politique aspectability angles/cusps |
| noeuds lunaires | `derived_object` astral_point | runtime astral points | oui | needs-user-decision | oui | oui partiel | non | non | projection pending | rester `ASTRAL_POINT` ou famille dédiée |
| Lilith | `derived_object` astral_point | runtime astral points | oui | needs-user-decision | oui | oui partiel | non | non | projection pending | projection produit et aspectability |
| apsides | `derived_object` astral_point | runtime astral points | oui | needs-user-decision | oui | oui partiel | non | non | projection pending | projection produit et aspectability |
| parts arabes/lots | `derived_object` reserved | enum/taxonomy only, no active producer | missing | missing | missing | missing | blocked-by-doctrine-decision | blocked-by-doctrine-decision | none | taxonomy, doctrine et producer owner |
| astéroïdes | `external_reference` reserved | documented/future only, no active producer | missing | missing | missing | missing | blocked-by-doctrine-decision | blocked-by-doctrine-decision | none | catalogue, priorité produit, source astronomique |
| Chiron | `external_reference` reserved | documented/future only, no active producer | missing | missing | missing | missing | blocked-by-doctrine-decision | blocked-by-doctrine-decision | none | famille objet et exposition produit |
| midpoints | `derived_object` reserved | future composite/synastry need, no active producer | missing | missing | missing | missing | non | blocked-by-doctrine-decision | none | méthode midpoint et owner composite |
| étoiles fixes | `external_reference` + `derived contact` | DB fixed stars + runtime conjunction contacts | oui catalogue/contact | contact-only | oui réduit | oui réduit | non | non | `fixed_star_display_v1` si approuvé | public/gated projection; parans/aspects absent |

Sources: CS-237 F-002/F-003/F-004; CS-239 F-001..F-006; CS-240 F-001..F-006; CS-244 F-001/F-003.

## Canonical Registry Decisions

### graph_family_registry

Decision: adopt.
Owner: architecture owner + backend astrology domain.

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `natal_chart_v1` | v1 | birth, location, options, ref, eph | graph manifest + execution result | semver by manifest | no silent alias | graph_code, version, input_hash, ref_version, eph_hash | CS-237 F-001, CS-242 F-001 |
| `transit_chart_v1` | v1 | base chart, transit date | pending manifest | blocked until registry | no public claim before runtime | family, dates, ref/eph | CS-237 F-001, CS-242 F-001 |
| `synastry_chart_v1` | v1 | chart A/B | pending manifest | blocked multi-chart | no duplicate router | pair hashes | CS-237 F-001, CS-242 F-001 |
| `solar_return_v1` | v1 | natal, year, return location | pending manifest | blocked doctrine/location | no implicit route | return date/location | CS-237 F-001 |
| `progressed_chart_v1` | v1 | natal, target date, progression rule | pending manifest | blocked doctrine | no implicit route | progression_rule | CS-237 F-001 |

### chart_object_capability_registry

Decision: adopt.
Owner: backend astrology domain + product astrology owner.

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `chart_object_capabilities_v1` | v1 | object type, payload, graph options | capability matrix | breaking if eligibility changes | no hidden type branch | object_code, capabilities, payloads | CS-239 F-001/F-002 |
| `non_planetary_object_taxonomy_v1` | v1 | lots, asteroids, Chiron, midpoints | owner decision table | blocked until decision | aliases forbidden | taxonomy_source | CS-237 F-004, CS-239 F-003 |

### projection_contract_registry

Decision: adopt.
Owner: product + API owner + frontend consumer owner.

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `chart_facts_v1` | v1 | chart_objects selected fields | public facts | additive only | no raw `chart_objects` | source graph, object ids | CS-238 F-001 |
| `fixed_star_display_v1` | v1 | fixed-star contacts | reduced public rows | additive only | no raw payload | rule/source/orb | CS-238 F-002, CS-244 F-003 |
| `beginner_summary_v1` | v1 | public facts + translations | masked beginner view | additive only | no LLM source truth | evidence ids | CS-244 F-002 |
| `expert_technical_v1` | v1 | dignities, conditions, dominance | expert fields | explicit field policy | no raw runtime | source facts | CS-244 F-001 |

### interpretation_input_registry

Decision: adopt.
Owner: backend interpretation owner + product narration owner.

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `interpretation_readiness_v1` | v1 | structural facts | ready/withheld reason codes | additive states | no narrative fallback | fact ids, reason codes | CS-243 F-002 |
| `llm_astrology_input_v1` | v1 | readiness + evidence | prompt-safe facts | version prompt/data separately | no prompt as source | input_version, prompt_version | CS-243 F-001/F-003 |

## Object / Entity Decisions

| Object | Kind | Lifecycle owner | Persistence | Serialization | Versioning | Surfaces | Decision | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Soleil | core_entity | reference/domain | ref DB + runtime | public selected | ref + capability v1 | public/internal/LLM | implemented canonical | CS-237 E-006, CS-239 E-006 |
| Lune | core_entity | reference/domain | ref DB + runtime | public selected | ref + capability v1 | public/internal/LLM | implemented canonical | CS-237 E-006, CS-239 E-006 |
| planètes classiques | core_entity | reference/domain | ref DB + runtime | public selected | ref + capability v1 | public/internal/LLM | implemented, doctrine-governed | CS-240 F-001..F-003 |
| planètes modernes | core_entity | reference/domain | ref DB + runtime | public selected | ref + capability v1 | public/internal/LLM | implemented, doctrine-governed | CS-237 |
| ASC/MC/angles | derived_object | chart runtime | runtime result | public selected | capability v1 | public/internal | aspectability needs-user-decision | CS-239 F-004 |
| noeuds lunaires | derived_object | astral point runtime | runtime result | projection pending | capability v1 | internal/public pending | active as astral points, category open | CS-237 F-003, CS-239 F-005 |
| Lilith | derived_object | astral point runtime | runtime result | projection pending | capability v1 | internal/public pending | partial, product projection open | CS-237 F-003 |
| apsides | derived_object | astral point runtime | runtime result | projection pending | capability v1 | internal/public pending | partial, product projection open | CS-237 F-003 |
| parts arabes/lots | derived_object | none yet | none | none | taxonomy v1 pending | none | blocked-by-doctrine-decision | CS-237 F-004, CS-239 F-003 |
| astéroïdes | external_reference | none yet | none | none | taxonomy v1 pending | none | missing | CS-237 F-004 |
| Chiron | external_reference | none yet | none | none | taxonomy v1 pending | none | missing | CS-237 F-004 |
| midpoints | derived_object | none yet | none | none | taxonomy v1 pending | internal/public pending | missing, needed for composite | CS-237 F-004 |
| étoiles fixes | external_reference + derived contact | fixed-star runtime | ref DB + runtime contacts | reduced projection only | fixed-star display v1 | internal/LLM/public pending | conjunction-only; parans missing | CS-237 F-002, CS-238 F-002 |
| trace d'exécution | debug_artifact | graph runtime | pending owner | admin/debug only | trace v1 | admin/observability | missing stable contract | CS-242 F-003 |
| projections produit | presentation_model | API/product | persisted only if contract says | public | projection v1 | public/frontend/LLM selected | adopt registry | CS-244 F-001..F-003 |

## Operational Rules

| Rule area | Rule | Applies to | Invalidated by | Trace requirement | Owner | Sources |
| --- | --- | --- | --- | --- | --- | --- |
| Versioning | Toute famille graphe porte `graph_code` + version manifest. | graph families | inputs, node IO, semantics, ordering | graph_code/version | architecture/backend | CS-242 F-001/F-002 |
| Trace | Trace stable séparée de provenance brute et replay. | runner/result/admin | schema/retention/exposure changes | node status, input/output keys, redaction | backend/security | CS-242 F-003, CS-238 F-003 |
| Cache | Runner-local seulement tant que l'app cache n'a pas owner. | CalculationGraphRunner | graph version, input fingerprint, ref version, ephemeris hash | cache hit/miss | backend/data | CS-242 F-005 |
| Replay | Replay snapshot est bloqué sans storage/retention/security decision. | support/debug | trace schema, persisted payload, PII policy | replay snapshot id | security/product | CS-242 F-003, CS-238 F-003 |
| Invalidation | Toute sortie durable dépend de graph, inputs, ref doctrine, ephemeris. | projections/cache/results | ref/source update, doctrine change, eph hash | invalidation keys | data owner | CS-240 F-001..F-006, CS-241 F-003 |
| Migration | Aucun alias legacy ou exposition brute pendant transition. | API/frontend/domain | raw runtime usage | scan no raw names | architecture/API | CS-238 F-001, CS-244 F-005 |
| Observability | Admin/debug protégé uniquement après authz/redaction. | debug/trace | exposure route, retention, auth | request id + graph trace | security/backend | CS-238 F-003 |
| Doctrine | Seuils/poids/profils classés DB-owned, Python-owned, mixed, needs-user-decision. | dignities/conditions/dominance | source owner change | rule source/version | product astrology/data | CS-240 F-001..F-006 |
| Narration | Prompts et texte final ne deviennent jamais source de vérité. | LLM/narrative | prompt version, readiness contract | input_version + evidence ids | narration/product | CS-243 F-001..F-003 |

## Blockers And Decision Owners

| Blocker | Type | Owner | Blocks | Decision needed | Sources |
| --- | --- | --- | --- | --- | --- |
| First temporal technique | product | product astrology owner | transits/returns/progressions roadmap | choisir première technique, recommandé transit | CS-237 F-001 |
| Multi-chart input model | architecture | backend architecture owner | synastry/composite | représenter chart A/B, pair hash, relation inputs | CS-242 F-001 |
| Node IO schema language | architecture | backend architecture owner | manifest validation | Pydantic/dataclass/JSON schema/minimal schema | CS-242 SC-002 |
| Trace persistence/exposure | security | security + backend | admin/debug/replay | in-process, persisted, retention, redaction | CS-238 F-003, CS-242 F-003 |
| Durable cache owner | data/architecture | data owner | app cache | no-cache or owner + invalidation keys | CS-242 F-005 |
| Doctrine source ownership | doctrine/data | product astrology + data owner | thresholds/weights/profile changes | DB-owned/Python-owned/mixed/index | CS-240 F-001..F-006 |
| Astronomical proof baseline | architecture/data | backend astrology owner | production claims for sensitive options | external references and tolerances | CS-241 F-002/F-004 |
| Debug astrologue surface | product/security | product + security | admin/debug UI/API | audience, authz, masking, retention | CS-244 F-004 |
| Non-planetary taxonomy | doctrine/product | product astrology owner | lots, Chiron, asteroids, midpoints | object kind and priority | CS-237 F-004, CS-239 F-003 |

## Ordered Implementation Roadmap

| Rang | Chantier | Pourquoi maintenant | Dépendances | Risque si ignoré | Taille estimée | Story candidate |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Platform prerequisites: graph family registry | évite routes graph ad hoc | none | familles futures divergentes | M | SC-Graph-Family-Registry |
| 2 | Platform prerequisites: graph manifest + node IO schema | rend contrats validables | registry | erreurs runtime tardives | M | SC-Graph-Manifest |
| 3 | Platform prerequisites: execution trace contract | support/debug/replay sans raw provenance | manifest | diagnostic non stable | M | SC-Trace-Contract |
| 4 | Raw exposure guards: public projection registry | pression produit sur `chart_objects` | object registry | fuite API/frontend | M | SC-Public-Projections |
| 5 | Doctrine governance: rule source ownership | évite drift seuils/poids | registries | divergences DB/Python | M | SC-Doctrine-Governance |
| 6 | Product surfaces: expert/beginner/fixed-star projections | valeur produit actuelle sans runtime brut | projection registry | UI couple internals | M | SC-Expert-Beginner-Fixed |
| 7 | Astronomy proof: golden suite and production mode proof | sécurise claims calculatoires avant temporalité publique | graph registry/manifest | précision surestimée | M/L | SC-Astronomy-Proof |
| 8 | Temporal techniques: select first implementation path | déverrouille forecasting après preuve minimale | astronomy proof + graph registry/manifest | batch prédictif confus | L | SC-First-Temporal |
| 9 | Object taxonomy: non-planetary intake | prérequis lots/midpoints/composite | capability registry | mauvais subtype durable | M | SC-Object-Taxonomy |
| 10 | Narration/AI: readiness + LLM input contract | scoring/narration sans prompt source truth | projections/readiness | prompts dictent la doctrine | M | SC-AI-Narrative-Input |

### Story 1: Define canonical astrology graph family registry

Story ID: needs-tracker-remap
Source label: CS-242 SC-003 source-label CS-245.
Goal: créer un registre des familles `natal_chart_v1`, `transit_chart_v1`, `synastry_chart_v1`, `solar_return_v1`, `progressed_chart_v1`, `composite_chart_v1` sans implémenter de nouvelle famille.
Source audits: CS-237, CS-242.
Source findings: CS-237 F-001/F-005; CS-242 F-001/F-005.
Scope: registry, input classes, cache boundary decision.
Out of scope: API, frontend, DB, nouveau calcul.
Dependencies: none.
Acceptance criteria:
- every family has owner, input model, graph status, blocker.
- source labels CS-243/244/245 are not reused as final IDs.
Validation evidence:
- targeted scans for family codes and duplicate routing.
Blockers / decisions:
- product decision for first temporal family.
Stop condition: no duplicate graph routing convention remains unowned.

### Story 2: Add graph manifest and node IO schema contract for canonical runtime

Story ID: needs-tracker-remap
Source label: CS-242 SC-002 source-label CS-244.
Goal: rendre `natal_chart_v1` validable par manifest et schema node IO.
Source audits: CS-242.
Source findings: F-002/F-004.
Scope: manifest v1, schema validation, comparison policy.
Out of scope: API/frontend/cache durable.
Dependencies: Story 1.
Acceptance criteria:
- every natal node has IO schema or documented blocker.
- compatibility comparison classifies breaking/non-breaking changes.
Validation evidence:
- graph contract/validator tests.
Blockers / decisions:
- schema language owner decision.
Stop condition: graph comparison is not a separate unowned concern.

### Story 3: Add calculation graph execution trace contract

Story ID: needs-tracker-remap
Source label: CS-242 SC-001 source-label CS-243.
Goal: séparer trace stable, provenance brute et replay.
Source audits: CS-238, CS-242.
Source findings: CS-238 F-003; CS-242 F-003.
Scope: trace DTO redacted, node statuses, errors, cache hits.
Out of scope: public route; replay persistence unless approved.
Dependencies: Story 2.
Acceptance criteria:
- success/error/cache traces are structurally tested.
- raw outputs are not the only diagnostic surface.
Validation evidence:
- runner trace tests and redaction scans.
Blockers / decisions:
- security decision for persisted/admin exposure.
Stop condition: trace exists or persistence is explicitly blocked.

### Story 4: Define chart object capability and object taxonomy matrix

Story ID: needs-tracker-remap
Source label: CS-239 SC-001/SC-003 and CS-237 SC-004.
Goal: figer capacités, payload phases et taxonomie lots/points/non-planétaires.
Source audits: CS-237, CS-239.
Source findings: CS-237 F-003/F-004; CS-239 F-001..F-005.
Scope: canonical capability matrix and user decisions.
Out of scope: calculators for missing objects.
Dependencies: Story 1.
Acceptance criteria:
- each object class has capability eligibility and payload validation status.
- lots, Chiron, asteroids, midpoints are decisioned or blocked.
Validation evidence:
- matrix + architecture guard/tests if implemented.
Blockers / decisions:
- doctrine/product object taxonomy.
Stop condition: no branch ad hoc by object type is required.

### Story 5: Define official product primitives and public projection roadmap

Story ID: needs-tracker-remap
Source label: CS-238 SC-001/SC-002 and CS-244 SC-001..SC-003.
Goal: définir `chart_facts_v1`, `expert_technical_v1`, `beginner_summary_v1`, `fixed_star_display_v1`.
Source audits: CS-238, CS-244.
Source findings: CS-238 F-001/F-002/F-005; CS-244 F-001..F-003.
Scope: public projection contracts and no-raw-runtime guards.
Out of scope: raw `chart_objects`, admin/debug.
Dependencies: Stories 2 and 4.
Acceptance criteria:
- public/API/frontend contracts exclude raw runtime names.
- beginner and expert projections have distinct owners.
Validation evidence:
- public contract tests, frontend/API scans.
Blockers / decisions:
- product field selection and fixed-star gating.
Stop condition: frontend needs no internal runtime object.

### Story 6: Select first temporal technique implementation path

Story ID: needs-tracker-remap
Source label: CS-237 SC-001.
Goal: choisir transits ou autre technique comme première famille post-natal.
Source audits: CS-237, CS-242, CS-241.
Source findings: CS-237 F-001; CS-242 F-001/F-005; CS-241 F-002/F-004.
Scope: decision + implementation contract for one technique. Implementation is allowed only after astronomy proof hardening is complete or an explicit product risk acceptance is recorded.
Out of scope: batch transits+synastry+returns.
Dependencies: Stories 1..3 and SC-Astronomy-Proof.
Acceptance criteria:
- selected family has runtime contract, test plan, and non-goals for others.
Validation evidence:
- absence scans before, focused runtime tests after.
Blockers / decisions:
- product selects first technique.
Stop condition: one technique is implementable without claiming others, and the astronomy proof gate is closed or explicitly accepted as residual risk.

### Story 6A: Harden astronomy proof before public temporal runtime

Story ID: needs-tracker-remap
Source label: CS-241 SC-001..SC-004.
Goal: fermer le risque CS-241 avant toute technique temporelle publique.
Source audits: CS-241, CS-242.
Source findings: CS-241 F-001..F-004; CS-242 F-005.
Scope: production-mode proof, sensitive golden suite, ephemeris trace evidence, accepted tolerance policy.
Out of scope: new temporal calculator, frontend, public API.
Dependencies: Stories 1..3 recommended, but this can run before temporal implementation.
Acceptance criteria:
- production path cannot silently use simplified mode for public accurate calculations.
- Paris, DST ambiguous/nonexistent, high latitude, Sidereal Lahiri, topocentric, whole sign and Placidus edge cases are covered or explicitly risk-accepted.
Validation evidence:
- CS-241 golden/prod-mode tests and ephemeris evidence scans.
Blockers / decisions:
- external references and tolerances.
Stop condition: temporal implementation has a trustworthy astronomical baseline or a named product risk acceptance.

### Story 7: Define astrology doctrine and school governance model

Story ID: needs-tracker-remap
Source label: CS-240 SC-001..SC-006.
Goal: classer thresholds, weights, profiles and doctrine sources.
Source audits: CS-240, CS-241.
Source findings: CS-240 F-001..F-006; CS-241 F-003.
Scope: ownership registry DB/Python/mixed/needs-user-decision.
Out of scope: silent value changes.
Dependencies: Story 4.
Acceptance criteria:
- every audited threshold/weight/profile has owner and version/source.
Validation evidence:
- governance tests/scans for constants and source metadata.
Blockers / decisions:
- doctrine owner approval.
Stop condition: no unclassified rule source can be introduced silently.

### Story 8: Define AI scoring and narrative input contract from canonical runtime

Story ID: needs-tracker-remap
Source label: CS-243 SC-001/SC-002 and CS-244 SC-002.
Goal: définir readiness + LLM input depuis faits structurels sans prompt source-of-truth.
Source audits: CS-243, CS-244.
Source findings: CS-243 F-001..F-003; CS-244 F-002.
Scope: `interpretation_readiness_v1`, `llm_astrology_input_v1`, narrative guards.
Out of scope: final copywriting, provider integration, scoring commercial.
Dependencies: Stories 4 and 5.
Acceptance criteria:
- every field is internal/public/LLM classified.
- structural runtime rejects narrative tokens.
Validation evidence:
- boundary guard tests and no-provider scans.
Blockers / decisions:
- product scoring/narration policy.
Stop condition: prompts consume evidence; they do not define astrology facts.

## Open Questions And Validation Plan

| Question | Why it matters | Owner | Blocks | Suggested default | Sources |
| --- | --- | --- | --- | --- | --- |
| Quelle première technique temporelle? | ordonne transits/returns/progressions | product | Story 6 | transits | CS-237 F-001 |
| Quel schema langage pour node IO? | conditionne manifest v1 | architecture | Story 2 | internal minimal schema first | CS-242 F-002 |
| Trace persistée ou in-process? | sécurité/replay/admin | security/backend | Story 3 | in-process redacted first | CS-238 F-003, CS-242 F-003 |
| Qui possède le cache durable? | invalidation produit | data/architecture | cache/app performance | no durable cache until owner | CS-242 F-005 |
| Les étoiles fixes sont-elles publiques? | projection produit | product | fixed-star display | reduced opt-in projection | CS-238 F-002, CS-244 F-003 |
| Angles/noeuds sont-ils aspectables? | capability matrix | doctrine/product | object taxonomy | keep current graph default until decision | CS-239 F-004/F-005 |
| Quelle preuve externe astronomique? | précision et confiance | architecture/data | temporal techniques | add golden sensitive cases | CS-241 F-002/F-004 |
| Debug astrologue est-il admin, expert, ou hors scope? | authz et exposition | product/security | admin/debug | blocked until audience decided | CS-244 F-004 |

Validation plan:
- `rg -n "CS-237|CS-238|CS-239|CS-240|CS-241|CS-242|CS-243|CS-244" "$($archiFolder.FullName)"`
- `rg -n "ChartObjectRuntimeData|CalculationGraph|natal_chart_v1|transit_chart_v1|synastry_chart_v1|progressed_chart_v1|solar_return_v1|profection|forecasting|scoring|narrative" "$($archiFolder.FullName)\00-architecture-plan.md"`
- `rg -n "blocked-by-product-decision|blocked-by-doctrine-decision|partially-ready|reference-only|missing|implemented" "$($archiFolder.FullName)\00-architecture-plan.md"`
- `rg -n "Public API|Admin/debug|LLM|Frontend|Projection|Guard" "$($archiFolder.FullName)\00-architecture-plan.md"`
- `git status --short -- frontend/src backend/app backend/tests backend/app/tests backend/migrations docs/db_seeder`
