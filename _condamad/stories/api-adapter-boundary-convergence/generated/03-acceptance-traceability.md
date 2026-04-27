# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `backend/app/api/v1/schemas` est indépendant de FastAPI. | Ancien paquet `schemas/routers` déplacé vers `app.services.api_contracts`; `schemas` ne contient plus d'objets FastAPI. | Guard AST `test_api_router_architecture.py`; scan `rg` zero hit. | PASS |
| AC2 | `services`, `domain`, `infra` et `core` ne dépendent plus de `app.api`. | Imports migrés vers `app.core.auth_context`, `app.core.api_constants`, `app.services.api_contracts`. | Guard AST; scans non-API zero hit. | PASS |
| AC3 | Les contrats déplacés ont un propriétaire canonique unique hors `app.api`. | Propriétaire `app.services.api_contracts`; API routers et services l'importent directement. | Scans anciens imports schemas zero hit; `removal-audit.md`. | PASS |
| AC4 | Les routeurs API v1 sont enregistrés via un registre unique. | Ajout `app/api/v1/routers/registry.py`; `main.py` appelle `include_api_v1_routers(app)`. | Tests architecture registry passent. | PASS |
| AC5 | Les surfaces d'erreur HTTP legacy ne restent pas nominales. | `raise_http_error`, `legacy_detail` et top-level `detail` supprimés du code actif. | Tests erreur + scan avec seul hit guard attendu. | PASS |
| AC6 | Toute surface historique hors `/v1` est classifiée avant action. | `/api/email/unsubscribe` gardée comme `external-active`; `/health` exception bootstrap. | Test non-v1 routes; `removal-audit.md`. | PASS |
| AC7 | Aucun gros routeur ne reçoit de nouvelle logique métier. | Changements routeurs limités aux imports/erreurs/enregistrement. | Diff review; tests ciblés passent. | PASS |
| AC8 | Les garde-fous No Legacy/DRY bloquent toute réintroduction. | Guards ajoutés pour contrats, imports non-API, registre et erreurs legacy. | `pytest -q app/tests/unit/test_api_router_architecture.py` passe. | PASS |
| AC9 | Le backend démarre et l'OpenAPI reste cohérent. | OpenAPI génère 192 paths après convergence. | Smoke OpenAPI passe; snapshot avant non capturé. | PASS_WITH_LIMITATIONS |
| AC10 | Lint, format et tests ciblés passent dans le venv. | Code formaté/linté; tests ciblés passent. | `pytest -q` complet timeout 10 min. | PASS_WITH_LIMITATIONS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
