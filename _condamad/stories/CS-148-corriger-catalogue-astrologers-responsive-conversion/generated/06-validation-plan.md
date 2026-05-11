# Validation Plan

## Targeted frontend checks

```powershell
cd frontend
npm run test -- AstrologersPage design-system visual-smoke
```

## Static guards

```powershell
cd frontend
rg -n "people-page|person-card" src/App.css
rg -n "astrologer-" src/styles/app src/features/astrologers
rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers
rg -n "mix-alend-mode|featured=\\{index === 0\\}|height:\\s*24[0-9]px|height:\\s*25[0-9]px" src/features/astrologers src/styles/app/cards.css src/styles/app/media.css src/tests
rg -n "toHaveClass\\(\"person-card--featured\"\\)|badges stay hidden|Provider default featured badges stay hidden" src/tests/visual-smoke.test.tsx src/tests/design-system-guards.test.ts
```

## Lint and regression

```powershell
cd frontend
npm run lint
npm run test
```

## Runtime evidence

```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Then capture and measure:

- `390x844`: one column, no horizontal scroll, visible CTA and signals, bottom nav safe.
- `768x1024`: readable two-column grid.
- `1440x1000`: equal grid, no first-card span.
- click card navigates to `/astrologers/:id`.
- dark mobile keeps cards and CTA visible.

## Skipped command rule

If a command cannot be run, record exact command, reason, risk, and compensating evidence.
