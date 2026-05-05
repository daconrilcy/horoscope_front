<!-- Baseline CS-052 des fallbacks CSS NatalChart avant reduction. -->

# CSS fallbacks before - CS-052 NatalChart

Scope: `frontend/src/pages/NatalChartPage.css`

Baseline command:

```powershell
Push-Location frontend
rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," src/pages/NatalChartPage.css
Pop-Location
```

Baseline count: 33 fallbacks.

Token proof sources:

- `frontend/src/main.tsx` imports `./styles/premium-theme.css` after global token files.
- `frontend/src/styles/premium-theme.css` declares these removable tokens in `:root`: `--premium-text-meta`, `--premium-text-strong`, `--premium-text-main`, `--premium-glass-border-strong`, `--premium-accent-purple-strong`, `--premium-glass-surface-1`, `--premium-glass-border`, `--premium-radius-card`, `--premium-shadow-card`, `--premium-shadow-focus`, `--premium-glass-surface-2`.
- `--premium-text-muted` and `--premium-glass-border-soft` are not declared in `premium-theme.css`; removal is blocked as `needs-user-decision`.

## Removal audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| L60 `--premium-text-meta` / `var(--text-faint` | CSS fallback | dead | natal header meta | `var(--premium-text-meta)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L72 `--premium-text-strong` / `var(--text-strong` | CSS fallback | dead | natal header title | `var(--premium-text-strong)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L86 `--premium-text-main` / `var(--text-main` | CSS fallback | dead | natal persona | `var(--premium-text-main)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L93 `--premium-glass-border-strong` / `rgba(255, 255, 255, 0.58` | CSS fallback | dead | header CTA border | `var(--premium-glass-border-strong)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L95 `--premium-accent-purple-strong` / `var(--primary-strong` | CSS fallback | dead | header CTA color | `var(--premium-accent-purple-strong)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L117 `--premium-text-muted` / `var(--text-muted` | CSS fallback | needs-user-decision | header info | none | keep | token absent from `premium-theme.css` | removing may change/invalid color |
| L134 `--premium-glass-surface-1` / `rgba(255, 255, 255, 0.45` | CSS fallback | dead | natal card background | `var(--premium-glass-surface-1)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L137 `--premium-glass-border` / `rgba(255, 255, 255, 0.5` | CSS fallback | dead | natal card border | `var(--premium-glass-border)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L138 `--premium-radius-card` / `24px` | CSS fallback | dead | natal card radius | `var(--premium-radius-card)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L140 `--premium-shadow-card` / `0 10px 30px rgba(0,0,0,0.05` | CSS fallback | dead | natal card shadow | `var(--premium-shadow-card)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L146 `--premium-shadow-focus` / `0 15px 45px rgba(0,0,0,0.08` | CSS fallback | dead | natal card hover shadow | `var(--premium-shadow-focus)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L153 `--premium-text-strong` / `var(--text-strong` | CSS fallback | dead | natal card h2 | `var(--premium-text-strong)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L218 `--premium-text-meta` / `var(--text-faint` | CSS fallback | dead | astro summary label | `var(--premium-text-meta)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L230 `--premium-accent-purple-strong` / `var(--primary-strong` | CSS fallback | dead | astro summary value | `var(--premium-accent-purple-strong)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L244 `--premium-text-main` / `var(--text-main` | CSS fallback | dead | card intro | `var(--premium-text-main)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L259 `--premium-text-main` / `var(--text-main` | CSS fallback | dead | card list item | `var(--premium-text-main)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L261 `--premium-glass-border-soft` / `rgba(255, 255, 255, 0.2` | CSS fallback | needs-user-decision | card list divider | none | keep | token absent from `premium-theme.css` | removing may drop divider border |
| L296 `--premium-text-strong` / `var(--text-strong` | CSS fallback | dead | data card title | `var(--premium-text-strong)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L302 `--premium-accent-purple-strong` / `var(--primary-strong` | CSS fallback | dead | data card value | `var(--premium-accent-purple-strong)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L317 `--premium-text-main` / `var(--text-main` | CSS fallback | dead | data reading | `var(--premium-text-main)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L328 `--premium-text-main` / `var(--text-main` | CSS fallback | dead | data pill | `var(--premium-text-main)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L337 `--premium-text-meta` / `var(--text-faint` | CSS fallback | dead | support text | `var(--premium-text-meta)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L343 `--premium-text-main` / `var(--text-main` | CSS fallback | dead | support label | `var(--premium-text-main)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L349 `--premium-glass-surface-2` / `rgba(255, 255, 255, 0.35` | CSS fallback | dead | guide background | `var(--premium-glass-surface-2)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L350 `--premium-glass-border-soft` / `rgba(255, 255, 255, 0.3` | CSS fallback | needs-user-decision | guide border | none | keep | token absent from `premium-theme.css` | removing may drop guide border |
| L351 `--premium-radius-card` / `24px` | CSS fallback | dead | guide radius | `var(--premium-radius-card)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L357 `--premium-glass-surface-1` / `rgba(255, 255, 255, 0.45` | CSS fallback | dead | open guide background | `var(--premium-glass-surface-1)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L358 `--premium-shadow-focus` / `0 15px 45px rgba(0,0,0,0.08` | CSS fallback | dead | open guide shadow | `var(--premium-shadow-focus)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L480 `--premium-accent-purple-strong` / `var(--primary-strong` | CSS fallback | dead | aspect badge | `var(--premium-accent-purple-strong)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L491 `--premium-text-strong` / `var(--text-strong` | CSS fallback | dead | aspect title | `var(--premium-text-strong)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L498 `--premium-text-main` / `var(--text-main` | CSS fallback | dead | aspect meaning | `var(--premium-text-main)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L522 `--premium-text-meta` / `var(--text-faint` | CSS fallback | dead | aspect meta label | `var(--premium-text-meta)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| L529 `--premium-text-strong` / `var(--text-strong` | CSS fallback | dead | aspect meta value | `var(--premium-text-strong)` | delete | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
