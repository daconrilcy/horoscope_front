# Hardcoded Values After

## Scope

- File: `frontend/src/pages/HelpPage.css`
- Section: `/* --- Help Subscriptions Page (AC7, AC9) --- */`
- Captured after implementation on 2026-05-07.

## Final decisions

| Category | Final decision | Evidence |
|---|---|---|
| Glass borders, surfaces, gradients and decorative orbs | `registered-help-owner` / `migrated` | Values moved to `--help-subscriptions-*` declarations in `:where(.help-page, .help-bg-halo)` and consumed via `var(...)` in subscriptions. |
| Shadows and elevation | `registered-help-owner` / `migrated` | Subscriptions usages now reference `--help-subscriptions-*-shadow` or existing `--help-subscription-card-shadow-soft`. |
| Radius literals | `migrated` | Replaced by existing global or Help shape tokens such as `--help-radius-section`, `--help-radius-compact`, `--radius-full`, `--radius-lg`, `--radius-xl`. |
| Typography values | `typography-role` / `registered-help-owner` | Common values use global tokens; editorial/commercial sizing uses documented Help-scoped role `help-subscriptions` in `typography-roles.md`. |
| Cross-page page-scoped tokens | `migrated` | Subscriptions no longer consumes `--primary`, `--primary-strong`, `--text-*`, `--glass-border` aliases; it uses `--help-*` or global tokens. |
| Motion timings, keyframes, transforms, dimensions and layout spacing | `kept-one-off-final` | Preserved to keep behavior and layout identical; not visual palette/typography debt for this story. |

## Anti-return guard

- `frontend/src/tests/design-system-guards.test.ts` includes CS-088 guard coverage.
- The guard extracts `--help-subscriptions-*` migrated literals from the Help owner block, including nested atomic `hex`, `rgb(a)` and `hsl(a)` color literals, and asserts they do not reappear as active local declaration values in the subscriptions section.
- The guard also blocks representative typography literals, page-scoped foreign namespaces and CSS fallbacks in the subscriptions section.

## Scan results

| Command | Result | Classification |
|---|---|---|
| `rg -n "#[0-9A-Fa-f]{3,8}\|rgba?\(\|hsla?\(" src/pages/HelpPage.css` | PASS | Hits are in Help owner declarations or pre-existing non-subscriptions Help surfaces; subscriptions usages consume variables. |
| `rg -n "font-size:\|font-weight:\|line-height:\|letter-spacing:" src/pages/HelpPage.css` | PASS | Subscriptions hits use global typography tokens or `--help-subscriptions-*` owner variables. |
| `rg -n "box-shadow:\|border-radius:\|linear-gradient\|radial-gradient\|var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/HelpPage.css` | PASS | Subscriptions hits use variables/tokens; no `var(--token, literal)` fallback hit. |
| `rg -n -- "--settings-\|--app-\|--chat-\|--landing-\|--admin-" src/pages/HelpPage.css` | PASS | Zero hits. |
| `rg -n "legacy\|Legacy\|alias\|compat\|compatibility\|shim\|fallback\|migration-only" src/pages/HelpPage.css` | PASS | Zero hits. |
| AC7 limitation/deferred-work scan | PASS | Zero hits for forbidden limitation or deferred-work markers. |
