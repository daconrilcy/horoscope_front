# Validation plan CS-142

- `npm run test -- LandingPage`
- `npm run lint`
- `rg -n "document\." src/pages/landing/LandingPage.tsx`
- `rg -n "AC[0-9]" src/pages/landing -g "*.tsx"`
- `rg -n "react-helmet|@helmet|head-manager|compat|fallback" package.json src/pages/landing`
