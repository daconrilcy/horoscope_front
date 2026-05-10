# CS-130 - Execution brief

Objectif: uniformiser la largeur utile non-admin sous les tokens et CSS de layout, sans toucher aux largeurs admin.

In scope:
- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/app/layout.css`
- `frontend/src/layouts/PageLayout.css`
- CSS de pages non-admin qui redefinissaient la largeur page-level
- guards Vitest design-system / AppBgStyles
- artefacts `layout-width-before.md`, `layout-width-after.md`, evidence finale

Non-goals:
- routes, navigation, backend, API, textes i18n
- `frontend/src/pages/admin/**`
- migration des layouts landing/admin vers le token non-admin

Guardrails applicables: `RG-047`, `RG-048`, `RG-059`, `RG-064`, `RG-068`, `RG-078`, `RG-080`, `RG-081`.
