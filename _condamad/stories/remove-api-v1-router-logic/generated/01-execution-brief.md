# Execution Brief - remove-api-v1-router-logic

## Objective

Supprimer `backend/app/api/v1/router_logic` sans shim et sortir de `api/v1` tout code qui ne concerne pas directement les routes, schemas et erreurs associees.

## Boundaries

- Ne pas changer les URLs ou les contrats HTTP publics.
- Ne pas creer `services/router_logic`, `api_v1_router_logic`, alias, re-export ou fallback.
- Ne pas creer ni conserver `backend/app/api/v1/handlers`.
- Garder `backend/app/api/v1/**` limite aux routeurs, schemas, constantes et erreurs HTTP.
- Migrer les responsabilites applicatives vers `backend/app/services/**`, par domaine deja existant quand il existe.

## Done Conditions

- `backend/app/api/v1/router_logic` n'existe plus.
- `backend/app/api/v1/handlers` n'existe pas.
- Aucun code `backend/app`, `backend/tests` ou `backend/docs` ne reference `router_logic` ou `app.api.v1.handlers`.
- Les routeurs et tests importent/patchent les services canoniques.
- Le garde d'architecture bloque le retour du namespace et de l'import.
- Ruff, tests cibles, scans negatifs, suite backend complete et import OpenAPI passent.
