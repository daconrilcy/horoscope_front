<!-- Inventaire apres migration CS-033 des valeurs visuelles et typographiques hardcodees. -->

# CS-033 Hardcoded Values After

Lot migre:

- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/UserMenu/UserMenu.css`

Resultat apres:

- `Select.css`: fallbacks retires pour `--space-*`, `--font-*`, `--line-height-*`, `--color-*`, `--radius-*`, `--shadow-card`, `--duration-fast`, `--easing-default`; deux fallbacks restent car classes par CS-035 (`--z-index-dropdown`, `--color-bg-surface`).
- `UserMenu.css`: fallbacks retires pour `--space-*`, `--radius-lg`, `--font-*`, `--primary`; ombre directe remplacee par `var(--shadow-card)`; duree directe remplacee par `var(--duration-fast) var(--easing-default)`.
- Aucun namespace de token nouveau n'a ete cree.

Commandes de preuve:

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens
npm run lint
Pop-Location
```

Resultats:

- `npm run test -- inline-style css-fallback design-system` - PASS, 3 fichiers, 11 tests.
- `npm run lint` - PASS.
- `npm run test` - PASS, 113 fichiers, 1234 tests passes, 8 skips existants.

Differences autorisees:

- `--color-bg-surface` et `--z-index-dropdown` restent avec fallback literal dans `Select.css`, documentes dans `frontend/src/styles/css-fallback-allowlist.md`.
