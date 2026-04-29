# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/01-evidence-log.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/02-finding-register.md`
- `_condamad/audits/backend-tests/2026-04-28-1600/03-story-candidates.md`
- `backend/app/tests/unit/test_story_70_21_services_llm_structure_guard.py`
- `backend/app/tests/unit/test_story_70_22_entitlement_structure_guard.py`
- `backend/app/tests/unit/test_story_70_23_services_structure_guard.py`
- Existing backend architecture guard tests near `backend/app/tests/unit`.

## Required searches before editing

```powershell
rg --files backend -g 'test_story_*.py'
rg -n "legacy|compat|shim|fallback|deprecated|alias" backend/app/tests backend/tests backend/app/domain -g 'test_*.py'
rg -n "^def test_" backend -g 'test_story_*.py'
```

## Modified files

- `_condamad/stories/reclassify-story-regression-guards/story-test-inventory-before.md`
- `_condamad/stories/reclassify-story-regression-guards/story-test-inventory-after.md`
- `_condamad/stories/reclassify-story-regression-guards/story-guard-mapping.md`
- `_condamad/stories/reclassify-story-regression-guards/generated/*`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/unit/test_backend_story_guard_names.py`
- `backend/app/tests/unit/test_backend_services_llm_structure_guard.py`
- `backend/app/tests/unit/test_backend_entitlement_structure_guard.py`
- `backend/app/tests/unit/test_backend_services_structure_guard.py`

## Renamed files

- `backend/app/tests/unit/test_story_70_21_services_llm_structure_guard.py` -> `backend/app/tests/unit/test_backend_services_llm_structure_guard.py`
- `backend/app/tests/unit/test_story_70_22_entitlement_structure_guard.py` -> `backend/app/tests/unit/test_backend_entitlement_structure_guard.py`
- `backend/app/tests/unit/test_story_70_23_services_structure_guard.py` -> `backend/app/tests/unit/test_backend_services_structure_guard.py`

## Forbidden or high-risk files

- `backend/app/api/**`: out of scope, no runtime route change.
- `frontend/**`: out of scope.
- `backend/requirements.txt`: must not be created.
