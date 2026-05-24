# Validation Plan

## Targeted checks

```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH='backend'
python -B -m pytest -q backend\tests\unit\domain\astrology\test_astrology_doctrine_governance.py
python -B -m pytest -q backend\tests\architecture\test_astrology_doctrine_governance_guardrails.py
python -B -m pytest -q backend\tests\architecture\test_api_contract_neutrality.py
```

## Architecture / negative scans

```powershell
rg -n "needs-user-decision|DB-owned|Python-owned|mixed|documentation-only|test-only" backend\app\domain\astrology\runtime backend\tests
rg -n "CS-253|temporal technique|Traditional, modern, and forecasting" backend\app\domain\astrology\runtime\astrology_doctrine_governance.py backend\tests\unit\domain\astrology\test_astrology_doctrine_governance.py
rg -n "doctrine-governance|DoctrineGovernance" backend\app\api frontend backend\alembic docs\db_seeder -g "*.py" -g "*.ts" -g "*.tsx" -g "*.json"
```

## Lint / static checks

```powershell
ruff format backend\app\domain\astrology\runtime\astrology_doctrine_governance.py backend\app\domain\astrology\runtime\__init__.py backend\tests\unit\domain\astrology\test_astrology_doctrine_governance.py backend\tests\architecture\test_astrology_doctrine_governance_guardrails.py backend\tests\architecture\test_api_contract_neutrality.py
ruff check backend
```

## Full regression checks

```powershell
python -B -m pytest -q backend\tests
```
