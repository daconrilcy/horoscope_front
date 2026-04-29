# Target Files

## Must read

- `AGENTS.md`
- `_condamad/stories/collect-retained-backend-tests/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/00-audit-report.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md`
- `backend/pyproject.toml`

## Must search

- `rg --files backend -g test_*.py -g *_test.py -g !backend/.tmp-pytest/**`
- `rg -n "testpaths|app/ai_engine/tests|backend_pytest_collection|collect-only" backend _condamad`
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" backend/app/tests backend/tests backend/app/domain -g test_*.py`

## Likely modified

- `backend/pyproject.toml`
- `backend/app/tests/unit/test_backend_pytest_collection.py`
- `_condamad/stories/collect-retained-backend-tests/generated/*.md`
- `_condamad/stories/collect-retained-backend-tests/*collection*.md`
- `_condamad/stories/collect-retained-backend-tests/*inventory*.md`
- `_condamad/stories/collect-retained-backend-tests/uncollected-tests-after.md`

## Forbidden unless justified

- `frontend/**`
- `backend/app/infra/**`
- `backend/tests/**` except adding evidence through collection
- `requirements.txt`
- New root directories under `backend/`

## Existing tests to inspect first

- `backend/app/tests/unit/test_api_router_architecture.py`
- `backend/app/tests/unit/test_story_70_23_services_structure_guard.py`
- Any existing `test_backend_pytest_collection.py` if present.
