<!-- Inventaire after des fallbacks CSS pour CS-064. -->

# CSS Fallbacks After

Commande:

```powershell
Push-Location frontend
rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," src -g "*.css"
Pop-Location
```

Resultat:

```text
src\App.css:3128:  width: calc(var(--usage-progress, 0) * 1%);
src\pages\settings\Settings.css:1052:  width: calc(var(--usage-progress, 0) * 1%);
```

Differences autorisees:

- `var(--glass-heavy, #1a1a1a)` a disparu de `AdminEntitlementsPage.css`.
- Les deux ponts runtime `--usage-progress` restent classes.
