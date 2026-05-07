# Target Files - CS-085

## Must read

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/package.json`
- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/pages/landing/sections/*.css`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/theme-tokens.test.ts`
- `frontend/src/tests/css-fallback-policy.test.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/tests/App.test.tsx`
- `frontend/src/tests/FaqSection.test.tsx`

## Must search

- `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/layouts/LandingLayout.css src/pages/landing --glob "*.css"`
- `rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/layouts/LandingLayout.css src/pages/landing --glob "*.css"`
- `rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/layouts/LandingLayout.css src/pages/landing --glob "*.css"`
- `rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/layouts/LandingLayout.css src/pages/landing --glob "*.css"`
- `rg -n --glob "*.css" -- "--settings-|--help-|--chat-|--app-" src/layouts/LandingLayout.css src/pages/landing`

## Likely modified

- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/pages/landing/sections/*.css`
- `frontend/src/styles/token-namespace-registry.md`
- `frontend/src/styles/typography-roles.md`
- `frontend/src/tests/design-system-guards.test.ts`
- Story evidence files under this capsule.

## Forbidden unless justified

- `frontend/package.json`
- `frontend/src/pages/landing/**/*.tsx`
- `backend/**`
- Other frontend clusters already protected by RG-055 to RG-059.
