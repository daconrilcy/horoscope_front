<!-- Preuves finales CONDAMAD pour CS-126. -->

# CS-126 Final Evidence

Status: done

## Implementation Summary

- Migrated consultation precision badges from App.css to
  `ConsultationPrecisionBadge.tsx` and `ConsultationPrecisionBadge.css`.
- Migrated natal evidence list/pill class consumers to `ni-evidence-*`
  feature-owned classes in `NatalInterpretation.css`.
- Removed `--app-precision-*`, `--app-evidence-*`, `.precision-badge*`,
  `.evidence-tags*`, and `.evidence-pill*` from `frontend/src/App.css`.
- Hardened design-system guards to fail if these families return to App.css.

## Files Changed

- `frontend/src/App.css`
- `frontend/src/features/consultations/components/ConsultationPrecisionBadge.tsx`
- `frontend/src/features/consultations/components/ConsultationPrecisionBadge.css`
- `frontend/src/features/consultations/components/ConsultationSummaryStep.tsx`
- `frontend/src/features/consultations/components/DataCollectionStep.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationEvidence.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/styles/token-namespace-registry.md`
- `_condamad/stories/CS-126-migrer-ou-garder-explicitement-precision-evidence/*`
- `_condamad/stories/story-status.md`

## Validation

| Command | Result |
|---|---|
| `npm run test -- ConsultationWizardPage ConsultationMigration natalInterpretation design-system visual-smoke` | PASS, 5 files / 71 tests |
| `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | PASS, 6 files / 148 tests |
| `npm run test` | PASS, 113 files / 1193 tests passed / 8 skipped |
| `npm run lint` | PASS |
| `npm run build` | PASS |
| `rg -n "precision-|evidence-" src/App.css src -g "*.tsx"` | PASS, canonical non-App.css hits only |
| `rg -n "\.precision-badge|\.evidence-tags|\.evidence-pill" src -g "*.css"` | PASS, zero hits |
| `rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css src/tests/design-system-allowlist.ts` | PASS, zero hits |
| `rg -n -- "--app-precision-|--app-evidence-|\.precision-badge|\.evidence-tags|\.evidence-pill" src/App.css` | PASS, zero hits |
| `git diff --check` | PASS |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-126-migrer-ou-garder-explicitement-precision-evidence/00-story.md` | PASS |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-126-migrer-ou-garder-explicitement-precision-evidence/00-story.md` | PASS |

## Legacy / DRY Evidence

- No old precision/evidence selectors remain in `App.css` or feature CSS.
- No duplicate active precision/evidence styling remains between App.css and
  feature CSS.
- No wildcard exception was added.
- Frontend implementation was delegated to `condamad-frontend-dev`.
- Independent review findings accepted and fixed: old selector guard now scans
  all CSS files, and targeted render tests assert canonical precision/evidence
  classes.

## Remaining Risks

None identified.
