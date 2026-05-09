<!-- Matrice de tracabilite des criteres d'acceptation pour CS-125. -->

# CS-125 Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Baseline reproduces current App prefix inventory. | `app-prefix-taxonomy-before.md` | Prefix declaration scan over `frontend/src/App.css` | PASS |
| AC2 | Every App prefix has an explicit final decision. | `APP_CSS_ACCEPTED_PREFIXES`; exact `--app-<prefix>-*` rows in `token-namespace-registry.md`; `app-prefix-taxonomy-after.md` | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | PASS |
| AC3 | `precision/evidence` prefix ownership is classified. | `precision/evidence` removed from `APP_CSS_ACCEPTED_PREFIXES` after CS-126 migration; `app-prefix-taxonomy-after.md` | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | PASS |
| AC4 | Non-generic prefixes have source-backed decisions. | Exact registry rows for retained App prefixes; `precision/evidence` routed to feature owners | Design-system guard and No Legacy scan | PASS |
| AC5 | App guard uses a positive accepted-prefix registry. | `frontend/src/tests/design-system-guards.test.ts`; `APP_CSS_ACCEPTED_PREFIXES` | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | PASS |
| AC6 | Retained-owner governance is synchronized. | `frontend/src/styles/token-namespace-registry.md`; `frontend/src/tests/design-system-allowlist.ts` | `npm run test -- theme-tokens` inside targeted suite | PASS |
| AC7 | Frontend validates after migration. | Frontend implementation and guard diffs | `npm run lint`; `npm run build`; targeted Vitest suites | PASS |
