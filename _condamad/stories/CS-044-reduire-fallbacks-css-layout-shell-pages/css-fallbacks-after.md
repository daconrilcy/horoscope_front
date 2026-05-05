<!-- Inventaire final des fallbacks CSS du lot CS-044. -->

# CS-044 CSS Fallbacks After

Commande:

```powershell
rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," frontend/src/App.css frontend/src/components/layout/Header.css frontend/src/components/layout/Sidebar.css frontend/src/pages/HelpPage.css frontend/src/pages/settings/Settings.css frontend/src/styles/glass.css frontend/src/styles/utilities.css
```

## Resultat

```text
frontend/src/pages/settings/Settings.css:1052:  width: calc(var(--usage-progress, 0) * 1%);
frontend/src/App.css:3596:  width: calc(var(--usage-progress, 0) * 1%);
```

## Decisions finales

- `App.css`: tous les fallbacks statiques ont ete migres vers `var(--token)`; `--usage-progress` reste `dynamic`.
- `Header.css`: tous les fallbacks du lot ont ete migres vers `var(--token)`.
- `Sidebar.css`: tous les fallbacks du lot ont ete migres vers `var(--token)`.
- `HelpPage.css`: les aliases `--settings-text-*` ont ete remplaces par les tokens canoniques directs `--text-1` et `--text-2`.
- `Settings.css`: les fallbacks statiques ont ete migres; `--usage-progress` reste `dynamic`.
- `glass.css` et `utilities.css`: `--surface-glass-blur` est consomme sans fallback literal.

Zero `unclassified`, `TODO` ou `TBD`.
