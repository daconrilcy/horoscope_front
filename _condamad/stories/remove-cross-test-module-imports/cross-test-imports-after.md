# Cross-test imports after

Command from `backend/` after implementation:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
rg -n "from app\.tests\.(integration|unit|regression)\.test_|from tests\.integration\.test_" app/tests tests -g test_*.py
```

Result: zero hit. `rg` returned exit code 1 because no matching line was found.
