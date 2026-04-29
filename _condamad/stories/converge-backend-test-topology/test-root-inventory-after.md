# Test Root Inventory After

Static inventory from:

`rg --files backend -g test_*.py -g *_test.py -g !.tmp-pytest/**`

| Parent directory | Test files |
|---|---:|
| `backend/app/tests` | 2 |
| `backend/app/tests/integration` | 119 |
| `backend/app/tests/regression` | 1 |
| `backend/app/tests/unit` | 207 |
| `backend/app/tests/unit/legacy_services` | 2 |
| `backend/app/tests/unit/prediction` | 2 |
| `backend/app/tests/unit/services` | 2 |
| `backend/tests/evaluation` | 3 |
| `backend/tests/integration` | 25 |
| `backend/tests/llm_orchestration` | 40 |
| `backend/tests/unit` | 12 |
| `backend/tests/unit/prediction` | 12 |

Total: 427 files.
