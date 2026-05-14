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

- `backend/app/domain/astrology/runtime/aspect_modifiers.py`
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py`
- `backend/app/domain/astrology/interpretation/aspect_strength_contracts.py`
- `backend/app/domain/astrology/interpretation/aspect_strength.py`
- `backend/tests/unit/domain/astrology/test_aspect_modifiers.py`
- `backend/tests/unit/domain/astrology/test_aspect_strength.py`

## Forbidden or high-risk files

- `backend/app/domain/prediction/**`: no prediction weight field or product scoring.
- `backend/migrations/**`: taxonomy is runtime/domain only.
- `frontend/**`: no UI change.
