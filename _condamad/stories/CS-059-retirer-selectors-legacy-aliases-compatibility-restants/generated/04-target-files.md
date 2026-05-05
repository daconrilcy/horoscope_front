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

- `frontend/src/App.css`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/pages/admin/AdminPromptsPage.css`

## Forbidden or high-risk files

- backend/ hors scope sans justification explicite
- contrats API et dependances hors scope
- fichiers frontend non lies aux guardrails design-system de la story