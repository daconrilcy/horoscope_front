# Implementation Plan

## Current architecture finding

- LLM generated/executable artifacts are allowed under `backend/docs/`.
- Human non-canonical LLM notes belong under `docs/llm/`.

## Selected target approach

- Move the three human notes.
- Update the existing governance registry and JSON cleanup registry.
- Extend the existing LLM docs guard instead of adding a second registry.

## Files to modify

- `docs/llm/*.md`
- `backend/docs/ownership-index.md`
- `_condamad/stories/CS-022-uniformiser-gouvernance-docs-llm-source-truth/llm-doc-governance.md`
- `backend/docs/llm-db-cleanup-registry.json`
- `backend/app/tests/unit/test_llm_docs_governance.py`

## Tests to add or update

- Update `test_llm_docs_governance.py` to include `docs/llm/` and forbid old paths.

## Deletion candidates

- Old `backend/docs/llm-*.md` human note paths only.

## Risk assessment

- Registry path drift is covered by integration test.

## Rollback strategy

- Restore old paths and registry rows if `docs/llm/` is rejected.
