<!-- Evidence finale CS-052 des fallbacks CSS NatalChart apres reduction. -->

# CSS fallbacks after - CS-052 NatalChart

Scope: `frontend/src/pages/NatalChartPage.css`

After command:

```powershell
Push-Location frontend
rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," src/pages/NatalChartPage.css
Pop-Location
```

After count: 3 fallbacks.

Delta: 30 fallbacks removed, 3 fallbacks kept and blocked as `needs-user-decision`.

Registry synchronization:

- `frontend/src/styles/css-fallback-allowlist.md` now keeps only the 3 remaining `NatalChartPage.css` exceptions.
- `frontend/src/tests/design-system-allowlist.ts` now keeps the matching 3 executable exceptions.

## Removal audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `--premium-text-meta` / `var(--text-faint` | CSS fallback | dead | 4 NatalChart declarations | `var(--premium-text-meta)` | deleted | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| `--premium-text-strong` / `var(--text-strong` | CSS fallback | dead | 5 NatalChart declarations | `var(--premium-text-strong)` | deleted | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| `--premium-text-main` / `var(--text-main` | CSS fallback | dead | 7 NatalChart declarations | `var(--premium-text-main)` | deleted | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| `--premium-glass-border-strong` / `rgba(255, 255, 255, 0.58` | CSS fallback | dead | header CTA border | `var(--premium-glass-border-strong)` | deleted | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| `--premium-accent-purple-strong` / `var(--primary-strong` | CSS fallback | dead | 4 NatalChart declarations | `var(--premium-accent-purple-strong)` | deleted | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| `--premium-glass-surface-1` / `rgba(255, 255, 255, 0.45` | CSS fallback | dead | 2 NatalChart declarations | `var(--premium-glass-surface-1)` | deleted | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| `--premium-glass-border` / `rgba(255, 255, 255, 0.5` | CSS fallback | dead | natal card border | `var(--premium-glass-border)` | deleted | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| `--premium-radius-card` / `24px` | CSS fallback | dead | 2 NatalChart declarations | `var(--premium-radius-card)` | deleted | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| `--premium-shadow-card` / `0 10px 30px rgba(0,0,0,0.05` | CSS fallback | dead | natal card shadow | `var(--premium-shadow-card)` | deleted | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| `--premium-shadow-focus` / `0 15px 45px rgba(0,0,0,0.08` | CSS fallback | dead | 2 NatalChart declarations | `var(--premium-shadow-focus)` | deleted | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| `--premium-glass-surface-2` / `rgba(255, 255, 255, 0.35` | CSS fallback | dead | guide background | `var(--premium-glass-surface-2)` | deleted | declared in `premium-theme.css` and imported by `main.tsx` | none identified |
| `--premium-text-muted` / `var(--text-muted` | CSS fallback | needs-user-decision | header info | none | kept | token absent from `premium-theme.css` | theme/product alias unresolved |
| `--premium-glass-border-soft` / `rgba(255, 255, 255, 0.2` | CSS fallback | needs-user-decision | card list divider | none | kept | token absent from `premium-theme.css` | theme/product alias unresolved |
| `--premium-glass-border-soft` / `rgba(255, 255, 255, 0.3` | CSS fallback | needs-user-decision | guide border | none | kept | token absent from `premium-theme.css` | theme/product alias unresolved |

## Remaining scan

```text
src/pages/NatalChartPage.css:117:  color: var(--premium-text-muted, var(--text-muted));
src/pages/NatalChartPage.css:261:  border-bottom: 1px solid var(--premium-glass-border-soft, rgba(255, 255, 255, 0.2));
src/pages/NatalChartPage.css:350:  border: 1px solid var(--premium-glass-border-soft, rgba(255, 255, 255, 0.3));
```
