# Target Files

## Must inspect before implementation

- `AGENTS.md`
- `backend/docs/ownership-index.md`
- `backend/docs/llm-db-cleanup-registry.json`
- `_condamad/stories/CS-022-uniformiser-gouvernance-docs-llm-source-truth/llm-doc-governance.md`
- `backend/app/tests/unit/test_backend_docs_ownership.py`
- `backend/app/tests/unit/test_llm_docs_governance.py`
- `backend/tests/integration/test_llm_db_cleanup_registry.py`

## Required searches before editing

```bash
rg -n "llm-db-governance|llm-runtime-source-of-truth|llm-canonical-consumption-rebuild" backend docs _condamad/stories
rg -n "legacy|compat|shim|fallback|deprecated|alias" backend/app backend/tests backend/docs docs _condamad/stories/CS-024-repositionner-notes-llm-non-canoniques
```

## Likely modified files

- `docs/llm/llm-db-governance.md`
- `docs/llm/llm-runtime-source-of-truth.md`
- `docs/llm/llm-canonical-consumption-rebuild.md`
- `backend/docs/ownership-index.md`
- `backend/docs/llm-db-cleanup-registry.json`
- `_condamad/stories/CS-022-uniformiser-gouvernance-docs-llm-source-truth/llm-doc-governance.md`
- `backend/app/tests/unit/test_llm_docs_governance.py`

## Forbidden or high-risk files

- `backend/app/domain/llm/**`
- `backend/migrations/**`
- `frontend/src/**`
- Old backend doc copies for the three moved LLM notes.
