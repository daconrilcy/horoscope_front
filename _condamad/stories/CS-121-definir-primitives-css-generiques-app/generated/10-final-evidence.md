# Final Evidence — CS-121 definir-primitives-css-generiques-app

## Story status

- Validation outcome: PASS
- Final status: done
- Capsule path: `_condamad/stories/CS-121-definir-primitives-css-generiques-app`
- Source finding closure: phased-with-map; residual work handled by CS-122, CS-123, CS-124.

## AC validation

| AC | Evidence | Status |
|---|---|---|
| AC1 | `app-css-standardization-before.md` records audit baseline. | PASS |
| AC2 | `frontend/src/App.css` exposes `.app-page`, `.app-section`, `.app-stack`, `.app-grid`, `.app-card`, `.app-panel`, `.app-state`, `.app-badge`, `.app-avatar`, `.app-modal`. | PASS |
| AC3 | `frontend/src/tests/design-system-guards.test.ts` includes App specificity guard. | PASS |
| AC4 | `frontend/src/styles/token-namespace-registry.md` and `frontend/src/styles/typography-roles.md` document App ownership. | PASS |
| AC5 | `APP_CSS_SPECIFICITY_EXCEPTIONS` is empty; No Legacy scan of `App.css` has zero hit. | PASS |

## Files changed

- `frontend/src/App.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- Story evidence files under this capsule.

## Commands run

| Command | Working directory | Result |
|---|---|---|
| `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | `frontend/` | PASS, 146 tests passed |
| `npm run test -- App router AstrologersPage ConsultationsPage SettingsPage DashboardPage ShortcutCard` | `frontend/` | PASS, 152 tests passed |
| `npm run test` | `frontend/` | PASS, 113 files passed, 1188 passed, 8 skipped |
| `npm run lint` | `frontend/` | PASS |
| `npm run build` | `frontend/` | PASS |
| `git diff --check` | repo root | PASS after whitespace fix |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py ...; python -B .../condamad_story_lint.py --strict ...` | repo root | PASS |

## DRY / No Legacy evidence

- No compatibility class alias added.
- `rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css` from `frontend/`: zero hit.
- App-specific domain scan is closed by CS-124 and `RG-075`.

## Remaining risks

- Aucun risque restant identifie.

