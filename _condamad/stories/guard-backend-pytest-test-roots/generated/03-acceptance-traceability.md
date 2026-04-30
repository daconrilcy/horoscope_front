# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Pytest roots are documented. | Add `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md`; point `test_backend_test_topology.py` to it. | `pytest -q app/tests/unit/test_backend_test_topology.py`; registry roots equal `backend/pyproject.toml` testpaths. | PASS |
| AC2 | Hidden backend test roots fail the guard. | Harden `test_backend_test_topology.py` to validate all backend test files, exact non-standard `tests` exceptions, and no test files under exceptions. | `pytest -q app/tests/unit/test_backend_test_topology.py`; zero-hit hidden-root scan. | PASS |
| AC3 | Standard collection remains stable. | No pytest config changes; guard only reads registry/config/filesystem. | `pytest --collect-only -q --ignore=.tmp-pytest` collected 3491 tests after the later benchmark-stabilization story. | PASS |
| AC4 | Topology evidence is persisted. | Add `backend-test-files-before.md`, `backend-test-files-after.md`, and final evidence. | Inventory count remains 431 files under documented roots only. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
