<!-- Inventaire initial des fallbacks CSS du lot CS-044. -->

# CS-044 CSS Fallbacks Before

Commande:

```powershell
rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," frontend/src/App.css frontend/src/components/layout/Header.css frontend/src/components/layout/Sidebar.css frontend/src/pages/HelpPage.css frontend/src/pages/settings/Settings.css frontend/src/styles/glass.css frontend/src/styles/utilities.css
```

## Resultat

- `frontend/src/App.css`: 21 fallbacks, dont `--usage-progress` runtime.
- `frontend/src/components/layout/Header.css`: 9 fallbacks.
- `frontend/src/components/layout/Sidebar.css`: 6 fallbacks.
- `frontend/src/pages/HelpPage.css`: 11 fallbacks de compatibilite texte.
- `frontend/src/pages/settings/Settings.css`: 3 fallbacks, dont `--usage-progress` runtime.
- `frontend/src/styles/glass.css`: 2 fallbacks `--surface-glass-blur`.
- `frontend/src/styles/utilities.css`: 2 fallbacks `--surface-glass-blur`.

Total initial du lot: 54 fallbacks.

## Classification initiale

- `migrate-token`: fallbacks de tokens deja definis globalement ou localement (`--space-*`, `--radius-*`, `--success`, `--error`, `--duration-normal`, `--surface-glass-blur`, `--settings-purple*`).
- `migrate-token-direct`: fallbacks de compatibilite `HelpPage.css` remplaces par les tokens canoniques directs `--text-1` et `--text-2`.
- `dynamic`: `--usage-progress` dans `App.css` et `Settings.css`, conserve car injecte au runtime.
