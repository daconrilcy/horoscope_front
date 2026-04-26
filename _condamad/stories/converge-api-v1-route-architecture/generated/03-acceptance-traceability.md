# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Inventaire routeurs v1 complet par racine HTTP effective calculee. | Audit `router-root-audit.md` et garde OpenAPI cible. | Scan `APIRouter/include_router/@router.`; audit versionne. | PASS |
| AC2 | Aucun fichier `b2b` ou `public` n'expose `/v1/ops/*`. | Routeurs ops B2B deplaces sous `routers/ops/b2b`. | Test architecture + scan `prefix="/v1/ops"` sous `routers/b2b` et `routers/public`. | PASS |
| AC3 | Aucun fichier `public` ou `ops` n'expose `/v1/b2b/*`. | Credentials B2B deplace sous `routers/b2b/credentials.py`. | Test architecture + scan `prefix="/v1/b2b"` sous `routers/public` et `routers/ops`. | PASS |
| AC4 | Toute route non-v1 sous `api/v1` est une exception active listee. | Matrice `NON_V1_ROUTE_EXCEPTIONS` dans le garde. | `pytest -q app/tests/unit/test_api_router_architecture.py`. | PASS |
| AC5 | `router_logic` ne contient plus de router FastAPI ni d'import wildcard. | Suppression des `APIRouter`, `router = ...` et wildcards dans `router_logic`. | Test architecture + scan `APIRouter/import *` dans `router_logic`. | PASS |
| AC6 | Les imports `routers.*` sont elimines hors registries. | Imports remplaces par `schemas` ou `router_logic`; exception registry exacte documentee. | Test architecture + scan `from app.api.v1.routers.`. | PASS |
| AC7 | Le helper commun d'erreur conserve JSON, status, headers et `request_id`. | Helpers existants conserves sans changement de payload; pas d'abstraction nouvelle inutile. | Tests integration cibles et suite complete backend. | PASS |
| AC8 | `backend/app/main.py` utilise les chemins canoniques. | Imports main mis a jour vers `routers/ops/b2b` et `routers/b2b/credentials`. | Test architecture + scans anciens imports. | PASS |
| AC9 | Les routes deplacees gardent le contrat OpenAPI avant/apres. | Baseline cible ajoutee dans `test_api_v1_router_contracts.py`. | `pytest -q app/tests/integration/test_api_v1_router_contracts.py`. | PASS |
| AC10 | Lint et tests backend cibles passent dans le venv Windows. | Code formate et imports stabilises. | `ruff format .`; `ruff check .`; tests cibles; `pytest -q`. | PASS |
| AC11 | Les anciens chemins Python deplaces ne sont plus importables. | Anciens fichiers supprimes, pas de wrapper/re-export. | Test architecture + scans anciens chemins. | PASS |
| AC12 | Les `operationId` restent stables si un client genere les consomme. | Baseline OpenAPI compare les `operationId`; scan clients generes realise. | Test contrat OpenAPI + scan generateurs OpenAPI. | PASS |
| AC13 | Les erreurs HTTP API v1 sont centralisees via modele documente, contrats et codes d'erreur. | `schemas/common.py`, `errors.py`, helpers locaux delegues a `api_error_response`. | Test contrat d'erreur + garde architecture helpers/modeles. | PASS |
| AC14 | Les constantes partagees sortent des routeurs/schemas/logiques vers un module dedie. | `constants.py` centralise limites, messages, valeurs autorisees et descriptions partagees. | Garde architecture contre les redefinitions locales des constantes suivies. | PASS |
| AC15 | Audit anti-duplication et organisation canonique des schemas. | Schemas sous `schemas/routers/<surface>` ou `schemas/common.py`; audit `schema-audit.md`. | Garde architecture racines canoniques + scan `ErrorPayload/ErrorEnvelope`. | PASS |
| AC16 | `router_logic/admin/llm/prompts.py` est decoupe par responsabilite. | Extraction `manual_execution.py` et `release_snapshots.py`; imports consommateurs mis a jour. | Garde taille/responsabilite + tests admin LLM + suite complete. | PASS |
| AC17 | `routers/ops/entitlement_mutation_audits.py` est decoupe par responsabilite. | `list_mutation_audits` delegue a `build_mutation_audit_list_response`. | Garde route fine + tests ops entitlement mutation audits. | PASS |
| AC18 | Les routeurs ne contiennent plus de logique metier non HTTP dans le flux cible. | Flux liste mutation-audits sorti du routeur; audit `service-boundary-audit.md` liste les limites residuelles. | Garde ciblé + audit boundary + suite complete. | PASS_WITH_LIMITATIONS |
| AC19 | Les constantes partagees sous `backend/app/api` sont centralisees. | `constants.py` et audit `api-constants-audit.md`; constantes content, entitlements, consultation et LLM sorties. | Garde constantes + scan uppercase sous `app/api`. | PASS |
