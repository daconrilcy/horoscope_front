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

- `frontend/src/components/prediction/PeriodCard.css`
- `frontend/src/components/prediction/KeyPointCard.css`
- `frontend/src/components/prediction/CategoryGrid.css`
- `frontend/src/components/prediction/DayPredictionCard.css`
- `frontend/src/components/TurningPointCard.css`

## Forbidden or high-risk files

- backend/ hors scope sans justification explicite
- contrats API et dependances hors scope
- fichiers frontend non lies aux guardrails design-system de la story