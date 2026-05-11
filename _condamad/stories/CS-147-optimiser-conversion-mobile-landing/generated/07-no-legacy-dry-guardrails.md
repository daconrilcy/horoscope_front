# No Legacy / DRY Guardrails

- Do not duplicate `SocialProofSection`; hero may expose only compact proof using landing-owned translations.
- Do not copy `pricingConfig` or active plan arrays; `PricingSection.tsx` must keep `getActivePlans()`.
- Do not introduce `app-bg--landing`, `ScopedLandingPage`, style inline, `App.css` fixes, or page-level background variants.
- Do not add `@keyframes`, `animation:`, `filter` or `backdrop-filter` outside exact `RG-088` exceptions.
- Do not add compatibility/fallback/legacy comments or wrappers.

## Required Negative Evidence

- `rg -n "app-bg--landing|style=" src/pages/landing src/layouts`
- `rg -n "@keyframes|animation:|backdrop-filter|filter:" src/pages/landing src/layouts/LandingLayout.css`
- `rg -n "getActivePlans|pricing_plan_select|register\\?plan" src/pages/landing src/tests`

All hits must be classified in final evidence.
