<!-- Matrice AC CS-116 maintenue par l'agent CONDAMAD. -->

# CS-116 Acceptance Traceability

| AC | Status | Evidence |
|---|---|---|
| AC1 | PASS | `component-usage-before.md`, `component-usage-after.md`, whole-components export-aware guard inventory. |
| AC2 | PASS | `component-usage-classification.md` and `component-usage-allowlist.ts`. |
| AC3 | PASS | `frontend/src/components/AppShell.tsx` and unreferenced prediction files classified `remove` were physically deleted with stale CSS where applicable. |
| AC4 | PASS | All retained unused-looking files have exact owner metadata. |
| AC5 | PASS | `component-usage-guards.test.ts` fails on any exported component under `components/**` not reachable from the `main.tsx` runtime import/export graph and no exact classification, including alias exports and type-only import exclusion. |
| AC6 | PASS | `npm run test -- components component-usage design-system` PASS. |
