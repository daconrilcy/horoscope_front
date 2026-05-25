# Validation Plan

## Executed Checks

```powershell
.\.venv\Scripts\Activate.ps1; python -B .\.agents\skills\condamad-dev-story\scripts\condamad_prepare.py .\_condamad\stories\CS-271-admin-data-permission-matrix\00-story.md --root . --capsule .\_condamad\stories\CS-271-admin-data-permission-matrix
.\.venv\Scripts\Activate.ps1; python -B .\.agents\skills\condamad-dev-story\scripts\condamad_validate.py .\_condamad\stories\CS-271-admin-data-permission-matrix
.\.venv\Scripts\Activate.ps1; ruff format .\backend\tests\unit\test_admin_permission_matrix_contract.py
.\.venv\Scripts\Activate.ps1; ruff check .\backend\tests\unit\test_admin_permission_matrix_contract.py
.\.venv\Scripts\Activate.ps1; python -B -m pytest -q .\backend\tests\unit\test_admin_permission_matrix_contract.py --tb=short
.\.venv\Scripts\Activate.ps1; python -B -m pytest -q .\backend\tests\unit\test_admin_permission_matrix_contract.py .\backend\tests\unit\test_internal_role_model_contract.py --tb=short
.\.venv\Scripts\Activate.ps1; Set-Location .\backend; ruff check .
.\.venv\Scripts\Activate.ps1; python -B -c "from app.core.rbac import VALID_ROLES; forbidden={'marketer','techno','astro_expert'}; roles={r.lower() for r in VALID_ROLES}; assert forbidden.isdisjoint(roles); assert 'admin' in roles; print('PASS runtime roles unchanged:', sorted(VALID_ROLES))"
rg -n "ADMIN|MARKETER|TECHNO|ASTRO_EXPERT|business|technical|astrology|debug|read|search|export|replay|correct|B2C|OPEN-ADMIN-PERM" .\docs\architecture\admin-permission-matrix.md
git status --short -- backend/app frontend/src backend/migrations
git diff --check -- .\docs\architecture\admin-permission-matrix.md .\backend\tests\unit\test_admin_permission_matrix_contract.py .\_condamad\stories\CS-271-admin-data-permission-matrix
```

## Results

- Capsule preparation: PASS after explicit `--capsule` because the story mentions CS-270 and CS-271.
- Capsule validation before implementation: PASS.
- Python format/lint for modified test: PASS.
- Backend lint from `backend/`: PASS.
- Targeted tests: PASS (`5 passed`, then `9 passed` with CS-270 role model tests).
- Runtime role check: PASS from repository root with venv activated.
- Matrix content `rg`: PASS.
- App-surface status: existing dirty files under `backend/app` and `backend/migrations` predate CS-271; no frontend changes shown.
- Diff whitespace check on CS-271 files: PASS.

## Not Executed

- Full pytest suite not executed: this story is documentation plus a targeted contract test, and the worktree already contains many unrelated modified/untracked backend files from other stories. Compensating evidence is targeted pytest, CS-270 role model pytest, backend ruff, runtime role AST/value check and scoped app-surface status.
- Local app startup not executed: no runtime application code or frontend code was changed by CS-271.
