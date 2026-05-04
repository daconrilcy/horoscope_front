<!-- Baseline des valeurs hardcodees repetees avant migration CS-027. -->

# Hardcoded Values Before

Scope:

- `frontend/src/App.css`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/AstrologerProfilePage.css`

Valeurs ciblees:

- `border-radius: 999px;`
- `gap: 8px;`
- `gap: 12px;`

Ces valeurs etaient presentes dans le lot avant migration et ont ete retenues
car leur remplacement par `--radius-full`, `--space-2` et `--space-3` est exact.
