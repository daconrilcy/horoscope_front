# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Inventaire complet de chaque fichier, symbole significatif et consommateur de `router_logic`. | `router-logic-service-audit.md` liste les 54 fichiers, consommateurs et destinations services. | Audit + scans sans hit legacy. | PASS |
| AC2 | Chaque responsabilite migree a un proprietaire canonique. | Les modules non-route sont sous `backend/app/services/**`, par domaine. | Audit par lot + `rg --files app/services`. | PASS |
| AC3 | Aucun code n'est duplique quand une fonction/classe equivalente existe deja. | Migration vers domaines existants; aucun package miroir. | `ruff check .`; suite complete. | PASS |
| AC4 | Les routeurs API v1 ne dependent plus de `app.api.v1.router_logic`. | Imports routeurs remplaces par `app.services.*`. | Architecture test + scan backend. | PASS |
| AC5 | `backend/app/api/v1/router_logic` est supprime sans shim. | Dossier supprime; test import negatif. | `Test-Path app/api/v1/router_logic` -> `False`; architecture test. | PASS |
| AC6 | Les tests qui patchaient/importaient `router_logic` ciblent les services canoniques. | Monkeypatches/imports tests remplaces par `app.services.*`. | Tests integration cibles + scan backend/tests. | PASS |
| AC7 | Les helpers morts, facades historiques et legacy trouves pendant l'audit sont supprimes. | Packages `router_logic` et `api/v1/handlers` absents; aucun re-export. | Audit + scans negatifs. | PASS |
| AC8 | Les contrats HTTP/OpenAPI des routes consommatrices restent inchanges. | Routeurs conservent leurs declarations; seuls les imports changent. | Tests integration cibles + `app.openapi()` genere 192 paths. | PASS |
| AC9 | Les gardes d'architecture interdisent la reintroduction de `router_logic`. | Tests absence filesystem/import/reference ajoutes, absence `api/v1/handlers`, et blocage des imports FastAPI dans `services`. | `pytest -q app/tests/unit/test_api_router_architecture.py`. | PASS |
| AC10 | Lint, format, tests backend cibles et tests de services migres passent dans le venv. | Ruff et pytest executes apres activation venv. | `ruff format .`; `ruff check .`; tests cibles; `pytest -q`. | PASS |
| AC11 | La migration est realisee par lots `admin`, `admin/llm`, `ops`, `b2b`, `public`, `internal`. | Audit contient mapping par lot; imports de chaque lot migres. | Audit par lot + tests cibles de chaque lot. | PASS |
| AC12 | Les helpers sont routes vers `services`, `core` ou `api/v1` selon leur responsabilite. | La logique applicative sort de `api/v1`; la construction HTTP reste cote routeurs/API v1, notamment `response_exports.py` pour les exports CSV. | Audit + scan services/API + architecture guards renforces. | PASS |
