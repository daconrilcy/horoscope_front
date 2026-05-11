# Dark Astral Background Before

## Owners inspected

- `frontend/src/layouts/RootLayout.tsx`: mounts `.app-shell.app-bg`, `StarfieldBackground`, and `.app-bg-container`; no landing/internal background variant yet.
- `frontend/src/components/StarfieldBackground.tsx`: renders 80 deterministic SVG circles only when theme is `dark`.
- `frontend/src/styles/backgrounds.css`: `.app-bg` uses `--premium-app-bg`; `.app-bg::before` uses `--premium-app-bg-atmosphere`; `.starfield-bg` is fixed, non-interactive and opacity `0.4`.
- `frontend/src/styles/premium-theme.css`: light background uses pastel token gradients; dark background uses cosmic violet/blue radial gradients and atmosphere.
- `frontend/src/layouts/LandingLayout.css`: landing remains transparent and aliases atmosphere to `--premium-app-bg`.

## Screenshots / visual notes

- Desktop landing/home before: not captured as bitmap in this pass; CSS/runtime source shows dark background is shared and not route-scoped.
- Desktop internal before: not captured as bitmap in this pass; same canonical dark gradient and starfield as landing.
- Mobile before: not captured as bitmap in this pass; no mobile-specific starfield reduction in owner CSS.
- Form/auth before: not captured as bitmap in this pass; no route-level sober variant exists in `RootLayout`.

## Tests baseline

- Existing targeted tests found: `StarfieldBackground.test.tsx`, `visual-smoke.test.tsx`, `theme-tokens.test.ts`, `design-system-guards.test.ts`, `page-architecture-guards.test.ts`, `AppBgStyles.test.ts`.
- Baseline command planned after implementation: `npm run test -- StarfieldBackground visual-smoke theme-tokens design-system`.

## Scans baseline

Les scans ci-dessous servent de comparaison before pour prouver zero nouveau hit apres implementation.

- `rg -n "style=" frontend/src -g "*.tsx" -g "*.jsx"`: pre-existing hits include `DomainRankingCard.tsx`, `components/ui/Skeleton/Skeleton.tsx`, `DayTimelineSectionV4.tsx`; none are in the expected touched files.
- `rg -n "background-image:\s*url\(" frontend/src/styles frontend/src/layouts frontend/src/pages -g "*.css" -g "*.scss"`: pre-existing SVG data URL hit in `styles/app/media.css`; no raster owner hit in `premium-theme.css`, `backgrounds.css` or `LandingLayout.css`.
- `rg -n "bg-halo|noise|landing-background|space-background|cosmic-background" frontend/src/styles frontend/src/layouts frontend/src/pages -g "*.css"`: pre-existing canonical/neutral page-level halo and noise selectors are guarded by `RG-084`.

## Applicable guardrails

- `RG-061`, `RG-078`: do not add active visual/background declarations to `App.css`.
- `RG-068`: keep route-level background mounting under `RootLayout`.
- `RG-081`: keep central width governed by layout tokens.
- `RG-082`: do not change font families.
- `RG-083`: preserve dark readability without inline/App.css fixes.
- `RG-084`, `RG-085`: keep one canonical global background per theme and prove no competing background, raster main image or inline style was added.
