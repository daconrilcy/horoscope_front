# CONDAMAD Code Review

## Review target

- Story: `CS-149-optimiser-hierarchie-premium-catalogue-astrologers`
- Scope reviewed: `/astrologers` catalogue hierarchy, card DOM/CSS, empty state, i18n, regression guards, visual evidence.

## Inputs reviewed

- `_condamad/stories/CS-149-optimiser-hierarchie-premium-catalogue-astrologers/00-story.md`
- Generated evidence files `03`, `06`, `07`, `10`
- `_condamad/stories/regression-guardrails.md`
- Current diff for `frontend/src/features/astrologers/**`, `frontend/src/pages/AstrologersPage.tsx`, `frontend/src/i18n/astrologers.ts`, `frontend/src/styles/app/**`, and changed tests.

## Iteration 1 findings

### CR-1 High - Required viewport evidence did not prove `/astrologers`

- Bucket: patch
- Location: `_condamad/stories/regression-guardrails.md:133`
- Source layer: validation / acceptance
- Evidence: `RG-090` requires captures 390/768/1440. Initial screenshots captured the login page because `/astrologers` redirected to `/login?returnTo=%2Fastrologers`.
- Impact: AC5, AC6, AC12 and RG-090 could be falsely accepted without visual proof of the catalogue.
- Fix applied: regenerated authenticated catalogue screenshots with a non-expired local visual token and copied them into the story capsule: `screenshots/astrologers-auth-390x844.png`, `screenshots/astrologers-auth-768x1024.png`, `screenshots/astrologers-auth-1440x1000.png`.

### CR-2 High - Primary badge decoration overlapped badge text

- Bucket: patch
- Location: `frontend/src/styles/app/cards.css`
- Source layer: edge / acceptance
- Evidence: authenticated screenshots showed the decorative `.person-card-icon` overlapping labels such as `DEBUTANTS`, `CYCLES`, and `ANALYSE PRECISE`.
- Impact: AC2 and RG-090 were only partially satisfied: the primary badge existed but was not reliably readable.
- Fix applied: changed the catalogue icon override from absolute positioning to relative flex positioning and updated design-system/visual-smoke guards.

### CR-3 Low - Modified test files missed the repository French file comment convention

- Bucket: patch
- Location: `frontend/src/tests/AstrologersPage.test.tsx`, `frontend/src/tests/visual-smoke.test.tsx`
- Source layer: diff integrity
- Evidence: repository `AGENTS.md` requires a French global comment for significantly modified applicative files.
- Impact: documentation discipline drift on modified validation surfaces.
- Fix applied: added concise French top-of-file comments.

## Iteration 2 findings

- None.

## Acceptance audit

| AC | Verdict | Evidence |
|---|---|---|
| AC1 | PASS | DOM order tests assert avatar/name/style before badges. |
| AC2 | PASS | Badge hierarchy is tested and screenshots confirm readable primary badge after CR-2 fix. |
| AC3 | PASS | CTA row CSS and DOM assertions pass. |
| AC4 | PASS | Card remains the only button; no nested `button` or `a`. |
| AC5 | PASS | CSS guard and 1440x1000 screenshot show three desktop columns. |
| AC6 | PASS | Mobile CSS guard and 390x844 screenshot show one column. |
| AC7 | PASS | Localized choice criteria rendered and tested. |
| AC8 | PASS | Empty state title, explanation and next action tested. |
| AC9 | PASS | Reduced-motion CSS guard present and tested. |
| AC10 | PASS | Forbidden catalogue scans pass; broad height hits are pre-existing non-catalogue surfaces. |
| AC11 | PASS | RG-079, RG-081, RG-083, RG-084, RG-087, RG-089, RG-090 preserved. |
| AC12 | PASS | Before/after markdown artifacts and authenticated viewport screenshots exist. |

## Validation audit

- `npm run test -- AstrologersPage design-system visual-smoke`: PASS, 87 tests.
- `npm run lint`: PASS.
- `npm run test`: PASS, 115 files, 1245 passed, 8 skipped.
- `git diff --check`: PASS.
- Forbidden scans for `App.css`, `.astrologer-*`, and inline `style=`: PASS.
- Catalogue-scoped fragile featured/height scan: PASS.
- Browser screenshots: PASS for 390x844, 768x1024, 1440x1000.
- `npm run test:e2e`: NOT_RUN, not required for this front-only visual hierarchy patch after targeted Vitest, full Vitest and browser screenshot evidence.

## DRY / No Legacy audit

- No duplicate card/grid component introduced.
- No `App.css` catalogue styles.
- No `.astrologer-*` selectors.
- No inline styles in touched route/feature files.
- No `featured={index === 0}` or `.person-card--featured`.

## Verdict

CLEAN
