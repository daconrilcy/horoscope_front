# Evidence Log - frontend-design-system

| ID | Evidence type | Command / Source | Path | Result | Notes |
|---|---|---|---|---|---|
| E-001 | source inventory | `rg --files frontend` | `frontend` | PASS | Frontend React/Vite tree inventoried, excluding no application files. |
| E-002 | token source review | `Get-Content frontend/src/styles/design-tokens.css frontend/src/styles/theme.css frontend/src/styles/premium-theme.css frontend/src/index.css frontend/src/main.tsx` | `frontend/src/styles`, `frontend/src/index.css`, `frontend/src/main.tsx` | PASS | Canonical and compatibility token layers inspected. |
| E-003 | hardcoded color scan | `rg color functions and hex values in frontend/src CSS excluding token source files` | `frontend/src` | FAIL | 1696 CSS color occurrences outside `design-tokens.css`, `theme.css`, and `premium-theme.css`. |
| E-004 | hardcoded spacing and radius scan | `rg CSS length literals in frontend/src CSS excluding token source files` | `frontend/src` | FAIL | 2823 non-tokenized spacing, margin, padding, border, radius, and related declarations. |
| E-005 | typography literal scan | `rg --pcre2 typography declarations not starting with var in frontend/src CSS` | `frontend/src` | FAIL | 1393 non-tokenized typography declarations. Top repeats include weights 700, 600, 500 and mixed px/rem sizes. |
| E-006 | inline style scan | `rg -n style frontend/src -g *.tsx` | `frontend/src` | FAIL | 90 `style` attributes found. Some are dynamic CSS variables or widths, but many encode layout and text styling. |
| E-007 | fallback token scan | `rg CSS var fallbacks in frontend/src CSS` | `frontend/src` | FAIL | 329 `var(--token, fallback)` usages found, including fallback values that differ from canonical tokens. |
| E-008 | repeated value aggregation | `PowerShell regex aggregation over CSS values` | `frontend/src` | FAIL | Repeated values include 18x `rgba(255, 255, 255, 0.48)`, 18x `rgba(255, 255, 255, 0.62)`, 78x `border-radius: 999px`, 72x `gap: 12px`, 56x `gap: 8px`. |
| E-009 | large CSS ownership inventory | `Get-ChildItem frontend/src *.css sorted by Length` | `frontend/src` | FAIL | Largest files: `App.css` 92064 bytes, `AdminPromptsPage.css` 47959, `HelpPage.css` 37802, `Settings.css` 28737, `AstrologerProfilePage.css` 26988. |
| E-010 | guardrail registry review | `Get-Content _condamad/stories/regression-guardrails.md` | `_condamad/stories/regression-guardrails.md` | PASS | Existing guardrails are backend/documentation focused; no active frontend design-system invariant applies directly. |
| E-011 | token test review | `Get-Content frontend/src/tests/theme-tokens.test.ts` | `frontend/src/tests/theme-tokens.test.ts` | PASS | Tests assert selected token values but do not guard consumption discipline or ban new hardcoded design values. |
| E-012 | legacy naming scan | `rg legacy classes and compatibility tokens in frontend/src CSS and TSX` | `frontend/src` | FAIL | Active classes and variables include `chat-layout-legacy`, `conversation-item-legacy`, `--text-main`, `--settings-*`, `--premium-*`, and legacy aliases `--text-1`, `--glass`, `--primary`. |

## Limitations

- Runtime visual regression was not executed because the request targets a static design-token audit and the skill is read-only by default.
- Counts are static approximations. Dynamic rendering exceptions such as progress widths and CSS custom properties must be classified before enforcement.
