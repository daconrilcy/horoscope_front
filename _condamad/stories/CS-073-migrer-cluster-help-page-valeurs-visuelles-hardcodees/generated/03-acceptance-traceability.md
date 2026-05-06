# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | The cluster is exactly bounded to `HelpPage.css`. | `HelpPage.css` main help cluster only; no React/API/backend change. | `hardcoded-values-before.md`, `git diff -- frontend/src/pages/HelpPage.css`. | PASS |
| AC2 | 100% of HelpPage values have final decisions. | Migrated cluster values mapped to `--help-*`, existing tokens, or final one-offs. | `hardcoded-values-after.md` decision table and targeted `rg` scans. | PASS |
| AC3 | Repeated values migrate to canonical owners. | Repeated colors/surfaces/shadows/radii centralized under registered `--help-*`; typography uses existing `--type-*`, `--font-*`, `--line-height-*`. | `npm run test -- design-system theme-tokens css-fallback legacy-style visual-smoke`. | PASS |
| AC4 | No forbidden namespace is introduced. | Added only `--help-*` semantic-extension; no fallback literal or legacy namespace. | `npm run test -- css-fallback theme-tokens legacy-style`; forbidden namespace scan zero hits. | PASS |
| AC5 | HelpPage visual smoke remains green. | Existing rendered HelpPage behavior unchanged; CSS-only migration. | `npm run test -- design-system theme-tokens css-fallback legacy-style visual-smoke`; `npm run test -- HelpPage`. | PASS |
| AC6 | Migrated literals cannot silently return. | `design-system-guards.test.ts` blocks migrated literals outside the `:where(.help-page, .help-bg-halo)` owner block and out-of-scope subscriptions block. | Combined Vitest command and lint PASS. | PASS |

Status used: `PASS`.
