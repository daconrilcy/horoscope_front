# Evidence Log - frontend-landing-page

| ID | Evidence type | Command / Source | Surface | Result | Detail |
|---|---|---|---|---|---|
| E-001 | required-reference | Read `_condamad/stories/regression-guardrails.md` | Guardrails RG-083 to RG-087 | PASS | Existing invariants protect dark mode, canonical background, landing background mounting and fixed viewport background. |
| E-002 | prior-history | `rg -n "[Ll]anding" _condamad/audits/frontend-layouts _condamad/audits/frontend-design-system _condamad/stories -g "*.md"` | Prior frontend audits/stories | PASS | Prior findings for landing layout bypass and landing literal migration are closed by CS-085/CS-104 and guarded. |
| E-003 | route-inventory | `Get-Content frontend/src/app/routes.tsx`; `Get-Content frontend/src/app/guards/LandingRedirect.tsx` | `/`, `LandingLayout`, `LandingRedirect` | PASS | `/` is nested under `RootLayout` then `LandingLayout`; `LandingRedirect` only decides token cleanup/authenticated redirect and lazy-loads `LandingPage`. |
| E-004 | file-inventory | `Get-ChildItem frontend/src/pages/landing -Recurse -File`; line-count command on `frontend/src/pages/landing/sections` | Landing files | PASS | Audited surface contains `LandingPage.tsx/.css`, 7 section TSX files, 8 section CSS files, and `LandingLayout.tsx/.css`. Largest section CSS is `LandingNavbar.css` at 342 lines; `LandingPage.css` is 19,609 bytes. |
| E-005 | token-complexity-scan | `(rg -n "^\\s*--landing-" frontend/src/layouts/LandingLayout.css \| Measure-Object).Count` | `frontend/src/layouts/LandingLayout.css` | FAIL | `LandingLayout.css` declares 256 `--landing-*` variables in one owner, spanning surfaces, shadows, type scale, navbar, language selector, mobile panel, hero device and theme overrides. |
| E-006 | visual-literal-scan | `Select-String -Path frontend/src/pages/landing/*.css,frontend/src/pages/landing/sections/*.css,frontend/src/layouts/LandingLayout.css -Pattern '#','rgba','linear-gradient','radial-gradient','clamp','letter-spacing: -'` | Landing CSS | FAIL | Raw visual values are centralized in `LandingLayout.css`; this follows the existing guard exception but keeps landing construction dense and hard to reason about. Examples: lines 21-148, 149-201, 207-271. |
| E-007 | side-effect-scan | `Select-String -Path frontend/src/pages/landing/**/*.tsx,frontend/src/pages/landing/*.tsx,frontend/src/layouts/LandingLayout.tsx,frontend/src/app/guards/LandingRedirect.tsx -Pattern 'window.setInterval','window.addEventListener','document.','role="dialog"','aria-modal','Ensure default','AC[0-9]'` | Landing runtime code | FAIL | `LandingPage.tsx` mutates document head/JSON-LD; `HeroSection.tsx` runs an 80ms interval; `LandingNavbar.tsx` owns scroll, Escape and modal state. These concerns are mixed into page/section components. |
| E-008 | screenshot-runtime | Playwright screenshot script against `http://127.0.0.1:5173/` | `screenshots/*.png` | PASS | Captured desktop/mobile, light/dark, full-page/midpage, and mobile menu screenshots. Runtime metrics: 6 sections, 46 card/panel/shell-like elements, no horizontal overflow at 1440px or 390px. |
| E-009 | visual-review | Manual review of `screenshots/desktop-light-viewport.png`, `desktop-dark-viewport.png`, `desktop-*-midpage.png`, `mobile-*-viewport.png`, `mobile-*-menu.png` | Landing UI | FAIL | Light mode reads as pale glass-on-pale-glass; dark mode reads as starfield-heavy with many low-contrast translucent panels. Dark and light are visually different systems rather than one coherent theme pair. |
| E-010 | targeted-tests | `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture` from `frontend/` | Frontend guards | PASS | 4 files passed, 125 tests passed. Existing guards cover layout, background, design-system and visual-smoke invariants. |
| E-011 | lint | `npm run lint` from `frontend/` | TypeScript lint/typecheck | PASS | `tsc --noEmit -p tsconfig.lint.json` and `tsc --noEmit -p tsconfig.node.json` passed. |
| E-012 | runtime-server | `npm run dev -- --host 127.0.0.1 --port 5173`; `Invoke-WebRequest http://127.0.0.1:5173/` | Local Vite server | PASS | Vite served the app at `http://127.0.0.1:5173/`; HTTP status 200. |
| E-013 | import-render-inventory | `Select-String -Path frontend/src/pages/landing/LandingPage.tsx -Pattern 'HeroSection','SocialProofSection','TestimonialsSection','ProblemSection','SolutionSection','PricingSection','FaqSection'` | `frontend/src/pages/landing/LandingPage.tsx` | PASS | `LandingPage.tsx` imports and renders all seven landing content sections at lines 6-12 and 144-150. |

## Screenshot Artifacts

- `screenshots/desktop-light-viewport.png`
- `screenshots/desktop-dark-viewport.png`
- `screenshots/desktop-light-fullpage.png`
- `screenshots/desktop-dark-fullpage.png`
- `screenshots/desktop-light-midpage.png`
- `screenshots/desktop-dark-midpage.png`
- `screenshots/mobile-light-viewport.png`
- `screenshots/mobile-dark-viewport.png`
- `screenshots/mobile-light-menu.png`
- `screenshots/mobile-dark-menu.png`
