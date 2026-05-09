<!-- Matrice de tracabilite des criteres d'acceptation pour CS-126. -->

# CS-126 Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Baseline records precision/evidence inventory. | `precision-evidence-before.md` | `rg -n "precision-|evidence-" src/App.css src -g "*.tsx"` | PASS |
| AC2 | Precision badge family has an explicit final decision. | `ConsultationPrecisionBadge.tsx`; `ConsultationPrecisionBadge.css`; `precision-evidence-after.md` | `npm run test -- ConsultationWizardPage ConsultationMigration natalInterpretation design-system visual-smoke` | PASS |
| AC3 | Evidence tags/pills family has an explicit final decision. | `NatalInterpretationEvidence.tsx`; `NatalInterpretation.css`; `precision-evidence-after.md` | `npm run test -- ConsultationWizardPage ConsultationMigration natalInterpretation design-system visual-smoke` | PASS |
| AC4 | Guard blocks unclassified `precision/evidence` in `App.css`. | `collectPrecisionEvidenceAppCssHits` guard in `design-system-guards.test.ts` | `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | PASS |
| AC5 | No forbidden CSS governance vocabulary is introduced. | No forbidden vocabulary added | `rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css src/tests/design-system-allowlist.ts` returned zero hits | PASS |
| AC6 | Frontend validation remains green after class/owner changes. | Frontend implementation and guard diffs | `npm run lint`; `npm run build` | PASS |
