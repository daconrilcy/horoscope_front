# Baseline before replacing deprecated LLMNarrator tests

Command:
```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q tests/unit/prediction/test_llm_narrator.py
```

Exit code: 0

Output:
```text
........                                                                 [100%]
8 passed in 1.16s
```
