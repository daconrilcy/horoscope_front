<!-- Commentaire global: ce document fixe le contrat canonique client_interpretation_projection_v1 sans creer d'implementation runtime ni de surface publique. -->

# Contrat `client_interpretation_projection_v1`

## Role

`client_interpretation_projection_v1` est la projection B2C interpretee par plan
pour les clients `free`, `basic` et `premium`.

Ce contrat documente la forme produit cible. Il ne cree pas de builder, de
service, de route API, de schema OpenAPI, de table, de migration, de client
frontend, de serializer runtime, de prompt definitif ou d'integration provider
LLM.

La valeur de cette projection vient de la narration, de la personnalisation
controlee, des sections autorisees par plan, des predictions quand le plan les
permet et de la richesse explicative. Elle ne vient jamais d'une exposition de
runtime technique brut.

## Sources et responsabilites

| Champ | Regle |
|---|---|
| `projection_id` | Valeur exacte: `client_interpretation_projection_v1`. |
| `audience` | Clients B2C `public-user`, `free`, `basic` et `premium`. |
| `source_projection` | Valeur exacte: `structured_facts_v1`. |
| `sibling_projection` | Valeur exacte: `beginner_summary_v1`, plus court et plus deterministe. |
| `plan_variant` | Une des valeurs controlees: `free`, `basic` ou `premium`. |
| `llm_role` | Le LLM est rédacteur: il redige depuis des faits prepares et des signaux interpretatifs; il n'est pas calculateur, astrologer engine ni source de verite de calcul. |
| `excluded_surfaces` | Runtime technique brut, proof internals, scoring proof internals, prompt internals, provider internals, audit internals et champs expert. |

`structured_facts_v1` reste l'upstream factual source. Les signaux
interpretatifs issus de `AINarrativeInterpretiveSignals` sont des entrees
pre-narratives qui orientent le texte; ils ne deviennent pas un payload
technique public.

## Contrat de shaping par plan

`client_interpretation_projection_v1` expose un contrat de shaping logique avant
toute implementation de prompt ou de rendu. Les objets ci-dessous sont les noms
canoniques a reprendre par les futures stories backend, LLM et frontend:

- `LLMInputSelection`: selection des familles de faits autorisees pour redaction.
- `EditorialDepthProfile`: profondeur redactionnelle attendue pour le plan.
- `FrontendVisibilityRules`: sections visibles, resumees ou masquees par plan.
- `precision_level`: granularite client-readable de specificity, prediction et
  densite de caveats.

Le shaping ne modifie pas la disponibilite de la projection. Les calculs et
interpretations existent pour `free`, `basic` et `premium`; seule la selection
des faits, la richesse redactionnelle et la presentation frontend varient.

| Plan | `LLMInputSelection.allowed_fact_groups` | `EditorialDepthProfile` | `precision_level` | `FrontendVisibilityRules` |
|---|---|---|---|---|
| `free` | `dominant_themes`, `core_strengths`, `reading_limits`, `upgrade_context` | `free_short`: texte court, une lecture principale, caveats explicites. | `orientation`: specificity faible, pas de calendrier fin. | Sections principales visibles, details avances masques, upgrade hints autorises. |
| `basic` | `free` plus `personal_themes`, `relationship_patterns`, `current_rhythm`, `practical_guidance` | `basic_contextual`: lecture contextualisee, exemples simples, conseil pratique. | `contextual`: specificity moyenne, tendances simples. | Sections free visibles, themes et conseils visibles, analyses profondes resumees. |
| `premium` | `basic` plus `tensions_resources`, `prediction_windows`, `nuance_arbitration`, `action_priorities` | `premium_deep`: lecture longue, nuances, arbitrages et limites detaillees. | `detailed`: specificity haute, fenetres controlees et caveats denses. | Toutes sections client autorisees visibles, avec display hints detailles. |

Les `evidence_refs` autorisees dans `LLMInputSelection` restent des labels
client-safe ou des references internes indirectes. Le payload client ne doit pas
exposer d'IDs d'audit bruts, de traces provider, de prompt final, de graphes de
calcul ou de preuves expert.

## Owners et validations futures

| Responsabilite | Owner canonique | Destination interdite |
|---|---|---|
| Autorisation et acces projection | `docs/architecture/b2c-projection-entitlement-policy.md` et backend service d'entitlement | Matrice locale React ou branchement UI par plan. |
| Contrat API public | `backend/app/services/api_contracts/public/projections.py` | Nouvelle route plan-specific ou schema divergent. |
| Builder projection client | `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` | Router API, frontend ou prompt provider. |
| Selection des faits LLM | owner `structured_facts_v1` plus future orchestration LLM natale | Copie complete de runtime brut dans le prompt. |
| Rendu frontend | `frontend/src/features/natal-chart/NatalInterpretation.tsx` et composants de projection | Politique commerciale, entitlement ou matrice free/basic/premium. |

Les futures validations doivent inclure:

- un test backend prouvant HTTP 200 pour `client_interpretation_projection_v1`
  avec `free`, `basic` et `premium`;
- un test backend prouvant que le shaping differencie au moins
  `LLMInputSelection`, `EditorialDepthProfile` ou `FrontendVisibilityRules`;
- un guard frontend bloquant une matrice locale `free`/`basic`/`premium`;
- un scan OpenAPI confirmant l'absence de route plan-specific pour la
  projection.

## Matrice des sections par plan

| Plan | Sections autorisees | Intention produit |
|---|---|---|
| `free` | `orientation_generale`, `points_forts`, `limite_de_lecture`, `upgrade_hint` | Donner une interpretation courte, utile et non anxiogene, avec peu de personnalisation et sans prediction detaillee. |
| `basic` | Sections `free` plus `themes_personnels`, `relations_aux_autres`, `rythme_actuel`, `conseil_pratique` | Offrir une lecture plus personnalisee, reliee aux themes dominants et a quelques appuis vulgarises. |
| `premium` | Sections `basic` plus `analyse_approfondie`, `tensions_et_ressources`, `fenetres_de_prediction`, `plan_d_action`, `nuances_et_arbitrages` | Produire une interpretation riche, nuancee, plus predictive et actionnable sans devenir une projection expert. |

Aucun plan ne recoit davantage de runtime technique brut. La difference entre
`free`, `basic` et `premium` porte uniquement sur la profondeur narrative, le
nombre de sections, la personnalisation, les predictions autorisees et la
richesse explicative.

## Profondeur narrative

| Dimension | `free` | `basic` | `premium` |
|---|---|---|---|
| `section_count` | Faible: quelques blocs courts et stables. | Moyen: sections thematiques lisibles. | Eleve: sections detaillees, reliees entre elles. |
| `personalization_depth` | Personnalisation minimale depuis les themes principaux. | Personnalisation par themes, relations et contexte de lecture. | Personnalisation approfondie, avec nuances, arbitrages et priorites. |
| `predictions_depth` | Pas de prediction detaillee; seulement une orientation prudente si disponible. | Tendances simples et conseils pratiques sans calendrier fin. | Fenetres de prediction controlees, conditions de lecture et limites explicites. |
| `explanatory_richness` | Explications courtes, vocabulaire simple. | Explications contextualisees et exemples concrets. | Explications riches, liens entre signaux, limites et pistes d'action. |

Les predictions restent des formulations de tendance. Elles ne promettent pas
un resultat certain et ne revelent pas les calculs, scores ou preuves internes.

## Elements d'appui vulgarises

La projection peut exposer des support elements client-readables pour aider le
client a comprendre l'interpretation:

- highlights vulgarises rattaches a une section, par exemple "theme dominant",
  "point d'attention" ou "ressource a mobiliser";
- confidence wording lisible, par exemple "lecture forte", "lecture prudente"
  ou "lecture limitee par les donnees disponibles";
- source labels non techniques, par exemple "position principale", "relation
  entre deux themes" ou "signal recurrent";
- display hints pour presenter une section courte, detaillee, degradee ou
  invitee a l'upgrade;
- personalization notes quand elles restent comprehensibles et justifiees par
  les faits prepares.

Ces elements d'appui ne sont pas des raw factual dumps. Ils ne contiennent pas
de trace IDs, graph payloads, evidence IDs internes, coefficients, scores bruts,
debug rows, payloads provider ou prompt payloads.

## Exclusions techniques client

`client_interpretation_projection_v1` interdit les surfaces suivantes dans tout
payload client futur:

- runtime technique brut, `ChartObjectRuntimeData`, `chart_objects`, graphes de
  calcul complets et traces runtime;
- proof internals, scoring proof internals, audit internals, evidence refs
  internes, tolerances, hashes techniques et details de calcul;
- prompt internals, definitive prompt templates, provider implementation,
  provider responses, model routing et model identifiers;
- `expert_technical_projection_v1`, champs expert, admin roles, debug
  astrologer data et diagnostics administrateur;
- full facts ou copie complete de `structured_facts_v1`.

Les preuves techniques restent internes ou reservees a des surfaces expert
controlees separees. Premium n'est pas une exception: il augmente la narration,
la personnalisation et l'explication, pas l'exposition technique.

## Relation avec les projections voisines

`beginner_summary_v1` reste le sibling B2C simple pour un resume court,
deterministe et compatible debutant. `client_interpretation_projection_v1`
peut s'appuyer sur la meme base factuelle, mais il ajoute une interpretation
redigee par plan.

`expert_technical_projection_v1` reste hors scope. Si une future story veut
exposer des champs expert, elle doit le faire dans un contrat expert separe,
avec audience, autorisation et validations propres.

## Frontieres applicatives

Cette story est OpenAPI-neutral. Toute exposition future devra definir une
story separee pour l'API, le builder, le serializer, le client frontend, les
droits d'acces, les tests de payload et les validations de non-exposition.

Un futur consommateur ne doit pas inferer ce contrat depuis les objets runtime.
Il devra consommer une projection controlee qui respecte `projection_id`,
`plan_variant`, les sections autorisees, la profondeur narrative et les
exclusions ci-dessus.
