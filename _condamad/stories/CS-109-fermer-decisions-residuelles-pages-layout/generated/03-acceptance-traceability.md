# CS-109 - Acceptance traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Privacy/billing routes have layout owners. | `routes.tsx` expose `/privacy`, `/billing/success`, `/billing/cancel`; allowlist owners explicites. | `npm run test -- page-architecture layout`; scans routes/allowlist. | PASS |
| AC2 | No `HomePage.tsx` route/export/shim/alias/wrapper exists. | `frontend/src/pages/HomePage.tsx` absent; aucun export ni route. | `rg --files src/pages -g "*.tsx" \| rg "HomePage"` zero-hit; `rg -n "HomePage" src/app src/pages/index.ts src/tests/page-architecture-allowlist.ts` zero-hit. | PASS |
| AC3 | `TestimonialsSection` uses `LandingPage` ownership classification. | `LandingPage.tsx` importe/rend `TestimonialsSection`; allowlist owner `LandingPage`. | `npm run test -- LandingPage visual-smoke`; scan `TestimonialsSection`. | PASS |
| AC4 | CS-107/CS-108/audit `1914` match runtime state. | Audit 1914 et evidence CS-108 historicalisent les anciens blocages et pointent CS-109. | Stale-blocked scan sur artefacts actifs; closure-before/after. | PASS |
| AC5 | CS-109 durable proof exists in `story-status.md`. | Capsule generated complete; `story-status.md` met a jour. | `rg -n "CS-109" _condamad/stories`; final evidence. | PASS |
| AC6 | Frontend route regression tests pass. | Tests routes/app/page architecture presents et verts. | `npm run lint`; targeted tests story. | PASS |
