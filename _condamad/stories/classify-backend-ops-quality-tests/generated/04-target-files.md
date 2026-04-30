# Target Files

## Must Read

- `AGENTS.md`
- `_condamad/stories/classify-backend-ops-quality-tests/00-story.md`
- `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/pyproject.toml`
- existing backend architecture guards under `backend/app/tests/unit/`

## Must Search

- `rg --files backend -g "test_*.py" | rg "(docs|scripts|ops|secret|security)"`
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" backend _condamad/stories/classify-backend-ops-quality-tests -g "*.py" -g "*.md"`

## Likely Modified

- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-tests-before.md`
- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-test-ownership.md`
- `_condamad/stories/classify-backend-ops-quality-tests/ops-quality-tests-after.md`
- `backend/app/tests/unit/test_backend_quality_test_ownership.py`
- `_condamad/stories/regression-guardrails.md`
- generated evidence files in this capsule

## Forbidden Unless Directly Justified

- `backend/app/api`
- `frontend/src`
- `backend/pyproject.toml` unless pytest markers or collection scope change
- dependency files
