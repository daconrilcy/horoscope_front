# Acceptance Traceability

<!-- Matrice de tracabilite AC vers preuves d'implementation et validation. -->

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Before artifact has owner mapping. | Added `astrologers-visual-before.md`. | `rg -n "Owner mapping" _condamad/stories/CS-128*/astrologers-visual-before.md` passed. | PASS |
| AC2 | Compact cards keep token-backed material. | Restored `.people-page .person-card` material in `cards.css`; guard in `design-system-guards.test.ts`. | `npm run test -- AstrologersPage design-system visual-smoke` passed. | PASS |
| AC3 | Featured card remains full-width. | Kept `.people-page .person-card--featured { grid-column: span 2; }` and distinct material. | `npm run test -- AstrologersPage design-system visual-smoke` passed. | PASS |
| AC4 | Small persona icon remains visible. | Kept `.people-page .person-card-icon` token-backed; rendered DOM smoke verifies class exists. | `npm run test -- AstrologersPage design-system visual-smoke` passed. | PASS |
| AC5 | Avatars keep visual relief. | Preserved media pseudo-elements and compact avatar material tokens. | `npm run test -- AstrologersPage design-system visual-smoke` passed. | PASS |
| AC6 | Specialty chips keep themed material. | Kept `.people-page .person-card-tag` token-backed and themed. | `npm run test -- theme-tokens css-fallback inline-style legacy-style` passed. | PASS |
| AC7 | Provider default featured badges stay hidden. | Kept compact badge selectors hidden; DOM smoke verifies badges still render for CSS hiding. | `npm run test -- AstrologersPage design-system visual-smoke` passed. | PASS |
| AC8 | `App.css` keeps zero active page style. | No code changes in `App.css`; guard/scans pass. | `rg -n "person-card\|people-page\|astrologer" src/App.css` zero-hit. | PASS |
| AC9 | No legacy astrologer selector returns. | No exact `.astrologer-*` selector or alias introduced. | Exact forbidden selector scan zero-hit; broad `default-astrologer-grid` Settings hits classified out of scope false positive. | PASS |
| AC10 | Existing route states still pass. | React behavior unchanged; route tests pass. | `npm run test -- AstrologersPage design-system visual-smoke` passed. | PASS |
| AC11 | After evidence records commands. | Added `astrologers-visual-after.md` and `validation-evidence.md`. | `rg -n "Commands run" _condamad/stories/CS-128*/astrologers-visual-after.md` passes. | PASS |
