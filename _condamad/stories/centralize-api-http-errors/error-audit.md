# Error Audit - centralize-api-http-errors

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `backend/app/api/v1/errors.py` | module | historical-facade | anciens services et tests | `backend/app/api/errors/` + `backend/app/core/exceptions.py` | supprime | `Test-Path backend/app/api/v1/errors.py` -> `False` | anciens imports externes non detectes hors repo |
| `app.api.v1.errors` | import path | historical-facade | backend first-party uniquement | `app.api.errors` pour HTTP, `app.core.exceptions` pour applicatif | migre | `rg "from app\.api\.v1\.errors|app\.api\.v1\.errors" backend/app backend/tests` ne retourne que les gardes historiques | references de test attendues |
| `api_error_response` | helper | dead | services API-support | `ApplicationError` levee + handler FastAPI | supprime | `rg "api_error_response\(" backend/app/api/v1/routers backend/app/api/dependencies backend/app/services` -> aucun hit | aucun |
| route-local `_error_response` | helper | dead | aucun routeur API v1 apres migration | `_raise_error` dans services support ou `ApplicationError` directe | supprime | `rg "def _error_response|def _create_error_response" backend/app/api/v1/routers` -> aucun hit | aucun |
| service-local `_error_response` | helper | historical-facade | services support importes par routeurs | `_raise_error` leve `ApplicationError` | renomme | `rg "def _error_response|def _create_error_response" backend/app/services` -> aucun hit | les services restent partiellement couples a des schemas/dependances API existants hors construction HTTP |
| `JSONResponse` dans services | HTTP response construction | dead | aucun service apres migration | handler `app.api.errors.handlers` | supprime | `rg "JSONResponse|HTTPException|api_error_response|_error_response\(" backend/app/services` -> aucun hit | aucun |
| `HTTPException` dans routeurs | HTTP exception FastAPI | dead | aucun routeur API apres migration | `ApplicationError` + handler central | supprime | `rg -n "HTTPException" backend/app/api` -> aucun hit | aucun |
| `JSONResponse` d'erreur dans routeurs | local error envelope | dead | routeurs publics/admin historiques | `build_error_response`, `raise_http_error` ou `ApplicationError` + handler central | migre | `test_api_routes_do_not_build_error_envelopes_with_json_response` + scan literal ne retourne que docstring ephemeris | seuls `JSONResponse` non-erreur restent pour status/succes speciaux |

## Post-full-suite Route Audit Addendum

Apres le retour utilisateur indiquant que le `pytest -q` complet passe, un scan strict des routeurs montre encore des constructions locales d'erreurs via `JSONResponse`.
Ces usages ne sont pas des `HTTPException` et ne touchent pas les services, mais ils contredisent le target state strict de la story pour les routes.

### Scans

| Scan | Result |
|---|---|
| `rg -n "status_code" backend/app/services` | no hit |
| `rg -n "JSONResponse|HTTPException|api_error_response|_error_response\(" backend/app/services` | no hit |
| `rg -n "from app\.api\.v1\.errors|app\.api\.v1\.errors" backend/app backend/tests` | only expected architecture guard references |
| `rg -n "HTTPException" backend/app/api` | no hit |
| `rg -n "error\.status_code|def status_code" backend/app/api backend/app/core backend/app/tests` | only expected test guard and unrelated LLM compactor test |
| `rg -n "JSONResponse\(" backend/app/api/v1/routers` | remaining route hits listed below |

### Remaining Route-local JSONResponse Calls

| File | Lines observed | Classification | Notes |
|---|---:|---|---|
| `backend/app/api/v1/routers/public/auth.py` | 119, 145, 197, 251 | resolved | Migrated to `build_error_response` in closure addendum. |
| `backend/app/api/v1/routers/public/chat.py` | 61, 118, 131, 150, 179, 193, 223, 245, 275, 297, 327, 352 | resolved | Migrated to `build_error_response` in closure addendum. |
| `backend/app/api/v1/routers/public/users.py` | 86, 111, 173, 222, 263, 278, 311, 342, 377, 420, 433, 447, 464, 513, 561, 591, 636, 650 | resolved | Migrated to `build_error_response` in closure addendum. |
| `backend/app/api/v1/routers/public/consultations.py` | 99, 118 | resolved | Migrated to `build_error_response` in closure addendum. |
| `backend/app/api/v1/routers/public/guidance.py` | 47, 70, 93, 125, 150, 171 | resolved | Migrated to `build_error_response` in closure addendum. |
| `backend/app/api/v1/routers/public/help.py` | 46, 105, 124, 137, 150, 196, 221 | resolved | Migrated to `build_error_response` in closure addendum. |
| `backend/app/api/v1/routers/public/entitlements.py` | 72, 129 | resolved | Migrated to `build_error_response` in closure addendum. |
| `backend/app/api/v1/routers/admin/pdf_templates.py` | 55, 70, 116, 138, 172 | resolved | Migrated to `build_error_response` in closure addendum. |
| `backend/app/api/v1/routers/ops/entitlement_mutation_audits.py` | 619 | non-error/special response | Idempotent `200` response for create suppression rule; not an error envelope. |
| `backend/app/api/v1/routers/public/ephemeris.py` | 38, 43, 56, 70 | non-error/status endpoint | Operational/status JSON responses; not all are error envelopes. |

### Audit Conclusion

- Services: conformes au perimetre "ne construisent plus de reponse HTTP".
- Routeurs: `HTTPException` et helpers legacy supprimes, mais plusieurs routes construisent encore directement l'enveloppe JSON d'erreur avec `JSONResponse`.
- Status: dette resolue par l'addendum de fermeture AC3/AC7/AC9; le garde d'architecture bloque maintenant les `JSONResponse(content={"error": ...})` en routeurs.

## AC3/AC7/AC9 Closure Addendum

Les constructions locales d'enveloppes d'erreur routeur identifiees dans l'addendum precedent ont ete migrees vers `build_error_response`.
Les `JSONResponse` restants sous `backend/app/api/v1/routers` sont des reponses non-erreur:

| File | Remaining JSONResponse use | Classification | Notes |
|---|---:|---|---|
| `backend/app/api/v1/routers/ops/entitlement_mutation_audits.py` | 1 | non-error/special response | Reponse idempotente `200` pour creation de regle de suppression deja existante. |
| `backend/app/api/v1/routers/public/ephemeris.py` | 2 | non-error/status response | Reponses de statut `{"status": ...}` pour endpoint diagnostic. Les erreurs 503 passent par `build_error_response`. |

### Final Scans

| Scan | Result |
|---|---|
| `rg -n "HTTPException" backend/app/api` | no hit |
| `rg -n "status_code" backend/app/services` | no hit |
| `rg -n "JSONResponse|HTTPException|api_error_response|_error_response\(" backend/app/services` | no hit |
| `rg -n -F '"error": {' backend/app/api/v1/routers` | no hit |
| `rg -n "error\.status_code|def status_code" backend/app/api backend/app/core backend/app/tests` | only expected test guard and unrelated LLM compactor test |

### Final Audit Conclusion

- Services: conformes au perimetre "ne construisent plus de reponse HTTP".
- Routeurs: les erreurs ne passent plus par `HTTPException` ni par `JSONResponse(content={"error": ...})`.
- AC3, AC7 et AC9 sont couverts sans limitation par les scans et tests d'architecture mis a jour.
