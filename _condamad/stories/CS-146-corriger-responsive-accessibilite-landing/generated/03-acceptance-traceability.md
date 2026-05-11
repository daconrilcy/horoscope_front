# CS-146 - Acceptance traceability

| AC | Statut | Code evidence | Validation evidence |
|---|---|---|---|
| AC1 Navbar sans overflow aux viewports cibles | PASS | `LandingNavbar.css` breakpoint desktop durci a `1024px`. | Runtime after: `768x1024` `scrollWidth=768`, `clientWidth=768`; `390x844` `scrollWidth=390`, `clientWidth=390`. |
| AC2 Focus confine dans le menu mobile ouvert | PASS | `LandingNavbar.tsx` focus initial, trap Tab/Shift+Tab, Escape, scroll lock, restauration focus. | `npm run test -- LandingPage` PASS; runtime after: 13 tabulations dans `#landing-mobile-menu`, Escape ferme et restaure le bouton. |
| AC3 Hero mobile respecte le seuil `#social-proof` | PASS | `LandingPage.css` hero mobile/tablette compactifie. | Runtime after: `#social-proof` mobile `y=1524.234375`, soit `278.25px` plus haut que le baseline et sous `y=1560`. |
| AC4 H1 expose un nom accessible avec separateur | PASS | `HeroSection.tsx` ajoute `aria-label` au H1 unique. | `LandingPage.test.tsx` assert un seul H1 nomme `Votre guide astrologique personnel - Toujours disponible`. |
| AC5 Interdits landing absents des fichiers touches | PASS | Aucun style inline ni fond dedie ajoute. | Scans `app-bg--landing|style=`, `style={{`, `--landing-(misc|common|temp|shared|base|general|global)-` zero-hit; `RG-088` garde les filters existants. |
| AC6 Validation frontend cible OK | PASS | Tests cibles mis a jour. | `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture` PASS; `npm run lint` PASS. |
