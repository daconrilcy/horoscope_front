# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | The real snapshot replay path succeeds. | `log_call -> ReplaySnapshotV1Service.create_snapshot -> replay` covered in `backend/tests/unit/test_replay_snapshot_v1_execution_audit.py`; replay checks `snapshot.input_hash`. | `python -B -m pytest -q tests\unit\test_replay_snapshot_v1_execution_audit.py --tb=short` PASS. | PASS |
| AC2 | Stored hash uses the canonical replay payload. | `build_replay_snapshot_v1_payload` and `compute_replay_snapshot_v1_payload_hash` own the canonical payload/hash; `input_enc` and `input_hash` are derived from the same payload. | `python -B -m pytest -q tests\integration\test_replay_snapshot_v1_db_redaction.py --tb=short --long` PASS. | PASS |
| AC3 | Invalid snapshot states are refused explicitly. | Existing service refusal statuses preserved; canonical mismatch now audits `input_hash_mismatch`; timezone normalization prevents false expiry comparison errors. | `python -B -m pytest -q tests\unit\test_replay_snapshot_v1_execution_audit.py --tb=short` PASS. | PASS |
| AC4 | Fabricated raw encrypted replay setup is not the success proof. | `_replay_ready_snapshot` now creates the snapshot through `log_call`, with no `encrypt_input(user_input)` success fixture. | `rg -n "encrypt_input\(user_input\)" backend\tests\unit\test_replay_snapshot_v1_execution_audit.py` PASS: no matches. | PASS |
| AC5 | DPO/security forbidden data remains absent. | Replay payload remains sanitized by `Sink.LLM_REPLAY_SNAPSHOTS`; audit counter `purged_count` is explicitly operational, not user content. | `python -B -m pytest -q tests\unit\test_replay_snapshot_v1_redaction.py --tb=short` PASS; replay DB redaction PASS. | PASS |
| AC6 | Admin replay exposure stays internal. | No API router change; runtime OpenAPI and route assertions remain limited to admin audit paths. | Admin API/public exposure tests PASS; `app.openapi()` and `app.routes` assertions PASS. | PASS |
| AC7 | Service ownership remains single-owner. | Canonical payload/hash helpers live in `backend/app/services/replay_snapshot_v1_service.py`; replay runtime consumes service helper only. | `python -B -m pytest -q tests\architecture\test_replay_snapshot_v1_execution_boundary.py --tb=short` PASS. | PASS |
| AC8 | Story evidence artifacts are persisted. | Evidence directory contains before/after hash evidence, guardrails, validation, and CS-299 recheck. | `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-300-replay-snapshot-v1-payload-hash-integrity` PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
