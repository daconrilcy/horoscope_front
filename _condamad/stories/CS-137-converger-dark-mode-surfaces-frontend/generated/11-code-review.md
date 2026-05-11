# Code review CS-137

Verdict: CLEAN.

## Review target

- Story: `CS-137-converger-dark-mode-surfaces-frontend`
- Scope: dark mode runtime surfaces and regression evidence for audited frontend routes.

## Findings fixed

### CR-1 High - Two audited dark surfaces stayed too opaque at runtime

- Bucket: patch
- Location: `frontend/src/components/ShortcutCard.css`, `frontend/src/pages/AstrologerProfilePage.css`
- Source layer: validation / runtime
- Evidence: `npm run test:e2e -- e2e/dark-mode-cs137.spec.ts` failed on 2026-05-11 because `.shortcut-card__subtitle` and `.profile-metrics-bar` had computed `backgroundColor` alpha `0.78`, while the CS-137 runtime guard expects `<= 0.12`.
- Impact: CS-137 could be falsely closed while mobile dark routes still exposed strong opaque panels on `/dashboard` and `/astrologers/:id`.
- Fix applied: both selectors now use `--premium-glass-surface-1` in dark mode, and the CS-137 design-system guard asserts the owners.

### CR-2 Low - Documentation comments missing on modified landing files

- Bucket: patch
- Location: `frontend/src/pages/landing/**`
- Source layer: diff / repository policy
- Evidence: `AGENTS.md` requires a French file-level comment for new or significantly modified applicative files and docstrings for public or non-trivial functions.
- Impact: implementation drift from repository documentation policy across CS-139 to CS-142 landing files.
- Fix applied: added file-level comments to modified landing TSX/CSS files and French JSDoc comments to the non-trivial `LandingHead` helpers and public components touched.

## Acceptance audit

- AC1: PASS. `dark-mode-before.md` and `dark-mode-after.md` exist.
- AC2: PASS. Fixes are in CSS owners, no inline style.
- AC3: PASS. Runtime E2E covers `/dashboard`, `/consultations`, `/astrologers/:id` in `html.dark`.
- AC4: PASS. Residual high-alpha surfaces found during review were patched and revalidated.
- AC5: PASS. `npm run test -- ShortcutCard AstrologersPage visual-smoke design-system`, full `npm run test`, and `npm run build` pass.
- AC6: PASS. `git diff --check` passes with CRLF warnings only; no `App.css` dark corrections were introduced.

## Validation

- `npm run test:e2e -- e2e/dark-mode-cs137.spec.ts` - PASS, 3 tests.
- `npm run test -- ShortcutCard AstrologersPage visual-smoke design-system` - PASS, 103 tests.
- `npm run lint` - PASS.
- `npm run test` - PASS, 115 files, 1235 passed, 8 skipped.
- `npm run build` - PASS.
- `git diff --check` - PASS, CRLF warnings only.

## Guardrails

- `RG-083`: PASS. Audited dark routes have runtime coverage and owner assertions.
- `RG-085`: PASS. No competing global dark background or raster background was introduced.
- `RG-086` / `RG-087`: PASS. No landing-specific background route variant was introduced.

## Verdict

CLEAN
