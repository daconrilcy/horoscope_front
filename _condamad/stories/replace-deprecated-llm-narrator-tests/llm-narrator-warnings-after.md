# Baseline after replacing deprecated LLMNarrator tests

Command:
```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q -W error::DeprecationWarning tests/unit/prediction
```

Exit code: 0

Output:
```text
.....................................................                    [100%]
53 passed in 2.00s
```
