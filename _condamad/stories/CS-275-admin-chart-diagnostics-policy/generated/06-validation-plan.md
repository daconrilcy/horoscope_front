# Validation Plan

## Targeted checks

```bash
cd backend
ruff check tests/unit/test_admin_chart_diagnostics_policy.py
python -B -m pytest -q tests/unit/test_admin_chart_diagnostics_policy.py --tb=short
python -B -c "from app.main import app; assert 'admin_chart_diagnostics' not in str(app.openapi())"
python -B -c "from app.main import app; assert all('admin_chart_diagnostics' not in getattr(r, 'path', '') for r in app.routes)"
```

## Early guard scans

Run these before expensive test suites and fix failures first.

```bash
rg -n "admin_chart_diagnostics_v1|retention|DPO-open|redaction|replay|storage owner|input reconstruction|version identity|retention approval|purge rules|actor|role|action|decision|timestamp|correlation id" docs/architecture/admin-chart-diagnostics-v1-policy.md
rg -n "admin_chart_diagnostics" backend/app/api backend/app/services backend/app/infra/db backend/migrations frontend/src -g "*.py" -g "*.ts" -g "*.tsx" -g "*.md"
git diff --check -- docs/architecture/admin-chart-diagnostics-v1-policy.md backend/tests/unit/test_admin_chart_diagnostics_policy.py _condamad/stories/CS-275-admin-chart-diagnostics-policy
```

## Lint / static checks

```bash
cd backend
ruff format tests/unit/test_admin_chart_diagnostics_policy.py
ruff check tests/unit/test_admin_chart_diagnostics_policy.py
```

## Full regression checks

```bash
Not required for this documentation-only story. Targeted pytest plus runtime
OpenAPI/route checks cover the changed surface; full suite is skipped because
the workspace contains substantial unrelated in-progress changes.
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
