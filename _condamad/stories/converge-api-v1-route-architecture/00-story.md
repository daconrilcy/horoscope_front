# Story converge-api-v1-route-architecture: Converger l'architecture des routes API v1 par racine HTTP

Status: ready-for-dev

## 1. Objective

Finaliser l'architecture `backend/app/api/v1` pour que chaque routeur actif soit range selon sa
racine HTTP effective, que les helpers transverses de reponse/erreur soient factorises, que
`router_logic` ne contienne plus de routeur FastAPI ni d'import wildcard, et que les imports entre
routeurs soient remplaces par des proprietaires canoniques. Les URLs publiques conservees ne doivent
pas changer.

## 2. Trigger / Source

- Source type: audit
- Source reference: audit Codex du 2026-04-26 sur `backend/app/api/v1` et demande utilisateur
  "rajoute le regroupement par racine egalement".
- Reason for change: la premiere reorganisation a classe les routeurs par domaines, mais l'audit
  releve encore des incoherences entre chemin fichier et racine HTTP, de la duplication d'erreurs,
  des imports croises entre routeurs, des `APIRouter` residuels dans `router_logic`, et des gros
  routeurs difficiles a maintenir.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/api/v1` route architecture
- In scope:
  - Auditer les routeurs, schemas et `router_logic` sous `backend/app/api/v1`.
  - Reconstruire la racine HTTP effective a partir de `include_router(prefix)` dans `main.py`,
    `APIRouter(prefix)` dans le module routeur, et chemin du decorator HTTP.
  - Regrouper les fichiers de routeurs selon leur racine HTTP effective:
    `/v1/admin`, `/v1/ops`, `/v1/b2b`, `/v1/internal`, ou `/v1/*` public.
  - Mettre a jour `backend/app/main.py` pour importer les routeurs depuis leurs chemins canoniques.
  - Creer une abstraction commune de reponse/erreur API v1 si elle remplace au moins deux helpers
    dupliques existants.
  - Centraliser la gestion d'erreur HTTP des routeurs via un modele de classe documente, des
    contrats de payload et des constantes de codes d'erreur dediees.
  - Sortir les constantes partagees des routeurs, schemas et `router_logic` vers des modules
    dedies par domaine API ou module commun.
  - Controler que les schemas API v1 ne dupliquent pas des schemas applicatifs existants et qu'ils
    sont organises par sous-dossier canonique: `admin`, `b2b`, `internal`, `ops`, `public` ou
    module commun justifie.
  - Refactoriser les fichiers API trop lourds
    `backend/app/api/v1/router_logic/admin/llm/prompts.py` et
    `backend/app/api/v1/routers/ops/entitlement_mutation_audits.py` vers des modules plus petits
    et des services centraux.
  - Deporter la logique metier residuelle des fonctions de route vers les couches backend
    canoniques `domain`, `infra` ou `services`.
  - Auditer `backend/app/api` pour sortir les constantes partagees des fichiers applicatifs vers
    des modules dedies.
  - Retirer les `APIRouter` et imports wildcard de `backend/app/api/v1/router_logic`.
  - Remplacer les imports entre routeurs par des imports depuis `schemas`, `router_logic` ou un
    module commun canonique.
  - Ajouter ou renforcer les tests d'architecture qui bloquent les derives de namespace, de racine
    HTTP et d'import.
  - Produire un audit versionne des decisions sous cette story.
- Out of scope:
  - Supprimer ou renommer une URL HTTP active.
  - Modifier le comportement metier des endpoints `billing`, `llm`, `privacy`, `support`,
    `users`, `predictions`, `astrology-engine` ou `astrologers`.
  - Repenser auth, quotas, entitlements, migrations DB, schemas metier ou clients frontend.
  - Decouper integralement les tres gros routeurs si le decoupage n'est pas strictement requis pour
    la convergence de racine ou la suppression d'un import croise.
- Explicit non-goals:
  - Ne pas creer de routes de compatibilite, wrappers, aliases ou re-exports pour les anciens
    chemins Python.
  - Ne pas modifier les prefixes HTTP pour "mieux ranger" les fichiers.
  - Ne pas ajouter de dependance.
  - Ne pas faire de refactor cosmetique hors des fichiers necessaires a cette convergence.
  - Ne pas faire de decoupage fonctionnel de gros routeur sauf si c'est necessaire pour isoler une
    racine HTTP effective ou supprimer un import croise interdit.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: namespace-convergence
- Archetype reason: la story converge les namespaces Python des routeurs, schemas et helpers vers
  une propriete canonique determinee par la racine HTTP effective.
- Behavior change allowed: no
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une URL active devrait etre renommee/supprimee, ou si un module semble
  consomme par une surface externe non prouvee par les tests/scans locaux.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/api/v1/routers/b2b/reconciliation.py` - declare
  `APIRouter(prefix="/v1/ops/b2b/reconciliation")`, donc le fichier vit sous `b2b` mais
  expose une racine `/v1/ops`.
- Evidence 2: `backend/app/api/v1/routers/b2b/entitlement_repair.py` - declare
  `APIRouter(prefix="/v1/ops/b2b/entitlements/repair")`, meme incoherence de racine.
- Evidence 3: `backend/app/api/v1/routers/b2b/entitlements_audit.py` - declare
  `APIRouter(prefix="/v1/ops/b2b/entitlements")`, meme incoherence de racine.
- Evidence 4: `backend/app/api/v1/routers/public/enterprise_credentials.py` - declare
  `APIRouter(prefix="/v1/b2b/credentials")`, donc le fichier vit sous `public` mais expose
  une racine `/v1/b2b`.
- Evidence 5: `backend/app/api/v1/routers/public/email.py` - declare
  `APIRouter(prefix="/email")` et `backend/app/main.py` l'inclut avec `prefix="/api"`, ce qui
  produit une route hors racine v1.
- Evidence 6: `backend/app/api/v1/routers/public/ephemeris.py` - utilise `APIRouter()` sans prefixe
  et declare `@router.get("/v1/ephemeris/status")` dans le decorator.
- Evidence 7: `backend/app/api/v1/router_logic/public/astrologers.py` - contient encore
  `router = APIRouter()` et `from app.api.v1.schemas.routers.public.astrologers import *`.
- Evidence 8: `backend/app/api/v1/router_logic/internal/llm/qa.py` - contient encore
  `router = APIRouter()` et un import wildcard de schemas.
- Evidence 9: `backend/app/api/v1/routers/internal/llm/qa.py` - importe des helpers depuis
  `app.api.v1.routers.public.predictions`, ce qui couple deux routeurs HTTP.
- Evidence 10: `backend/app/api/v1/routers/public/natal_interpretation.py` - importe
  `ErrorEnvelope` depuis `app.api.v1.routers.public.users`.
- Evidence 11: `backend/app/api/v1/schemas/routers/admin/llm/prompts.py` - importe
  `AdminLlmErrorCode` depuis `app.api.v1.routers.admin.llm.error_codes`, donc un schema depend
  d'un routeur.
- Evidence 12: `backend/app/tests/unit/test_api_router_architecture.py` - contient deja des
  garde-fous d'architecture pour les routeurs v1; il doit etre etendu plutot que contourne.

## 6. Target State

After implementation:

- Chaque fichier sous `backend/app/api/v1/routers` vit dans le namespace correspondant a sa racine
  HTTP effective.
- La racine HTTP effective est calculee de facon deterministe avec:
  `include_router(prefix)` + `APIRouter(prefix)` + chemin du decorator.
- `backend/app/main.py` importe les routeurs depuis les chemins canoniques et ne maintient aucun
  alias d'ancien emplacement.
- `router_logic` ne declare plus d'`APIRouter`, n'importe plus `APIRouter`, et n'utilise plus
  d'import wildcard depuis les schemas.
- Les schemas ne dependent plus de modules `routers.*`.
- Les routeurs ne s'importent plus entre eux pour partager helpers, schemas ou constantes; ces
  elements vivent dans un module commun ou dans le namespace canonique non HTTP.
- Les helpers de reponse/erreur dupliques sont remplaces par une abstraction commune API v1.
- Les erreurs HTTP des routeurs utilisent un modele central documente avec constantes de codes
  d'erreur et contrats de payload explicites.
- Les constantes partagees vivent dans des modules dedies, jamais enfouies dans les routeurs quand
  elles sont consommees par plusieurs modules.
- Les schemas API v1 sont inventories, dedupliques contre les schemas applicatifs existants, et
  ranges par sous-dossier canonique.
- Les deux fichiers API les plus lourds cibles sont decomposes sans changement d'URL ni de contrat
  HTTP.
- Les fonctions de route ne portent plus de logique metier: elles resolvent les dependances HTTP,
  valident l'entree, appellent un service central et traduisent la reponse.
- La gestion d'erreur API utilise des classes et de l'heritage pour specialiser les erreurs HTTP,
  les codes documentes et les payloads.
- Les constantes partagees sous `backend/app/api` sont inventoriees et sorties vers des modules
  dedies par domaine ou commun justifie.
- Les tests d'architecture detectent les nouveaux mismatches racine HTTP/fichier, imports croises,
  `APIRouter` dans `router_logic`, imports wildcard, et re-exports de compatibilite.
- Les routes non-v1 sous `backend/app/api/v1` sont des exceptions actives explicitement listees, et
  aucun nouveau cas non-v1 non liste ne peut etre ajoute.

## 6.1. Effective Route Calculation Rule

For each route, the effective OpenAPI path must be reconstructed from the running FastAPI app,
not only from static string scans.

The architecture guard must compare:

- the Python module path owning the router;
- the router object registered in `backend/app/main.py`;
- the final OpenAPI path exposed by `app.openapi()`;
- the expected canonical root declared in `expected_router_roots`.

Static scans are secondary evidence only. The source of truth is the registered FastAPI app.

## 6.2. OpenAPI Baseline Rule

The OpenAPI contract test must store a targeted baseline for moved routes before refactor.

The baseline must include:

- path;
- method;
- tags;
- `operationId` when required;
- declared response status codes.

After refactor, the test must compare the live `app.openapi()` output against this baseline.

## 6.3. Allowlist Strictness Rule

Allowlists must be declarative, narrow and justified.

Each allowlisted registry, import, or non-v1 exception must include:

- exact file path;
- exact symbol or route;
- reason;
- expiry condition or explicit statement that it is a permanent architecture exception.

Wildcard allowlists, directory-wide allowlists and broad regex allowlists are forbidden.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Inventaire routeurs v1 complet par racine HTTP effective calculee. | `rg -n "APIRouter\\(|include_router\\(|@router\\." backend/app`; audit `router-root-audit.md`. |
| AC2 | Aucun fichier `b2b` ou `public` n'expose `/v1/ops/*`. | Arch test; `rg -n "prefix=\"/v1/ops" app/api/v1/routers/b2b app/api/v1/routers/public`. |
| AC3 | Aucun fichier `public` ou `ops` n'expose `/v1/b2b/*`. | Arch test; `rg -n "prefix=\"/v1/b2b" app/api/v1/routers/public app/api/v1/routers/ops`. |
| AC4 | Toute route non-v1 sous `api/v1` est une exception active listee. | `pytest -q app/tests/unit/test_api_router_architecture.py`; scan audit `non-v1`. |
| AC5 | `router_logic` ne contient plus de router FastAPI ni d'import wildcard. | `pytest -q app/tests/unit/test_api_router_architecture.py`; scan `router_logic`. |
| AC6 | Les imports `routers.*` sont elimines hors registries. | `pytest -q app/tests/unit/test_api_router_architecture.py`; `rg -n "app\\.api\\.v1\\.routers" app/api/v1`. |
| AC7 | Le helper commun d'erreur conserve JSON, status, headers et `request_id`. | `pytest -q app/tests/integration/test_api_v1_router_contracts.py`; scan `_error_response`. |
| AC8 | `backend/app/main.py` utilise les chemins canoniques. | `pytest -q app/tests/unit/test_api_router_architecture.py`; scan des anciens imports. |
| AC9 | Les routes deplacees gardent le contrat OpenAPI avant/apres. | `pytest -q app/tests/integration/test_api_v1_router_contracts.py`; snapshot OpenAPI cible. |
| AC10 | Lint et tests backend cibles passent dans le venv Windows. | `ruff format .`; `ruff check .`; `pytest -q app/tests/unit/test_api_router_architecture.py`. |
| AC11 | Les anciens chemins Python deplaces ne sont plus importables. | `pytest -q app/tests/unit/test_api_router_architecture.py`; scans anciens chemins. |
| AC12 | Les `operationId` restent stables si un client genere les consomme. | `pytest -q app/tests/integration/test_api_v1_router_contracts.py`; audit clients generes. |
| AC13 | Les erreurs HTTP des routeurs passent par un modele central documente. | `pytest -q app/tests/unit/test_api_router_architecture.py`; tests erreur routeurs migres. |
| AC14 | Les constantes partagees vivent dans des modules dedies et documentes. | `pytest -q app/tests/unit/test_api_router_architecture.py`; scan constantes dans routeurs. |
| AC15 | Les schemas API v1 sont dedupliques et ranges par sous-dossier canonique. | `pytest -q app/tests/unit/test_api_router_architecture.py`; audit `schema-audit.md`. |
| AC16 | `router_logic/admin/llm/prompts.py` est decoupe par responsabilite. | `pytest -q app/tests/unit/test_api_router_architecture.py`; tests admin LLM cibles. |
| AC17 | `routers/ops/entitlement_mutation_audits.py` est decoupe par responsabilite. | `pytest -q app/tests/unit/test_api_router_architecture.py`; tests ops entitlements cibles. |
| AC18 | Les routeurs ne contiennent plus de logique metier non HTTP. | `pytest -q app/tests/unit/test_api_router_architecture.py`; audit service-boundary. |
| AC19 | Les constantes partagees sous `backend/app/api` sont centralisees. | `pytest -q app/tests/unit/test_api_router_architecture.py`; audit `api-constants-audit.md`. |

AC6 allowlist detail: seuls `backend/app/main.py`, les `__init__.py` et les registries
explicitement allowlistes peuvent importer des routeurs.

AC12 evidence detail: l'audit doit lister les chemins inspectes pour les clients generes et le
resultat du scan; le snapshot OpenAPI compare strictement les `operationId` si un client genere est
detecte.

AC13 inheritance detail: la centralisation des erreurs doit utiliser une classe de base et des
classes specialisees par famille d'erreurs HTTP ou domaine API. Les routeurs ne doivent plus
construire manuellement des payloads d'erreur sauf exception allowlistee et justifiee.

## 8. Implementation Tasks

- [ ] Task 1 - Produire l'audit racine HTTP avant modification (AC: AC1, AC4, AC11, AC12)
  - [ ] Subtask 1.1 - Lister chaque `include_router`, chaque `APIRouter(prefix=VALUE)`, chaque
    decorator `@router.get/post/put/patch/delete`, et reconstruire les chemins OpenAPI finaux.
  - [ ] Subtask 1.2 - Classer chaque routeur dans une racine effective: `/v1/admin`, `/v1/ops`,
    `/v1/b2b`, `/v1/internal`, `/v1/public-resource`, ou `non-v1`.
  - [ ] Subtask 1.3 - Ecrire `_condamad/stories/converge-api-v1-route-architecture/router-root-audit.md`
    avec chemin actuel, prefixe HTTP, chemin canonique cible, decision et risque.
  - [ ] Subtask 1.4 - Pour chaque route non-v1 sous `api/v1`, renseigner path OpenAPI exact,
    raison historique et decision: `kept-as-active-exception`, `moved-without-url-change`, ou
    `blocker-user-decision`.
  - [ ] Subtask 1.5 - Auditer les clients generes ou leur absence pour determiner si les
    `operationId` doivent etre strictement compares.

- [ ] Task 2 - Ecrire les gardes d'architecture en echec avant refactor (AC: AC2, AC3, AC4, AC5, AC6, AC11)
  - [ ] Subtask 2.1 - Ajouter les nouveaux tests d'architecture sans deplacer encore les fichiers.
  - [ ] Subtask 2.2 - Executer `pytest -q app/tests/unit/test_api_router_architecture.py` sur
    l'etat actuel et conserver la preuve des echecs attendus.
  - [ ] Subtask 2.3 - Verifier que les echecs prouvent les derives visees: racine HTTP mal rangee,
    `APIRouter` dans `router_logic`, imports wildcard ou imports croises interdits.
  - [ ] Subtask 2.4 - Ne commencer les deplacements/refactors qu'apres cette preuve d'echec.

- [ ] Task 3 - Converger les fichiers vers leur namespace de racine HTTP (AC: AC2, AC3, AC4, AC8, AC9, AC11, AC12)
  - [ ] Subtask 3.1 - Deplacer les routeurs `/v1/ops/b2b/*` depuis `routers/b2b` vers
    `routers/ops/b2b`.
  - [ ] Subtask 3.2 - Deplacer le routeur `/v1/b2b/credentials` depuis `routers/public` vers
    `routers/b2b/credentials.py`.
  - [ ] Subtask 3.3 - Documenter et garder explicitement les exceptions `non-v1` si elles restent
    intentionnelles; ne pas changer leur URL dans cette story.
  - [ ] Subtask 3.4 - Mettre a jour `backend/app/main.py`, les imports de tests et les chemins de
    patch vers les namespaces canoniques.
  - [ ] Subtask 3.5 - Prouver par scan que les anciens chemins de modules deplaces ne sont plus
    references dans `backend`, `_condamad`, `scripts`, `docs` et `frontend`.

- [ ] Task 4 - Nettoyer `router_logic` comme couche non HTTP (AC: AC5, AC7)
  - [ ] Subtask 4.1 - Supprimer les declarations `router = APIRouter()` et imports `APIRouter`
    de `backend/app/api/v1/router_logic`.
  - [ ] Subtask 4.2 - Remplacer chaque import wildcard de schema par des imports explicites ou par
    un deplacement du type vers le module qui en a besoin.
  - [ ] Subtask 4.3 - Inventorier les `_error_response` remplaces avec leur payload JSON actuel,
    status code, headers utiles et usage de `request_id`.
  - [ ] Subtask 4.4 - Creer ou reutiliser un helper commun de reponse API v1 uniquement si deux
    duplications reelles minimum sont prouvees.
  - [ ] Subtask 4.5 - Ajouter des tests qui comparent exactement les erreurs avant/apres sur au
    moins deux routes migrees.

- [ ] Task 5 - Centraliser erreurs HTTP, constantes et contrats (AC: AC7, AC13, AC14)
  - [ ] Subtask 5.1 - Inventorier les helpers d'erreur, codes d'erreur HTTP, messages constants et
    constantes partagees dans `routers`, `router_logic` et `schemas`.
  - [ ] Subtask 5.2 - Creer un module canonique pour le modele de classe d'erreur HTTP routeur,
    les contrats de payload et les constantes de codes d'erreur documentees.
  - [ ] Subtask 5.2a - Mettre en place une classe de base d'erreur API et des sous-classes par
    famille HTTP ou domaine API; interdire les payloads manuels concurrents dans les routeurs.
  - [ ] Subtask 5.3 - Deplacer les constantes partagees vers des modules dedies par domaine API ou
    module commun justifie, avec commentaire global en francais.
  - [ ] Subtask 5.4 - Adapter les routeurs migres pour utiliser le modele central sans changer le
    JSON, le status code, les headers utiles ou le `request_id`.
  - [ ] Subtask 5.5 - Ajouter un garde qui echoue si une constante partagee reste definie dans un
    routeur alors qu'elle est consommee hors du fichier.

- [ ] Task 6 - Controler et organiser les schemas API v1 (AC: AC6, AC15)
  - [ ] Subtask 6.1 - Produire `_condamad/stories/converge-api-v1-route-architecture/schema-audit.md`
    avec chaque schema API v1, son domaine, ses consommateurs et ses doublons potentiels.
  - [ ] Subtask 6.2 - Comparer les schemas API v1 avec les schemas applicatifs existants sous
    `backend/app` pour eviter de recreer un contrat deja disponible.
  - [ ] Subtask 6.3 - Ranger les schemas par sous-dossier canonique `admin`, `b2b`, `internal`,
    `ops`, `public` ou `common` justifie.
  - [ ] Subtask 6.4 - Ajouter un garde qui interdit les nouveaux schemas hors organisation
    canonique ou les duplications nominales non justifiees dans l'audit.

- [ ] Task 7 - Refactoriser les gros fichiers API cibles (AC: AC16, AC17, AC18)
  - [ ] Subtask 7.1 - Auditer les responsabilites de
    `backend/app/api/v1/router_logic/admin/llm/prompts.py`: catalog, personas, schemas, use cases,
    prompt history, replay, observability et helpers.
  - [ ] Subtask 7.2 - Extraire les responsabilites de `prompts.py` vers modules non HTTP dedies,
    en reutilisant `domain`, `infra` et `services` avant tout nouveau helper API.
  - [ ] Subtask 7.3 - Auditer les responsabilites de
    `backend/app/api/v1/routers/ops/entitlement_mutation_audits.py`: listes, details, reviews,
    retries, suppressions, batch actions et alertes.
  - [ ] Subtask 7.4 - Extraire la logique metier du routeur ops vers des services centraux; le
    routeur doit rester une couche HTTP fine.
  - [ ] Subtask 7.5 - Ajouter des gardes de taille/responsabilite pour ces deux fichiers ou
    documenter une limite mesurable dans l'audit.

- [ ] Task 8 - Sortir la logique metier des routeurs API (AC: AC18)
  - [ ] Subtask 8.1 - Auditer les fonctions de route sous `backend/app/api` qui contiennent des
    decisions metier, requetes complexes, mutations d'etat ou orchestration lourde.
  - [ ] Subtask 8.2 - Deplacer cette logique vers `backend/app/services`, `backend/app/domain` ou
    `backend/app/infra` selon sa responsabilite.
  - [ ] Subtask 8.3 - Garder dans les routeurs uniquement dependances FastAPI, parsing HTTP, appel
    service, mapping erreur/reponse et status code.
  - [ ] Subtask 8.4 - Ajouter un garde ou audit `service-boundary-audit.md` listant les exceptions
    restantes avec justification et decision utilisateur si necessaire.

- [ ] Task 9 - Auditer et centraliser les constantes API (AC: AC14, AC19)
  - [ ] Subtask 9.1 - Produire `_condamad/stories/converge-api-v1-route-architecture/api-constants-audit.md`
    couvrant `backend/app/api`.
  - [ ] Subtask 9.2 - Deplacer les constantes partagees vers des modules dedies par domaine API ou
    `backend/app/api/v1/constants.py` seulement si le partage traverse plusieurs domaines.
  - [ ] Subtask 9.3 - Ajouter un garde qui interdit une constante partagee dans un routeur,
    schema ou fichier de logique si elle est importee ailleurs.

- [ ] Task 10 - Casser les imports entre routeurs (AC: AC6, AC7, AC9)
  - [ ] Subtask 10.1 - Deplacer `AdminLlmErrorCode` hors `routers/admin/llm/error_codes.py` vers un
    module non HTTP canonique si des schemas l'utilisent.
  - [ ] Subtask 10.2 - Deplacer `ErrorEnvelope` partage vers un schema commun plutot que l'importer
    depuis `routers/public/users.py`.
  - [ ] Subtask 10.3 - Deplacer les helpers partages de `routers/public/predictions.py` vers
    `router_logic/public/predictions.py` ou un service non HTTP.
  - [ ] Subtask 10.4 - Verifier qu'aucun schema ni `router_logic` ne depend de `routers.*`.

- [ ] Task 11 - Finaliser les gardes d'architecture (AC: AC2, AC3, AC4, AC5, AC6, AC8, AC11, AC13, AC14, AC15, AC16, AC17, AC18, AC19)
  - [ ] Subtask 11.1 - Ajouter une matrice declarative `expected_router_roots` dans le test
    d'architecture, avec ancien chemin interdit, chemin canonique attendu, racine effective attendue
    et statut d'exception eventuel.
  - [ ] Subtask 11.2 - Ajouter un garde qui interdit `APIRouter` et `import *` dans `router_logic`.
  - [ ] Subtask 11.3 - Ajouter un garde qui interdit les imports entre routeurs hors namespaces
    `__init__.py`, `backend/app/main.py` et registries explicitement autorises.
  - [ ] Subtask 11.4 - Ajouter un garde qui echoue si un ancien chemin de module migre reste
    importable ou reference.
  - [ ] Subtask 11.5 - Ajouter un garde qui interdit toute nouvelle route non-v1 sous `api/v1` si
    elle n'est pas dans la matrice d'exceptions.
  - [ ] Subtask 11.6 - Interdire les allowlists wildcard, par dossier complet, ou par regex large;
    chaque exception doit lister fichier exact, symbole ou route, raison et condition d'expiration.
  - [ ] Subtask 11.7 - Ajouter des gardes pour erreurs HTTP centralisees, constantes dediees et
    organisation des schemas.
  - [ ] Subtask 11.8 - Ajouter des gardes ou audits pour limites de responsabilite des deux gros
    fichiers cibles et absence de logique metier dans les routeurs.

- [ ] Task 12 - Valider le contrat HTTP conserve (AC: AC9, AC10, AC12, AC13)
  - [ ] Subtask 12.1 - Generer une baseline OpenAPI cible avant refactor pour les routeurs deplaces:
    paths, methods, tags, status principaux et `operationId` si requis.
  - [ ] Subtask 12.2 - Comparer apres refactor le `app.openapi()` live contre cette baseline cible.
  - [ ] Subtask 12.3 - Executer lint, tests d'architecture, tests OpenAPI et tests cibles des routes
    deplacees.
  - [ ] Subtask 12.4 - Documenter tout test non execute et son risque residuel dans le recap de dev.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/api/v1/router_logic` pour la logique non HTTP deja extraite.
  - `backend/app/api/v1/schemas` et `backend/app/api/v1/schemas/routers` pour les contrats Pydantic.
  - Les schemas applicatifs existants sous `backend/app` avant toute creation de schema API v1
    equivalent.
  - `backend/app/tests/unit/test_api_router_architecture.py` comme garde existant a etendre.
  - `app.core.request_id.resolve_request_id` pour la meta `request_id`.
  - Les services existants sous `backend/app/services`, `backend/app/domain` et `backend/app/infra`
    avant toute extraction supplementaire.
- Do not recreate:
  - Un helper d'erreur par routeur quand une forme commune existe.
  - Une nouvelle constante dans un routeur si elle est consommee par plusieurs modules.
  - Des schemas identiques dans plusieurs namespaces.
  - Des wrappers Python conservant l'ancien chemin apres deplacement.
  - Une seconde convention de classement par domaine qui contredit la racine HTTP effective.
  - Un helper commun qui modifie la forme JSON, le status code, les headers utiles ou le
    `request_id` des erreurs existantes.
  - Une logique metier locale dans un routeur quand un service/domain/infra peut l'heberger.
- Shared abstraction allowed only if:
  - Elle remplace une duplication prouvee dans au moins deux routeurs actifs.
  - Elle ne change pas la forme JSON des reponses existantes.
  - Elle vit dans un module non HTTP de `backend/app/api/v1` ou dans un module core deja approprie.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `router = APIRouter(` inside `backend/app/api/v1/router_logic`
- `from app.api.v1.schemas.any_module import *`
- `from app.api.v1.routers.public.predictions import` outside router registration namespaces
- `from app.api.v1.routers.public.users import ErrorEnvelope`
- `from app.api.v1.routers.admin.llm.error_codes import AdminLlmErrorCode` from schemas
- shared constants defined in router files when imported elsewhere
- duplicated API schemas with equivalent fields and semantics in another schema module
- business decisions, DB orchestration or domain rules embedded directly in route handlers
- large mixed-responsibility API files after refactor of the two targeted files
- `/v1/ops` prefixes under `backend/app/api/v1/routers/b2b`
- `/v1/b2b` prefixes under `backend/app/api/v1/routers/public`
- new non-v1 route under `backend/app/api/v1` when absent from `expected_router_roots`
- Re-export modules whose only purpose is preserving an old Python import path.

## 11. Removal Classification Rules

- Removal classification: not applicable

This story does not remove active HTTP routes. Deletion is limited to obsolete Python namespace
wrappers, duplicate private helpers, or local declarations proven replaced by canonical modules.
If an active URL would need removal or rename, stop and request a user decision.

## 12. Removal Audit Format

- Removal audit: not applicable

Required architecture audit table:

| Item | Current path | Router prefix | Main prefix | Decorator path | OpenAPI path | Effective root | Canonical path | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|---|---|

Audit output path:

- `_condamad/stories/converge-api-v1-route-architecture/router-root-audit.md`
- `_condamad/stories/converge-api-v1-route-architecture/schema-audit.md`
- `_condamad/stories/converge-api-v1-route-architecture/api-constants-audit.md`
- `_condamad/stories/converge-api-v1-route-architecture/service-boundary-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Admin API v1 routes | `backend/app/api/v1/routers/admin/**` for `/v1/admin/**` | any `/v1/admin` router outside `routers/admin` |
| Ops API v1 routes | `backend/app/api/v1/routers/ops/**` for `/v1/ops/**` | `/v1/ops/b2b/**` files under `routers/b2b` |
| B2B public/client API v1 routes | `backend/app/api/v1/routers/b2b/**` for `/v1/b2b/**` | `/v1/b2b/credentials` under `routers/public` |
| Internal API v1 routes | `backend/app/api/v1/routers/internal/**` for `/v1/internal/**` | any `/v1/internal` router outside `routers/internal` |
| Public/user API v1 routes | `backend/app/api/v1/routers/public/**` for public `/v1/{resource}` routes | public files exposing admin/ops/b2b/internal roots |
| Shared API v1 responses | `backend/app/api/v1/responses.py` or equivalent canonical non-HTTP module | repeated `_error_response` helpers |
| Shared schemas | `backend/app/api/v1/schemas/**` | schemas importing from `routers.*` |
| Shared constants | `backend/app/api/v1/constants.py` or domain constants module | constants shared from routers or schemas |
| HTTP router errors | API v1 error model and code constants module | ad hoc `_error_response` variants per router |
| Business logic | `backend/app/services`, `backend/app/domain`, `backend/app/infra` | decisions or orchestration inside route handlers |
| Non-HTTP router helpers | `backend/app/api/v1/router_logic/**` | `APIRouter` or wildcard schema imports inside `router_logic` |

## 14. Delete-Only Rule

Items classified as obsolete Python namespace artifacts must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

This rule applies only to Python namespaces/helpers, not to active HTTP URLs.

## 15. External Usage Blocker

If a moved module path is referenced by external docs, generated clients, operational scripts, or
non-test tooling, do not preserve it through a shim. Stop and record:

- the exact external evidence;
- the deletion or move risk;
- the canonical path proposed;
- the user decision required.

## 16. Reintroduction Guard

The implementation must add or update architecture guards that fail if drift returns.

The guard must check:

- registered router prefixes against canonical file roots;
- effective roots reconstructed from `main.py` prefix, `APIRouter` prefix, and decorator path;
- live FastAPI `app.openapi()` paths as source of truth for effective route ownership;
- `APIRouter` usage inside `router_logic`;
- wildcard imports inside `router_logic`;
- imports from `app.api.v1.routers.*` inside schemas and router logic;
- shared constants defined in routeur files and imported outside the same file;
- duplicated schemas or schemas outside canonical folder organization;
- ad hoc router error helpers where the centralized model should be used;
- route handlers containing business decisions, direct multi-step orchestration, or complex DB logic;
- the two targeted large files exceeding the agreed responsibility boundary after refactor;
- imports from old moved module paths in backend app/tests;
- external references to old moved module paths in `_condamad`, `scripts`, `docs` and `frontend`;
- non-v1 routes under `backend/app/api/v1` unless explicitly listed;
- OpenAPI paths for route presence after module moves.
- exact allowlist entries only; no wildcard, directory-wide, or broad regex allowlists.

Required forbidden examples:

- `backend/app/api/v1/routers/b2b/reconciliation.py` exposing `/v1/ops/b2b/reconciliation`
- `backend/app/api/v1/routers/public/enterprise_credentials.py` exposing `/v1/b2b/credentials`
- `router = APIRouter(` in `backend/app/api/v1/router_logic`
- `from app.api.v1.schemas.routers.public.astrologers import *`
- `from app.api.v1.routers.public.predictions import`
- shared constants imported from router modules
- local business logic in route handlers instead of central services
- duplicated schema names or equivalent schema fields outside justified `common` ownership

## 17. Generated Contract Check

Required generated-contract evidence:

- A targeted OpenAPI baseline for moved routes must be captured before refactor.
- FastAPI OpenAPI paths for moved routers must still include the same URL paths and methods.
- OpenAPI tags for moved routers must remain the same unless the audit records a deliberate,
  reviewed tag correction.
- OpenAPI `operationId` values for moved routes must remain stable when a generated client exists.
- Response status codes declared in OpenAPI for moved routes must remain stable unless the audit
  records a deliberate correction.
- No generated frontend/backend contract should reference old Python module paths.

If no generated client exists for a route, the implementation evidence must record that and use the
OpenAPI path/method/tag/status assertion plus targeted integration tests as replacement evidence.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/main.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/app/api/v1/routers/b2b/reconciliation.py`
- `backend/app/api/v1/routers/b2b/entitlement_repair.py`
- `backend/app/api/v1/routers/b2b/entitlements_audit.py`
- `backend/app/api/v1/routers/public/enterprise_credentials.py`
- `backend/app/api/v1/routers/public/email.py`
- `backend/app/api/v1/routers/public/ephemeris.py`
- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/api/v1/router_logic/public/astrologers.py`
- `backend/app/api/v1/router_logic/internal/llm/qa.py`
- `backend/app/api/v1/schemas/routers/admin/llm/prompts.py`
- `backend/app/api/v1/schemas/routers/admin/llm/assemblies.py`
- `backend/app/api/v1/schemas/routers/admin/llm/sample_payloads.py`
- `backend/app/api/v1/router_logic/admin/llm/prompts.py`
- `backend/app/api/v1/routers/ops/entitlement_mutation_audits.py`
- `backend/app/services`
- `backend/app/domain`
- `backend/app/infra`

## 19. Expected Files to Modify

Likely files:

- `_condamad/stories/converge-api-v1-route-architecture/router-root-audit.md` - audit racine.
- `backend/app/main.py` - imports et inclusions depuis chemins canoniques.
- `backend/app/api/v1/responses.py` - helper commun de reponse/erreur si le nom est retenu.
- `backend/app/api/v1/errors.py` - modele central d'erreur HTTP routeur si le nom est retenu.
- `backend/app/api/v1/constants.py` - constantes communes si un module commun est justifie.
- `backend/app/api/v1/schemas/common.py` - schemas partages si un module commun est justifie.
- `backend/app/api/v1/router_logic/admin/llm/**` - modules plus petits pour responsabilites LLM admin.
- `backend/app/api/v1/routers/ops/entitlement_mutation_audits.py` - routeur aminci.
- `backend/app/services/**` - services centraux pour logique metier extraite si necessaire.
- `backend/app/domain/**` - regles metier extraites si necessaire.
- `backend/app/infra/**` - acces techniques extraits si necessaire.
- `backend/app/api/v1/routers/ops/b2b/reconciliation.py` - nouveau chemin canonique du routeur ops B2B.
- `backend/app/api/v1/routers/ops/b2b/entitlement_repair.py` - nouveau chemin canonique du routeur ops B2B.
- `backend/app/api/v1/routers/ops/b2b/entitlements_audit.py` - nouveau chemin canonique du routeur ops B2B.
- `backend/app/api/v1/routers/b2b/credentials.py` - nouveau chemin canonique du routeur credentials B2B.
- `backend/app/api/v1/router_logic/**` - suppression `APIRouter`, imports wildcard, helpers dupliques.
- `backend/app/api/v1/schemas/**` - deplacement des constantes/schemas partages hors routeurs.
- `backend/app/tests/unit/test_api_router_architecture.py` - gardes de convergence.

Likely tests:

- `backend/app/tests/unit/test_api_router_architecture.py` - garde racine/import/router_logic.
- `backend/app/tests/unit/test_api_error_contracts.py` - contrat du modele d'erreur si cree.
- Tests admin LLM et ops entitlements existants - regression des deux gros fichiers refactorises.
- `backend/app/tests/integration/test_api_v1_router_contracts.py` - contrat OpenAPI des routes deplacees, si ce fichier existe ou est cree.
- Snapshot cible genere par le test de contrat - comparaison before/after des paths, methods, tags,
  status principaux et `operationId` si requis.
- Tests d'integration existants couvrant `b2b`, `ops`, `enterprise_credentials`, `internal/llm/qa`,
  `natal_interpretation` et `predictions` lorsque leurs imports de patch changent.

Files not expected to change:

- `backend/pyproject.toml` - aucune dependance nouvelle.
- `frontend/package.json` - aucune dependance frontend nouvelle.
- `backend/alembic` - aucune migration DB attendue.
- `backend/app/infra/db/models` - aucun modele DB ne doit changer.
- `frontend/src` - aucun changement attendu sauf si un test backend prouve un chemin de patch/documentation
  first-party a mettre a jour; dans ce cas documenter le risque.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_api_router_architecture.py
pytest -q app/tests/unit/test_api_error_contracts.py
pytest -q app/tests/integration/test_api_v1_router_contracts.py
pytest -q app/tests/integration/test_enterprise_credentials_api.py
pytest -q app/tests/integration/test_llm_qa_router.py
pytest -q app/tests/integration/test_daily_prediction_api.py
pytest -q app/tests/integration/test_ops_entitlement_mutation_audits_api.py
rg -n "prefix=\"/v1/ops" app/api/v1/routers/b2b app/api/v1/routers/public
rg -n "prefix=\"/v1/b2b" app/api/v1/routers/public app/api/v1/routers/ops
rg -n "APIRouter|import \\*" app/api/v1/router_logic
rg -n "from app\\.api\\.v1\\.routers\\." app/api/v1/schemas app/api/v1/router_logic app/api/v1/routers
rg -n "^[A-Z][A-Z0-9_]+\\s*=" app/api/v1/routers app/api/v1/router_logic app/api/v1/schemas
rg -n "class .*Error|def _error_response|JSONResponse\\(" app/api/v1
rg -n "select\\(|db\\.execute\\(|db\\.commit\\(|db\\.rollback\\(" app/api/v1/routers
rg -n "app\\.api\\.v1\\.routers\\.public\\.enterprise_credentials" ../backend ../_condamad ../scripts ../docs ../frontend
rg -n "app\\.api\\.v1\\.routers\\.b2b\\.(reconciliation|entitlement_repair|entitlements_audit)" ../backend ../_condamad ../scripts ../docs ../frontend
cd ..
```

Expected negative scans must return no result, except for documented `__init__.py` router registry
imports, `backend/app/main.py`, and registries explicitly allowed by the architecture guard. If a
listed test file does not exist, create the narrowest equivalent test or record the skip and
residual risk.

For the `from app.api.v1.routers.` scan, any remaining result must belong exclusively to
`backend/app/main.py`, `__init__.py`, or an explicitly documented registry allowlist. Any other
result is a failure.

## 22. Regression Risks

- Risk: casser un import de test qui patchait l'ancien chemin Python.
  - Guardrail: mettre a jour les patch paths vers le proprietaire canonique et ajouter un garde qui
    interdit l'ancien chemin.
- Risk: changer involontairement une URL ou un tag OpenAPI en deplacant un fichier.
  - Guardrail: test OpenAPI ciblant path, methode et tag avant/apres.
- Risk: creer un helper commun trop generique.
  - Guardrail: accepter uniquement une abstraction qui remplace une duplication prouvee dans au
    moins deux routeurs actifs.
- Risk: creer une hierarchie de schemas trop locale ou dupliquer un schema applicatif deja existant.
  - Guardrail: schema audit obligatoire et garde d'organisation par sous-dossier canonique.
- Risk: deplacer des constantes vers un module commun trop large.
  - Guardrail: module dedie par domaine d'abord; module commun uniquement si au moins deux domaines
    API l'utilisent.
- Risk: confondre route publique B2B et route ops B2B.
  - Guardrail: la racine HTTP effective prime sur le theme metier secondaire.
- Risk: garder des exceptions `non-v1` invisibles.
  - Guardrail: les exceptions doivent apparaitre dans l'audit et dans le garde d'architecture.

## 23. Dev Agent Instructions

- Implement only this story.
- Commencer par ajouter les nouveaux tests d'architecture et les faire echouer sur l'etat actuel;
  conserver la preuve de ces echecs attendus avant tout deplacement/refactor.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Ne pas supprimer ou renommer une URL HTTP active dans cette story.
- Ne pas faire de decoupage fonctionnel de routeur sauf si c'est necessaire pour isoler une racine
  HTTP effective ou supprimer un import croise interdit.
- Ne pas classer une route non-v1 comme exception sans path OpenAPI exact, preuve d'activite,
  raison historique et garde anti-ajout.
- Ne pas creer un schema API v1 sans verifier l'existence d'un schema applicatif equivalent.
- Ne pas laisser une constante partagee dans un routeur ou un schema si elle est consommee par un
  autre module.
- Respecter l'activation du venv avant toute commande Python: `.\.venv\Scripts\Activate.ps1`.
- Ne pas creer de `requirements.txt`; `backend/pyproject.toml` reste la source unique.
- Tout fichier applicatif nouveau ou significativement modifie doit contenir un commentaire global
  en francais et des docstrings en francais pour les fonctions publiques ou non triviales.
- Ne pas ajouter de dossier de base dans `backend/` hors sous-dossiers deja presents sous
  `backend/app/api/v1`.

## 24. References

- `backend/app/api/v1/routers` - routeurs HTTP v1 a converger.
- `backend/app/api/v1/router_logic` - logique non HTTP a garder sans FastAPI router.
- `backend/app/api/v1/schemas` - proprietaire canonique des schemas et enveloppes partagees.
- `backend/app/main.py` - registre FastAPI actif.
- `backend/app/tests/unit/test_api_router_architecture.py` - garde d'architecture existant.
- `_condamad/stories/refactor-api-v1-routers/00-story.md` - story precedente de reorganisation.
- `_condamad/stories/refactor-api-v1-routers/router-audit.md` - audit precedent a reutiliser.
