<!-- Preuve post-implementation CS-144. -->

# Landing Visual Contract After

Final roles:

- `--landing-contract-surface-primary`
- `--landing-contract-surface-secondary`
- `--landing-contract-border`
- `--landing-contract-text`
- `--landing-contract-text-muted`
- `--landing-contract-cta-bg`
- `--landing-contract-cta-border`

Consumers:

- `LandingPage.css`: hero eyebrow, secondary CTA and reassurance surfaces.
- `LandingNavbar.css`: mobile panel background and border.
- `design-system-guards.test.ts`: owner group `contract` is classified and consumed.

Mobile menu changes:

- Overlay blur reduced from `blur(16px)` to `blur(6px)`.
- Panel now uses contract surface and border.
- Panel shadow reduced from `0 24px 60px rgba(50, 34, 78, 0.24)` to `0 18px 42px rgba(50, 34, 78, 0.16)`.

Screenshots after:

- `screenshots-after/desktop-light-top.png`
- `screenshots-after/desktop-dark-top.png`
- `screenshots-after/desktop-light-mid.png`
- `screenshots-after/desktop-dark-mid.png`
- `screenshots-after/mobile-light-menu.png`
- `screenshots-after/mobile-dark-menu.png`

Runtime metrics:

- `desktop-light-top`: `scrollWidth === clientWidth`.
- `desktop-dark-top`: `scrollWidth === clientWidth`.
- `mobile-light-menu`: `scrollWidth === clientWidth`.
- `mobile-dark-menu`: `scrollWidth === clientWidth`.

Validation:

- `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture` - PASS.
- `rg -n -- "app-bg--landing|style=|#0000ee|color:\s*blue" src/pages/landing src/layouts src/App.css` - PASS, zero hit.
- `rg -n -- "--landing-(misc|common|temp|shared|base|general|global)-" src/pages/landing src/layouts` - PASS, zero hit.
