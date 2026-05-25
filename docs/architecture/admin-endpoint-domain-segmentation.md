<!-- Commentaire global: ce document definit la segmentation cible des endpoints admin par domaine sans changer les routes existantes. -->

# Admin Endpoint Domain Segmentation

## Objectif

Ce contrat fixe la segmentation cible des endpoints admin entre les familles `business`, `technical` et `astrology`. Il sert de reference pour
les prochaines stories d'API admin et complete la matrice CS-271 sans activer de nouveaux roles runtime, sans refactorer les routes actuelles
et sans exposer de nouvelles donnees aux clients.

Etat operationnel courant:

- `ADMIN` reste le seul role operationnel pour les surfaces admin existantes.
- `MARKETER`, `TECHNO` et `ASTRO_EXPERT` sont des roles cibles issus de CS-271 et restent non actifs tant qu'une story RBAC dediee n'est pas
  livree.
- Les prefixes actuels `/v1/admin/...` restent inchanges; ce document classe les familles, il ne les deplace pas.
- Les contrats OpenAPI internes admin restent separes de l'OpenAPI client public definie par CS-266.

## Familles de routes admin

| domain_family | route_family | target_roles | current_access_state | logging_rule | openapi_visibility | client_exclusion | source_dependency |
|---|---|---|---|---|---|---|---|
| `business` | `/v1/admin/dashboard`, `/v1/admin/users`, `/v1/admin/entitlements`, `/v1/admin/exports`, `/v1/admin/support` | `ADMIN` actif; `MARKETER` cible non actif | Acces admin existant, roles cibles refuses | Journaliser `actor`, `route_family`, `action`, `correlation_id` pour export, modification, support et revelation de donnees | `internal-admin`; non promu dans un contrat client public | Aucune route client ne doit exposer exports admin, donnees de facturation completes, gestes commerciaux ou support interne | CS-271, CS-266 |
| `technical` | `/v1/admin/ai`, `/v1/admin/logs`, `/v1/admin/llm`, `/v1/admin/llm/observability`, `/v1/admin/llm/sample-payloads`, `/v1/admin/llm/consumption`, `/v1/admin/llm/assembly`, `/v1/admin/llm/releases` | `ADMIN` actif; `TECHNO` cible non actif | Acces admin existant, roles cibles refuses | Journaliser `actor`, `route_family`, `action`, `correlation_id` pour trace, replay, prompt, release, payload et diagnostic | `internal-technical`; jamais ajoute a l'OpenAPI client public | Les endpoints client sont exclus de `debug`, `replay`, `trace`, `prompt` et donnees runtime techniques completes | CS-271, CS-266 |
| `astrology` | `/v1/admin/content`, `/v1/admin/pdf-templates`, `/v1/admin/answer-audits`, `/v1/admin/audit` | `ADMIN` actif; `ASTRO_EXPERT` cible non actif | Acces admin existant, roles cibles refuses | Journaliser `actor`, `route_family`, `action`, `correlation_id` pour correction, audit, publication, rejet et revue experte | `internal-admin`; schemas internes non publies comme contrat client | Les endpoints client sont exclus des surfaces d'audit, debug, replay, trace, prompt et full astrology runtime | CS-271, CS-266 |

## Regles de rattachement aux roles CS-271

- La famille `business` consomme la matrice CS-271 pour les besoins futurs `MARKETER`, mais aucun acces courant n'est accorde a ce role.
- La famille `technical` consomme la matrice CS-271 pour les besoins futurs `TECHNO`, mais aucun acces courant n'est accorde a ce role.
- La famille `astrology` consomme la matrice CS-271 pour les besoins futurs `ASTRO_EXPERT`, mais aucun acces courant n'est accorde a ce role.
- Toute ouverture d'un role cible exige une story RBAC separee, des tests d'autorisation et des logs d'audit dedies.

## Regles OpenAPI interne

- `OpenAPI interne` des familles admin: les routes `/v1/admin/...` peuvent rester visibles dans l'application FastAPI courante, mais elles sont
  classees comme contrats `internal-admin` ou `internal-technical`.
- L'OpenAPI client public ne doit pas devenir le support de publication des schemas internes de debug, replay, trace, prompt ou runtime
  astrologique complet.
- `app.openapi()` est la source de verification runtime pour prouver l'absence de projections internes publiques, conformement a CS-266.
- Toute publication volontaire d'un contrat admin separe doit utiliser un artefact explicite et ne doit pas reutiliser silencieusement le contrat
  client.

## Regles de logging sensible

Les familles admin sensibles doivent produire ou preparer un journal d'acces contenant au minimum:

- `actor`: identite technique ou utilisateur interne ayant declenche l'action.
- `route_family`: famille admin segmentee, par exemple `business`, `technical` ou `astrology`.
- `action`: lecture, recherche, export, correction, replay, publication, rejet ou diagnostic.
- `correlation_id`: identifiant de correlation pour relier requete, audit et incident.

Ces champs ne changent pas le comportement actuel dans cette story. Ils definissent le minimum attendu pour les futures implementations.

## Exclusions client

- Aucun endpoint client ne doit partager une surface admin de `debug`, `replay`, `trace`, `prompt` ou full astrology runtime.
- Les donnees de naissance, prompts, payloads bruts, traces d'execution, snapshots de replay et diagnostics astrologiques admin restent hors
  contrat client.
- Les endpoints client peuvent exposer des projections produit controlees, mais jamais les surfaces internes permettant de rejouer, diagnostiquer
  ou auditer l'execution complete.

## Hors perimetre

Ce contrat ne refactore aucun endpoint, ne renomme aucune route, n'active pas `MARKETER`, `TECHNO` ou `ASTRO_EXPERT`, ne cree pas d'ecran admin,
ne modifie pas l'authentification, ne cree pas de migration, n'ajoute pas de replay et ne change pas les schemas OpenAPI existants.
