<!-- Commentaire global: ce document fixe le contrat API admin_answer_audit_v1 sans creer de route runtime, persistence, UI, replay ou exposition client. -->

# Contrat API `admin_answer_audit_v1`

`admin_answer_audit_v1` est la surface API interne protegee qui permettra aux
administrateurs autorises de consulter les audits de reponses narratives IA.
Le contrat est declaratif pour cette story: il ne cree pas de route FastAPI, de
schema OpenAPI runtime, de table, de repository, de migration, de client
frontend, d'ecran admin, de job de replay ou de couplage au debug de calcul.

## Surface protegee

| Element | Regle |
|---|---|
| `contract_id` | Valeur exacte: `admin_answer_audit_v1`. |
| Route liste | `GET /v1/admin/answer-audits`. |
| Route detail | `GET /v1/admin/answer-audits/{answer_id}`. |
| Protection | Acces admin-only via le pattern existant `require_admin_user`. |
| Public cible | Administrateurs autorises uniquement; aucune route client-facing. |
| Source metier | `narrative_answer_audit_v1` pour l'audit de reponse et `evidence_refs` pour les preuves. |

La surface est un contrat de consultation et de diagnostic admin. Les futures
routes devront conserver ce chemin canonique au lieu de creer un endpoint client,
un endpoint public ou une variante de debug parallele.

## Cas d'usage admin

| Cas d'usage | Comportement attendu |
|---|---|
| Consultation | L'admin filtre et liste les audits de reponses narratives pour comprendre leur etat de generation et de grounding. |
| Diagnostic review | L'admin ouvre un detail pour verifier les versions, hashes, provider, model, prompt_version et `evidence_refs` rattaches. |
| Reponses rejetees | L'admin consulte les reponses rejetées avec leur statut `rejected` et leur `rejection_reason`, meme si elles ne sont pas exposees au client. |

La consultation admin n'est pas un replay complet. Elle donne un acces lisible
aux preuves techniques deja portees par les contrats amont, sans executer a
nouveau le calcul astrologique ni la generation LLM.

## Filtres de liste

`GET /v1/admin/answer-audits` accepte les filtres suivants:

| Filtre | Regle |
|---|---|
| `status` | Filtre sur `grounded`, `partial`, `ungrounded`, `rejected` ou `not_checked`. |
| `plan` | Filtre sur le plan commercial applique au moment de generation. |
| `created_from` | Debut inclusif de date range sur `created_at`. |
| `created_to` | Fin inclusive de date range sur `created_at`. |
| `provider` | Filtre sur l'identifiant provider LLM. |
| `model` | Filtre sur le modele provider. |

Les noms de champs JSON restent en snake_case.

## Champs de liste

Chaque item de liste expose uniquement les champs consultables suivants:

| Champ | Regle |
|---|---|
| `contract_id` | Toujours `admin_answer_audit_v1`. |
| `answer_id` | Identifiant de la reponse narrative auditee. |
| `answer_type` | Categorie heritee de `narrative_answer_audit_v1`. |
| `plan` | Plan commercial de generation. |
| `status` | Statut d'audit: `grounded`, `partial`, `ungrounded`, `rejected` ou `not_checked`. |
| `created_at` | Horodatage de generation ou d'audit. |
| `projection_version` | Version de projection factuelle auditee. |
| `projection_hash` | Hash stable de la projection. |
| `llm_input_version` | Version du contrat d'entree LLM. |
| `llm_input_hash` | Hash stable du payload d'entree LLM. |
| `prompt_version` | Version du prompt contractuel. |
| `provider` | Identifiant du fournisseur LLM. |
| `model` | Identifiant du modele provider. |
| `evidence_refs` | Resume admin des references de preuves et de leur etat. |
| `birth_data` | Resume masque uniquement. |
| `rejection_reason` | Present uniquement pour une reponse `rejected`. |

`user_id` et `chart_id` ne sont pas retournes par defaut dans la liste.

## Champs de detail

`GET /v1/admin/answer-audits/{answer_id}` expose les champs de liste et peut
ajouter, selon le niveau d'autorisation admin:

| Champ | Regle |
|---|---|
| `user_id` | Identifiant utilisateur, accessible uniquement aux admins autorises. |
| `chart_id` | Identifiant de theme, accessible uniquement aux admins autorises. |
| `evidence_refs` | Detail des preuves admin: source, version, hash, validation_state et grounding_status. |
| `permission_policy` | Rappel de la politique admin-only et du dependency pattern `require_admin_user`. |
| `error_policy` | Regles d'erreur applicables a la consultation. |

Le detail peut afficher les preuves techniques reservees a l'admin autorise,
mais ne doit pas exposer de payload brut de naissance ni de traces de calcul.

## Masquage des donnees de naissance

`birth_data` est toujours masque par defaut. Il peut indiquer une categorie
utile au diagnostic, par exemple `has_birth_profile: true` ou un niveau de
precision general, mais il ne doit jamais retourner les donnees brutes suivantes
dans les reponses par defaut:

- `birth_date`;
- `birth_time`;
- `birth_place`;
- `birth_coordinates`;
- `birth_lat`;
- `birth_lon`;
- `birth_timezone`;
- latitude, longitude ou timezone brute.

Tout besoin futur d'acces exceptionnel a ces donnees doit faire l'objet d'un
contrat separe, journalise et explicitement autorise.

## Permissions et erreurs

| Code | Regle |
|---|---|
| `200` | Consultation liste ou detail reussie pour un admin autorise. |
| `401` | Authentification absente ou invalide. |
| `403` | Utilisateur authentifie sans role admin suffisant. |
| `404` | `answer_id` inconnu ou audit non disponible pour ce perimetre. |
| `503` | Backing audit store indisponible ou non initialise. |

Les erreurs doivent etre explicites et ne doivent pas basculer vers un fallback
silencieux, une route publique ou une reponse client partielle.

## Separation des owners

`admin_answer_audit_v1` reste separe de `admin_chart_diagnostics_v1`.
La surface d'audit narrative peut referencer des versions, hashes, provider,
model, prompt_version et `evidence_refs`, mais elle ne devient pas proprietaire:

- du debug de calcul astrologique;
- des diagnostics de theme;
- des endpoints client;
- du replay workflow;
- de la persistence future de `narrative_answer_audit_v1`;
- de la validation future de `evidence_refs`.

Les futures stories CS-288, CS-289 et CS-290 devront reutiliser ce contrat au
lieu de creer une surface parallele ou de fusionner avec les diagnostics de
calcul.
