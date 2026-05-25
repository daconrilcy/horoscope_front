# Validation Plan

## Targeted Checks

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend\tests\unit\test_replay_snapshot_v1_storage_security_model.py
ruff check backend\tests\unit\test_replay_snapshot_v1_storage_security_model.py
python -B -m pytest -q backend\tests\unit\test_replay_snapshot_v1_storage_security_model.py --tb=short
```

## Runtime Neutrality

```powershell
cd backend
..\.venv\Scripts\Activate.ps1
python -B -c "from app.main import app; assert 'replay_snapshot_v1' not in str(app.openapi())"
python -B -c "from app.main import app; assert 'replay_snapshot_v1' not in {getattr(r, 'path', '') for r in app.routes}"
```

Actual command used `..\.venv\Scripts\Activate.ps1` from `backend`.

## Static / Guard Scans

```powershell
rg -n "replay_snapshot_v1|snapshot|stockage|sécurité|rétention|audit IA|diagnostics" docs _story_briefs
rg -n "replay_snapshot_v1" backend\app frontend\src backend\migrations -g "!**/__pycache__/**" -g "!**/.pytest_cache/**" -g "!**/.ruff_cache/**"
git status --short -- backend\app frontend\src
git diff --check -- docs\architecture\replay-snapshot-v1-storage-security-model.md backend\tests\unit\test_replay_snapshot_v1_storage_security_model.py _condamad\stories\CS-277-replay-snapshot-v1-storage-security-model _condamad\stories\story-status.md
```

For the negative `rg` over runtime surfaces, exit code 1 means PASS/no matches.

## Broader Checks Not Run

- Full `ruff check .`: skipped because this story adds one Python test and the worktree contains many pre-existing unrelated dirty files from prior stories.
- Full `python -B -m pytest -q --tb=short`: skipped for the same unrelated dirty-worktree risk; targeted contract tests and loaded FastAPI runtime checks cover CS-277 scope.
