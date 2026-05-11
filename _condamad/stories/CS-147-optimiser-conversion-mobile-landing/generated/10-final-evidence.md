# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-147-optimiser-conversion-mobile-landing`
- Source story: `_condamad/stories/CS-147-optimiser-conversion-mobile-landing/00-story.md`
- Capsule path: `_condamad/stories/CS-147-optimiser-conversion-mobile-landing/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: pre-existing `story-status.md`, `.codex-artifacts/*.png`, CS-147 capsule directory.
- AGENTS.md considered: `AGENTS.md`.
- Guardrail registry read: yes.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story present. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated before code edits. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC10 listed. |
| `generated/04-target-files.md` | yes | yes | PASS | Target map generated. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands discovered from package scripts and story. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific DRY/no-legacy guards generated. |
| `generated/10-final-evidence.md` | yes | yes | PASS | In progress. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `LandingPage.css` compact mobile; `.hero-reassurance` masquée mobile. | After runtime `.hero-device y=833` on `390x844`; targeted tests PASS. | PASS | Seuil `y < 844` atteint. |
| AC2 | CTA hero préservé dans `HeroSection.tsx`. | After runtime `.hero-ctas bottom=711`; `LandingPage` PASS. | PASS | |
| AC3 | `.hero-proof-strip` ajouté. | After runtime `y=723 bottom=816`; `LandingPage` PASS. | PASS | |
| AC4 | Preuve depuis `t.socialProof.badges.swiss` et `t.socialProof.proofs.swiss`. | Test DOM vérifie badge et proof. | PASS | Source landing owned. |
| AC5 | Filtres landing non essentiels supprimés; `RG-088` réduit. | `design-system-guards` PASS + scan filtres classifié. | PASS | Reste navbar shell/menu + reduced-motion. |
| AC6 | `PricingSection.tsx` conserve `getActivePlans()`. | Test DOM pricing Free/Basic/Premium PASS. | PASS | |
| AC7 | Hrefs pricing inchangés. | Test DOM `/register?plan=free|basic|premium` PASS. | PASS | |
| AC8 | Event `pricing_plan_select` conservé. | Test interaction Basic PASS. | PASS | |
| AC9 | `FaqSection.tsx` CTA final conservé. | Test DOM href `/register` PASS. | PASS | |
| AC10 | Tests, scans et lint exécutés. | Lint PASS, targeted PASS, full Vitest PASS, scans PASS/classifiés. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `frontend/src/pages/landing/sections/HeroSection.tsx` | modified | Ajout preuve compacte hero. | AC3, AC4 |
| `frontend/src/pages/landing/LandingPage.css` | modified | Densité mobile hero et style preuve compacte. | AC1, AC2, AC3 |
| `frontend/src/pages/landing/sections/LandingNavbar.css` | modified | Retrait filtres langue/dropdown. | AC5, AC10 |
| `frontend/src/pages/landing/sections/SocialProofSection.css` | modified | Retrait filtre social proof. | AC5, AC10 |
| `frontend/src/pages/landing/sections/TestimonialsSection.css` | modified | Retrait filtres testimonials. | AC5, AC10 |
| `frontend/src/pages/landing/sections/PricingSection.css` | modified | Hover pricing limité desktop. | AC6 |
| `frontend/src/tests/LandingPage.test.tsx` | modified | Tests preuve hero, pricing, tracking, FAQ. | AC3-AC9 |
| `frontend/src/tests/visual-smoke.test.tsx` | modified | Guards statiques densité mobile et hover desktop. | AC1, AC10 |
| `frontend/src/tests/design-system-guards.test.ts` | modified | Allowlist `RG-088` réduite aux filtres restants. | AC5, AC10 |
| `_condamad/stories/CS-147-optimiser-conversion-mobile-landing/landing-conversion-before.md` | added | Baseline runtime. | AC1-AC7 |
| `_condamad/stories/CS-147-optimiser-conversion-mobile-landing/landing-conversion-after.md` | added | Preuve after runtime/scans. | AC1-AC10 |
| `_condamad/stories/CS-147-optimiser-conversion-mobile-landing/generated/*` | added/modified | Capsule CONDAMAD. | AC1-AC10 |
| `_condamad/stories/story-status.md` | modified | Statut `ready-to-review`. | AC10 |
| `_condamad/stories/CS-147-optimiser-conversion-mobile-landing/00-story.md` | modified | Statut et tâches cochées. | AC1-AC10 |

## Files deleted

None.

## Tests added or updated

- `LandingPage.test.tsx`: preuve compacte hero, plans/hrefs pricing, tracking `pricing_plan_select`, CTA final FAQ.
- `visual-smoke.test.tsx`: densité mobile hero et hover pricing desktop.
- `design-system-guards.test.ts`: exceptions `RG-088` exactes mises à jour.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture` | `frontend/` | PASS | 0 | 5 files, 140 tests passed. |
| `npm run lint` | `frontend/` | PASS | 0 | TypeScript lint configs passed. |
| `npm run test` | `frontend/` | PASS | 0 | 115 files, 1243 tests passed, 8 skipped. |
| `rg -n "app-bg--landing|style=" src/pages/landing src/layouts` | `frontend/` | PASS | 1 | Zero hit. |
| `rg -n "@keyframes|animation:|backdrop-filter|filter:" src/pages/landing src/layouts/LandingLayout.css` | `frontend/` | PASS | 0 | Only classified navbar filters and reduced-motion hit. |
| `rg -n "Cormorant|Petit Formal|Brush Script|font-family:\s*\"" src -g "*.css" -g "*.scss"` | `frontend/` | PASS | 1 | Zero hit. |
| `rg -n "getActivePlans|pricing_plan_select|register\?plan" src/pages/landing src/tests` | `frontend/` | PASS | 0 | Canonical pricing usage and tests only. |
| Playwright Chromium runtime measurement via `node --input-type=module -e ...` | `frontend/` | PASS | 0 | Before and after metrics captured for `390x844`, `768x1024`, `1440x1000`. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; only line-ending warnings reported. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| `npm run test:e2e` | no | Story validation plan targeted Vitest/runtime measurement, no E2E flow modified. | Browser-level route regressions outside landing could be missed. | Playwright runtime measurement + full Vitest suite. |

## DRY / No Legacy evidence

- No duplicate social proof section introduced; hero uses compact proof from `t.socialProof`.
- Pricing remains sourced by `getActivePlans()`.
- No `App.css`, `RootLayout`, backend, SEO/head or pricing config changes.
- `app-bg--landing|style=` scan zero hit in landing/layouts.
- Remaining filter/motion hits are exact and guarded.

## Diff review

- Changes are scoped to landing owners, tests, and CS-147 evidence.
- No dependency changes.
- No files deleted.

## Final worktree status

```text
 M _condamad/stories/story-status.md
 M frontend/src/pages/landing/LandingPage.css
 M frontend/src/pages/landing/sections/HeroSection.tsx
 M frontend/src/pages/landing/sections/LandingNavbar.css
 M frontend/src/pages/landing/sections/PricingSection.css
 M frontend/src/pages/landing/sections/SocialProofSection.css
 M frontend/src/pages/landing/sections/TestimonialsSection.css
 M frontend/src/tests/LandingPage.test.tsx
 M frontend/src/tests/design-system-guards.test.ts
 M frontend/src/tests/visual-smoke.test.tsx
?? .codex-artifacts/landing-desktop.png
?? .codex-artifacts/landing-mobile-menu.png
?? .codex-artifacts/landing-mobile.png
?? .codex-artifacts/landing-tablet.png
?? _condamad/stories/CS-147-optimiser-conversion-mobile-landing/
```

## Remaining risks

- `npm run test:e2e` not run; covered by targeted Chromium measurements and full Vitest.

## Suggested reviewer focus

- Review the mobile hero density tradeoff: micro reassurance is hidden on mobile in favor of compact proof + product shell visibility.
- Review `RG-088` allowlist reduction and remaining navbar filter justifications.
