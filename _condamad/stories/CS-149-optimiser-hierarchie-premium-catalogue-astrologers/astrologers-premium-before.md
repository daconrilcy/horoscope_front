# CS-149 Before Evidence

## Baseline summary

- `AstrologerCard.tsx`: before implementation, `.person-card-topline` renders icon and badge stack before avatar/name/style.
- `cards.css`: before implementation, `.people-page .person-grid` uses `repeat(auto-fit, minmax(min(100%, 280px), 1fr))`, allowing denser desktop cards.
- `.person-card-cta`: before implementation, CTA is underlined text, not a full action row.
- `AstrologersPage.tsx`: header contains title and subtitle only.
- `AstrologerGrid.tsx`: empty state contains icon and short message only.
- `media.css`: orbit animations exist without a catalogue-specific reduced-motion guard.

## Required scans planned

- `rg -n "people-page|person-card" src/App.css`
- `rg -n "astrologer-" src/styles/app src/features/astrologers`
- `rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers`
- `rg -n "featured=\{index === 0\}|person-card--featured|height:\s*24[0-9]px|height:\s*25[0-9]px" src/features/astrologers src/styles/app src/tests`

## Viewport baseline

- `1440x1000`: static CSS target before change permits narrow cards from `280px` minimum.
- `768x1024`: grid relies on auto-fit and remains readable from existing CS-148 guards.
- `390x844`: existing mobile media rule forces one column.
