# Preuve after CS-142 - SEO/head landing

## Owner final

- Owner SEO/head: `frontend/src/pages/landing/LandingHead.tsx`.
- Page de composition: `frontend/src/pages/landing/LandingPage.tsx`.
- `LandingPage.tsx` conserve `track("landing_view", getUtmParams())` et rend les sections marketing.

## Comportement teste

- Pose `title`, description, Open Graph, canonical et JSON-LD.
- Met a jour puis restaure les tags preexistants au demontage.
- Supprime les tags crees par la landing au demontage.
- N'ajoute aucune dependance de head-management.

## Validation

- `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture` - PASS, 131 tests.
- `npm run lint` - PASS.
- `rg -n "document\." src/pages/landing/LandingPage.tsx` - PASS, zero-hit.
- `rg -n "AC[0-9]" src/pages/landing -g "*.tsx"` - PASS, zero-hit.
- `rg -n "react-helmet|@helmet|head-manager|compat|fallback" package.json src/pages/landing` - PASS, zero-hit.
