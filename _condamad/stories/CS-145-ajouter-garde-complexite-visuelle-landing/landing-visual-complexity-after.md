<!-- Preuve post-implementation CS-145. -->

# Landing Visual Complexity After

Executable guard:

- Added `borne la complexite visuelle motion et filters landing par exceptions exactes` in `frontend/src/tests/design-system-guards.test.ts`.
- The guard fails on any landing `@keyframes`.
- The guard fails on any `animation`, `filter`, `backdrop-filter` or `-webkit-backdrop-filter` not listed by exact file, selector, property and value.
- The guard rejects wildcard-like entries and entries missing reason or exit condition.
- The guard rejects stale exceptions that no longer match a real landing CSS declaration.

Exact retained exceptions:

- `LandingNavbar.css` `.landing-navbar__shell` `backdrop-filter: blur(14px)`.
- `LandingNavbar.css` `.landing-navbar__lang` `backdrop-filter: blur(18px) saturate(135%)`.
- `LandingNavbar.css` `.landing-navbar__lang-dropdown` `backdrop-filter: blur(22px) saturate(145%)`.
- `LandingNavbar.css` `.landing-navbar__mobile-menu` `backdrop-filter: blur(6px)`.
- `SocialProofSection.css` `.social-proof__container` `backdrop-filter: blur(18px)`.
- `TestimonialsSection.css` `.testimonial-card` `backdrop-filter: blur(18px) saturate(140%)`.
- `TestimonialsSection.css` `.testimonial-card` `-webkit-backdrop-filter: blur(18px) saturate(140%)`.

Validation:

- `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture` - PASS.
- `npm run test -- design-system visual-smoke LandingPage` - PASS after review fix, including stale-exception rejection.
- `rg -n "@keyframes|animation:|backdrop-filter|filter:" src/pages/landing src/layouts/LandingLayout.css` - PASS with all hits classified above; `animation: none !important` is reduced-motion only and ignored by the executable guard.
- `rg -n -- "--landing-(misc|common|temp|shared|base|general|global)-" src/pages/landing src/layouts` - PASS, zero hit.

Registry update:

- Added `RG-088` to `_condamad/stories/regression-guardrails.md`.
