# Execution Brief

## Story

- Story key: `CS-138-implementer-fond-dark-astral-avant-aube`
- Source: `_condamad/stories/CS-138-implementer-fond-dark-astral-avant-aube/00-story.md`
- Objective: mettre en oeuvre un fond dark astral avant l'aube, global, canonique, performant, dark-only, plus riche sur la landing et plus sobre ailleurs.

## Boundaries

- In scope: `RootLayout`, `StarfieldBackground`, `premium-theme.css`, `backgrounds.css`, `LandingLayout.css` si besoin, tests et preuves de story.
- Out of scope: backend, API, routes, contenu page, light mode hors preuve de non-regression, nouvelles dependances, images raster principales.

## Guardrails

- Applicable: `RG-061`, `RG-068`, `RG-078`, `RG-081`, `RG-082`, `RG-083`, `RG-084`, `RG-085`.
- No new inline style, no `App.css` background fix, no page-level competing background, no raster background image.

## Done

- AC1-AC10 have code and validation evidence.
- Targeted tests/scans, lint and build are run or explicitly classified.
- `dark-astral-background-before.md`, `dark-astral-background-after.md`, traceability and final evidence are complete.
- `_condamad/stories/story-status.md` is updated to `ready-to-review` only if validation is complete.
