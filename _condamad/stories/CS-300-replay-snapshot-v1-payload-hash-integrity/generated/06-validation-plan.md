# Validation Plan

## Targeted checks

```bash
python -B -m pytest -q tests\unit\test_replay_snapshot_v1_execution_audit.py --tb=short
python -B -m pytest -q tests\integration\test_replay_snapshot_v1_db_redaction.py --tb=short --long
python -B -m pytest -q tests\unit\test_replay_snapshot_v1_redaction.py --tb=short
python -B -m pytest -q tests\api\admin\test_replay_snapshot_v1_api.py --tb=short
python -B -m pytest -q tests\architecture\test_replay_snapshot_v1_execution_boundary.py --tb=short
python -B -m pytest -q tests\architecture\test_admin_replay_snapshot_v1_public_exposure.py --tb=short
```

## Early guard scans

Run these before expensive test suites and fix failures first.

```bash
rg -n "encrypt_input\(user_input\)" backend\tests\unit\test_replay_snapshot_v1_execution_audit.py
rg -n '"/v1/replay_snapshot_v1"|"/v1/public/replay_snapshot_v1"|"/api/replay_snapshot_v1"|"/replay_snapshot_v1"' backend\app
git diff --check
```

## Lint / static checks

```bash
ruff check .
```

## Full regression checks

```bash
python -B -m pytest -q backend\tests\unit\test_replay_snapshot_v1_storage_security_model.py backend\tests\unit\test_replay_snapshot_v1_storage.py backend\tests\unit\test_replay_snapshot_v1_service_retention.py backend\tests\unit\test_replay_snapshot_v1_service_ownership.py backend\tests\unit\test_replay_snapshot_v1_service_metadata.py backend\tests\unit\test_replay_snapshot_v1_service_manual_purge.py backend\tests\unit\test_replay_snapshot_v1_service_audit.py backend\tests\unit\test_replay_snapshot_v1_retention.py backend\tests\unit\test_replay_snapshot_v1_redaction.py backend\tests\unit\test_replay_snapshot_v1_purge.py backend\tests\unit\test_replay_snapshot_v1_ownership.py backend\tests\unit\test_replay_snapshot_v1_execution_audit.py backend\tests\integration\test_replay_snapshot_v1_service_purge.py backend\tests\integration\test_replay_snapshot_v1_service_non_cascade.py backend\tests\integration\test_replay_snapshot_v1_db_redaction.py --tb=short --long
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
