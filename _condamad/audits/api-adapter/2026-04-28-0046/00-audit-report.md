# CONDAMAD Domain Audit Report

## Scope

- Domain target: `backend/app/api`
- Archetype: `api-adapter-boundary-audit`
- Mode: read-only audit, report artifacts only
- Output folder: `_condamad/audits/api-adapter/2026-04-28-0046`
- Guardrails consulted: `_condamad/stories/regression-guardrails.md` (`RG-007`, `RG-008`)

## Expected Responsibility

La couche API doit rester un adaptateur HTTP: parser les requêtes, valider les contrats, appeler les services applicatifs, mapper les erreurs applicatives et exposer OpenAPI. Elle ne doit pas posséder les règles métier, l'orchestration de persistance ou des facades historiques concurrentes.

## Post-Refactor Delta

Le précédent audit du 2026-04-27 signalait quatre écarts principaux: double propriétaire admin LLM observability, dette SQL dans les routeurs, exceptions de montage hors registre non formalisées, et absence de garde SQL. Le nouvel état montre:

- Observability LLM: corrigé et gardé.
- Exceptions de routes: corrigées via registre structuré.
- Garde SQL: ajoutée avec allowlist exacte.
- Dette SQL: encore active, mais gouvernée.

## Evidence Summary

Les preuves combinent scans `rg`, inspection AST en lecture seule, génération OpenAPI runtime, lecture du registre d'exceptions, lecture du registre de guardrails et exécution de tests ciblés dans le venv. Les preuves détaillées sont dans `01-evidence-log.md`.

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 1 |
| Medium | 1 |
| Low | 0 |
| Info | 3 |

## Key Findings

### F-001 API Persistence Debt Remains Active But Guarded

La couche API contient encore 848 entrées SQL/session/dépendance DB directes dans l'allowlist. La situation est meilleure qu'avant parce que la croissance silencieuse est bloquée, mais l'écart de frontière reste réel.

### F-002 Public Email Unsubscribe Historical URL Remains Active

`/api/email/unsubscribe` reste une URL publique historique hors `/v1`. Elle est désormais explicitement inventoriée, ce qui réduit le risque de dérive, mais son statut cible reste à décider.
Le caractère public est attendu pour un lien de désabonnement email, mais la route doit rester durcie autour du token: réponse non énumérante, absence de cache, vigilance sur les logs de query string et choix explicite entre action `GET` directe ou confirmation `GET` + action `POST`.

### F-003 Admin LLM Observability Ownership Is Corrected

Le runtime OpenAPI expose les endpoints observability depuis `app.api.v1.routers.admin.llm.observability` uniquement.

### F-004 Route Registration Exceptions Are Now Structured

Les exceptions de montage sont centralisées dans `route_exceptions.py`, avec tests runtime et structurels.

### F-005 Downstream Dependency Direction Remains Clean

Les scans ne détectent pas d'import inverse vers `app.api` depuis les couches non-API.

## DRY, No Legacy, Mono-Domain, Dependency Direction

- DRY: succès sur le retrait de la duplication LLM observability.
- No Legacy: partiel; `/api/email/unsubscribe` reste une surface historique gouvernée mais non convergée.
- Mono-domain: partiel; la dette SQL API reste active.
- Dependency direction: succès sur les scans non-API vers API et FastAPI hors couche API.

## Story Candidate Summary

2 story candidates sont proposés dans `03-story-candidates.md`.

## Validation Notes

Commandes exécutées avec venv activé:

- `pytest -q app/tests/unit/test_api_router_architecture.py`: 52 passed.
- `pytest -q app/tests/integration/test_admin_llm_config_api.py app/tests/integration/test_api_v1_router_contracts.py app/tests/integration/test_api_openapi_contract.py`: 11 passed.
