# Target Files

## Must read

- `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/00-story.md`
- `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/unit/test_backend_test_helper_imports.py`
- `AGENTS.md`

## Must search

- `rg -n "BACKEND_ROOT|TEST_ROOTS|test_backend_test_helper_imports|from app\.tests\.(integration|unit|regression)\.test_|from tests\.(integration|unit|regression)\.test_" backend _condamad -g "*.py" -g "*.md"`
- `rg -n "from app\.tests\.(integration|unit|regression)\.test_|from tests\.(integration|unit|regression)\.test_" app/tests tests -g "test_*.py"`

## Likely modified

- `backend/app/tests/unit/test_backend_test_helper_imports.py`
- `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-guard-before.md`
- `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/cross-import-guard-after.md`
- `_condamad/stories/cover-both-backend-test-roots-in-cross-import-guard/generated/*.md`

## Forbidden unless justified

- `backend/app/tests/conftest.py`
- `backend/pyproject.toml`
- `requirements.txt`
- Any new duplicate guard file for the same responsibility.
