# Release / PR Checklist - CS-256 to CS-291

## Release identity

| Field | Value |
|---|---|
| Release scope | CS-256 to CS-291 closure, including CS-292 to CS-301 follow-up closure evidence |
| HEAD | `677d1e6c` - `CONDAMAD implementation implementation-review-fix: cs-301` |
| Branch | `main` |
| Delivery report | `_condamad/reports/CS-256-CS-291-delivery-report.md` |
| Local CI evidence | `_condamad/reports/CS-256-CS-291-local-ci-evidence.md` |
| External CI logs | Not available; local CI-equivalent evidence attached |

## Required documents

| Document | Status |
|---|---|
| `docs/architecture/astrology-disclaimer-projection-policy.md` | Tracked in Git |
| `docs/architecture/replay-snapshot-v1-dpo-security-approval-request.md` | Tracked in Git |
| `_condamad/reports/CS-256-CS-291-delivery-report.md` | Tracked in Git; updated with local CI-equivalent evidence |
| `_condamad/reports/CS-256-CS-291-local-ci-evidence.md` | Added for release evidence |

## Backend commands

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
python -B -m pytest -q tests\unit\test_replay_snapshot_v1_execution_audit.py tests\integration\test_replay_snapshot_v1_db_redaction.py tests\api\admin\test_replay_snapshot_v1_api.py tests\architecture\test_replay_snapshot_v1_execution_boundary.py tests\architecture\test_admin_replay_snapshot_v1_public_exposure.py --tb=short --long
```

Status: PASS locally.

## Smoke OpenAPI

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -c "from app.main import app; paths=app.openapi()['paths']; assert '/v1/astrology/projections' in paths; assert all(path.startswith('/v1/admin/') for path in paths if 'replay' in path)"
```

Status: PASS locally.

## Replay validation

| Requirement | Status |
|---|---|
| Real `log_call -> snapshot -> replay` path covered | PASS |
| Canonical replay payload hash checked against `snapshot.input_hash` | PASS |
| Replay output does not expose raw provider payload | PASS |
| Replay routes stay admin-only | PASS |
| Public/client replay route absent | PASS |

## Release decision

Local release readiness: PASS with local validation evidence.

Remaining release-side gap: no hosted CI system exists. This checklist records the local replacement evidence and must be superseded by CI run links if hosted CI is introduced.
