# Validation plan - CS-298

Executed:
- `ruff format <modified python files>`
- `ruff check .` from `backend`
- `python -B -m pytest -q tests\unit\test_replay_snapshot_v1_execution_audit.py tests\architecture\test_replay_snapshot_v1_execution_boundary.py tests\api\admin\test_replay_snapshot_v1_api.py ... --tb=short`
- `python -B -m pytest -q --tb=short` from `backend`
- `python -B -c "from app.main import app; assert all('/admin/' in p for p in app.openapi()['paths'] if 'replay_snapshot_v1' in p)"`
- `python -B -c "from app.main import app; assert not any(getattr(r,'path','') == '/replay_snapshot_v1' for r in app.routes)"`
- `git diff --check`
- scoped sensitive field scan on touched app files
- `condamad_validate.py`
- `condamad_story_validate.py`
- `condamad_story_lint.py --strict`

Skipped:
- none.
