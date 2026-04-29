# Test Root Inventory Before

Static inventory from:

`rg --files backend -g test_*.py -g *_test.py -g !.tmp-pytest/**`

| Parent directory | Test files |
|---|---:|
| `backend/app/domain/llm/prompting/tests` | 1 |
| `backend/app/tests` | 2 |
| `backend/app/tests/integration` | 119 |
| `backend/app/tests/regression` | 1 |
| `backend/app/tests/unit` | 206 |
| `backend/app/tests/unit/legacy_services` | 2 |
| `backend/app/tests/unit/prediction` | 2 |
| `backend/app/tests/unit/services` | 2 |
| `backend/tests/evaluation` | 3 |
| `backend/tests/integration` | 25 |
| `backend/tests/llm_orchestration` | 39 |
| `backend/tests/unit` | 12 |
| `backend/tests/unit/prediction` | 12 |

Total: 426 files.
