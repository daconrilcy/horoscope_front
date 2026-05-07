<!-- Evidence apres migration du cluster admin CS-086. -->

# CS-086 Hardcoded Values After

## Scope

La migration reste bornee a:

- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/pages/admin/*.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`

## Final decisions

| Decision | Owner | Evidence |
|---|---|---|
| `migrated` | tokens globaux existants | `--color-glass-*`, `--color-text-*`, `--font-weight-*`, `--font-size-*`, `--space-*`, `--radius-*`, `--shadow-*` consommes par le cluster admin. |
| `registered-semantic-owner` | `frontend/src/styles/design-tokens.css` | nouveaux tokens `--type-admin-*`, `--radius-admin-*`, `--shadow-admin-*`, `--color-admin-*` et `--space-px`. |
| `registered-semantic-owner` | `frontend/src/styles/token-namespace-registry.md` | namespaces `--type-admin-*`, `--radius-admin-*`, `--shadow-admin-*` documentes. |
| `registered-semantic-owner` | `frontend/src/styles/typography-roles.md` | roles `admin-compact` et `admin-control` documentes. |
| `runtime-custom-property` | none | Aucun nouveau custom property runtime ajoute. |
| `kept-one-off-final` | `AdminPromptsPage.css` | selecteurs `fallback` conserves comme vocabulaire metier du graphe de prompts, pas comme mecanisme CSS de compatibilite. |

## Guard source

La garde executable `frontend/src/tests/design-system-guards.test.ts` bloque:

- couleurs brutes `hex`, `rgb(a)`, `hsl(a)` dans les CSS admin;
- `box-shadow` non tokenise;
- `border-radius` literal;
- `font-size`, `font-weight`, `line-height`, `letter-spacing` literals;
- fallback CSS literal `var(--token, value)`;
- consommation de namespaces page-scoped non admin;
- exemples d'espacements migres: `padding: 4px 12px`, `padding: 0.75rem 1rem`, `gap: 2px`, `margin: 0 0 4px`, `margin-bottom: 0.25rem`, `padding-left: 1.5rem`, `margin-top: 0.5rem`.

## After scans

| Command | Result | Classification |
|---|---|---|
| `rg -n "var\(\s*--[a-zA-Z0-9_-]+\s*," src/layouts/AdminLayout.css src/pages/admin -g "*.css"` | zero hit | `PASS` - aucun fallback CSS literal. |
| `rg -n --glob "*.css" -- "--settings-\|--help-\|--chat-\|--app-\|--landing-" src/layouts/AdminLayout.css src/pages/admin` | zero hit | `PASS` - aucun namespace page-scoped non admin. |
| `rg -n --glob "*.css" "#[0-9A-Fa-f]{3,8}\|rgba?\(\|hsla?\(" src/layouts/AdminLayout.css src/pages/admin` | zero hit | `PASS` - les couleurs brutes admin ont migre vers tokens ou `color-mix`. |
| `rg -n "padding:\s*(?:4px 12px\|0\.75rem 1rem)\|gap:\s*2px\|margin:\s*0 0 4px\|margin-bottom:\s*0\.25rem\|padding-left:\s*1\.5rem\|margin-top:\s*0\.5rem" src/layouts/AdminLayout.css src/pages/admin -g "*.css"` | zero hit | `PASS` - les espacements exacts migres ne reviennent pas. |
| `rg -n "legacy\|Legacy\|alias\|compat\|compatibility\|shim\|fallback\|migration-only\|TODO" src/layouts/AdminLayout.css src/pages/admin -g "*.css"` | 9 hits | `PASS` - hits limites aux selecteurs metier `AdminPromptsPage.css` `logic-graph/*fallback*`, couverts par tests admin prompts existants et non lies a une compatibilite CSS. |

## Allowed differences

- Les differences visuelles autorisees sont les substitutions tokenisees equivalentes vers `--color-admin-*`, `--radius-admin-*`, `--shadow-admin-*`, `--type-admin-*`, `--font-*`, `--space-*` et `--color-glass-*`.
- Aucun changement React, route, client API, permission, store ou backend.
