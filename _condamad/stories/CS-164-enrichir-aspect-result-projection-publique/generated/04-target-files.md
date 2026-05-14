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

- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_aspects_calculator.py`
- `backend/app/tests/unit/test_chart_result_service.py`

## Forbidden or high-risk files

- `backend/app/domain/prediction/**`: no prediction ownership transfer.
- `backend/migrations/**`: no database shape change.
- `frontend/**`: public payload is produced server-side only.
