# CS-149 After Evidence

## Runtime contract summary

- `390x844`: CSS mobile rule remains `.people-page .person-grid { grid-template-columns: minmax(0, 1fr); }`.
- `768x1024`: cards keep auto-fit grid behavior with wider minimum and no horizontal overflow rule added.
- `1440x1000`: catalogue target now uses `repeat(auto-fit, minmax(min(100%, 340px), 1fr))`, steering the existing content width away from four narrow cards.
- Card DOM: avatar, full name, display name and style now precede `.person-card-topline` badges.
- CTA DOM: `.person-card-cta` remains a non-interactive `span`; tests assert no nested `button` or `a`.
- Decoration: catalogue orbit animation is disabled under `prefers-reduced-motion: reduce`.
- Captures authentifiees:
  - `_condamad/stories/CS-149-optimiser-hierarchie-premium-catalogue-astrologers/screenshots/astrologers-auth-390x844.png`
  - `_condamad/stories/CS-149-optimiser-hierarchie-premium-catalogue-astrologers/screenshots/astrologers-auth-768x1024.png`
  - `_condamad/stories/CS-149-optimiser-hierarchie-premium-catalogue-astrologers/screenshots/astrologers-auth-1440x1000.png`

## Allowed differences

- Header subtitle and choice criteria changed to make comparison criteria explicit.
- Empty state now includes title, explanation and next action.
- Provider/default badges are visually secondary; featured badge remains the primary choice badge.
- CTA is a full-width action row instead of underlined text.
- The header quick criteria list was removed after product feedback; comparison signals now stay on the cards where they are actionable.

## Commands run

| Command | Result | Evidence |
|---|---|---|
| `npm run test -- AstrologersPage design-system visual-smoke` | PASS after one fixed failure | 3 files, 87 tests passed. Initial failure was `letter-spacing: 0`; removed the literal and reran successfully. |
| `npm run lint` | PASS | TypeScript lint/typecheck scripts completed with exit 0. |
| `npm run test` | PASS | 115 files passed, 1245 tests passed, 8 skipped. |
| `Invoke-WebRequest http://127.0.0.1:5173/astrologers` | PASS | HTTP 200; port 5173 was already listening. |
| `npx playwright screenshot --viewport-size=390,844/768,1024/1440,1000` | PASS | Captures catalogue authentifiees generees avec 6 cartes visibles. |
| `git diff --check` | PASS | No whitespace/conflict-marker errors; Git emitted line-ending warnings only. |

## Scans

| Scan | Result | Notes |
|---|---|---|
| `rg -n "people-page\|person-card" src/App.css` | PASS | Zero hits. |
| `rg -n "astrologer-" src/styles/app src/features/astrologers` | PASS | Zero hits. |
| `rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers` | PASS | Zero hits. |
| `rg -n "featured=\{index === 0\}\|person-card--featured\|height:\s*24[0-9]px\|height:\s*25[0-9]px" src/features/astrologers src/styles/app/cards.css src/styles/app/media.css src/tests/AstrologersPage.test.tsx src/tests/visual-smoke.test.tsx src/tests/design-system-guards.test.ts` | PASS | Zero hits in catalogue scope. |
| Broad story scan on `src/styles/app src/tests` | PASS_WITH_CLASSIFICATION | Hits in `forms.css` and `states.css` are `min-height` values outside catalogue/card scope. |

## Regression guardrails

- `RG-079`: PASS, relief token-backed preserved and no `App.css`/`.astrologer-*` pollution.
- `RG-081`: PASS, no central width/layout owner changed.
- `RG-083`: PASS, full frontend tests and design-system dark-mode guards pass.
- `RG-084`: PASS, no new page-level background owner added.
- `RG-087`: PASS, global viewport background untouched.
- `RG-089`: PASS, grid remains equal, mobile one column, CTA non-nested.
- `RG-090`: PASS, identity-first card order, action-row CTA, wider desktop grid, reduced-motion guard and captures 390/768/1440 ajoutees. Le chevauchement initial de l'icone du badge principal a ete corrige par positionnement flex relatif.
