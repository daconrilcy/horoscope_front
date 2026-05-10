# Profile UI Before

## Scope

- Route: `/astrologers/:id`
- Files inspected: `AstrologerProfilePage.tsx`, `AstrologerProfilePage.css`, `AstrologerProfileSections.tsx`, `AstrologersPage.test.tsx`
- Runtime browser baseline: pending live e2e before code changes; static source baseline captured here.

## Observations

- Horizontal overflow candidates are local to `AstrologerProfilePage.css`: fixed `390px` / `320px` / `286px` avatar containers, wide hero grid, absolute decorative orbit/halo, large fixed right column `440px`, and fixed-min-width final CTA.
- No global `overflow-x: hidden` is present in `AstrologerProfilePage.css`; the fix must keep this property absent and correct the local sizing source.
- The primary consultation CTA is only in `AstrologerProfileFinalCta`, after metrics, about, mission, specialties, method and reviews.
- Hero badges mix default status/action, provider type, positioning and personal metadata in one flow, making the default action compete with identity.
- Metrics use value/label rendering but no helper copy to normalize interpretation across cards.
- Method steps render four labels without helper text.
- Empty review copy says there are no public reviews, but the header can still render a non-zero score with `(0 avis)`.
- Mobile CSS collapses metrics to one column at `520px`, despite the story target of readable 2x2 until the smallest breakpoint.

## Required before/after deltas

- Add hero consultation CTA without changing `handleConsultationCta`.
- Correct local sizing with responsive constraints and no `overflow-x: hidden`.
- Keep active profile styles out of `frontend/src/App.css`.
- Split empty public reviews from positive-review stats.
- Add deterministic tests/guards for the new invariant.
