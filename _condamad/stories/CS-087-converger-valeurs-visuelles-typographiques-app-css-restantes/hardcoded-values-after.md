<!-- Decisions finales apres convergence CS-087 de App.css. -->

# CS-087 Hardcoded Values After

Scope: `frontend/src/App.css` uniquement.

## Final decisions

| Surface | Decision | Owner |
|---|---|---|
| Declarations `#root --app-*` | `registered-semantic-owner` | `frontend/src/App.css`, namespace documente dans `token-namespace-registry.md`; noms de roles App sans segments mecaniques repetes |
| Declarations `--astro-*` | `registered-semantic-owner` | `frontend/src/App.css`, namespace documente dans `token-namespace-registry.md` |
| Couleurs, gradients, elevations, radius actifs hors custom properties | `migrated` | variables `--app-*` ou tokens globaux existants |
| Typographie active hors custom properties | `migrated` | variables `--app-*`, tokens `--font-*`, `--line-height-*`, `--letter-spacing-*` |
| Valeurs d'animation/keyframes | `runtime-animation-value` | declarations locales d'animation, hors surfaces visuelles/type migrees |
| Selecteurs d'etat image de remplacement existants | `kept-one-off-final` | etat UI nominal d'image, aucun mecanisme de compatibilite CSS ajoute |

## Guard source

`frontend/src/tests/design-system-guards.test.ts` contient la garde `CS-087` qui parse les declarations CSS et echoue si `App.css` contient une declaration active hors `#root` ou hors custom property avec:

- couleur brute `hex`, `rgb(a)`, `hsl(a)` ou `color-mix`;
- gradient brut;
- `font-size`, `font-weight`, `line-height`, `letter-spacing` non routes;
- `border-radius`, `box-shadow`, `text-shadow` non routes;
- fallback CSS literal `var(--token, value)`.
- nom de variable `--app-*` mecanique avec segment repete ou notation BEM brute.

## After scans

| Command | Result | Classification |
|---|---|---|
| AST declaration scan hors `#root` et hors custom properties | 0 hit | `PASS` - aucune declaration active visuelle/type non routee |
| `rg -n "var\(\s*--[a-zA-Z0-9_-]+\s*," frontend/src/App.css` | hit exact `--usage-progress, 0` | `PASS` - fallback runtime classe dans `css-fallback-allowlist.md` et `CSS_FALLBACK_EXCEPTIONS` |
| `rg -n "#[0-9A-Fa-f]{3,8}\|rgba?\(\|hsla?\(" frontend/src/App.css` | hits limites aux custom properties `--app-*` et `--astro-*` | `PASS` - owners semantiques documentes |
| `rg -n "font-size:\|font-weight:\|line-height:\|letter-spacing:" frontend/src/App.css` | declarations actives routees via `var(...)` ou tokens | `PASS` - roles typographiques App documentes |
| `rg -n "box-shadow:\|border-radius:\|linear-gradient\|radial-gradient" frontend/src/App.css` | declarations actives routees via `var(...)` ou tokens | `PASS` - valeurs brutes conservees uniquement dans owners |
| garde des noms `--app-*` mecaniques | 0 hit | `PASS` - aucun segment de nom App repete ou BEM brut dans l'owner |

## Registry updates

- `frontend/src/styles/token-namespace-registry.md`: la ligne `--app-*` couvre maintenant les roles visuels et typographiques App-owned.
- `frontend/src/styles/typography-roles.md`: ajout du role `app-scoped`.
- `_condamad/stories/regression-guardrails.md`: ajout de `RG-061` pour la garde App CS-087.

## Allowed differences

Les differences autorisees sont des substitutions equivalentes vers `--app-*` ou tokens existants dans `App.css`. Aucun changement React, route, store, client API, payload ou backend.
