<!-- Commentaire global: ce document fixe le contrat canonique evidence_refs pour relier les sections narratives auditees a des sources validees et hashables sans exposer les preuves techniques au client. -->

# Contrat `evidence_refs`

`evidence_refs` est le contrat versionne qui relie chaque section narrative auditee a des sources controlees.
Il sert a l'audit admin et a la validation anti-hallucination des reponses narratives, sans creer de route, schema OpenAPI, table, migration, builder, service, prompt, provider call, frontend ou serializer runtime.

## Role

| Champ | Regle |
|---|---|
| `contract_id` | Valeur exacte: `evidence_refs`. |
| `contract_version` | Version du contrat de references de preuves, par exemple `evidence_refs.v1`. |
| `owner` | Contrat documentaire canonique: `docs/architecture/evidence-refs-contract.md`. |
| `audit_parent` | `narrative_answer_audit_v1`, qui porte l'audit de reponse et le `grounding_status` global. |
| `fact_base` | `structured_facts_v1`, projection factuelle stable, versionnee et hashable. |
| `client_exposure_policy` | Les preuves techniques restent internes; les surfaces client-facing ne peuvent exposer qu'un support vulgarise approuve. |

## Section auditee

Une section auditee est une portion stable d'une reponse narrative que l'audit peut verifier separement.
Chaque section doit porter un `section_id` stable, independant du texte rendu, afin de relier une ou plusieurs preuves au meme fragment metier meme si la prose change.

Exemples de sections admissibles:

- `identity.summary`;
- `dominants.overview`;
- `relationship.patterns`;
- `timing.context`;
- `plan.premium.deep_dive`.

Le `section_id` ne doit pas etre derive d'une position dans un tableau, d'un libelle UI traduisible ou d'une phrase generee.
Il appartient au contrat d'audit narratif ou a une projection aval explicite, pas au client frontend.

## Forme d'une reference

Chaque entree `evidence_ref` doit contenir les champs suivants:

| Champ | Obligation |
|---|---|
| `evidence_ref_id` | Identifiant stable de la preuve, unique dans l'audit de reponse. |
| `section_id` | Identifiant stable de la section narrative auditee. |
| `source_type` | Type de source autorise: `structured_fact`, `interpretive_signal` ou `projection_version`. |
| `source_id` | Identifiant de la source validee pointee par la preuve. |
| `source_version` | Version du contrat, de la regle ou de la projection source. |
| `source_hash` | Hash stable du payload source ou de l'artefact de projection valide. |
| `validation_state` | Etat de validation de la preuve. |
| `grounding_status` | Resultat de rattachement de la section aux preuves disponibles. |

Une `evidence_ref` sans `source_id`, sans `source_version` ou sans `source_hash` n'est pas une preuve valide.
Une chaine decorative telle que "voir le Soleil en Lion" ne suffit jamais: la reference doit pointer vers une source validee et un hash stable.

## Sources autorisees

`source_type` accepte exactement les valeurs suivantes:

| Valeur | Source controlee | Regle |
|---|---|---|
| `structured_fact` | Fait issu de `structured_facts_v1`. | Le `source_id` pointe vers une famille ou un fait stable, et le `source_hash` respecte le hash input boundary de `structured_facts_v1`. |
| `interpretive_signal` | Signal pre-narratif issu des owners interpretatifs, compatible avec `AINarrativeInterpretiveSignals`. | Le `source_id` pointe vers un code de signal explicite, versionne par `source_version`. |
| `projection_version` | Version de projection publique, interne ou LLM-only autorisee par la gouvernance produit. | Le `source_id` pointe vers la projection ou le lien de projection, avec hash de l'artefact valide. |

Aucun autre `source_type` n'est autorise par implication.
Les prompts, textes rendus, reponses LLM, labels UI, explications client, provider internals et payloads debug bruts ne sont pas des sources autorisees pour `evidence_refs`.

## Validation des sources

La validation d'une preuve doit verifier toutes les conditions suivantes:

1. la source existe dans le owner canonique attendu;
2. le `source_type` est autorise;
3. le `source_version` correspond a un contrat ou artefact versionne;
4. le `source_hash` est present;
5. le `source_hash` correspond au payload canonique valide;
6. la preuve est reliee a un `section_id` auditable.

`validation_state` prend exactement l'une des valeurs suivantes:

| Valeur | Sens |
|---|---|
| `validated` | La preuve pointe vers une source validee et hashable, et le hash correspond. |
| `missing_source` | Le `source_id` ne pointe vers aucune source validee disponible. |
| `unsupported_source_type` | Le `source_type` n'appartient pas a l'ensemble autorise. |
| `missing_hash` | Le `source_hash` est absent ou vide. |
| `hash_mismatch` | Le hash fourni ne correspond pas au payload source canonique. |

Toute erreur de validation doit rester visible dans l'audit admin.
Elle ne doit pas etre convertie en fallback silencieux ni en preuve nominale.

## Statut de grounding par section

Le `grounding_status` d'une section auditee prend exactement l'une des valeurs suivantes:

| Valeur | Sens |
|---|---|
| `grounded` | Toutes les affirmations importantes de la section sont rattachees a des preuves validees. |
| `partial` | Une partie de la section est rattachee a des preuves validees, mais au moins une reserve reste visible. |
| `unfounded` | Une preuve manquante, invalide ou en `hash_mismatch` empeche de fonder la section. |
| `not_checked` | Le controle n'a pas encore ete execute; l'etat doit rester explicite. |

Une section sans preuve attendue peut rester `not_checked` uniquement si le controle n'a pas encore ete execute.
Une section qui attendait une preuve mais ne dispose d'aucune `evidence_ref` valide doit pouvoir devenir `unfounded`.

## Separation admin et client

`admin_proof` designe les metadonnees techniques internes utilisables par l'audit et les controles anti-hallucination:

- identifiants de source;
- versions de contrats;
- hashes;
- etats de validation;
- details d'erreur tels que `missing_source`, `unsupported_source_type`, `missing_hash` et `hash_mismatch`.

`client_support` designe un element d'appui vulgarise, optionnel, redige pour une surface client-facing future.
Il peut expliquer qu'une interpretation s'appuie sur des themes ou facteurs astrologiques, mais il ne doit pas exposer `admin_proof`, hashes, prompt internals, provider internals, audit rows ou payloads techniques.

La presence de `client_support` ne valide jamais une preuve.
La validation vient uniquement d'une `evidence_ref` rattachee a une source validee et hashable.

## Frontieres applicatives

Cette story ne publie pas `evidence_refs` dans une route, un schema OpenAPI, une table, une migration, un client frontend ou une UI.
Toute implementation future devra reutiliser ce contrat au lieu de creer un chemin parallele.

Les surfaces suivantes restent explicitement hors ownership de ce document:

- calculs astrologiques;
- prompt templates;
- provider calls;
- stockage et retention;
- viewer admin;
- projections client-facing;
- composants frontend.

## Exemple documentaire

```json
{
  "contract_id": "evidence_refs",
  "contract_version": "evidence_refs.v1",
  "section_id": "dominants.overview",
  "evidence_ref_id": "dominants.overview.ref.001",
  "source_type": "structured_fact",
  "source_id": "dominants.primary",
  "source_version": "structured_facts_v1",
  "source_hash": "sha256:example-stable-source-hash",
  "validation_state": "validated",
  "grounding_status": "grounded"
}
```

Cet exemple illustre la forme du contrat.
Il ne definit pas un serializer runtime et ne constitue pas un payload public.
