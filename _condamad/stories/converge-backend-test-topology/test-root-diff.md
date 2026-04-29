# Test Root Diff

| Parent directory | Before | After | Difference | Classification |
|---|---:|---:|---:|---|
| `backend/app/domain/llm/prompting/tests` | 1 | 0 | -1 | Embedded test root removed from active test inventory. |
| `backend/tests/llm_orchestration` | 39 | 40 | +1 | `test_qualified_context.py` moved into documented LLM orchestration root. |
| `backend/app/tests/unit` | 206 | 207 | +1 | New topology guard `test_backend_test_topology.py`. |
| Other documented roots | unchanged | unchanged | 0 | No unrelated test movement. |

Net change: +1 active test file, caused by the new topology guard.
