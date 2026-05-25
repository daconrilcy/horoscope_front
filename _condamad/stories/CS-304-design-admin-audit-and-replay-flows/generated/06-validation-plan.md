# Validation Plan

## Targeted checks

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q tests/api/admin/test_rejected_answer_review_workflow.py --tb=short
python -B -m pytest -q tests/api/admin/test_replay_snapshot_v1_api.py --tb=short
```

## Runtime contract checks

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -c "from app.main import app; ..."
```

Required assertions:

- consumed answer-audit and replay-snapshot paths are present in `app.routes`;
- consumed answer-audit and replay-snapshot paths are present in `app.openapi()`;
- consumed paths remain under `/v1/admin/`;
- forbidden route families `/v1/replay_snapshot_v1`, `/api/replay_snapshot_v1`, replay public and replay support paths are absent.

## Documentation and sensitive-field checks

```powershell
.\.venv\Scripts\Activate.ps1
python -B -c "from pathlib import Path; ..."
rg -n "visible_fields.*(raw|birth_date|birth_time|birth_place|birth_lat|birth_lon|birth_timezone|secret|provider token|payload)" docs\architecture\admin-audit-replay-flows.md
rg -n "raw prompt|raw provider payload|raw AI answer|raw birth|exact coordinates|secrets|API keys|credentials|provider tokens" docs\architecture\admin-audit-replay-flows.md
```

## Static checks

```powershell
git diff --check
```

`ruff check` is not applicable for this implementation because no Python file changed. Existing backend behavior is covered by the targeted pytest commands above.

## Capsule validation

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-304-design-admin-audit-and-replay-flows
```
