# CS-146 - Validation plan

## Commandes ciblees

```powershell
cd frontend
npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture
npm run lint
rg -n "app-bg--landing|style=" src/pages/landing src/layouts
rg -n "@keyframes|animation:|backdrop-filter|filter:" src/pages/landing src/layouts/LandingLayout.css
```

## Evidence runtime

- Serveur Vite local.
- Mesures `scrollWidth/clientWidth` a `1440x1000`, `768x1024`, `390x844`.
- Mesure `#social-proof` mobile.
- Sequence de focus du menu mobile ouvert.
- Nom accessible du H1.

