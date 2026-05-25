# Validation Plan — CS-268-answer-audit-access-logs

## Executed / Recorded

- Validate capsule structure after generated repair.
- Confirm story-status row path and brief source for CS-268.
- Confirm CS-288 remains `ready-to-dev`.
- Confirm CS-267 contract is declarative and no runtime answer-audit route exists.
- Check runtime `app.routes` and `app.openapi()` for absence of `/v1/admin/answer-audits`.
- Scan for forbidden access-log stores and public/client access-log routes.
- Check retention documentation contains RGPD / retention / policy wording.

## Blocked Runtime Validation

- `pytest -q backend/tests/api/admin/test_answer_audit_access_logs.py` is blocked because the target test file and runtime consultation surface do not exist yet.
- Success, denied and logging-failure access-event tests are blocked until CS-288 provides the canonical persisted `narrative_answer_audit_v1` owner and the admin consultation route can be implemented without creating a parallel store.

## Limited Validation Notes

- `python -B -m pytest -q app\tests\integration\test_admin_answer_audit_contract.py --tb=short` was attempted from `backend` with venv active, but current pytest collection deselected the five tests.
- Static and runtime checks still prove the relevant blocker: the admin answer-audit runtime surface is absent.
