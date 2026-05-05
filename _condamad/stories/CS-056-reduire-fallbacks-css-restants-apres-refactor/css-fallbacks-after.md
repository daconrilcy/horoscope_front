# CSS fallbacks after CS-056

Scan command: `rg -n "var\\(\\s*--[A-Za-z0-9_-]+\\s*," src -g "*.css"` from `frontend`.

Final fallback count: 10 entries.
Deleted from priority lot: 14 allowlist entries removed from CSS/registers.
Remaining priority lot blockers: `NatalInterpretation.css` `--premium-glass-border-soft` and `NatalChartPage.css` premium fallbacks, kept because their premium tokens are not guaranteed.

| File | Result | Evidence |
|---|---|---|
| `frontend/src/components/prediction/PeriodCard.css` | all priority fallbacks removed | `--color-text-muted`, `--color-text-secondary`, `--color-error` consumed directly |
| `frontend/src/components/prediction/KeyPointCard.css` | all priority fallbacks removed | `--shadow-hero-card`, `--color-hero-ink`, `--color-hero-ink-accent` consumed directly |
| `frontend/src/components/NatalInterpretation.css` | guaranteed token fallbacks removed; absent premium token fallback kept | `--premium-radius-pill`, `--space-*`, `--font-size-sm` direct; `--premium-glass-border-soft` remains classified |
| `frontend/src/pages/NatalChartPage.css` | blocked fallbacks kept | premium ambiguity remains `needs-user-decision` |
| `frontend/src/styles/css-fallback-allowlist.md` | synchronized | removed deleted entries only |
| `frontend/src/tests/design-system-allowlist.ts` | synchronized | `CSS_FALLBACK_EXCEPTIONS` matches runtime scan |

Validation: `npm run test -- css-fallback design-system theme-tokens inline-style legacy-style visual-smoke` PASS; `npm run lint` PASS.
