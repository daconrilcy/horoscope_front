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

- `backend/app/domain/astrology/runtime/aspect_runtime_data.py`
- `backend/app/domain/astrology/runtime/__init__.py`
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py`
- `backend/tests/unit/domain/astrology/test_astrology_public_exports.py`

## Forbidden or high-risk files

- `backend/app/domain/prediction/**`: ownership prediction product/editorial, not canonical aspect runtime.
- `backend/migrations/**`: story has no schema change.
- `frontend/**`: story is backend/domain scoped.
