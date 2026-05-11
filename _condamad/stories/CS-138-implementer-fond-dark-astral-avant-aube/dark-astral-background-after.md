# Dark Astral Background After

## Implementation summary

- `premium-theme.css`: dark `--premium-app-bg` now uses deep indigo/blue-black layers plus a subtle low amber dawn glow; `--premium-app-bg-atmosphere` carries the diffuse Milky Way and vignette.
- `backgrounds.css`: keeps `.app-bg` and `.app-bg::before` as canonical owners, adds `app-bg--landing` full intensity and `app-bg--internal` sober intensity, disables shooting-star motion on mobile and `prefers-reduced-motion`.
- `RootLayout.tsx`: adds the single route-level scope: `/` gets `app-bg--landing`; every other path gets `app-bg--internal`.
- `StarfieldBackground.tsx`: remains dark-only, deterministic and non-interactive; renders 118 stars, one diffuse Milky Way path and 3 rare shooting-star lines.

## Screenshots

- `screenshots/landing-desktop-dark-after.png`
- `screenshots/login-desktop-dark-after.png`
- `screenshots/landing-mobile-dark-after.png`
- `screenshots/login-mobile-dark-after.png`

Visual notes: landing uses the richer astral field; login/internal uses the sober variant with reduced starfield opacity and no active shooting stars. Mobile screenshots were captured with shooting stars disabled by CSS.

## Tests

- `npm run test -- StarfieldBackground visual-smoke theme-tokens design-system` PASS: 4 files, 186 tests.
- `npm run test -- layout` PASS: 2 files, 8 tests.
- `npm run test -- App` PASS: 4 files, 61 tests.
- `npm run lint` PASS.
- `npm run build` PASS.
- `npm run test` first run had one non-reproducible `router.test.tsx` failure; isolated `npm run test -- router` PASS; second full `npm run test` PASS: 114 files, 1221 passed, 8 skipped.

## Scans

- `rg -n "style=" src/layouts/RootLayout.tsx src/components/StarfieldBackground.tsx`: zero hits.
- `rg -n "background-image:\s*url\(" src/styles/premium-theme.css src/styles/backgrounds.css src/layouts/LandingLayout.css`: zero hits.
- `rg -n "dark|html\.dark|starfield|premium-app-bg" src/App.css`: zero hits.
- `rg -n "prefers-reduced-motion|shooting|meteor|starfield" src/components src/styles src/layouts -g "*.tsx" -g "*.css"`: expected hits in `backgrounds.css`, `StarfieldBackground.tsx`, and pre-existing `AstroMoodBackground.tsx`.
- Global `style=` scan: only pre-existing hits in `DomainRankingCard.tsx`, `DayTimelineSectionV4.tsx`, `Skeleton.tsx`.
- Global `background-image: url(` scan: only pre-existing SVG data URL in `styles/app/media.css`.
- Global `bg-halo|noise|landing-background|space-background|cosmic-background` scan: only pre-existing canonical/neutral halo and noise selectors; no new page-level competing background.

## Guardrails

- `RG-061`, `RG-078`: PASS; `App.css` unchanged and scan zero-hit for dark/background terms.
- `RG-068`: PASS; route-level scope remains in `RootLayout`.
- `RG-081`: PASS; no central width change; layout tests and design-system guards pass.
- `RG-082`: PASS; no font-family changes.
- `RG-083`: PASS; dark surfaces stay token-backed and visual-smoke/design-system pass.
- `RG-084`, `RG-085`: PASS; one canonical background path remains, no raster main image, no inline style, `prefers-reduced-motion` guarded.

## Runtime

- Local dev server started with `npm.cmd run dev`.
- URL: `http://localhost:5173/`
