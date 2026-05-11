# Validation Plan

## Environment Assumptions

- Frontend root: `frontend/`
- Package scripts: `npm run lint`, `npm run test`, `npm run dev`.
- No Python command is required for this frontend story.

## Commands

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Targeted landing and guards | `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture` | `frontend/` | yes | all tests pass |
| Lint/typecheck | `npm run lint` | `frontend/` | yes | no TypeScript errors |
| Style/landing forbidden scan | `rg -n "app-bg--landing|style=" src/pages/landing src/layouts` | `frontend/` | yes | no active hit |
| Motion/filter scan | `rg -n "@keyframes|animation:|backdrop-filter|filter:" src/pages/landing src/layouts/LandingLayout.css` | `frontend/` | yes | only classified hits |
| Decorative font scan | `rg -n "Cormorant|Petit Formal|Brush Script|font-family:\s*\"" src -g "*.css" -g "*.scss"` | `frontend/` | yes | no forbidden direct font hit |
| Runtime before/after | `npm run dev -- --host 127.0.0.1 --port 5173` + Playwright measurement | `frontend/` | yes | mobile/tablet/desktop metrics captured |

Skipped commands must be recorded with reason, risk and compensating evidence.
