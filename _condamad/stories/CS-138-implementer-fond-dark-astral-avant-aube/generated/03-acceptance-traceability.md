# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Fond dark reconstruit en couches astrales sobres. | `premium-theme.css`, `backgrounds.css`, `StarfieldBackground.tsx`. | `npm run test -- StarfieldBackground visual-smoke theme-tokens design-system` PASS; `npm run test` PASS. | PASS |
| AC2 | Light mode inchange hors ecarts documentes. | Light tokens kept in `:root`; dark overrides only. | `npm run test -- theme-tokens design-system` PASS; before/after evidence records no light-mode code path change. | PASS |
| AC3 | Centre de lecture lisible. | Atmosphere/vignette avoids center saturation; shared dark surfaces tuned through premium tokens. | `npm run test -- visual-smoke` PASS; Playwright screenshots generated for landing/login desktop/mobile. | PASS |
| AC4 | Variante complete activee sur landing. | `RootLayout` emits `app-bg--landing` on `/`. | `npm run test -- App` PASS; `npm run test -- layout` PASS. | PASS |
| AC5 | Variante sobre activee hors landing. | `RootLayout` emits `app-bg--internal` outside `/`. | `npm run test -- App` PASS; `npm run test -- layout` PASS. | PASS |
| AC6 | `prefers-reduced-motion` respecte. | CSS media query disables shooting-star animation; mobile disables shooting stars. | `npm run test -- StarfieldBackground` PASS; motion scan PASS. | PASS |
| AC7 | Aucun nouveau fond page-level concurrent. | Canonical `--premium-app-bg` / `--premium-app-bg-atmosphere` preserved. | `npm run test -- design-system` PASS; page-level scan has only pre-existing classified hits. | PASS |
| AC8 | Aucune nouvelle image raster lourde en fond principal. | CSS gradients and SVG only; no new asset. | Targeted `background-image: url(` scan on owners zero-hit; global scan only pre-existing SVG data URL hits. | PASS |
| AC9 | Owners canoniques; aucun inline style ni App.css actif. | No `style=` in touched React; `App.css` unchanged. | Targeted inline/App.css scans PASS; `npm run test -- design-system visual-smoke` PASS. | PASS |
| AC10 | Preuves before/after presentes. | Added before/after markdown and screenshots. | `dark-astral-background-before.md`, `dark-astral-background-after.md`, screenshots present. | PASS |
