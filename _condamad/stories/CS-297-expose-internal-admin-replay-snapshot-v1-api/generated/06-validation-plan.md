# Validation Plan

## Targeted checks

```bash
python -B -m pytest -q tests\api\admin\test_replay_snapshot_v1_api.py tests\architecture\test_admin_replay_snapshot_v1_public_exposure.py --tb=short
```

## Early guard scans

Run these before expensive test suites and fix failures first.

```bash
python -c "from app.main import app; assert all(p.startswith('/v1/admin/audit') for p in app.openapi()['paths'] if 'replay_snapshot_v1' in p)"
python -c "from app.main import app; assert not any(getattr(r,'path','') in {'/v1/replay_snapshot_v1','/replay_snapshot_v1'} for r in app.routes)"
rg -n "/v1/replay_snapshot_v1|/v1/public/replay_snapshot_v1|/v1/support/replay_snapshot_v1|/api/replay_snapshot_v1" backend/app frontend/src
git diff --check
```

## Lint / static checks

```bash
ruff check .
ruff format .
```

## Full regression checks

```bash
python -B -m pytest -q --tb=short
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
