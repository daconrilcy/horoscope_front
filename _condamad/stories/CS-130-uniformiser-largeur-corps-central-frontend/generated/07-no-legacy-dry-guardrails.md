# CS-130 - No Legacy / DRY guardrails

## Decisions

- One page-level non-admin width owner: `--layout-page-max-width` in `design-tokens.css`.
- Consumers: `.app-bg-container` and `.page-layout`.
- No compatibility selector, alias, fallback, wrapper or re-export added.
- Admin width remains separate through `--layout-admin-max-width`, `.app-bg-container--admin`, and `AdminLayout.css`.

## Negative evidence

- Removed page-level `--layout-max-width` from Dashboard/Daily/Profile.
- Removed local `--layout-page-max-width` override from Natal.
- Removed chat `.app-bg-container:has(.is-chat-page)` width bypass.
- Removed `max-width: none !important` width bypasses from non-admin wrappers.
- Removed page-level `overflow-x: hidden` used to mask width defects in chat.
- Removed stale `DashboardPage.css` after confirming `DashboardPage.tsx` no longer consumed `.dashboard-*` selectors.
- Removed the active `.page-layout.people-page` width cap from `styles/app/cards.css`.
- Moved the billing return `600px` cap from the page wrapper to the internal card.

## Guard

`frontend/src/tests/design-system-guards.test.ts` now fails on unclassified non-admin page-level width owners across the active App CSS modules and page CSS surfaces.
