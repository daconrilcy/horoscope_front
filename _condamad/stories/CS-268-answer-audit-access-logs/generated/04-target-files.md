# Target Files — CS-268-answer-audit-access-logs

## Inspected Before Decision

- `AGENTS.md`
- `_story_briefs/cs-268-add-admin-answer-audit-access-logs.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/CS-268-answer-audit-access-logs/00-story.md`
- `_condamad/stories/CS-267-admin-answer-audit-api/00-story.md`
- `_condamad/stories/CS-288-narrative-answer-audit-v1-persistence/00-story.md`
- `docs/architecture/admin-answer-audit-api.md`
- `backend/app/api/v1/routers/admin/audit.py`
- `backend/app/services/ops/audit_service.py`
- `backend/app/infra/db/models/audit_event.py`
- `backend/app/tests/integration/test_admin_logs_api.py`
- `backend/app/tests/integration/test_admin_answer_audit_contract.py`

## Modified Files

- `docs/architecture/admin-answer-audit-access-retention.md` - documents RGPD retention uncertainty without creating runtime behavior.
- `_condamad/stories/CS-268-answer-audit-access-logs/evidence/source-checklist.md`
- `_condamad/stories/CS-268-answer-audit-access-logs/evidence/app-surface-status.txt`
- `_condamad/stories/CS-268-answer-audit-access-logs/evidence/sensitive-detail-scan.txt`
- `_condamad/stories/CS-268-answer-audit-access-logs/evidence/validation.txt`
- `_condamad/stories/CS-268-answer-audit-access-logs/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-268-answer-audit-access-logs/generated/04-target-files.md`
- `_condamad/stories/CS-268-answer-audit-access-logs/generated/06-validation-plan.md`
- `_condamad/stories/CS-268-answer-audit-access-logs/generated/07-no-legacy-dry-guardrails.md`
- `_condamad/stories/CS-268-answer-audit-access-logs/generated/09-dev-log.md`
- `_condamad/stories/CS-268-answer-audit-access-logs/generated/10-final-evidence.md`

## Not Modified Because Blocked

- `backend/app/api/v1/routers/admin/**` - no protected answer-audit runtime route exists yet.
- `backend/app/services/ops/audit_service.py` - canonical future owner already exists; no orphan wrapper added.
- `backend/app/infra/db/models/**` - no new audit/access-log table authorized.
- `backend/tests/api/admin/test_answer_audit_access_logs.py` - runtime tests cannot be meaningful until CS-288 provides the persisted answer-audit owner.

## Forbidden / High-Risk Files

- Frontend source, generated clients, public routers and migrations remain out of scope.
