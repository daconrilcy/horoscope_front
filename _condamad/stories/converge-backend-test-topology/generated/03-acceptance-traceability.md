# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Les racines autorisees sont documentees. | `backend-test-topology.md` liste les racines standard et les suites opt-in; `test_backend_test_topology.py` lit cette documentation. | `pytest -q app/tests/unit/test_backend_test_topology.py` PASS. | PASS |
| AC2 | Aucun test backend ne reste dans une racine non approuvee. | `test_qualified_context.py` migre vers `backend/tests/llm_orchestration`; l'ancienne exception opt-in est retiree. | `rg --files backend -g test_*.py -g *_test.py -g !.tmp-pytest/**`; garde de topologie PASS. | PASS |
| AC3 | Pytest collecte les racines canoniques ou opt-in documentees. | `backend/pyproject.toml` contient les racines documentees; aucune suite opt-in active. | `pytest --collect-only -q --ignore=.tmp-pytest` PASS, 3475 tests collected; `pytest -q app/tests/unit/test_backend_pytest_collection.py` PASS. | PASS |
| AC4 | Une garde empeche la reapparition de racines non documentees. | `backend/app/tests/unit/test_backend_test_topology.py` verifie doc/config, racines et tests embarques. | `pytest -q app/tests/unit/test_backend_test_topology.py` PASS. | PASS |
