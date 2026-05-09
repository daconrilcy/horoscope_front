<!-- Inventaire avant implementation des familles precision/evidence pour CS-126. -->

# CS-126 Precision / Evidence Before

## Command

```powershell
Push-Location frontend
rg -n "precision-|evidence-" src/App.css src -g "*.tsx"
Pop-Location
```

## App.css Hits

- `--app-precision-badge-*` declarations in `#root`.
- `.precision-badge` and `.precision-badge--high|medium|limited|blocked`
  selectors.
- `--app-evidence-tags-*` and `--app-evidence-pill-*` declarations in `#root`.
- `.evidence-tags`, `.evidence-tags__title`, `.evidence-tags__list`,
  `.evidence-pill`, `.evidence-pill__dot`,
  `.evidence-pill--planet|aspect|angle` selectors.

## Active TSX Consumers

- `frontend/src/features/consultations/components/ConsultationSummaryStep.tsx`
  consumes `precision-badge precision-badge--${precheck.precision_level}`.
- `frontend/src/features/consultations/components/DataCollectionStep.tsx`
  consumes `precision-badge precision-badge--${precheck.precision_level}`.
- `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx`
  consumes `evidence-tags__list`, `evidence-pill`,
  `evidence-pill--${modifier}`, and `evidence-pill__dot`.

## Baseline Conclusion

`F-002` is reproduced: `precision/evidence` remain active in `App.css` and
must be migrated out or retained with exact source-backed owner decisions and
guards.
