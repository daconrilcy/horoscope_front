# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | La commande standard collecte tous les tests retenus. | `backend/pyproject.toml` couvre `app/tests`, `tests/evaluation`, `tests/integration`, `tests/llm_orchestration` et `tests/unit`; inventaires avant/apres persistés. | `pytest --collect-only -q --ignore=.tmp-pytest` collecte 3468 tests; `uncollected-tests-after.md` indique 0 fichier retenu hors collecte. | Passed |
| AC2 | Aucune racine `testpaths` inexistante ne reste configuree. | `app/ai_engine/tests` est retire de `backend/pyproject.toml`; la garde verifie que chaque racine existe. | `pytest -q app/tests/unit/test_backend_pytest_collection.py` passe. | Passed |
| AC3 | Toute suite opt-in est explicite. | `uncollected-tests-after.md` liste une exception exacte: `app/domain/llm/prompting/tests/test_qualified_context.py`, justifiee par son package de collecte non importable sans donnees locales absentes. | Garde `test_opt_in_test_files_are_exact_existing_exceptions`; `rg -n "opt-in\|exception" ../_condamad/stories`. | Passed |
| AC4 | Une garde bloque les tests hors collecte. | `backend/app/tests/unit/test_backend_pytest_collection.py` ajoute la comparaison statique vs collecte runtime. | `pytest -q app/tests/unit/test_backend_pytest_collection.py` passe avec 3 tests. | Passed |
