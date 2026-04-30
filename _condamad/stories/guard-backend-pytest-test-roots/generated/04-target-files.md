# Target Files

## Must inspect before implementation

- `AGENTS.md` files in scope
- `_condamad/stories/regression-guardrails.md`
- `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md`
- `backend/pyproject.toml`
- `backend/app/tests/unit/test_backend_test_topology.py`
- `_condamad/stories/converge-backend-test-topology/backend-test-topology.md`

## Required searches before editing

```bash
rg --files backend -g "test_*.py" -g "*_test.py" -g "!backend/.tmp-pytest/**"
rg --files backend/app -g "test_*.py" -g "*_test.py" -g "!backend/app/tests/**" -g "!backend/.tmp-pytest/**"
rg "legacy|compat|shim|fallback|deprecated|alias" _condamad/stories/guard-backend-pytest-test-roots backend/app/tests/unit/test_backend_test_topology.py backend/pyproject.toml
```

Adapt searches to the story and repository layout.

## Likely modified files

- `_condamad/stories/guard-backend-pytest-test-roots/backend-test-topology.md`
- `_condamad/stories/guard-backend-pytest-test-roots/backend-test-files-before.md`
- `_condamad/stories/guard-backend-pytest-test-roots/backend-test-files-after.md`
- `_condamad/stories/guard-backend-pytest-test-roots/generated/*.md`
- `backend/app/tests/unit/test_backend_test_topology.py`

## Forbidden or high-risk files

- `backend/pyproject.toml`: read-only unless collection roots are wrong.
- `backend/app/tests/conftest.py`: out of scope.
- `frontend/`: out of scope.
