<!-- Inventaire before des fallbacks CSS pour CS-064. -->

# CSS Fallbacks Before

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
src\pages\admin\AdminEntitlementsPage.css:44:  background: var(--glass-heavy, #1a1a1a);
```

Classification:

| File | Token | Literal | Classification | Decision | Proof |
|---|---|---|---|---|---|
| `frontend/src/App.css` | `--usage-progress` | `0` | dynamic runtime bridge | keep | progression injectee par propriete CSS runtime |
| `frontend/src/pages/settings/Settings.css` | `--usage-progress` | `0` | dynamic runtime bridge | keep | progression injectee par propriete CSS runtime |
| `frontend/src/pages/admin/AdminEntitlementsPage.css` | `--glass-heavy` | `#1a1a1a` | migration-only | delete fallback | `--glass-heavy` est declare comme token canonique dans `design-tokens.css` avant consommation sans fallback |
