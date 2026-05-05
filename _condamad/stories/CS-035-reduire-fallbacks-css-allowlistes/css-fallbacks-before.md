<!-- Inventaire avant migration CS-035 des fallbacks CSS allowlistes. -->

# CS-035 CSS Fallbacks Before

Lot selectionne:

- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/UserMenu/UserMenu.css`

Commande:

```powershell
Push-Location frontend
rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," src/components/ui/Select/Select.css src/components/ui/UserMenu/UserMenu.css
Pop-Location
```

Resultat initial:

- `Select.css`: fallbacks nombreux pour tokens requis (`--space-*`, `--font-*`, `--color-*`, `--radius-*`, `--shadow-card`, `--duration-fast`, `--easing-default`) plus exceptions de surface (`--z-index-dropdown`, `--color-bg-surface`).
- `UserMenu.css`: fallbacks pour tokens requis (`--space-*`, `--radius-lg`, `--font-*`, `--primary`).

Statuts:

- migration-only: fallbacks des tokens globaux requis deja declares.
- compatibility/semantic-extension: `--z-index-dropdown` et `--color-bg-surface`.
