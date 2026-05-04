# Validation Plan

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| LLM docs governance | `pytest -q app/tests/unit/test_llm_docs_governance.py` | `backend` | yes | pass |
| Generated model structure | `pytest -q tests/unit/test_llm_canonical_perimeter.py` | `backend` | yes | pass |
| Cleanup registry | `pytest -q tests/integration/test_llm_db_cleanup_registry.py` | `backend` | yes | pass |
| Runtime LLM governance | `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py` | `backend` | yes | pass |
| Full backend regression | `pytest -q` | `backend` | yes | pass |
