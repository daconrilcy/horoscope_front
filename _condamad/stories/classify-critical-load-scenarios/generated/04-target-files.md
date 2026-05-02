# Target Files

## Must Read

- `AGENTS.md`
- `_condamad/stories/classify-critical-load-scenarios/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `scripts/load-test-critical.ps1`
- `scripts/load-test-critical-matrix.ps1`
- `scripts/generate-performance-report.ps1`
- `backend/app/tests/unit/test_backend_quality_test_ownership.py`
- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md`

## Must Search

- `rg -n "Story 66\\.35|Legacy critical scenarios|privacy_delete_request|Invoke-ScenarioByProfile -Name" scripts/load-test-critical.ps1`
- `rg --files backend -g "test_*load*critical*.py" -g "test_*scripts*.py" -g "test_*ownership*.py"`
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" scripts/load-test-critical.ps1 backend/app/tests/unit/test_load_test_critical_script.py`

## Likely Modified

- `scripts/load-test-critical.ps1`
- `backend/app/tests/unit/test_load_test_critical_script.py`
- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md`
- `_condamad/stories/classify-critical-load-scenarios/generated/*.md`
- `_condamad/stories/classify-critical-load-scenarios/scenario-baseline.txt`
- `_condamad/stories/classify-critical-load-scenarios/scenario-after.txt`

## Forbidden Unless Directly Justified

- `backend/app/api/v1/routers/**`
- `frontend/src/**`
- API contracts, OpenAPI generation, or backend endpoint implementations.
