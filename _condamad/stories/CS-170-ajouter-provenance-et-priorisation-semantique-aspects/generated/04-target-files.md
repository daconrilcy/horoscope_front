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

- `backend/app/domain/astrology/interpretation/aspect_semantic_provenance.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_contracts.py`
- `backend/app/domain/astrology/interpretation/__init__.py`
- `backend/tests/unit/domain/astrology/test_aspect_semantic_provenance.py`
- `backend/tests/unit/domain/astrology/test_aspect_interpretation_facts.py`

## Forbidden or high-risk files

- `backend/app/domain/prediction/**`: semantic candidate prioritization is domain astrology only.
- `backend/migrations/**`: provenance has no persistence change.
- `frontend/**`: no presentation change.
