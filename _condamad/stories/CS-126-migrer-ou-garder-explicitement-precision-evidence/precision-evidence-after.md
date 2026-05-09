<!-- Decision apres implementation des familles precision/evidence pour CS-126. -->

# CS-126 Precision / Evidence After

## Commands

```powershell
Push-Location frontend
rg -n "precision-|evidence-" src/App.css src -g "*.tsx"
rg -n -- "--app-precision-|--app-evidence-|\.precision-badge|\.evidence-tags|\.evidence-pill" src/App.css
Pop-Location
```

## Decision Table

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `.precision-badge*` | selector family | canonical-active migrated | `ConsultationSummaryStep.tsx`, `DataCollectionStep.tsx` | `ConsultationPrecisionBadge` + `.consultation-precision-badge*` | migrate to consultation feature owner | App.css zero-hit scan; consultation tests pass | low |
| `--app-precision-*` | variable family | migrated | precision badge CSS | `--consultation-precision-*` in `ConsultationPrecisionBadge.css` | delete from App.css | App.css zero-hit scan; token registry row for `--consultation-precision-*` | low |
| `.evidence-tags__list` | selector | canonical-active migrated | `NatalInterpretationEvidence.tsx` | `.ni-evidence-tags-list` | migrate to natal interpretation owner | App.css zero-hit scan; natal tests pass | low |
| `.evidence-pill*` | selector family | canonical-active migrated | `NatalInterpretationEvidence.tsx` | `.ni-evidence-pill*` | migrate to natal interpretation owner | App.css zero-hit scan; natal tests pass | low |
| `--app-evidence-*` | variable family | migrated | evidence pill CSS | existing `NatalInterpretation.css` tokens/classes | delete from App.css | App.css zero-hit scan; design-system guard | low |

## Scan Result

The broad `precision-|evidence-` scan now returns only canonical non-`App.css`
hits:

- `ConsultationPrecisionBadge.tsx`
- `NatalInterpretationEvidence.tsx`

The strict App.css scan for `--app-precision-`, `--app-evidence-`,
`.precision-badge`, `.evidence-tags`, and `.evidence-pill` returns zero hits.

## Guard Evidence

`design-system-guards.test.ts` includes `collectPrecisionEvidenceAppCssHits`
and asserts zero hits, so future unclassified `precision/evidence` App.css
surfaces fail the design-system suite.
