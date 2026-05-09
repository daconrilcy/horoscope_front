# Astrologers Visual After

<!-- Preuve visuelle apres restauration du relief compact /astrologers. -->

## Restored details

- `.people-page .person-card` utilise maintenant les tokens compacts `--app-person-card-compact-background`, `--app-person-card-compact-border` et `--app-person-card-compact-box-shadow` pour restaurer une surface coloree avec halo et profondeur visibles.
- `.people-page .person-card--featured` garde `grid-column: span 2` avec `--app-person-card-compact-featured-background`, border et shadow distincts.
- `.people-page .person-card-icon` est repositionnee en pastille absolue visible et themee via `--app-person-card-compact-icon-*`.
- `.people-page .person-card-avatar` conserve le crop rond et gagne une ombre compacte token-backed via `--app-person-card-compact-avatar-box-shadow`; les pseudo-elements media restent inchanges.
- `.people-page .person-card-tag` conserve un format compact mais recupere background, border et shadow token-backed via `--app-person-card-compact-tag-*`.
- Les badges provider/default/featured restent presents dans le DOM mais caches dans le scope compact.

## Follow-up correction

- La capture utilisateur du 2026-05-10 montrait que la premiere restauration etait encore trop plate: cartes blanches, icones presque invisibles, ombrages faibles et chips peu materialisees.
- Correction: les valeurs visuelles compactes ont ete deplacees dans `frontend/src/styles/app/tokens.css`, puis consommees par `frontend/src/styles/app/cards.css` pour respecter `RG-045`, `RG-061` et `CS-087`.
- Les garde-fous testent maintenant l'usage des tokens compacts plutot que des valeurs brutes dans les declarations actives.
- Correction runtime supplementaire: les tokens compacts qui dependent de `--astro-*`
  sont resolus sur `.person-card`, pas sur `#root`, afin que le navigateur
  calcule vraiment les backgrounds, bordures et ombres.
- Correction pastille: `.people-page .person-card-topline` redevient statique
  dans le scope compact pour que `.person-card-icon` soit positionnee par
  rapport a la carte, comme dans la capture d'origine.
- Micro-ajustements finaux:
  `person-card-icon` utilise `z-index: 5`, un anneau degrade token-backed via
  `::before`, et un decalage vertical qui laisse environ 6 px avant l'avatar;
  le divider compact est renforce pour rester visible sur Etienne; le style
  d'astrologue utilise `--app-person-card-compact-style-color`.
- Correction shell finalisee: `.app-header` garde `position: sticky`,
  `z-index: 220`, un fond token-backed plus opaque, un `backdrop-filter`
  renforce et un voile `::before`, pour que le contenu scrolle visuellement
  sous le top menu.

## Allowed differences

- Changements visuels limites a la matiere de `/astrologers`: surface translucide, ombres, bordures themees, icone, avatar et chips.
- Aucun changement attendu sur route, API, donnees, navigation, rotation, textes ou page profil.
- Aucun style actif ajoute dans `frontend/src/App.css`.

## Commands run

| Command | Working directory | Result | Summary |
|---|---|---|---|
| `npm run test -- AstrologersPage design-system visual-smoke` | `frontend/` | PASS | 3 files, 68 tests passed after DOM smoke addition. |
| `npm run test -- theme-tokens css-fallback inline-style legacy-style` | `frontend/` | PASS | 4 files, 108 tests passed. |
| `npm run lint` | `frontend/` | PASS | TypeScript lint configs pass. |
| `npm run build` | `frontend/` | PASS | Vite production build succeeds. |
| `git diff --check` | repo root | PASS | No whitespace/conflict-marker errors; line-ending warnings only. |
| `rg -n "person-card\|people-page\|astrologer" src/App.css` | `frontend/` | PASS | Zero hits. |
| `rg -n "\.astrologer-(card\|grid\|card-avatar\|card-specialties)" src/styles/app src/features/astrologers src/pages/AstrologersPage.tsx` | `frontend/` | PASS | Zero hits for exact forbidden legacy selectors. |
| `rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers/components/AstrologerCard.tsx src/features/astrologers/components/AstrologerGrid.tsx` | `frontend/` | PASS | Zero hits. |
| `rg --files src/styles/app` | `frontend/` | PASS | Only approved App CSS modules listed. |

## Skipped checks

| Check | Reason | Risk | Compensating evidence |
|---|---|---|---|
| Browser screenshot capture | Dev server screenshot was not captured in this session. | Manual visual comparison remains reviewer responsibility. | DOM smoke, CSS guard, build and targeted tests prove route/card structure and material tokens. |

## Screenshots

- Controlled after screenshot: `generated/visual-after-icon-fix.png`.
- Micro-adjustment hover screenshot: `generated/visual-after-micro-icon-hover.png`.
- Header scroll glass screenshot: `generated/visual-header-glass-scroll.png`.
- Earlier comparison captures kept for review: `generated/visual-current-controlled-before-second-pass.png`, `generated/visual-after-second-pass.png`, `generated/visual-after-third-pass.png`, `generated/visual-after-fourth-pass.png`.
- Runtime app: local dev server available at `http://127.0.0.1:5176/` during validation.

## Scan classification

The broad story scan `rg -n "astrologer-card|astrologer-grid|compat|compatibility|legacy|alias|shim" src/styles/app src/pages src/features/astrologers` returns existing `default-astrologer-grid` hits in Settings.
Classification: out of scope false positive for CS-128, because it is not `.astrologer-grid`, is outside `/astrologers`, and predates this story. The exact forbidden selector scan is zero-hit.
