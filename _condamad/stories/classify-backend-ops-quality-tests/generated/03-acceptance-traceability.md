# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Classified test inventory is persisted. | Add `ops-quality-tests-before.md` and `ops-quality-tests-after.md`. | `pytest --collect-only -q --ignore=.tmp-pytest`; inventory scan. | PASS |
| AC2 | Every classified test has one owner. | Add `ops-quality-test-ownership.md` and `backend/app/tests/unit/test_backend_quality_test_ownership.py`. | `pytest -q app/tests/unit/test_backend_quality_test_ownership.py`. | PASS |
| AC3 | Pytest collection impact is explicit. | Registry states tests remain in standard backend pytest collection with exact commands. | `pytest --collect-only -q --ignore=.tmp-pytest`. | PASS |
| AC4 | User decision blocks backend scope change. | No backend scope change made; registry records no approval required for unchanged collection. | Diff review and collect-only evidence. | PASS |
