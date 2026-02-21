# Development Guide - Backend

## Prerequisites
- Python 3.13
- PowerShell (Windows target)
- Virtual environment at repo root: `.venv`

## Setup
```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pip install -e ".[dev]"
```

## Run
```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m uvicorn app.main:app --reload
```

## Quality
```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
pytest -q
```

## Migrations
```powershell
.\.venv\Scripts\Activate.ps1
cd backend
alembic upgrade head
```

## Operational Scripts (repo root)
- `scripts/quality-gate.ps1`
- `scripts/predeploy-check.ps1`
- `scripts/security-verification.ps1`
- `scripts/backup-db.ps1` / `scripts/restore-db.ps1`
- `scripts/load-test-critical.ps1`
