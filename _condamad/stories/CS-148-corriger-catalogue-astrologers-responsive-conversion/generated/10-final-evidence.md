# Final Evidence - CS-148

## Story status

done

## Preflight

- Root `AGENTS.md`, story `00-story.md`, generated capsule files, frontend references and `_condamad/stories/regression-guardrails.md` were read.
- Initial dirty workspace contained modified `_condamad/stories/story-status.md`, untracked CS-148 capsule folder and untracked `output/`.
- Applicable guardrails: `RG-079`, `RG-081`, `RG-084`, `RG-087`, `RG-058`, `RG-059`, `RG-060`, `RG-061`, `RG-078`, `RG-082`, `RG-083`.

## Capsule validation

- Capsule generated with `condamad_prepare.py`.
- `condamad_validate.py` initially failed because this evidence file missed required section headings; fixed in this revision.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `featured` prop removed; catalogue featured span styles removed. | Desktop `1440x1000`: 4 equal columns, no featured class. | PASS |
| AC2 | Responsive `.people-page .person-grid` plus mobile override. | Mobile `390x844`: 1 column. | PASS |
| AC3 | Grid minmax uses viewport-safe width. | Mobile `390x844`: `horizontalOverflow=false`. | PASS |
| AC4 | `.person-card-cta` localized CTA rendered per card. | `AstrologersPage.test.tsx` and Playwright `ctaCount=6`. | PASS |
| AC5 | Provider/default/editorial badges visible. | DOM tests and Playwright counts. | PASS |
| AC6 | Catalogue fixed heights 244/256 removed. | Scoped scan zero-hit. | PASS |
| AC7 | Existing card click navigation preserved. | Test and Playwright click navigate to `/astrologers/:id`. | PASS |
| AC8 | `media.css` typo fixed. | `mix-blend-mode` replaces typo; scoped scan zero-hit. | PASS |
| AC9 | No forbidden destinations touched. | `App.css`, inline styles and `.astrologer-*` scans zero-hit. | PASS |
| AC10 | Guards updated and `RG-089` added. | Targeted `AstrologersPage design-system visual-smoke` passes. | PASS |
| AC11 | CTA in card flow with no fixed card height. | Playwright mobile: final CTA visible above bottom nav. | PASS |
| AC12 | CTA rendered as `span`; no child button added. | DOM test and Playwright `nestedInteractiveCount=0`. | PASS |

## Files changed

- `frontend/src/features/astrologers/components/AstrologerGrid.tsx`
- `frontend/src/features/astrologers/components/AstrologerCard.tsx`
- `frontend/src/i18n/astrologers.ts`
- `frontend/src/styles/app/cards.css`
- `frontend/src/styles/app/media.css`
- `frontend/src/tests/AstrologersPage.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/story-status.md`
- `_condamad/stories/CS-148-corriger-catalogue-astrologers-responsive-conversion/astrologers-catalog-before.md`
- `_condamad/stories/CS-148-corriger-catalogue-astrologers-responsive-conversion/astrologers-catalog-after.md`
- `_condamad/stories/CS-148-corriger-catalogue-astrologers-responsive-conversion/astrologers-after-*.png`
- `_condamad/stories/CS-148-corriger-catalogue-astrologers-responsive-conversion/generated/*.md`

## Files deleted

None.

## Tests added or updated

- `AstrologersPage.test.tsx`: CTA, visible choice signals and no nested button/no featured class.
- `AstrologersPage.test.tsx`: shared `AstrologerGrid` keeps the profile CTA opt-in outside the `/astrologers` catalogue.
- `visual-smoke.test.tsx`: responsive grid, visible badges, CTA, line clamp and anti typo.
- `design-system-guards.test.ts`: CS-148 guard against featured span, hidden badges and typo regression.

## Commands run

- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-dev-story/scripts/condamad_prepare.py ... --with-optional` - PASS.
- `cd frontend; npm run test -- AstrologersPage design-system visual-smoke` - PASS, 87 tests after review fix.
- `cd frontend; npm run lint` - PASS.
- `cd frontend; npm run test` - PASS, 115 files, 1245 tests passed, 8 skipped.
- `cd frontend; rg -n "people-page|person-card" src/App.css` - PASS, zero hit.
- `cd frontend; rg -n "astrologer-" src/styles/app src/features/astrologers` - PASS, zero hit.
- `cd frontend; rg -n "style=" src/pages/AstrologersPage.tsx src/features/astrologers` - PASS, zero hit.
- `cd frontend; rg -n "mix-alend-mode|featured=\\{index === 0\\}|height:\\s*24[0-9]px|height:\\s*25[0-9]px" src/features/astrologers src/styles/app/cards.css src/styles/app/media.css src/tests` - PASS, zero hit.
- `cd frontend; rg -n "toHaveClass\\(\"person-card--featured\"\\)|badges stay hidden|Provider default featured badges stay hidden" src/tests/visual-smoke.test.tsx src/tests/design-system-guards.test.ts` - PASS, zero hit.
- `git diff --check` - PASS.
- `cd frontend; npm run dev -- --host 127.0.0.1 --port 5173` - PASS, HTTP 200 on `/astrologers`.
- Playwright runtime script - PASS, viewports `390x844`, `768x1024`, `1440x1000`, dark mobile and click navigation measured.

## Review fix loop

- Iteration 1 verdict: `CHANGES_REQUESTED`.
- Finding fixed: the visual profile CTA leaked from the `/astrologers` catalogue into shared `AstrologerGrid` consumers such as the natal persona selector. The CTA is now opt-in via `showProfileCta` and enabled only by `AstrologersPage`.
- Iteration 2 verdict: `CLEAN`.

## Commands skipped or blocked

- `npm run test:e2e` - NOT_RUN: the story validation contract requires targeted Vitest guards plus viewport runtime evidence; direct Playwright runtime checks covered the required page flow without running the full E2E suite. Risk: unrelated E2E-only flows were not revalidated.

## DRY / No Legacy evidence

- No duplicate card or grid component was introduced.
- `featured={index === 0}` removed from catalogue owner.
- No `App.css` change, no inline style, no `.astrologer-*`.
- No new dependency, store, API call or route introduced.
- `RG-089` added to block reintroduction.
- Profile CTA is opt-in on the shared grid, preventing misleading copy in selection flows that do not navigate to `/astrologers/:id`.

## Diff review

- Diff reviewed with `git diff --stat` and focused `git diff` on frontend owners/tests.
- No backend changes.
- Broad all-`src` scan for `height:\s*24/25` still finds unrelated pre-existing heights outside catalogue; the durable CS-148 guard is scoped to catalogue owners and tests.

## Final worktree status

```text
 M _condamad/stories/regression-guardrails.md
 M _condamad/stories/story-status.md
 M frontend/src/features/astrologers/components/AstrologerCard.tsx
 M frontend/src/features/astrologers/components/AstrologerGrid.tsx
 M frontend/src/i18n/astrologers.ts
 M frontend/src/pages/AstrologersPage.tsx
 M frontend/src/styles/app/cards.css
 M frontend/src/styles/app/media.css
 M frontend/src/tests/AstrologersPage.test.tsx
 M frontend/src/tests/design-system-guards.test.ts
 M frontend/src/tests/visual-smoke.test.tsx
?? _condamad/stories/CS-148-corriger-catalogue-astrologers-responsive-conversion/
?? output/
```

## Remaining risks

- Badge density on very small translated labels should be reviewed visually for Spanish/English copy, although clamps and wrapping are in place.
- Full Playwright E2E suite was not run.

## Suggested reviewer focus

- Visual balance of visible provider/default/editorial badges on `390x844`.
- Scope and usefulness of the new `RG-089` guard.
