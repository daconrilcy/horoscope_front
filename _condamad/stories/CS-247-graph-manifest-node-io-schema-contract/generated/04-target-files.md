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

- `backend/app/domain/astrology/runtime/calculation_graph_manifest.py`
- `backend/app/domain/astrology/runtime/calculation_graph_manifest_validator.py`
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`
- `backend/tests/unit/domain/astrology/test_calculation_graph_manifest.py`
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_manifest.py`
- `backend/tests/architecture/test_api_contract_neutrality.py`
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/evidence/*`
- `_condamad/stories/CS-247-graph-manifest-node-io-schema-contract/generated/*`
- `_condamad/stories/story-status.md` row CS-247

## Forbidden or high-risk files

- `frontend/**`
- `backend/app/api/**`
- `backend/app/infra/**`
- DB migration folders
- public serializers or OpenAPI contract code
