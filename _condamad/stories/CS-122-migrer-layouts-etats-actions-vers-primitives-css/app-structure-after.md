# Mapping structure App apres CS-122

| Famille | Surface canonique | Preuve |
|---|---|---|
| Page / section | `.app-page`, `.app-section` | `frontend/src/App.css` |
| Stack / grid / list | `.app-stack`, `.app-grid`, `.app-list` | `frontend/src/App.css` et consumers TSX modifies |
| Etats | `.app-state` + variantes | `frontend/src/tests/design-system-guards.test.ts` |
| Actions | `.app-actions`, `.app-action--danger` | `frontend/src/App.css` et consumers TSX modifies |

Scans apres implementation:

- `rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css` depuis `frontend`: zero hit.
- `npm run test -- design-system visual-smoke App router`: couvert par validations finales ciblees et suite complete.

