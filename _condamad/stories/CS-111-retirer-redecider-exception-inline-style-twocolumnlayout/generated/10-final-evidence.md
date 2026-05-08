<!-- Evidence finale CS-111, toutes les AC sont en PASS. -->

# Final Evidence CS-111

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Review verdict: CLEAN
- Story key: `CS-111-retirer-redecider-exception-inline-style-twocolumnlayout`

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `twocolumnlayout-inline-style-before.md` and `twocolumnlayout-inline-style-after.md` classify all hits. | Consumer scans run before/after. | PASS | No arbitrary `sidebarWidth` consumer found. |
| AC2 | `TwoColumnLayout.css` owns width via `--layout-sidebar-width`; `design-tokens.css` preserves the historical `320px` default; chat CSS uses `--chat-sidebar-width`. | `npm run test -- inline-style design-system` and `npm run test -- theme-tokens` PASS. | PASS | CSS-owned finite widths without visual default drift. |
| AC3 | `TwoColumnLayout` removed from inline/design allowlists. | Allowlist scan zero hit. | PASS | No layout inline-style exception remains. |
| AC4 | No runtime arbitrary width requirement remains. | Inventory + tests PASS. | PASS | Decision record not required because branch did not apply. |
| AC5 | Inline-style guard suite passes. | `npm run test -- inline-style design-system` PASS, 25 tests. | PASS | `RG-047` preserved. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `frontend/src/layouts/TwoColumnLayout.tsx` | modified | Remove `sidebarWidth` prop and inline style. | AC2, AC5 |
| `frontend/src/layouts/TwoColumnLayout.css` | modified | Route width to `--layout-sidebar-width`. | AC2 |
| `frontend/src/pages/ChatPage.css` | modified | Replace `--sidebar-width` with `--chat-sidebar-width`. | AC1, AC2 |
| `frontend/src/styles/design-tokens.css` | modified | Preserve `TwoColumnLayout` historical default width through CSS token. | AC2 |
| `frontend/src/styles/token-namespace-registry.md` | modified | Remove stale generic sidebar namespace. | AC2 |
| `frontend/src/tests/design-system-allowlist.ts` | modified | Remove `TwoColumnLayout` exception. | AC3 |
| `frontend/src/tests/inline-style-allowlist.ts` | modified | Remove `TwoColumnLayout` dynamic entry. | AC3 |
| `frontend/src/tests/inline-style-policy.test.ts` | modified | Remove stale dynamic mapper branch for `--sidebar-width`. | AC3, AC5 |
| `frontend/src/tests/theme-tokens.test.ts` | modified | Guard `--layout-sidebar-width` at `320px`. | AC2 |
| `_condamad/stories/CS-111-retirer-redecider-exception-inline-style-twocolumnlayout/*` | added | Baseline, after inventory, capsule evidence. | AC1-AC5 |

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `npm run test -- inline-style design-system` | `frontend/` | PASS | 0 | 25 tests passed. |
| `npm run test -- theme-tokens` | `frontend/` | PASS | 0 | Theme token tests passed, including `--layout-sidebar-width`. |
| `npm run test -- page-architecture layout` | `frontend/` | PASS | 0 | 29 tests passed. |
| `npm run lint` | `frontend/` | PASS | 0 | TypeScript lint/static check passed. |
| `npm run test` | `frontend/` | PASS | 0 | 122 files passed, 1302 tests passed, 8 skipped. |
| `rg -n "TwoColumnLayout|sidebarWidth|--sidebar-width|style=" frontend/src` | repo root | PASS | 0 | Remaining hits classified; no `sidebarWidth`, no `--sidebar-width`, no layout inline style. |
| `rg -n "TwoColumnLayout|--sidebar-width" frontend/src/tests/design-system-allowlist.ts frontend/src/tests/inline-style-allowlist.ts` | repo root | PASS | 1 | Zero hit expected. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py ...; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict ...` | repo root | PASS | 0 | Story validate and strict lint passed with venv active. |

## Remaining risks

Aucun risque restant identifie.

## Suggested reviewer focus

Verifier que la suppression de `sidebarWidth` est acceptable au regard de l'absence de consommateurs actifs et que le namespace chat remplace correctement le token generique.
