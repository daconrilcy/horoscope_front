# Validation Plan

## Environment assumptions

- PowerShell on Windows.
- All Python, Ruff, and Pytest commands run after `.\.venv\Scripts\Activate.ps1`.
- Backend commands run from `backend/` after activation.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| OpenAPI path smoke | `python -B -c "from app.main import app; paths = app.openapi()['paths']; assert '/api/email/unsubscribe' in paths"` | `backend/` | yes | kept route is exposed |
| Consumer scan | `rg -n "api/email/unsubscribe|/email/unsubscribe|get_unsubscribe_link|unsubscribe_url" ..\backend ..\frontend ..\_condamad` | `backend/` | yes | hits are classified in audit/evidence |
| Duplicate handler scan | `rg -n "def unsubscribe|/unsubscribe|api/email/unsubscribe" ..\backend\app` | `backend/` | yes | only registered route, route exception, and link generation are active |

## Unit tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Route architecture guard | `pytest -q app/tests/unit/test_api_router_architecture.py` | `backend/` | yes | exact exception register passes |

## Integration tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Public unsubscribe behavior | `pytest -q tests/integration/test_email_unsubscribe.py` | `backend/` | yes | existing behavior remains unchanged |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend/` | yes | no formatting drift remains |
| Lint | `ruff check .` | `backend/` | yes | no lint errors |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-scoped files changed |
| Whitespace/conflict check | `git diff --check` | repo root | yes | no whitespace errors or conflict markers |
| Final status | `git status --short` | repo root | yes | expected files only |
