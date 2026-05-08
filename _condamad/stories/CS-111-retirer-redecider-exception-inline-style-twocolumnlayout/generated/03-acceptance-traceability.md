<!-- Matrice de tracabilite AC vers preuves pour CS-111. -->

# Acceptance Traceability CS-111

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `TwoColumnLayout` consumers are inventoried. | Before/after inventories list `TwoColumnLayout`, `sidebarWidth`, `--sidebar-width`. | `rg -n "TwoColumnLayout|sidebarWidth" frontend/src` classified. | PASS |
| AC2 | Remediable width usage is CSS-owned. | `TwoColumnLayout.css` uses `--layout-sidebar-width`; the token preserves the historical `320px` default; chat uses `--chat-sidebar-width`. | `npm run test -- inline-style design-system` and `npm run test -- theme-tokens` PASS. | PASS |
| AC3 | Layout inline-style allowlists are removed after remediation. | `TwoColumnLayout` rows removed from both allowlists. | `rg -n "TwoColumnLayout|--sidebar-width" frontend/src/tests/design-system-allowlist.ts frontend/src/tests/inline-style-allowlist.ts` zero hit. | PASS |
| AC4 | Required arbitrary width has an approved decision record. | No arbitrary runtime width remains required; no decision record needed. | Consumer inventory and guard tests PASS. | PASS |
| AC5 | Inline-style guard passes for the layout surface. | Existing inline-style guard now rejects any unlisted layout inline style. | `npm run test -- inline-style design-system` PASS. | PASS |
