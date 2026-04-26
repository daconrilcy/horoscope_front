# Implementation Plan

## Initial repository findings

- `backend/app/main.py` importait les routeurs ops B2B depuis `routers/b2b` et credentials depuis `routers/public`.
- `router_logic` contenait des restes generes: `APIRouter`, `router = APIRouter(...)` et imports wildcard de schemas.
- Des schemas/helpers LLM admin importaient `AdminLlmErrorCode` depuis un routeur.
- `internal/llm/qa.py` importait des helpers depuis le routeur public `predictions`.
- `natal_interpretation.py` importait `ErrorEnvelope` depuis le routeur public `users`.

## Proposed changes

- Deplacer les routeurs selon leur racine HTTP effective sans modifier les prefixes HTTP.
- Deplacer les schemas/helpers associes quand le namespace racine etait incoherent.
- Remplacer les imports entre routeurs par `router_logic` ou `schemas`.
- Ajouter des gardes d'architecture et une baseline OpenAPI cible.
- Centraliser le contrat d'erreur API v1 dans `schemas/common.py` et la fabrique HTTP dans `errors.py`.
- Extraire les constantes partagees vers `constants.py` et interdire leur redefinition dans routeurs/schemas/logique.
- Ranger les schemas de routeurs sous `schemas/routers/<surface>` et documenter l'audit anti-duplication.

## Files to modify

- `backend/app/main.py`
- `backend/app/api/v1/routers/**`
- `backend/app/api/v1/router_logic/**`
- `backend/app/api/v1/schemas/**`
- `backend/app/api/v1/errors.py`
- `backend/app/api/v1/constants.py`
- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/app/tests/unit/test_api_error_contracts.py`
- `backend/app/tests/integration/test_api_v1_router_contracts.py`
- `backend/app/tests/integration/test_enterprise_credentials_api.py`
- `backend/tests/evaluation/__init__.py`

## Files to delete

- Anciens modules Python deplaces sous `routers/b2b`, `routers/public`, `router_logic/b2b`, `router_logic/public` et schemas correspondants.
- `backend/app/api/v1/routers/admin/llm/error_codes.py`, remplace par le schema canonique.

## Tests to add or update

- Garde architecture: anciens modules non importables, modules canoniques enregistres, `router_logic` sans routeur/wildcard, imports `routers.*` controles, non-v1 allowlist exact.
- Garde architecture: contrat d'erreur centralise, helpers d'erreur locaux branches sur `api_error_response`, constantes partagees non redefinies localement, schemas sous racines canoniques.
- Contrat OpenAPI: baseline path/method/tags/status/operationId pour les routes deplacees.
- Contrat d'erreur: status, headers, code, message, details et `request_id` stables.

## Risk assessment

- Risque principal: patch paths de tests ou tooling vers anciens modules Python. Traite via mise a jour de `test_enterprise_credentials_api.py`, `backend/tests/evaluation/__init__.py` et scans anciens chemins.
- Risque OpenAPI: couvert par baseline cible.
- Risque de rupture d'imports internes apres deplacement des schemas plats: couvert par Ruff et tests cibles.

## Rollback strategy

- Revenir aux imports et fichiers deplaces via git si un consommateur externe non detecte depend d'un ancien chemin Python; ne pas ajouter de shim.
