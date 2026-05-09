# Final Evidence

<!-- Preuve finale CONDAMAD pour CS-128. Ce fichier est complete apres implementation et validation. -->

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-128-restaurer-relief-visuel-astrologers`
- Source story: `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md`
- Capsule path: `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Story source: capsule directory
- Initial `git status --short`: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md` modified; CS-128 capsule untracked.
- Pre-existing dirty files: `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, CS-128 source files.
- AGENTS.md files considered: user-provided repository instructions.
- Capsule generated: yes, missing `generated/` files created.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story readable. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC11 covered. |
| `generated/04-target-files.md` | yes | yes | PASS | Created. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Created. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Created. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `astrologers-visual-before.md` owner mapping table. | `rg -n "Owner mapping" _condamad/stories/CS-128*/astrologers-visual-before.md` PASS. | PASS | |
| AC2 | `cards.css` compact card background/border/shadow restored to `--app-person-card-*`; guard added. | `npm run test -- AstrologersPage design-system visual-smoke` PASS. | PASS | |
| AC3 | `.people-page .person-card--featured` keeps `grid-column: span 2` and featured material tokens. | `npm run test -- AstrologersPage design-system visual-smoke` PASS. | PASS | |
| AC4 | `.people-page .person-card-icon` keeps token-backed background/shadow; DOM smoke checks icon class. | `npm run test -- AstrologersPage design-system visual-smoke` PASS. | PASS | |
| AC5 | Compact avatar keeps token-backed background/border/shadow; media pseudo-elements unchanged. | `npm run test -- AstrologersPage design-system visual-smoke` PASS. | PASS | |
| AC6 | `.people-page .person-card-tag` keeps token-backed background/border/shadow. | `npm run test -- theme-tokens css-fallback inline-style legacy-style` PASS. | PASS | |
| AC7 | Compact provider/default/featured badge selector remains `display: none`; DOM smoke verifies badges remain present for CSS hiding. | `npm run test -- AstrologersPage design-system visual-smoke` PASS. | PASS | |
| AC8 | No `App.css` changes for this surface; design guard checks import entry. | `rg -n "person-card\|people-page\|astrologer" src/App.css` zero-hit. | PASS | |
| AC9 | No exact `.astrologer-*` legacy selector added. | `rg -n "\.astrologer-(card\|grid\|card-avatar\|card-specialties)" src/styles/app src/features/astrologers src/pages/AstrologersPage.tsx` zero-hit. | PASS | Broad `default-astrologer-grid` Settings hits classified out of scope false positive. |
| AC10 | `AstrologersPage` route behavior unchanged. | Existing `AstrologersPage` tests pass in targeted suite. | PASS | |
| AC11 | `astrologers-visual-after.md` and `validation-evidence.md` added. | `rg -n "Commands run" _condamad/stories/CS-128*/astrologers-visual-after.md` PASS. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` | modified | Synchronize source story status, tasks and review findings after adversarial review. | Closure |
| `frontend/src/styles/app/cards.css` | modified | Restore compact astrologer card material tokens. | AC2-AC7 |
| `frontend/src/styles/app/tokens.css` | modified | Add compact token owners for stronger `/astrologers` colors, shadows, icon, avatar and chip material. | AC2-AC7 |
| `frontend/src/tests/design-system-guards.test.ts` | modified | Add CS-128 static design-system guard. | AC2-AC9 |
| `frontend/src/tests/visual-smoke.test.tsx` | modified | Add CS-128 CSS and rendered DOM smoke checks. | AC4-AC10 |
| `_condamad/stories/CS-127-reduire-app-css-par-primitives-types-modulaires/app-css-variable-usage.md` | modified | Classify retained single-use compact visual tokens required by CS-128. | Guard |
| `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/astrologers-visual-before.md` | added | Before owner mapping. | AC1 |
| `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/astrologers-visual-after.md` | added | After evidence and command summary. | AC11 |
| `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/validation-evidence.md` | added | Validation log and scan classification. | AC1-AC11 |
| `_condamad/stories/CS-128-restaurer-relief-visuel-astrologers/generated/*` | added/modified | Capsule traceability and final evidence. | AC1-AC11 |
| `_condamad/stories/story-status.md` | modified | Synchronize story status. | Closure |

## Files deleted

None.

## Tests added or updated

- `design-system-guards.test.ts`: CS-128 static guard for compact card material, featured span, icon/avatar/chip tokens, hidden badges, App.css and legacy selector absence.
- `visual-smoke.test.tsx`: CS-128 CSS smoke plus rendered DOM smoke for `/astrologers`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `npm run test -- AstrologersPage design-system visual-smoke` | `frontend/` | PASS | 0 | 3 files, 68 tests passed. |
| `npm run test -- theme-tokens css-fallback inline-style legacy-style` | `frontend/` | PASS | 0 | 4 files, 108 tests passed. |
| `npm run lint` | `frontend/` | PASS | 0 | TypeScript lint configs pass. |
| `npm run build` | `frontend/` | PASS | 0 | Production build succeeds. |
| `rg -n "person-card\|people-page\|astrologer" src/App.css` | `frontend/` | PASS | 1 | Zero hits. |
| `rg -n "\.astrologer-(card\|grid\|card-avatar\|card-specialties)" src/styles/app src/features/astrologers src/pages/AstrologersPage.tsx` | `frontend/` | PASS | 1 | Zero exact forbidden selector hits. |
| `rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers/components/AstrologerCard.tsx src/features/astrologers/components/AstrologerGrid.tsx` | `frontend/` | PASS | 1 | Zero hits. |
| `rg --files src/styles/app` | `frontend/` | PASS | 0 | Approved modules only. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict-marker errors. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` | repo root | PASS | 0 | Story validation passed. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` | repo root | PASS | 0 | Contract explanation shows no missing required contracts. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` | repo root | PASS | 0 | Story lint passed. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/00-story.md` | repo root | PASS | 0 | Strict story lint passed. |
| `npm run lint` | `frontend/` | PASS | 0 | Re-run after adversarial review metadata fixes; TypeScript lint configs pass. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Browser screenshot capture | no | Not captured in this session. | Manual visual inspection still recommended. | DOM smoke, CSS guards, tests, lint and build passed. |

## DRY / No Legacy evidence

- No new dependency.
- No new `frontend/src/styles/app/` module.
- No `frontend/src/App.css` active selector or variable added.
- Exact forbidden legacy selector scan is zero-hit.
- Broad `default-astrologer-grid` Settings hits are pre-existing, outside `/astrologers`, and not the forbidden `.astrologer-grid` selector.

## Diff review

- Scope reviewed: frontend changes limited to `cards.css`, `design-system-guards.test.ts`, `visual-smoke.test.tsx`.
- Evidence changes limited to CS-128 capsule and status synchronization.
- No backend/API/data/route behavior changes.

## Final worktree status

`git status --short` after implementation:

```text
 M _condamad/stories/regression-guardrails.md
 M _condamad/stories/story-status.md
 M frontend/src/styles/app/cards.css
 M frontend/src/tests/design-system-guards.test.ts
 M frontend/src/tests/visual-smoke.test.tsx
?? _condamad/stories/CS-128-restaurer-relief-visuel-astrologers/
```

## Remaining risks

- Screenshot evidence was not captured; reviewer should visually inspect `/astrologers` if needed.

## Suggested reviewer focus

Review compact `/astrologers` material restoration, guard specificity, DOM smoke coverage, and the classified broad-scan false positive `default-astrologer-grid` outside scope.

## Adversarial re-review

- 2026-05-10: new adversarial review found closure metadata drift in `00-story.md`
  and stale capsule wording.
- Correction applied: source story status and tasks synchronized to `done`,
  review findings persisted in `00-story.md`, final evidence wording corrected.
- Validation after correction: story validation PASS, strict story lint PASS,
  `npm run test -- AstrologersPage design-system visual-smoke` PASS, `npm run lint` PASS,
  `git diff --check` PASS.
- 2026-05-10: user screenshot showed the first visual correction remained
  insufficient: missing color, weak shadows, muted icons and flat chips.
- Correction applied: compact visual values moved into `tokens.css`,
  `cards.css` now consumes those tokens, and tests guard token-backed relief
  instead of raw declaration values.
- 2026-05-10: controlled Playwright capture showed compact token runtime
  failure because `#root` tokens referenced card-scoped `--astro-*` variables.
- Correction applied: compact visual tokens that depend on `--astro-*` now
  resolve on `.person-card`; compact card height/radius/spacing were aligned
  with the original capture; `.person-card-icon` is positioned relative to the
  card instead of the topline.
- Visual evidence: `generated/visual-after-icon-fix.png`.
- 2026-05-10: micro-adjustments applied after user review:
  icon depth `z-index: 5` over avatar `z-index: 1`, gradient ring via
  `--app-person-card-compact-icon-ring-background`, Etienne divider contrast
  restored, and `person-card-style` color set to
  `--app-person-card-compact-style-color`.
- Visual evidence: `generated/visual-after-micro-icon-hover.png`.
- 2026-05-10: final shell adjustment applied after scroll review:
  `.app-header` keeps `position: sticky`, `top: 0`, `z-index: 220`,
  token-backed translucent background, `backdrop-filter: blur(24px)
  saturate(1.7)` at runtime, and a `::before` veil so content scrolls
  visually underneath the top menu.
- Visual evidence: `generated/visual-header-glass-scroll.png`.
