# Target Files

## Must read

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/pyproject.toml`
- `backend/app/tests/unit/test_backend_pytest_collection.py`
- `backend/app/domain/llm/prompting/tests/test_qualified_context.py`
- `_condamad/audits/backend-tests/2026-04-28-1600/00-audit-report.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md`

## Must search

- `rg --files backend -g test_*.py -g *_test.py -g !.tmp-pytest/**`
- `rg "testpaths|python_files|addopts|markers" backend/pyproject.toml backend -g pyproject.toml -g pytest.ini -g conftest.py`
- `rg "app.domain.llm.prompting.tests|prompting/tests|test_qualified_context" backend _condamad -g *.py -g *.md`
- `rg "legacy|compat|shim|fallback|deprecated|alias" _condamad/stories/converge-backend-test-topology backend/app/tests/unit backend/tests/unit -g *.md -g *.py`

## Likely modified

- `backend/app/tests/unit/test_backend_pytest_collection.py`
- `backend/app/tests/unit/test_backend_test_topology.py`
- `backend/tests/llm_orchestration/test_qualified_context.py`
- `_condamad/stories/converge-backend-test-topology/backend-test-topology.md`
- `_condamad/stories/converge-backend-test-topology/test-root-inventory-before.md`
- `_condamad/stories/converge-backend-test-topology/test-root-inventory-after.md`
- `_condamad/stories/converge-backend-test-topology/test-root-diff.md`

## Likely deleted or moved

- Move `backend/app/domain/llm/prompting/tests/test_qualified_context.py` to `backend/tests/llm_orchestration/test_qualified_context.py`.
- Delete obsolete embedded test `conftest.py` if no test remains in that embedded folder.

## Forbidden unless justified

- `frontend/`
- `backend/app/infra`
- `backend/app/api`
- `requirements.txt`
