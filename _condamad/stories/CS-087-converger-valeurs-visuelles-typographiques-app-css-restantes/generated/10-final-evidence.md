<!-- Evidence finale CONDAMAD pour CS-087. -->

# CS-087 Final Evidence

Story status: ready-to-review.

## Implementation summary

- `frontend/src/App.css` garde les valeurs brutes visuelles et typographiques uniquement dans les owners `#root --app-*` et `--astro-*` documentes.
- Les declarations actives hors custom properties consomment maintenant `var(...)`, tokens globaux, ou roles documentes.
- La garde CS-087 parse les declarations CSS, limite le fallback runtime `--usage-progress` a son exception exacte, et echoue sur les noms `--app-*` mecaniques.
- Aucun changement React, route, store, client API, payload ou backend.

## Files changed

- `frontend/src/App.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/CS-087-converger-valeurs-visuelles-typographiques-app-css-restantes/**`

## Validation results

| Command | Result |
|---|---|
| `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | PASS - 6 files, 143 tests |
| `npm run lint` | PASS |
| `npm run build` | PASS - Vite chunk-size warning unchanged and out of scope |
| `npm run test` | PASS - 115 files, 1261 passed, 8 skipped |
| `rg -n "var\(\s*--[a-zA-Z0-9_-]+\s*," src/App.css` | PASS - hit exact `--usage-progress, 0` classe dans `css-fallback-allowlist.md` |
| AST declaration scan hors `#root` et hors custom properties | PASS - zero active violation, hors fallback runtime allowliste |
| garde noms `--app-*` mecaniques | PASS - zero segment repete ou BEM brut dans l'owner App |
| `rg -n "legacy\|Legacy\|alias\|compat\|compatibility\|shim\|fallback\|migration-only" src/App.css` | PASS - hits limites aux selecteurs d'etat image de remplacement existants et keyframe `skeleton-shimmer`; aucun mecanisme de compatibilite CSS ajoute |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-087-converger-valeurs-visuelles-typographiques-app-css-restantes/00-story.md` | PASS |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-087-converger-valeurs-visuelles-typographiques-app-css-restantes/00-story.md` | PASS |
| `npm run dev -- --host 127.0.0.1` + `Invoke-WebRequest http://127.0.0.1:5173/` | PASS - HTTP 200, serveur PID 65340 |
| `rg -n "\bany\b" <modified frontend files>` | PASS - zero hit |
| `rg -n "fetch\(|axios\." <modified frontend files>` | PASS - zero hit |
| `rg -n "style=\{\{" frontend/src` | PASS - hits uniquement dans allowlist existante, aucun nouveau hit dans fichiers modifies |

## Acceptance criteria

| AC | Result | Evidence |
|---|---|---|
| AC1 | PASS | `hardcoded-values-before.md`, `hardcoded-values-after.md`, migration bornee a `App.css` |
| AC2 | PASS | decisions finales dans `hardcoded-values-after.md` |
| AC3 | PASS | `--app-*` documente dans `token-namespace-registry.md`, `app-scoped` documente dans `typography-roles.md` |
| AC4 | PASS | fallback runtime App preserve via allowlist exacte existante; tests css/inline/legacy passent |
| AC5 | PASS | garde CS-087 dans `design-system-guards.test.ts`, `RG-061` ajoute |
| AC6 | PASS | visual-smoke, build et full Vitest passent |
| AC7 | PASS | evidence sans AC limitee; scans No Legacy classes |

## Regression guardrails

Applicable: `RG-044`, `RG-045`, `RG-046`, `RG-047`, `RG-048`, `RG-049`, `RG-050`, `RG-052`, `RG-053`, `RG-057`, `RG-059`, `RG-060`, `RG-061`.

Registry update: `RG-061` added for CS-087 App active declaration guard and App owner naming guard.

## Skipped checks

- `npm run test:e2e`: not run; CS-087 is a CSS ownership migration with no route or user-flow behavior change, and story validation plan did not require E2E.

## Remaining risks

- `App.css` now has a large App-scoped owner block. The CS-087 guard blocks the most mechanical owner-name drift; future stories can still promote repeated App roles to global tokens when a cross-surface owner emerges.
