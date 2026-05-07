<!-- Synthese executive de l'audit frontend design-system apres refactors. -->

# Executive Summary - frontend-design-system

The frontend design-system refactors are in a better state than the previous audit: targeted guard tests, lint, and production build all pass.

The old 50-file residual list is obsolete after the latest refactors. The current exhaustive implementation files to modify are:

- `frontend/src/App.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/components/prediction/DailyAdviceCard.css`
- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/glass.css`

Three story candidates are recommended:

- `SC-001`: converge remaining App CSS values.
- `SC-002`: converge Help subscriptions values.
- `SC-003`: converge shared premium background/glass/daily advice values.

Validation status:

- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke`: passed.
- `npm run lint`: passed.
- `npm run build`: passed with the existing Vite chunk-size warning.

Recommended next action: write and implement `SC-001` first, because `App.css` has the highest hit count and largest cross-page blast radius.

