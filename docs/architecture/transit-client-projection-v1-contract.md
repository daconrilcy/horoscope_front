<!-- Commentaire global: ce document fixe le contrat cible transit_client_projection_v1 sans creer de runtime, route publique, schema OpenAPI, frontend, migration ni promesse produit. -->

# Contrat `transit_client_projection_v1`

`transit_client_projection_v1` est une projection B2C future pour les clients
`free`, `basic` et `premium`. Elle est couchee au-dessus du runtime interne
`transit_chart_v1`, mais elle reste non public tant que le proof gate
astronomique, les versions de sources, les limites doctrinales et la validation
de projection ne sont pas clos.

Cette projection ne calcule aucun transit. Elle decrit seulement la forme cible
d'une narration client lisible, preparee depuis des faits et signaux transit
valides. La difference entre plans vient de la narration, de la profondeur de
timing, de l'explanatory richness et du guidage, jamais d'un acces debug.

## Champs contractuels

| Champ | Definition |
|---|---|
| `projection_id` | Valeur exacte: `transit_client_projection_v1`. |
| `audience` | Clients B2C `public-user`, `free`, `basic` et `premium`. |
| `source_runtime` | Valeur exacte: `transit_chart_v1`, runtime interne non expose. |
| `source_projection_policy` | Reutilise les regles de projection par plan de `client_interpretation_projection_v1`. |
| `plan_variant` | Une des valeurs controlees: `free`, `basic` ou `premium`. |
| `client_content` | Sections narratives et support elements lisibles par plan. |
| `degraded_state` | Etat affiche quand preuve, donnees, technique ou doctrine limitent la projection. |
| `proof_gate` | Statut obligatoire avant exposition: astronomical evidence, source versions, doctrine limits et projection validation evidence doivent etre valides. |
| `llm_role` | Le LLM est rédacteur depuis des faits prepares et des signaux transit; not calculator, not proof owner, not doctrine authority. |
| `excluded_surfaces` | Raw runtime, graph traces, proof internals, debug fields, API route, frontend, DB, migration, entitlement et product promise. |

## Matrice de contenu par plan

| Plan | `client_content` autorise | Intention |
|---|---|---|
| `free` | `orientation_generale`, `periode_active_simplifiee`, `theme_du_moment`, `limite_de_lecture`, `upgrade_hint` non technique | Donner une lecture courte, prudente et utile sans prediction detaillee ni diagnostic technique. |
| `basic` | Sections `free` plus `fenetres_de_timing`, `transits_principaux_vulgarises`, `conseil_pratique`, `points_de_vigilance` | Relier les transits dominants a des themes personnels avec plus de contexte, sans exposer les objets runtime. |
| `premium` | Sections `basic` plus `sequence_temporelle`, `nuances_et_arbitrages`, `priorites_d_action`, `lecture_des_cycles`, `limites_explicites` | Produire une narration plus riche, nuancee et actionnable, tout en restant une projection client non expert. |

Aucun plan ne donne acces aux debug fields, graph traces, proof internals,
raw runtime payloads, objets `ChartObjectRuntimeData` ou diagnostics expert.
`premium` augmente la richesse explicative et la granularite narrative; il ne
devient pas une surface d'audit, d'administration ou de calcul.

## Profondeur narrative

| Dimension | `free` | `basic` | `premium` |
|---|---|---|---|
| `narration` | Message synthetique et non anxiogene. | Narration contextualisee par themes dominants. | Narration multi-etapes avec nuances, arbitrages et priorites. |
| `timing_depth` | Periode large et prudente, sans fenetre fine. | Fenetres de timing vulgarisees si le proof gate les autorise. | Sequence temporelle plus detaillee avec limites affichees. |
| `explanatory_richness` | Vocabulaire simple, peu de causalite. | Explications client-readables sur les signaux principaux. | Liens entre signaux, doctrine limits et conseils d'usage. |
| `guidance_framing` | Orientation generale. | Conseils pratiques limites. | Pistes d'action priorisees sans promesse predictive certaine. |

La projection doit afficher explicitement que les transits sont des indications
d'interpretation. Elle ne promet pas un evenement, ne remplace pas une decision
humaine et ne transforme pas la doctrine astrologique en garantie produit.

## Etats degrades et indisponibles

| Etat | Cause | Sortie client autorisee |
|---|---|---|
| `proof_gate_blocked` | Le proof gate astronomique ou la validation de projection n'est pas valide. | Etat unavailable: expliquer que les transits client ne sont pas encore disponibles. |
| `data_incomplete` | Donnees natales, date de transit, source version ou contexte requis manquant. | Etat degraded: afficher les limites et reduire la narration aux elements fiables. |
| `unsupported_technique` | Technique temporelle hors famille `transit_chart_v1` ou non supportee. | Etat unavailable: ne pas simuler une lecture avec un fallback silencieux. |
| `doctrine_limited` | Doctrine limits non resolues, source owner absent ou conflit de regle. | Etat degraded ou unavailable selon gravite; afficher la limite sans detail interne. |
| `source_version_mismatch` | Versions de source ou ephemeris incompatibles avec le contrat attendu. | Etat unavailable jusqu'a validation explicite. |

Un etat degraded ne doit jamais masquer une absence de preuve. Un etat
unavailable doit bloquer l'exposition plutot que produire une narration
rassurante depuis des donnees insuffisantes.

## Proof gate obligatoire

Avant toute exposition publique, `transit_client_projection_v1` exige:

- astronomical evidence validee pour la famille `transit_chart_v1`;
- source versions explicites pour ephemeris, runtime, doctrine et projection;
- doctrine limits lisibles par le produit et non transformees en certitudes;
- projection validation evidence couvrant la matrice `free`, `basic`, `premium`;
- preuve que l'OpenAPI public, les routes client, le frontend et les clients
  generes restent fermes tant qu'une story separee ne les autorise pas.

Tant que ces preuves ne sont pas presentes, le statut reste non public. Aucune
route, schema, serializer, entitlement, migration ou UI ne peut inferer une
disponibilite produit depuis ce document.

## Role du LLM

Le LLM peut etre utilise comme rédacteur seulement apres preparation de faits
et signaux transit controles. Il redige une sortie client-readable a partir de
ces entrees et des limites de plan.

Le LLM n'est pas calculator, proof owner, doctrine authority, ephemeris owner ou
runtime builder. Il ne choisit pas les transits valides, ne corrige pas un proof
gate bloque, ne cree pas de doctrine alternative et ne decide pas du statut
`degraded` ou `unavailable`.

## Exclusions techniques

`transit_client_projection_v1` exclut toutes les surfaces suivantes:

- raw runtime objects, raw runtime payloads et objets `ChartObjectRuntimeData`;
- graph traces, calculation graph payloads, internal trace keys et debug fields;
- proof internals, ephemeris internals, evidence IDs internes et audit rows;
- `expert_technical_projection_v1`, `astrology_full_data_v1` et diagnostics
  admin ou expert;
- public API route, OpenAPI schema, backend runtime builder, serializer,
  service orchestration, provider call, prompt template definitif;
- frontend route, screen, component, generated client, CSS, i18n et navigation;
- DB model, migration, persistence, entitlement enforcement, pricing ou product
  promise.

Toute implementation future doit avoir une story separee pour le contrat API,
le client frontend, l'UI, la persistance ou l'entitlement. Ce document reste le
seul contrat canonique de contenu pour la projection transit client par plan.

## Relation aux contrats existants

`client_interpretation_projection_v1` fournit le modele de differentiation par
plan: profondeur narrative, personnalisation, timing autorise et explanatory
richness. `transit_client_projection_v1` reutilise ce modele sans creer un
second systeme d'entitlement ou de debug par plan.

`transit_chart_v1` reste le runtime interne. Ses objets structurels, preuves et
traces servent de source controlee a de futures projections, mais ne deviennent
pas des payloads client. Le proof gate temporel conserve la priorite sur toute
ambition de narration produit.
