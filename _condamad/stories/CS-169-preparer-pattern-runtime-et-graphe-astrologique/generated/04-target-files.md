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

- `backend/app/domain/astrology/runtime/pattern_runtime_data.py`
- `backend/app/domain/astrology/runtime/astrological_graph_contracts.py`
- `backend/app/domain/astrology/runtime/__init__.py`
- `backend/tests/unit/domain/astrology/test_pattern_runtime_contract.py`
- `backend/tests/unit/domain/astrology/test_astrology_public_exports.py`

## Forbidden or high-risk files

- `backend/app/domain/prediction/**`: graph readiness contracts remain astrology runtime owned.
- `backend/app/api/**`: no graph endpoint exposed by this story.
- `frontend/**`: no graph visualization in scope.
