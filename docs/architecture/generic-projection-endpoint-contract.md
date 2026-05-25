<!-- Commentaire global: ce document fixe le contrat canonique du futur endpoint B2C de projections sans creer de route, de schema OpenAPI, de service runtime, de persistence ou de client frontend. -->

# Contrat `POST /v1/astrology/projections`

`POST /v1/astrology/projections` est une commande B2C future qui pourra
consolider l'appel client autour de deux responsabilites backend separees:
calculer ou retrouver le theme astrologique, puis construire une projection
produit autorisee. Ce document est contractuel uniquement; il ne publie pas
l'endpoint dans `app.routes`, `app.openapi()`, un routeur FastAPI, un serializer,
une table, une migration, un builder, un service ou un client frontend genere.

Le registre de gouvernance reste
`docs/architecture/official-product-primitives-public-projections.md`. Les
contrats `structured_facts_v1`, `beginner_summary_v1`,
`client_interpretation_projection_v1` et `narrative_answer_audit_v1` restent les
sources de vocabulaire produit et d'exclusion technique.

## Audience et portee

L'audience de ce contrat est le client B2C authentifie. La commande est
destinee aux experiences `public-user`, `free`, `basic` et `premium` selon la
politique produit de chaque `projection_type`.

Le comportement B2B API est explicitement hors scope: ce contrat ne definit ni
route partenaire, ni payload partenaire, ni usage `/v1/b2b`, ni endpoint
`/v1/partners`, ni garantie pour une integration entreprise.

## Payload de requete

Le corps JSON accepte les cles suivantes, avec ces noms exacts:

| Champ | Statut | Regle |
|---|---|---|
| `chart_id` | optionnel conditionnel | Identifiant d'un theme existant appartenant au client B2C authentifie. |
| `birth_input` | optionnel conditionnel | Donnees de naissance utilisees quand aucun theme existant reutilisable n'est choisi. |
| `projection_type` | obligatoire | Identifiant de projection B2C autorise par type et par plan ou entitlement. |
| `projection_version` | obligatoire | Version explicite du contrat de projection demande; aucune valeur implicite ou fallback silencieux n'est admis. |
| `persist` | optionnel | Booleen indiquant si la future commande peut persister un artefact eligible. |

`projection_type` et `projection_version` sont requis pour chaque requete.
`projection_version` est obligatoire meme quand le client fournit un
`chart_id`, afin d'eviter une resolution implicite de version.

## Selection du theme

La requete doit fournir exactement une source de theme acceptee:

| Cas | Resultat contractuel |
|---|---|
| `chart_id` seul | Le futur endpoint retrouve le theme via l'owner existant de lookup `chart_id`, aujourd'hui `backend/app/infra/db/repositories/chart_result_repository.py`, et verifie qu'il appartient au client authentifie. |
| `birth_input` seul | Le futur endpoint demande un calcul de theme au service de calcul astrologique avant la construction de projection. |
| `chart_id` et `birth_input` ensemble | Requete invalide: le choix de source est ambigu. |
| Ni `chart_id` ni `birth_input` | Requete invalide: aucune source de theme n'est disponible. |

Le contrat ne deplace pas la responsabilite de lookup de `chart_id` dans le
document d'endpoint et ne cree pas de repository parallele.

## Responsabilites de services

Le calcul du theme et la construction de projection restent deux services
conceptuellement distincts.

| Responsabilite | Owner conceptuel | Interdiction |
|---|---|---|
| Recuperer un theme existant par `chart_id` | Repository de resultats de theme existant. | Ne pas coder le lookup dans un routeur ou dans un builder de projection. |
| Calculer un theme depuis `birth_input` | Service de calcul astrologique. | Ne pas melanger les regles de projection produit avec le calcul natal. |
| Construire la projection demandee | Futur service de projection produit. | Ne pas recalculer le theme ni exposer le runtime technique brut. |
| Appliquer l'autorisation B2C | Couche d'orchestration future avec politique plan ou entitlement. | Ne pas ouvrir les projections internes par defaut. |

Une future implementation pourra offrir une commande HTTP consolidee, mais elle
devra conserver cette separation interne et journaliser les indisponibilites
bloquantes.

## Projection types autorises

L'acces B2C est decide par `projection_type`, puis par plan ou entitlement. Une
projection n'est accessible au client que si son contrat public la declare
eligible pour l'audience B2C demandee.

| `projection_type` | Politique B2C |
|---|---|
| `beginner_summary_v1` | Accessible aux experiences debutant, `public-user`, `free` et `basic` selon la politique produit. |
| `client_interpretation_projection_v1` | Accessible aux clients `free`, `basic` et `premium`; la profondeur narrative depend du plan ou entitlement. |
| `structured_facts_v1` | Base factuelle upstream, pas un dump B2C direct par defaut; exposition client future seulement via champs explicitement autorises par contrat. |
| `narrative_answer_audit_v1` | Interne a l'audit; non client-facing. |

Les projections techniques internes sont interdites aux clients B2C. Sont
notamment exclus: `astrologer_debug_data`, `llm_input`, `ChartObjectRuntimeData`,
`chart_objects`, raw calculation graph payloads, debug traces, prompt internals,
provider internals, audit rows et tout payload de preuve technique non approuve.

## Reponses et erreurs controlees

| Statut | Code contractuel | Condition |
|---|---|---|
| `200` | `projection.ready` | Projection construite sans creation d'un nouvel artefact persiste. |
| `201` | `projection.persisted` | Projection construite et artefact eligible persiste parce que `persist` le permet. |
| `400` | `projection.invalid_chart_source` | `chart_id` et `birth_input` sont tous deux fournis, ou aucun des deux n'est fourni. |
| `401` | `projection.unauthenticated` | Le client B2C n'est pas authentifie. |
| `403` | `projection.unauthorized` | `projection_type` est interdit au client, a son plan ou a ses entitlements. |
| `404` | `projection.chart_not_found` | `chart_id` est inconnu, inaccessible ou n'appartient pas au client authentifie. |
| `409` | `projection.dependency_unavailable` | Le calcul du theme ou le service de projection requis est indisponible. |
| `422` | `projection.invalid_payload` | La forme JSON est invalide, un champ obligatoire manque, ou `projection_version` est unsupported. |

Les indisponibilites de calcul ou de projection sont bloquantes: la future
implementation ne doit pas retourner une projection degradee par fallback
silencieux. Ces issues doivent etre loguees avec un message operationnel
controle, sans fuite de payload brut, trace debug, prompt ou detail fournisseur.

## Politique OpenAPI et runtime

Cette story est OpenAPI-neutral. Tant qu'une story d'implementation separee ne
cree pas explicitement la route, `/v1/astrology/projections` ne doit apparaitre
ni dans `app.routes`, ni dans `app.openapi().paths`, ni dans un client frontend
genere.

Toute implementation future devra reutiliser ce document comme contrat
canonique, prouver les memes exclusions B2C/B2B et conserver un seul chemin
public: `POST /v1/astrology/projections`.
