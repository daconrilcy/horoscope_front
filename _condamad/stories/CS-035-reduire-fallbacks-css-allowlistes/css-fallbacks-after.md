<!-- Inventaire apres migration CS-035 des fallbacks CSS allowlistes. -->

# CS-035 CSS Fallbacks After

Lot migre:

- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/UserMenu/UserMenu.css`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`

Resultat apres:

- `UserMenu.css`: zero fallback `var(--token, value)` restant.
- `Select.css`: deux fallbacks restants et classes exactement:
  - `--z-index-dropdown, 1000` comme extension semantique existante.
  - `--color-bg-surface, #ffffff` comme compatibility documentee pour composant UI isolable.
- `CSS_FALLBACK_EXCEPTIONS` a ete reduit pour retirer les fallbacks migres de `Select.css` et `UserMenu.css`.
- `css-fallback-allowlist.md` documente l'exception `--color-bg-surface`.

Commandes de preuve:

```powershell
Push-Location frontend
rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," src/components/ui/Select/Select.css src/components/ui/UserMenu/UserMenu.css
npm run test -- css-fallback design-system
npm run lint
Pop-Location
```

Resultats:

- Scan cible - PASS avec seulement les deux exceptions classees dans `Select.css`.
- `npm run test -- inline-style css-fallback design-system` - PASS, 3 fichiers, 11 tests.
- `npm run lint` - PASS.

Differences autorisees:

- Aucun fallback de token requis conserve dans le lot; seules les deux exceptions classees restent.
