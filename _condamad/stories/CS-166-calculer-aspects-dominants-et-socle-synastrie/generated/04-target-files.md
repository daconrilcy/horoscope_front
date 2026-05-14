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

- `backend/app/domain/astrology/interpretation/dominant_aspects.py`
- `backend/app/domain/astrology/runtime/dominant_aspect_runtime_data.py`
- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/domain/astrology/calculators/__init__.py`
- `backend/tests/unit/domain/astrology/test_dominant_aspects.py`
- `backend/tests/unit/domain/astrology/test_interchart_aspects.py`

## Forbidden or high-risk files

- `backend/app/domain/prediction/**`: dominant aspect runtime must not become prediction ownership.
- `backend/migrations/**`: no persistence change.
- `frontend/**`: no UI behavior in scope.
