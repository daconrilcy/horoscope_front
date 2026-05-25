<!-- Commentaire global: ce document fixe le contrat canonique narrative_answer_audit_v1 sans creer d'implementation runtime, persistence, API ou frontend. -->

# Contrat `narrative_answer_audit_v1`

`narrative_answer_audit_v1` est le contrat d'audit versionne des reponses narratives produites avec assistance LLM.
Il rattache chaque prose generee ou rejetee aux faits, aux entrees LLM, au prompt, au provider, au model et a l'etat de grounding utilises au moment de generation.

Ce contrat est declaratif. Il ne cree pas de table, migration, repository, route API, schema OpenAPI, serializer, client frontend, ecran admin, prompt template ou integration provider.

## Role

| Champ | Regle |
|---|---|
| `contract_id` | Valeur exacte: `narrative_answer_audit_v1`. |
| `role` | Preuve interne permettant d'auditer une reponse narrative basic, premium, long, sensitive ou free_short. |
| `source_of_truth` | Les faits astrologiques restent portes par `structured_facts_v1` et les entrees controlees de `AINarrativeInputContract`, jamais par la prose finale. |
| `client_exposure_policy` | Les payloads client-facing ne doivent exposer ni technical proof, ni provider internals, ni prompt payload, ni audit rows. |

## Identite obligatoire

Chaque ligne d'audit doit conserver les champs d'identite suivants:

| Champ | Obligation |
|---|---|
| `answer_id` | Identifiant unique de la reponse narrative produite ou rejetee. |
| `answer_type` | Categorie fonctionnelle de la reponse: `basic`, `premium`, `long`, `sensitive` ou `free_short`. |
| `chart_id` | Identifiant du theme ayant servi a produire la projection auditee. |
| `user_id` | Identifiant du proprietaire metier de la reponse au moment de generation. |
| `plan` | Plan commercial applique au moment de generation. |
| `projection_version` | Version de la projection factuelle utilisee comme base. |
| `projection_hash` | Hash stable et obligatoire du payload de projection audite. |

`projection_hash` n'est pas une metadata optionnelle: il est l'ancre de comparaison entre la narration et la projection factuelle.

## Provenance LLM obligatoire

Le contrat conserve la provenance LLM minimale suivante:

| Champ | Obligation |
|---|---|
| `llm_input_version` | Version du contrat d'entree LLM, par exemple le contrat interne issu de `AINarrativeInputContract`. |
| `llm_input_hash` | Hash stable et obligatoire du payload d'entree LLM transmis a la generation. |
| `prompt_version` | Version du prompt contractuel utilise. |
| `provider` | Identifiant interne du fournisseur LLM. |
| `model` | Identifiant interne du modele provider utilise. |

`llm_input_hash` doit etre conserve meme si la reponse est rejetee, afin de prouver quel contexte a ete evalue.

## Stockage du prompt

La preuve de prompt doit suivre l'une des deux formes controlees suivantes:

| Mode | Contenu requis |
|---|---|
| `full prompt` | Texte complet du prompt conserve dans l'audit interne. |
| `prompt_ref` + `payload snapshot` | Reference stable vers le prompt versionne et snapshot du payload variable utilise. |

Le choix entre `full prompt` et `prompt_ref` plus `payload snapshot` releve d'une future politique de retention. Cette story ne definit pas la retention RGPD finale.

## Statut de grounding

`grounding_status` est obligatoire et prend exactement l'une des valeurs suivantes:

| Valeur | Sens |
|---|---|
| `grounded` | La reponse est coherente avec les faits et preuves attendus. |
| `partial` | La reponse est majoritairement rattachee aux faits, avec une reserve explicite d'audit. |
| `ungrounded` | La reponse ne peut pas etre suffisamment rattachee aux faits ou preuves. |
| `rejected` | La reponse a ete refusee avant exposition ou usage metier. |
| `not_checked` | Le controle de grounding n'a pas encore ete execute; l'etat doit rester visible et auditable. |

## Reponses rejetees

Les reponses `rejected` restent dans le perimetre d'audit. Elles doivent conserver:

- `answer_id`, `answer_type`, `chart_id`, `user_id` et `plan`;
- `projection_version` et `projection_hash`;
- `llm_input_version` et `llm_input_hash`;
- `prompt_version`, `provider`, `model` et la preuve de prompt;
- la raison de rejet et les metadonnees de source disponibles.

Une reponse rejetee ne doit pas etre supprimee de l'audit simplement parce qu'elle n'est pas client-facing.

## Exposition client

Les projections client-facing peuvent afficher une reponse interpretee, des messages de degradation ou des explications utilisateur.
Elles ne doivent pas exposer:

- `projection_hash`, `llm_input_hash`, `prompt_version`, `provider` ou `model`;
- prompt brut, `full prompt`, `prompt_ref` ou `payload snapshot`;
- technical proof, provider internals, model internals ou audit rows;
- details de rejet reserves au diagnostic interne.

Les surfaces publiques futures devront definir un contrat API separe. `narrative_answer_audit_v1` reste un contrat interne d'audit.

## Frontieres

`narrative_answer_audit_v1` peut referencer `structured_facts_v1`, `projection_hash`, `AINarrativeInputContract` et `llm_input_hash`.
Il ne devient pas le proprietaire du calcul astrologique, de la projection publique, du prompt, de la persistence ou de l'administration.

Les implementations futures de persistence, validation d'evidence, acces admin et retention devront reutiliser ce contrat au lieu de creer un chemin parallele.
