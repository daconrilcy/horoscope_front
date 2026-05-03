# Dev-Only Contract

## Classification

`scripts/natal-cross-tool-report-dev.py` is a local backend development diagnostic command. It is not a backend runtime module, API endpoint, production job, or CI command.

## Execution

Run from the repository root after activating the backend virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
python .\scripts\natal-cross-tool-report-dev.py --format both --output-dir .\artifacts\cross-tool
```

## Import boundary

- The script may import `app.tests.golden.pro_fixtures` because its purpose is local comparison against the golden-pro dataset.
- Backend runtime packages under `backend/app` outside `backend/app/tests` must not import `app.tests.golden`.
- The report helper remains `backend/scripts/cross_tool_report.py`, imported as `scripts.cross_tool_report` from backend Python path.
- No root helper `scripts/cross_tool_report.py` is allowed.

## CI boundary

`ensure_dev_only_runtime` rejects CI-like environments (`CI`, `GITHUB_ACTIONS`, `GITLAB_CI`, `BUILD_BUILDID`) before report generation. The dedicated pytest guard verifies `CI=true` rejects the script with a clear dev-only message.
