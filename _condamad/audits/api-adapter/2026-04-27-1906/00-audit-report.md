# CONDAMAD Domain Audit Report

## Scope

- Domain target: `backend/app/api`
- Archetype: `api-adapter-boundary-audit`
- Mode: read-only audit, report artifacts only
- Output folder: `_condamad/audits/api-adapter/2026-04-27-1906`

## Expected Responsibility

La couche API doit rester un adaptateur HTTP: parser les requêtes, valider les contrats, appeler les services applicatifs, mapper les erreurs applicatives et exposer OpenAPI. Elle ne doit pas posséder les règles métier, l'orchestration de persistance ou des facades historiques concurrentes.

## Evidence Summary

Les preuves combinent scans `rg`, inspection AST en lecture seule, inventaire du montage `main.py`, tests d'architecture existants et génération runtime OpenAPI via venv activé. Les preuves détaillées sont dans `01-evidence-log.md`.

## Findings Summary

| Severity | Count |
|---|---:|
| Critical | 0 |
| High | 2 |
| Medium | 2 |
| Low | 0 |
| Info | 1 |

## Key Findings

### F-001 Duplicate LLM Observability Route Owners

Les endpoints `/v1/admin/llm/call-logs`, `/dashboard`, `/replay` et `/call-logs/purge` existent dans `admin/llm/observability.py`, mais ce routeur n'est pas monté. Les mêmes endpoints restent dans `admin/llm/prompts.py` et apparaissent dans l'OpenAPI runtime.

### F-002 API Routers Own Persistence Orchestration

Un scan AST détecte des opérations DB directes dans 39 routeurs API. Cette distribution montre que la dette n'est pas locale: elle touche admin, public, b2b, ops et internal.

### F-003 API v1 Registration Has Hard-Coded Main Exceptions

Le registre v1 existe, mais `main.py` conserve des montages directs pour `email_router` et le routeur interne QA conditionnel. Les tests les autorisent comme exceptions, sans registre d'exceptions structuré.

### F-004 Missing Guard Against Router-Level SQL

Les tests d'architecture protègent plusieurs règles API, mais pas l'interdiction de SQLAlchemy ou des commits dans les routeurs.

### F-005 Downstream Dependency Direction Is Currently Clean

Aucun import inverse depuis `services` ou `domain` vers `app.api` n'a été détecté.

## DRY, No Legacy, Mono-Domain, Dependency Direction

- DRY: échec sur les endpoints admin LLM observability dupliqués.
- No Legacy: échec sur la facade résiduelle `prompts.py` qui garde le runtime des endpoints extraits.
- Mono-domain: échec partiel car l'API possède de l'orchestration DB qui appartient aux services ou à l'infra.
- Dependency direction: succès pour les dépendances descendantes depuis `services` et `domain`.

## Story Candidate Summary

4 story candidates sont proposés dans `03-story-candidates.md`.

## Validation Notes

La génération OpenAPI a été exécutée avec le venv activé. `python -S` masque les packages du venv dans cet environnement, donc la preuve runtime applicative a utilisé `python -B` après activation.
