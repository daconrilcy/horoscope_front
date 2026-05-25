# Traceability - CS-298

| AC | Requirement | Status | Code evidence | Validation evidence |
|---|---|---|---|---|
| AC1 | Admin metadata reads are audited. | PASS | `ReplaySnapshotV1Service.get_snapshot_metadata(..., audit=True)` records `replay_snapshot_v1.metadata_read`; route GET commits and returns `audit_event_id`. | API/unit tests and full backend suite PASS. |
| AC2 | Replay attempts are audited. | PASS | `start_replay_attempt` records admin acceptance/refusal; `replay()` records real provider success/failure through `ReplaySnapshotActivityAuditDetails`. | `tests/unit/test_replay_snapshot_v1_execution_audit.py` PASS. |
| AC3 | Purge outcomes are audited. | PASS | `purge_snapshot` records success and refusal events under `replay_snapshot_v1.purge`. | API/unit tests PASS. |
| AC4 | Unsafe snapshot states are refused. | PASS | `expired`, `already_purged`, `not_found` and `incomplete` return explicit statuses before replay payload use. | Unit test `test_incomplete_snapshot_is_refused_before_replay_payload_use` PASS. |
| AC5 | Audit details do not leak sensitive material. | PASS | Audit DTO permits only `action/status/snapshot_id/request_id/reason/diff_summary`. | Non-leakage assertions PASS; scoped scan classified only non-detail hits. |
| AC6 | Runtime API wiring stays internal. | PASS | Routes stay under `/v1/admin/audit/replay_snapshot_v1`. | `app.routes`, `app.openapi()` and API tests PASS. |
| AC7 | Replay execution stays bounded. | PASS | AST guard verifies route has no provider execution and replay service validates snapshot before `gateway.execute`. | `tests/architecture/test_replay_snapshot_v1_execution_boundary.py` PASS. |
| AC8 | Reproducibility limits are documented. | PASS | `evidence/reproducibility.md` documents deterministic inputs and provider nondeterminism. | Evidence file persisted. |
| AC9 | Story evidence artifacts are persisted. | PASS | Evidence folder and generated files completed. | `condamad_story_validate.py` and `condamad_story_lint.py --strict` PASS. |
