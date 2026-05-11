# Target Files

## Must Read

- `frontend/src/pages/landing/LandingPage.tsx`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/pages/landing/sections/HeroSection.tsx`
- `frontend/src/pages/landing/sections/SocialProofSection.tsx`
- `frontend/src/pages/landing/sections/SocialProofSection.css`
- `frontend/src/pages/landing/sections/LandingNavbar.css`
- `frontend/src/pages/landing/sections/TestimonialsSection.css`
- `frontend/src/pages/landing/sections/PricingSection.tsx`
- `frontend/src/pages/landing/sections/PricingSection.css`
- `frontend/src/pages/landing/sections/FaqSection.tsx`
- `frontend/src/pages/landing/sections/FaqSection.css`
- `frontend/src/config/pricingConfig.ts`
- `frontend/src/tests/LandingPage.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/AppBgStyles.test.ts`

## Must Search

- `rg -n "@keyframes|animation:|backdrop-filter|filter:" frontend/src/pages/landing frontend/src/layouts/LandingLayout.css`
- `rg -n "app-bg--landing|style=" frontend/src/pages/landing frontend/src/layouts`
- `rg -n "pricing_plan_select|register\\?plan|getActivePlans" frontend/src`

## Likely Modified

- `HeroSection.tsx`, `LandingPage.css`, landing CSS section files, `LandingPage.test.tsx`, `visual-smoke.test.tsx`, `design-system-guards.test.ts`, story evidence files.

## Forbidden Unless Explicitly Justified

- `frontend/src/App.css`
- `frontend/src/layouts/RootLayout.tsx`
- `frontend/src/pages/landing/LandingHead.tsx`
- `frontend/src/config/pricingConfig.ts`
- `backend/**`
