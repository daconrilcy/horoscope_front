<!-- Commentaire global: ce document fixe les primitives produit publiques sans transformer les surfaces runtime internes en API. -->

# Official Product Primitives And Public Projection Roadmap

Ce document est l'owner canonique des primitives produit publiques pour les
projections astrologiques. Il consolide CS-238, CS-244, CS-249 et CS-250 sans
modifier les routes, serializers, calculateurs, clients frontend ou composants
UI existants.

CS-283 ajoute l'owner d'entitlement B2C
`docs/architecture/b2c-projection-entitlement-policy.md` pour la matrice
`b2c_projection_entitlement_policy` des plans `free`, `basic` et `premium`. Ce
document de gouvernance reste le registre des primitives; la politique CS-283
decide seulement quels plans B2C peuvent demander les projections client
autorisees.

## Regles de gouvernance

- Les primitives produit sont des contrats de projection nommes, pas des dumps
  runtime.
- `chart_objects`, `ChartObjectRuntimeData`, les raw calculation graph payloads
  et `interpretation_input` restent des surfaces internes ou LLM-only.
- Les futures stories doivent separer les couches `API contract`,
  `frontend client` et `UI component`.
- La compatibilite OpenAPI actuelle est `OpenAPI-neutral`: aucune primitive de
  ce document n'ajoute de schema ou route publique par elle-meme.

## Primitives officielles

| primitive_id | Primitive produit | audience | public_status | source_runtime | public_projection_owner | forbidden_raw_surfaces | api_contract_story | frontend client story | UI component story | openapi_policy |
|---|---|---|---|---|---|---|---|---|---|---|
| `structured_facts` | structured facts | expert, PDF, AI, public-user | public | projections natales publiques existantes, `json_builder.py`, audits CS-238/CS-244 | futur contrat public de faits structures | `chart_objects`, `ChartObjectRuntimeData`, raw calculation graph payloads | CS-255 API contract | CS-255 frontend client | CS-255 UI component | OpenAPI-ready |
| `beginner_summary` | beginner summary | beginner, public-user, AI, PDF | public | projections publiques existantes, contexte natal compact LLM | `docs/architecture/beginner-summary-v1-contract.md` (`beginner_summary_v1`, CS-257) | `chart_objects`, raw score breakdowns, raw calculation graph payloads | future API contract, not CS-257 | future frontend client, not CS-257 | future UI component, not CS-257 | OpenAPI-neutral in CS-257 |
| `client_interpretation_projection` | client interpretation by plan | free, basic, premium, public-user | public | `structured_facts_v1`, signaux interpretatifs pre-narratifs, contexte natal compact LLM | `docs/architecture/client-interpretation-projection-v1-contract.md` (`client_interpretation_projection_v1`, CS-258) | runtime technique brut, proof internals, prompt internals, provider internals, `expert_technical_projection_v1` | future API contract, not CS-258 | future frontend client, not CS-258 | future UI component, not CS-258 | OpenAPI-neutral in CS-258 |
| `transit_client_projection` | transit client projection by plan | free, basic, premium, public-user | blocked | `transit_chart_v1` interne, apres proof gate astronomique et doctrine limits valides | `docs/architecture/transit-client-projection-v1-contract.md` (`transit_client_projection_v1`, CS-281) | raw runtime payloads, graph traces, proof internals, debug fields, `expert_technical_projection_v1`, public transit route | future API contract only after proof gate, not CS-281 | future frontend client blocked, not CS-281 | future UI component blocked, not CS-281 | OpenAPI-neutral in CS-281; blocked until proof gate |
| `expert_technical_projection` | expert technical projection | ADMIN, futur ASTRO_EXPERT target-only | internal-only | dignities, conditions, dominance, aspects et houses issus de sources stabilisees | `docs/architecture/expert-technical-projection-v1-contract.md` (`expert_technical_projection_v1`, CS-273) | raw runtime traces, prompt internals, replay payloads complets, provider debug dumps, unrestricted technical diagnostics | none for public API | none for public frontend client | none for public UI component | OpenAPI-neutral; non client |
| `astrology_full_data` | full astrology expert data | ADMIN, futur ASTRO_EXPERT target-only | internal-only | `structured_facts_v1`, positions, houses, dignities, conditions, aspects, dominance, fixed-star policy et source metadata | `docs/architecture/astrology-full-data-v1-contract.md` (`astrology_full_data_v1`, CS-274) | `admin_chart_diagnostics_v1`, raw runtime traces, replay payloads complets, provider debug dumps, raw fixed-star catalog data, unrestricted technical diagnostics | none for public API | none for public frontend client | none for public UI component | OpenAPI-neutral; non client |
| `fixed_star_contacts` | fixed-star contacts | expert, public-user, AI | needs-user-decision | `backend/app/domain/astrology/fixed_stars/**`, payloads rattaches aux objets | none until product decision | raw fixed star catalog dump, raw conjunction payloads, `ChartObjectRuntimeData` | future API contract blocked until policy decision | future frontend client blocked until policy decision | future UI component blocked until policy decision | blocked |
| `astrologer_debug_data` | astrologer/debug data | astrologer, debug | needs-user-decision | traces de calcul, audit rows, graph runtime interne | none | `chart_objects`, raw calculation graph payloads, internal IDs, audit internals | none until audience/auth decision | none until audience/auth decision | none until audience/auth decision | blocked |
| `llm_input` | LLM input | AI | LLM-only | `interpretation_input`, contexte natal compact, evidence catalog | none for public API | `interpretation_input`, prompt internals, evidence IDs beyond display need | none | none | none | OpenAPI-neutral |

## Mapping CS-244 par audience

| Audience CS-244 | Besoin produit | Primitive cible | Decision |
|---|---|---|---|
| beginner | Soleil/Lune/Ascendant compacts, themes dominants, labels traduits, masquage des details techniques | `beginner_summary` | public |
| expert | dignites, conditions, analyse traditionnelle, dominance, aspects techniques | `expert_technical_projection` et `structured_facts` | interne; non client; usage ADMIN et futur ASTRO_EXPERT target-only |
| astrologer | payload expert, historique, notes diagnostiques eventuelles | `astrologer_debug_data` | needs-user-decision avant exposition |
| debug | traces, payloads internes, audit rows, garde runtime | `astrologer_debug_data` | rejected for public; needs-user-decision pour surface protegee |
| AI | contexte natal compact, evidence catalog, metadata persona/use-case, disclaimers | `llm_input` et `beginner_summary` | LLM-only pour input brut; public uniquement via reponse interpretee |
| PDF | interpretation persistee, sections, highlights, labels Soleil/Ascendant, disclaimers | `structured_facts` et `beginner_summary` | public to owning user |
| public-user | resume debutant, highlights, conseils, etats paywall/degrades | `beginner_summary` et `client_interpretation_projection` | public |

## Surfaces explicitement non publiques

| Surface | Classification | Raison |
|---|---|---|
| `chart_objects` | internal | Source runtime canonique, couplage trop fort pour le frontend/API public. |
| `ChartObjectRuntimeData` | internal | Contrat de payload objet non stabilise pour produit public. |
| raw calculation graph payloads | internal | Traces et noeuds de calcul reserves au runtime/debug protege. |
| `interpretation_input` | LLM-only | Contrat oriente prompt et narration, pas contrat frontend/API public. |
| raw fixed-star conjunction payloads | internal | La politique fixed-star public/gated n'est pas encore decidee. |

## Roadmap de projection publique

| Sequence | Primitive | API contract | frontend client | UI component | Stop condition |
|---|---|---|---|---|---|
| 1 | `expert_technical_projection` | Hors roadmap publique: CS-273 definit `expert_technical_projection_v1` comme contrat interne non client. | Aucun client frontend public. | Aucun composant public. | `expert_technical_projection_v1` reste absent d'OpenAPI public, des clients B2C et de l'UI publique. |
| 2 | `beginner_summary` | CS-257 definit `beginner_summary_v1` comme contrat deterministic de resume debutant. | Client dedie hors scope CS-257, apres contrat API separe. | Composant public-user hors scope CS-257. | Masquage des degres, orbes, scores bruts et graph runtime. |
| 3 | `client_interpretation_projection` | CS-258 definit `client_interpretation_projection_v1` par profondeur free/basic/premium. | Client dedie hors scope CS-258, apres contrat API separe. | Composant public-user hors scope CS-258. | Variation par narration et support vulgarise, jamais par runtime technique brut. |
| 4 | `transit_client_projection` | CS-281 definit `transit_client_projection_v1` comme cible future par plan, bloquee tant que le proof gate temporel reste non valide. | Client dedie hors scope CS-281; interdit avant proof gate et contrat API separe. | Composant public-user hors scope CS-281. | Statut non public, aucun raw runtime, aucune trace, aucun debug, aucune promesse produit. |
| 5 | `fixed_star_contacts` | Bloque tant que la politique est `needs-user-decision`. | Client interdit avant decision public/gated. | Section UI interdite avant decision public/gated. | Decision explicite sur public, gated ou abandon produit. |
| 6 | `astrologer_debug_data` | Aucune story tant que l'audience, l'auth et la retention ne sont pas decidees. | Aucun client public. | Aucun composant public. | Decision produit et securite separee. |
| 7 | `llm_input` | Aucun contrat public: input reserve aux services LLM. | Aucun client frontend pour input brut. | Aucune UI exposant l'input brut. | Reponse interpretee uniquement, jamais prompt/input brut. |

## Consequence fixed-star

`fixed_star_contacts` reste `needs-user-decision`. Aucune story ne peut exposer de
projection fixed-star tant que le produit n'a pas choisi l'un de ces statuts:

- `public`: contacts lisibles avec star display name, target object, orb reduit
  et display rule;
- `gated`: meme projection, mais routee derriere autorisation/entitlement;
- `rejected`: aucune section publique; usage limite a `llm_input` ou debug
  protege.

Tant que la decision manque, les contacts fixed-star restent internes/LLM-only
et OpenAPI reste bloque pour cette primitive.
