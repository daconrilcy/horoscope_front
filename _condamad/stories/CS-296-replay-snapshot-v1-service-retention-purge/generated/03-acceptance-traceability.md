# CS-296 acceptance traceability

| AC | Requirement | Status | Code evidence | Validation evidence |
|---|---|---|---|---|
| AC1 | One lifecycle service owns decisions. | PASS | `backend/app/services/replay_snapshot_v1_service.py`; `observability_service.py` and `replay_service.py` delegate lifecycle decisions | `test_replay_snapshot_v1_service_ownership.py` PASS; `service-ownership.txt` |
| AC2 | `create_snapshot` applies 30-day retention. | PASS | `ReplaySnapshotV1Service.create_snapshot`, `REPLAY_SNAPSHOT_V1_RETENTION_DAYS = 30` | `test_replay_snapshot_v1_service_retention.py` PASS |
| AC3 | Expired snapshots are unusable. | PASS | `get_snapshot_metadata` and `get_replay_payload_snapshot` return `expired` before replay payload use | `test_replay_snapshot_v1_service_metadata.py` PASS |
| AC4 | Metadata reads return controlled states. | PASS | `ReplaySnapshotResult`, `ReplaySnapshotMetadata`, statuses `success/not_found/expired/already_purged/validation_failed` | `test_replay_snapshot_v1_service_metadata.py` PASS |
| AC5 | Automatic purge affects expired rows only. | PASS | `purge_expired` deletes `LlmReplaySnapshotModel` rows with `expires_at <= now` only | `test_replay_snapshot_v1_service_purge.py` PASS |
| AC6 | Manual purge returns controlled outcomes. | PASS | `purge_snapshot` returns `success`, `not_found`, `expired`, `already_purged` | `test_replay_snapshot_v1_service_manual_purge.py` PASS |
| AC7 | Related audit rows remain unchanged. | PASS | Purge service touches only `LlmReplaySnapshotModel`; no references to narrative or chart diagnostics owners | `test_replay_snapshot_v1_service_non_cascade.py` PASS; `purge-non-cascade.txt` |
| AC8 | Safe audit hook payloads are bounded. | PASS | `ReplaySnapshotPurgeAuditDetails`; `AuditService.record_event` integration | `test_replay_snapshot_v1_service_audit.py` PASS |
| AC9 | Public API exposure is unchanged. | PASS | No API/router/frontend file modified for replay_snapshot_v1 | `app.openapi()` PASS; `app.routes` PASS; API/frontend rg PASS |
| AC10 | Story evidence artifacts are persisted. | PASS | CS-296 `evidence/` files and generated trace/final evidence updated | `condamad_validate.py` PASS after evidence format fix |

Validation rollup:
- Targeted CS-296 suite: 9 passed, 2 deselected.
- Nearby replay regression suite: 9 passed, 1 deselected.
- Backend unit+integration: 803 passed, 215 deselected.
- Full project pytest: 3306 passed, 1 skipped, 1216 deselected.
- `ruff check .`: PASS.
