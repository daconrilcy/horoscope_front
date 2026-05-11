# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-138-implementer-fond-dark-astral-avant-aube`
- Source story: `_condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/00-story.md`
- Capsule path: `_condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: clean at first check.
- AGENTS.md considered: `AGENTS.md`.
- Regression guardrails read: yes; applicable `RG-061`, `RG-068`, `RG-078`, `RG-081`, `RG-082`, `RG-083`, `RG-084`, `RG-085`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Generated. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Generated. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated. |
| `generated/10-final-evidence.md` | yes | yes | PASS | This file. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Dark canonical tokens and starfield layers updated in `premium-theme.css`, `backgrounds.css`, `StarfieldBackground.tsx`. | Targeted tests PASS; full `npm run test` PASS after rerun. | PASS | Astral/dawn/milky/shooting terms guarded. |
| AC2 | Light `:root` background tokens left unchanged; dark-only overrides changed. | `theme-tokens` and `design-system` PASS. | PASS | No light-mode code path changed. |
| AC3 | Center-friendly background density and dark glass surfaces updated via premium tokens. | Visual-smoke PASS; screenshots generated. | PASS | Review screenshots for final artistic approval. |
| AC4 | `RootLayout` emits `app-bg--landing` for `/`. | `npm run test -- App` PASS. | PASS | |
| AC5 | `RootLayout` emits `app-bg--internal` outside `/`. | `npm run test -- App` PASS. | PASS | |
| AC6 | `backgrounds.css` disables shooting-star animation on mobile and reduced motion. | `StarfieldBackground` tests and motion scan PASS. | PASS | |
| AC7 | Canonical `--premium-app-bg` / `--premium-app-bg-atmosphere` retained. | `design-system` PASS; global background scan has no new competing hit. | PASS | |
| AC8 | No raster asset or new background image owner added. | Targeted owner scan zero-hit; global scan only pre-existing SVG data URL hits. | PASS | |
| AC9 | No `App.css` change and no inline style in touched React. | Targeted scans PASS; `design-system` PASS. | PASS | |
| AC10 | Before/after evidence and screenshots created. | Artifact files present; screenshot file list verified. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `frontend/src/styles/premium-theme.css` | modified | Dark astral/dawn canonical tokens and readable dark surfaces. | AC1, AC2, AC3 |
| `frontend/src/styles/backgrounds.css` | modified | Full/sober scope, starfield CSS, reduced-motion/mobile guards. | AC1, AC4, AC5, AC6, AC7 |
| `frontend/src/components/StarfieldBackground.tsx` | modified | Deterministic denser stars, Milky Way path, rare shooting stars. | AC1, AC6, AC8 |
| `frontend/src/layouts/RootLayout.tsx` | modified | Route-level `app-bg--landing` / `app-bg--internal` ownership. | AC4, AC5 |
| `frontend/src/tests/StarfieldBackground.test.tsx` | modified | Runtime/starfield/motion tests. | AC1, AC6, AC8 |
| `frontend/src/tests/visual-smoke.test.tsx` | modified | Astral dark background assertions. | AC1, AC3 |
| `frontend/src/tests/design-system-guards.test.ts` | modified | Canonical background guard update for CS-138. | AC2, AC7, AC9 |
| `frontend/src/tests/AppBgStyles.test.ts` | modified | Background CSS expectations for new dark layers. | AC1 |
| `frontend/src/tests/App.test.tsx` | modified | Route-level landing/internal scope assertions. | AC4, AC5 |
| `_condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/dark-astral-background-before.md` | added | Baseline evidence. | AC10 |
| `_condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/dark-astral-background-after.md` | added | After evidence. | AC10 |
| `_condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/screenshots/*.png` | added | Visual after evidence. | AC3, AC10 |
| `_condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/generated/*` | added/modified | CONDAMAD capsule and final evidence. | AC10 |
| `_condamad/stories/story-status.md` | modified | Story registry status. | AC10 |
| `_condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/00-story.md` | modified | Story status only. | AC10 |

## Files deleted

None.

## Tests added or updated

- Updated `StarfieldBackground.test.tsx`, `visual-smoke.test.tsx`, `design-system-guards.test.ts`, `AppBgStyles.test.ts`, `App.test.tsx`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `npm run test -- StarfieldBackground visual-smoke theme-tokens design-system` | `frontend/` | PASS | 0 | 4 files, 186 tests passed after one CSS-token guard fix. |
| `npm run test -- layout` | `frontend/` | PASS | 0 | 2 files, 8 tests passed. |
| `npm run test -- App` | `frontend/` | PASS | 0 | 4 files, 61 tests passed. |
| `npm run test -- StarfieldBackground visual-smoke theme-tokens design-system` | `frontend/` | PASS | 0 | Review rerun: 4 files, 186 tests passed. |
| `npm run test -- layout` | `frontend/` | PASS | 0 | Review rerun: 2 files, 8 tests passed. |
| `npm run test -- App` | `frontend/` | PASS | 0 | Review rerun: 4 files, 61 tests passed. |
| `rg -n "style=" src/layouts/RootLayout.tsx src/components/StarfieldBackground.tsx` | `frontend/` | PASS | 1 | Zero hits. |
| `rg -n "background-image:\s*url\(" src/styles/premium-theme.css src/styles/backgrounds.css src/layouts/LandingLayout.css` | `frontend/` | PASS | 1 | Zero hits. |
| `rg -n "prefers-reduced-motion\|shooting\|meteor\|starfield" src/components src/styles src/layouts -g "*.tsx" -g "*.css"` | `frontend/` | PASS | 0 | Expected owner hits plus pre-existing `AstroMoodBackground`. |
| `rg -n "premium-app-bg\|premium-app-bg-atmosphere\|app-bg\|starfield-bg" src/styles src/layouts src/components -g "*.css" -g "*.tsx"` | `frontend/` | PASS | 0 | Canonical owner hits. |
| `rg -n "dark\|html\.dark\|starfield\|premium-app-bg" src/App.css` | `frontend/` | PASS | 1 | Zero hits. |
| `rg -n "style=" src -g "*.tsx" -g "*.jsx"` | `frontend/` | PASS | 0 | Only pre-existing allowlisted hits outside touched files. |
| `rg -n "background-image:\s*url\(" src/styles src/layouts src/pages -g "*.css" -g "*.scss"` | `frontend/` | PASS | 0 | Only pre-existing SVG data URL in `styles/app/media.css`. |
| `rg -n "bg-halo\|noise\|landing-background\|space-background\|cosmic-background" src/styles src/layouts src/pages -g "*.css"` | `frontend/` | PASS | 0 | Only pre-existing canonical/neutral halo/noise hits. |
| `npm run lint` | `frontend/` | PASS | 0 | TypeScript lint configs passed. |
| `npm run build` | `frontend/` | PASS | 0 | Production Vite build passed. |
| `npm run test` | `frontend/` | FAIL | 1 | First full run had one non-reproducible `router.test.tsx` failure. |
| `npm run test -- router` | `frontend/` | PASS | 0 | Isolated router suite passed. |
| `npm run test` | `frontend/` | PASS | 0 | 114 files, 1221 tests passed, 8 skipped. |
| `npm run lint` | `frontend/` | PASS | 0 | Review rerun: TypeScript lint configs passed. |
| `npm run build` | `frontend/` | PASS | 0 | Review rerun: production Vite build passed. |
| `npm run test` | `frontend/` | PASS | 0 | Review rerun: 114 files, 1221 tests passed, 8 skipped. |
| `npm.cmd run dev` | `frontend/` | PASS | 0 | Dev server running at `http://localhost:5173/`. |
| Playwright screenshot script | `frontend/` | PASS | 0 | 4 dark-mode screenshots generated. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; line-ending warnings only. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `npm run test:e2e` | no | Story changed global background rendering, not a critical browser flow; Playwright screenshots and full Vitest suite were run. | Browser-level navigation regressions outside screenshots would not be fully covered. | `npm run test`, targeted route tests, dev server startup, screenshots. |

## DRY / No Legacy evidence

- No new dependency, raster asset, page-level background owner, inline style or `App.css` override.
- `RG-085` already existed in `_condamad/stories/regression-guardrails.md`; no registry update needed.
- Background remains canonical through `--premium-app-bg`, `--premium-app-bg-atmosphere`, `.app-bg`, `.app-bg::before`, and `StarfieldBackground`.

## Diff review

- `git diff --stat` reviewed; changed files are scoped to frontend theme/background tests and story evidence.
- `git diff --check` PASS with CRLF warnings only.

## Final worktree status

`git status --short` after implementation:

```text
 M _condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/00-story.md
 M _condamad/stories/story-status.md
 M frontend/src/components/StarfieldBackground.tsx
 M frontend/src/layouts/RootLayout.tsx
 M frontend/src/styles/backgrounds.css
 M frontend/src/styles/premium-theme.css
 M frontend/src/tests/App.test.tsx
 M frontend/src/tests/AppBgStyles.test.ts
 M frontend/src/tests/StarfieldBackground.test.tsx
 M frontend/src/tests/design-system-guards.test.ts
 M frontend/src/tests/visual-smoke.test.tsx
?? _condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/dark-astral-background-after.md
?? _condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/dark-astral-background-before.md
?? _condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/generated/
?? _condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/screenshots/
```

## Review/fix closure

- Review iteration 1 found closure-evidence issues only: missing persisted `generated/11-code-review.md`, story registry still `ready-to-review`, and two non-ASCII comment accents in `StarfieldBackground.tsx`.
- Fix applied: added final clean review artifact, set story and registry status to `done`, normalized comments to ASCII, and reran targeted validation.
- Review iteration 2 verdict: CLEAN.

## Remaining risks

- Artistic validation remains subjective; screenshots are available for reviewer/product review.
- `npm run test:e2e` not run; risk is low for this visual background-only story.

## Suggested reviewer focus

- Route-level full/sober scope in `RootLayout`.
- Canonical dark background layering in `premium-theme.css` and `backgrounds.css`.
- Starfield DOM weight and motion accessibility.
