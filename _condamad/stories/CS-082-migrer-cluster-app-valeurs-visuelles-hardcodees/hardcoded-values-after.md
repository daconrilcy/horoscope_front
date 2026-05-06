<!-- Decisions finales apres migration du cluster App. -->

# CS-082 Hardcoded Values After

Scope: `frontend/src/App.css` uniquement.

## Decisions finales

| Surface | Decision | Owner |
|---|---|---|
| Shell App principal | migrated | `--app-shell-*` dans `#root` |
| Navigation mobile | migrated | `--app-mobile-*`, `--app-bottom-nav-*` |
| Boutons globaux App | migrated | `--app-button-*` |
| Etats loading, empty, success, danger | migrated | `--app-state-*`, `--app-danger-*` |
| Catalogue astrologues page | migrated | `--app-astro-catalog-*` |
| Carte resume dashboard | migrated | `--app-dashboard-summary-*` |
| Valeurs restantes hors sous-surfaces ci-dessus | kept-one-off-final | hors lot CS-082, non modifiees |

## Decisions exactes du lot migre

| Literal / pattern | Decision | Owner |
|---|---|---|
| `22px 18px` | migrated | `--app-shell-main-padding` |
| `48px` | migrated | `--app-shell-sidebar-offset` |
| `16px` navigation inset | migrated | `--app-mobile-nav-inset` via `--space-4` |
| `24px` navigation radius | migrated | `--app-mobile-nav-radius` via `--radius-xl` |
| `10px` navigation padding | migrated | `--app-mobile-nav-padding` |
| `18px` bottom nav item/button radius | migrated | `--app-bottom-nav-item-radius`, `--app-button-radius` |
| Button border/background/shadows | migrated | `--app-button-*` |
| Loading, empty, success, danger surfaces and borders | migrated | `--app-state-*`, `--app-danger-*` |
| Catalogue radial background and atmosphere | migrated | `--app-astro-catalog-*` |
| Catalogue title/copy colors | migrated | `--app-astro-catalog-title-color`, `--app-astro-catalog-copy-color` |
| Dashboard summary background, glow, line, action and shadows | migrated | `--app-dashboard-summary-*` |
| Typography and spacing still present in unrelated selectors | kept-one-off-final | outside CS-082 migrated subset |

## Owners documentes

- `frontend/src/App.css`: declarations `--app-*` dans `#root`.
- `frontend/src/styles/token-namespace-registry.md`: namespace `--app-*` classe `semantic-extension`.
- `frontend/src/tests/design-system-guards.test.ts`: garde anti-retour CS-082.

## Scans apres implementation

- `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/App.css` - PASS, les valeurs migrees apparaissent dans `#root`; les autres hits sont des one-off finaux ou hors lot.
- `rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/App.css` - PASS, les hits restants sont hors lot ou deja tokenises.
- `rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/App.css` - PASS, aucun deuxieme argument dans `var(--app-*)`; les sous-surfaces migrees consomment `var(--app-*)`.
- Suite Vitest design-system complete avec theme tokens, politiques CSS, inline-style, visual-smoke et AdminPromptsPage - PASS.
