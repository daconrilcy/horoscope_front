# Local CI Evidence - CS-256 to CS-291

## Scope

This file substitutes a CI attachment for the current repository state because no external CI pipeline is available.
It is intentionally labeled as local CI-equivalent evidence, not as a remote CI run.

## Run metadata

| Field | Value |
|---|---|
| Run type | Local CI-equivalent validation |
| Date | 2026-05-25 |
| Repository | `c:\dev\horoscope_front` |
| Branch | `main` |
| HEAD | `677d1e6c` - `CONDAMAD implementation implementation-review-fix: cs-301` |
| Python environment | `.venv` activated before Python/Ruff commands |
| External CI | Not available |

## Commands

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
python -B -m pytest -q tests\unit\test_replay_snapshot_v1_execution_audit.py tests\integration\test_replay_snapshot_v1_db_redaction.py tests\api\admin\test_replay_snapshot_v1_api.py tests\architecture\test_replay_snapshot_v1_execution_boundary.py tests\architecture\test_admin_replay_snapshot_v1_public_exposure.py --tb=short --long
python -B -c "from app.main import app; paths=app.openapi()['paths']; assert '/v1/astrology/projections' in paths; assert all(path.startswith('/v1/admin/') for path in paths if 'replay' in path); print('openapi smoke ok', sorted(path for path in paths if 'replay' in path or path == '/v1/astrology/projections'))"
```

## Results

| Check | Result | Output summary |
|---|---|---|
| Backend lint | PASS | `All checks passed!` |
| Replay runtime validation | PASS | `22 passed in 5.52s` |
| OpenAPI smoke | PASS | `/v1/astrology/projections` present; replay paths are admin-only |

## OpenAPI smoke paths

```text
/v1/admin/audit/replay_snapshot_v1/{snapshot_id}
/v1/admin/audit/replay_snapshot_v1/{snapshot_id}/replay-attempt
/v1/admin/llm/replay
/v1/astrology/projections
```

## Interpretation

The local CI-equivalent run confirms the backend lint, replay runtime validation and OpenAPI smoke checks needed for the CS-256 to CS-291 closure report.
It does not replace a hosted CI system; if a CI system is added later, attach the remote run URL to the release checklist.
