# Evidence after - catalogue `/astrologers`

Date: 2026-05-11

## Runtime local

Dev server: `http://127.0.0.1:5173/astrologers`

Captures generees:

- `astrologers-after-mobile-390x844.png`
- `astrologers-after-tablet-768x1024.png`
- `astrologers-after-desktop-1440x1000.png`
- `astrologers-after-dark-mobile-390x844.png`

Mesures Playwright apres connexion avec l'utilisateur de test:

| Viewport | Colonnes | Scroll horizontal | Featured class | CTA | Badges provider | Default badge |
|---|---:|---:|---:|---:|---:|---:|
| `390x844` | 1 | false | false | 6 | 6 | 1 |
| `768x1024` | 2 | false | false | 6 | 6 | 1 |
| `1440x1000` | 4 | false | false | 6 | 6 | 1 |

Validation runtime complementaire:

- Mobile `390x844`: le CTA de la derniere carte reste visible au-dessus de la bottom nav apres scroll.
- DOM carte: `nestedInteractiveCount = 0`; la carte reste une action unique.
- Navigation: clic premiere carte vers `/astrologers/c0a80101-8edb-4e1a-8f1a-8f1a8f1a8f1a`.
- Dark mobile: 6 cartes et 6 CTA visibles apres activation de `html.dark`.

## Tests et scans

```text
npm run test -- AstrologersPage design-system visual-smoke
PASS - 3 fichiers, 86 tests

npm run lint
PASS - tsc --noEmit lint + node

npm run test
PASS - 115 fichiers, 1244 tests passes, 8 skipped

rg -n "people-page|person-card" src/App.css
PASS - zero hit

rg -n "astrologer-" src/styles/app src/features/astrologers
PASS - zero hit

rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers
PASS - zero hit

rg -n "mix-alend-mode|featured=\\{index === 0\\}|height:\\s*24[0-9]px|height:\\s*25[0-9]px" src/features/astrologers src/styles/app/cards.css src/styles/app/media.css src/tests
PASS - zero hit sur la surface CS-148
```

Note: le scan large sur tout `src` remonte des `min-height`/`height` existants
hors catalogue (`DayClimateHero.css`, `Select.css`, landing, forms, states).
Ils ne touchent pas `/astrologers`; le guard RG-089 est donc scope aux owners
catalogue.

## Differences autorisees

- La premiere carte n'a plus de classe featured et ne span plus deux colonnes.
- Les badges provider/default/editorial sont visibles dans les cartes catalogue.
- Un CTA visuel localise `Voir le profil` est rendu comme `span`, sans bouton
  enfant.
- Les cartes utilisent une grille responsive egale et des hauteurs robustes par
  `min-height`, line clamp et espacement vertical.
- `mix-blend-mode` remplace la typo CSS `mix-alend-mode`.
