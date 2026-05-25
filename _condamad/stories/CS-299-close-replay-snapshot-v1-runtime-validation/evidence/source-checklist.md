# CS-299 source checklist

## CS-295-replay-snapshot-v1-storage-redaction
- final evidence: True
- code review: True
- validation evidence: True
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-295-replay-snapshot-v1-storage-redaction\generated\10-final-evidence.md:5: - Validation outcome: pass
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-295-replay-snapshot-v1-storage-redaction\generated\10-final-evidence.md:7: - Implementation review outcome: CLEAN
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-295-replay-snapshot-v1-storage-redaction\generated\10-final-evidence.md:38: | AC1 | Single owner remains `LlmReplaySnapshotModel` / `llm_replay_snapshots`; no second replay store. | `test_replay_snapshot_v1_ownership.py`; owner `rg` scan. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-295-replay-snapshot-v1-storage-redaction\generated\10-final-evidence.md:39: | AC2 | Approved schema fields and JSON metadata shape implemented. | `test_replay_snapshot_v1_storage.py`; model column inspection. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-295-replay-snapshot-v1-storage-redaction\generated\10-final-evidence.md:40: | AC3 | New snapshots derive expiry from creation + 30 days. | `test_replay_snapshot_v1_retention.py`. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-295-replay-snapshot-v1-storage-redaction\generated\10-final-evidence.md:41: | AC4 | Replay metadata excludes raw prompt, birth data, coordinates, identifiers and secrets. | `test_replay_snapshot_v1_redaction.py`; scoped negative storage scan. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-295-replay-snapshot-v1-storage-redaction\generated\10-final-evidence.md:42: | AC5 | Persisted DB row metadata and decrypted replay payload exclude raw sensitive values. | `test_replay_snapshot_v1_db_redaction.py`. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-295-replay-snapshot-v1-storage-redaction\generated\10-final-evidence.md:43: | AC6 | Alembic head and model metadata align on replay columns. | `test_llm_db_invariants.py`; `alembic heads` => `20260525_0140 (head)`. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-295-replay-snapshot-v1-storage-redaction\generated\10-final-evidence.md:44: | AC7 | Purge deletes expired snapshot row without deleting unrelated active logs. | `test_replay_snapshot_v1_purge.py`. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-295-replay-snapshot-v1-storage-redaction\generated\10-final-evidence.md:45: | AC8 | No public route/OpenAPI/frontend exposure. | Runtime `app.routes` and `app.openapi()` guards PASS; `frontend/src` clean. | PASS |

## CS-296-replay-snapshot-v1-service-retention-purge
- final evidence: True
- code review: True
- validation evidence: True
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-296-replay-snapshot-v1-service-retention-purge\generated\10-final-evidence.md:6: - Status: `done`
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-296-replay-snapshot-v1-service-retention-purge\generated\10-final-evidence.md:13: - Status: `done`
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-296-replay-snapshot-v1-service-retention-purge\generated\10-final-evidence.md:29: | AC1 | Canonical `ReplaySnapshotV1Service`; observability/replay delegate decisions; operations filter `replay_snapshot_v1` rows | Ownership pytest | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-296-replay-snapshot-v1-service-retention-purge\generated\10-final-evidence.md:30: | AC2 | `create_snapshot` retention 30 days | Retention pytest | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-296-replay-snapshot-v1-service-retention-purge\generated\10-final-evidence.md:31: | AC3 | expired metadata returns `expired` | Metadata pytest | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-296-replay-snapshot-v1-service-retention-purge\generated\10-final-evidence.md:32: | AC4 | controlled metadata states | Metadata pytest | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-296-replay-snapshot-v1-service-retention-purge\generated\10-final-evidence.md:33: | AC5 | automatic purge deletes expired `replay_snapshot_v1` rows only and keeps non-v1 rows untouched | Integration purge pytest | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-296-replay-snapshot-v1-service-retention-purge\generated\10-final-evidence.md:34: | AC6 | manual purge outcomes `success/not_found/expired/already_purged` | Manual purge pytest | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-296-replay-snapshot-v1-service-retention-purge\generated\10-final-evidence.md:35: | AC7 | call logs/releases unchanged and no narrative/diagnostics service references | Non-cascade pytest | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-296-replay-snapshot-v1-service-retention-purge\generated\10-final-evidence.md:36: | AC8 | Manual and automatic purge audit details are bounded; AuditService events stay payload-free | Audit pytest and integration purge pytest | PASS |

## CS-297-expose-internal-admin-replay-snapshot-v1-api
- final evidence: True
- code review: True
- validation evidence: True
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-297-expose-internal-admin-replay-snapshot-v1-api\generated\10-final-evidence.md:5: - Validation outcome: PASS.
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-297-expose-internal-admin-replay-snapshot-v1-api\generated\10-final-evidence.md:26: | AC1 | `backend/app/api/v1/routers/admin/audit.py` registers the admin metadata, replay-attempt and purge operations. | Runtime route guards and API tests. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-297-expose-internal-admin-replay-snapshot-v1-api\generated\10-final-evidence.md:27: | AC2 | OpenAPI replay paths are only under `/v1/admin/audit`. | Runtime OpenAPI guards and architecture test. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-297-expose-internal-admin-replay-snapshot-v1-api\generated\10-final-evidence.md:28: | AC3 | Metadata response uses `AdminReplaySnapshotV1MetadataResponse` without forbidden raw fields. | API redaction test. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-297-expose-internal-admin-replay-snapshot-v1-api\generated\10-final-evidence.md:29: | AC4 | Replay attempt delegates to `ReplaySnapshotV1Service.start_replay_attempt`. | API replay-attempt test. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-297-expose-internal-admin-replay-snapshot-v1-api\generated\10-final-evidence.md:30: | AC5 | Manual purge delegates to `ReplaySnapshotV1Service.purge_snapshot`. | API purge test. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-297-expose-internal-admin-replay-snapshot-v1-api\generated\10-final-evidence.md:31: | AC6 | All routes use the approved admin dependency. | Access-control evidence and API denial test. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-297-expose-internal-admin-replay-snapshot-v1-api\generated\10-final-evidence.md:32: | AC7 | Missing snapshot maps to `404`. | API state test. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-297-expose-internal-admin-replay-snapshot-v1-api\generated\10-final-evidence.md:33: | AC8 | Expired snapshot maps to `410`. | API state test. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-297-expose-internal-admin-replay-snapshot-v1-api\generated\10-final-evidence.md:34: | AC9 | Already purged snapshot maps to `410`. | API state test. | PASS |

## CS-298-replay-snapshot-v1-execution-audit
- final evidence: True
- code review: True
- validation evidence: True
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-298-replay-snapshot-v1-execution-audit\generated\10-final-evidence.md:10: - Status: `done`.
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-298-replay-snapshot-v1-execution-audit\generated\10-final-evidence.md:22: | AC1 | Metadata GET records `replay_snapshot_v1.metadata_read` and returns audit event id. | API/unit tests and full suite PASS. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-298-replay-snapshot-v1-execution-audit\generated\10-final-evidence.md:23: | AC2 | Admin replay attempts and real `replay()` execution record success and failed audit events. | Unit tests and full suite PASS. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-298-replay-snapshot-v1-execution-audit\generated\10-final-evidence.md:24: | AC3 | Purge records success and failed audit events. | API/unit tests and full suite PASS. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-298-replay-snapshot-v1-execution-audit\generated\10-final-evidence.md:25: | AC4 | Expired, purged, missing and incomplete snapshots are refused before payload replay. | Unit tests and full suite PASS. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-298-replay-snapshot-v1-execution-audit\generated\10-final-evidence.md:26: | AC5 | Audit details are bounded and tests reject forbidden fields. | Non-leakage tests and scoped scan PASS_WITH_CLASSIFIED_HITS. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-298-replay-snapshot-v1-execution-audit\generated\10-final-evidence.md:27: | AC6 | Runtime and OpenAPI replay paths stay under admin audit namespace. | `app.routes`, `app.openapi()` and API tests PASS. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-298-replay-snapshot-v1-execution-audit\generated\10-final-evidence.md:28: | AC7 | AST guard blocks route-level provider execution and validates snapshot check ordering. | Architecture test PASS. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-298-replay-snapshot-v1-execution-audit\generated\10-final-evidence.md:29: | AC8 | Reproducibility note persisted. | Evidence file present. | PASS |
- evidence: C:\dev\horoscope_front\_condamad\stories\CS-298-replay-snapshot-v1-execution-audit\generated\10-final-evidence.md:30: | AC9 | Evidence artifacts persisted under the CS-298 capsule. | Capsule validation PASS. | PASS |
PASS CS-295..CS-298 final, review, validation artifacts exist
