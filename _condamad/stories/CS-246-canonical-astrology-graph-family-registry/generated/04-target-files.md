# Target Files

## Must inspect before implementation

- `AGENTS.md` files in scope
- Files and directories named by `../00-story.md`
- Existing tests near the affected code

## Required searches before editing

```bash
rg "<main symbol or feature name>" .
rg "legacy|compat|shim|fallback|deprecated|alias" .
```

Adapt searches to the story and repository layout.

## Likely modified files

- `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`
- `backend/tests/unit/domain/astrology/test_astrology_graph_family_registry.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `backend/tests/architecture/test_astrology_runtime_boundary.py`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/evidence/validation.md`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/evidence/openapi-routes.md`
- `_condamad/stories/CS-246-canonical-astrology-graph-family-registry/evidence/family-registry.md`
- `_condamad/stories/story-status.md`

## Forbidden or high-risk files

- `frontend/**`: forbidden by story and unchanged.
- `backend/app/api/**`: forbidden for route changes and unchanged.
- `backend/migrations/**`: forbidden by story and unchanged.
- `backend/app/infra/**`: forbidden by story and unchanged.
