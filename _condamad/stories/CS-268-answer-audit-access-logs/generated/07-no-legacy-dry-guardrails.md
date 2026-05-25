# No Legacy / DRY Guardrails — CS-268-answer-audit-access-logs

## Decision

CS-268 is blocked for runtime implementation because the canonical persisted
answer-audit owner from CS-288 is absent. Implementing the access logs now would
require creating at least one of the following unauthorized parallel surfaces:

- a runtime `admin_answer_audit_v1` route before its real backing store exists;
- a synthetic answer-audit persistence path;
- an orphan access-log wrapper without a real consultation owner;
- a test-only fake consultation flow.

## Preserved Guardrails

- `AuditService.record_event` remains the single future persistence path for access events.
- `audit_events` remains the only audit-event store.
- No `AnswerAuditAccessLogModel`, `admin_answer_audit_access_logs` table or `answer_audit_access_log_repository` was added.
- No public/client access-log route was added.
- No frontend source, generated client, replay endpoint or migration was added.

## Future Implementation Guard

When CS-288 is implemented, CS-268 can be retried by adding a thin access-event
call at the protected admin answer-audit consultation boundary. The event details
must include only `source_contract`, safe `justification` and bounded `reason`
codes, and must not persist prompt, proof payload, secret or raw birth fields.
