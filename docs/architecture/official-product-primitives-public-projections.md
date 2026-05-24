<!-- Commentaire global: ce document fixe les primitives produit publiques sans transformer les surfaces runtime internes en API. -->

# Official Product Primitives And Public Projection Roadmap

Ce document est l'owner canonique des primitives produit publiques pour les
projections astrologiques. Il consolide CS-238, CS-244, CS-249 et CS-250 sans
modifier les routes, serializers, calculateurs, clients frontend ou composants
UI existants.

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
| `beginner_summary` | beginner summary | beginner, public-user, AI, PDF | public | projections publiques existantes, contexte natal compact LLM | futur contrat public resume debutant | `chart_objects`, raw score breakdowns, raw calculation graph payloads | CS-256 API contract | CS-256 frontend client | CS-256 UI component | OpenAPI-ready |
| `expert_technical_projection` | expert technical projection | expert, astrologer | public | dignities, conditions, dominance, aspects publics stabilises | futur contrat public expert | `ChartObjectRuntimeData`, raw dominance payloads, raw dignity payloads, `interpretation_input` | CS-255 API contract | CS-255 frontend client | CS-255 UI component | OpenAPI-ready |
| `fixed_star_contacts` | fixed-star contacts | expert, public-user, AI | needs-user-decision | `backend/app/domain/astrology/fixed_stars/**`, payloads rattaches aux objets | none until product decision | raw fixed star catalog dump, raw conjunction payloads, `ChartObjectRuntimeData` | CS-257 API contract blocked until policy decision | CS-257 frontend client blocked until policy decision | CS-257 UI component blocked until policy decision | blocked |
| `astrologer_debug_data` | astrologer/debug data | astrologer, debug | needs-user-decision | traces de calcul, audit rows, graph runtime interne | none | `chart_objects`, raw calculation graph payloads, internal IDs, audit internals | none until audience/auth decision | none until audience/auth decision | none until audience/auth decision | blocked |
| `llm_input` | LLM input | AI | LLM-only | `interpretation_input`, contexte natal compact, evidence catalog | none for public API | `interpretation_input`, prompt internals, evidence IDs beyond display need | none | none | none | OpenAPI-neutral |

## Mapping CS-244 par audience

| Audience CS-244 | Besoin produit | Primitive cible | Decision |
|---|---|---|---|
| beginner | Soleil/Lune/Ascendant compacts, themes dominants, labels traduits, masquage des details techniques | `beginner_summary` | public |
| expert | dignites, conditions, analyse traditionnelle, dominance, aspects techniques | `expert_technical_projection` et `structured_facts` | public avec selection de champs explicite |
| astrologer | payload expert, historique, notes diagnostiques eventuelles | `astrologer_debug_data` | needs-user-decision avant exposition |
| debug | traces, payloads internes, audit rows, garde runtime | `astrologer_debug_data` | rejected for public; needs-user-decision pour surface protegee |
| AI | contexte natal compact, evidence catalog, metadata persona/use-case, disclaimers | `llm_input` et `beginner_summary` | LLM-only pour input brut; public uniquement via reponse interpretee |
| PDF | interpretation persistee, sections, highlights, labels Soleil/Ascendant, disclaimers | `structured_facts` et `beginner_summary` | public to owning user |
| public-user | resume debutant, highlights, conseils, etats paywall/degrades | `beginner_summary` | public |

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
| 1 | `expert_technical_projection` | CS-255 definit la liste de champs expert et les exclusions runtime. | CS-255 met a jour le client uniquement apres contrat API. | CS-255 adapte le panneau expert uniquement aux champs approuves. | Aucun nom raw runtime dans OpenAPI, client ou UI. |
| 2 | `beginner_summary` | CS-256 definit un contrat deterministic de resume debutant. | CS-256 ajoute le client dedie apres contrat API. | CS-256 ajoute ou adapte le composant public-user. | Masquage des degres, orbes, scores bruts et graph runtime. |
| 3 | `fixed_star_contacts` | CS-257 reste bloque tant que la politique est `needs-user-decision`. | CS-257 client interdit avant decision public/gated. | CS-257 section UI interdite avant decision public/gated. | Decision explicite sur public, gated ou abandon produit. |
| 4 | `astrologer_debug_data` | Aucune story tant que l'audience, l'auth et la retention ne sont pas decidees. | Aucun client public. | Aucun composant public. | Decision produit et securite separee. |
| 5 | `llm_input` | Aucun contrat public: input reserve aux services LLM. | Aucun client frontend pour input brut. | Aucune UI exposant l'input brut. | Reponse interpretee uniquement, jamais prompt/input brut. |

## Consequence fixed-star pour CS-257

`fixed_star_contacts` reste `needs-user-decision`. CS-257 ne peut pas exposer de
projection fixed-star tant que le produit n'a pas choisi l'un de ces statuts:

- `public`: contacts lisibles avec star display name, target object, orb reduit
  et display rule;
- `gated`: meme projection, mais routee derriere autorisation/entitlement;
- `rejected`: aucune section publique; usage limite a `llm_input` ou debug
  protege.

Tant que la decision manque, les contacts fixed-star restent internes/LLM-only
et OpenAPI reste bloque pour cette primitive.
