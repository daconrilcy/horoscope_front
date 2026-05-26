# Browser QA — CS-307

Date: 2026-05-26
Route: `/natal`
Source runtime: `node _condamad\stories\CS-307-audit-ux-natal-apres-wiring-projections\evidence\cs307-ux-audit.mjs`
Ledger: `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/browser-qa-ledger.json`

| Viewport | State | Result | Screenshot | Decision |
|---|---|---|---|---|
| desktop 1366x900 | success | PASS | `browser-screenshots/browser-desktop.png` | acceptable |
| tablet 820x1180 | success | PASS | `browser-screenshots/browser-tablet.png` | acceptable |
| mobile 390x844 | success | PASS | `browser-screenshots/browser-mobile.png` | acceptable |
| mobile 390x844 | degraded | PASS | `browser-screenshots/browser-mobile-degraded.png` | acceptable |
| mobile 390x844 | entitlement | PASS | `browser-screenshots/browser-mobile-entitlement.png` | acceptable |
| mobile 390x844 | error | PASS | `browser-screenshots/browser-mobile-error.png` | acceptable |
| mobile 390x844 | empty | PASS | `browser-screenshots/browser-mobile-empty.png` | acceptable |

## Findings

- Projection hierarchy remains readable on desktop, tablet, and mobile.
- Critical controls do not overlap the projections panel.
- The legal disclaimer remains visible below projections without overlap.
- Degraded, entitlement, API error, and empty states remain understandable on mobile.
