<!-- Preuves finales CONDAMAD pour CS-125. -->

# CS-125 Final Evidence

Status: done

## Implementation Summary

- Added a positive App prefix registry in
  `frontend/src/tests/design-system-allowlist.ts`.
- Replaced the broad `--app-*` namespace registry row with exact retained
  `--app-<prefix>-*` rows in `frontend/src/styles/token-namespace-registry.md`.
- Hardened `frontend/src/tests/design-system-guards.test.ts` to reject unknown,
  stale, duplicated, or unregistered App prefixes across all App.css
  declarations, not only `#root`.
- Integrated the `CS-126` outcome: `precision/evidence` are no longer App
  prefixes and are protected by a zero-hit App.css guard.

## Files Changed

- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/styles/token-namespace-registry.md`
- `_condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/*`
- `_condamad/stories/story-status.md`

## Validation

| Command | Result |
|---|---|
| `npm run test -- ConsultationWizardPage ConsultationMigration natalInterpretation design-system visual-smoke` | PASS, 5 files / 71 tests |
| `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | PASS, 6 files / 148 tests |
| `npm run test` | PASS, 113 files / 1193 tests passed / 8 skipped |
| `npm run lint` | PASS |
| `npm run build` | PASS |
| `rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css src/tests/design-system-allowlist.ts` | PASS, zero hits |
| `rg -n -- "--app-precision-|--app-evidence-|\.precision-badge|\.evidence-tags|\.evidence-pill" src/App.css` | PASS, zero hits |
| `git diff --check` | PASS |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/00-story.md` | PASS |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/00-story.md` | PASS |

## Legacy / DRY Evidence

- No wildcard App prefix allowlist remains.
- No broad `--app-*` namespace registry row remains.
- No precision/evidence App.css alias remains after `CS-126`.
- Independent review finding accepted and fixed: the App prefix guard now scans
  all `--app-*` declarations in `frontend/src/App.css`.
- Frontend implementation was delegated to `condamad-frontend-dev`; no
  unrelated frontend surface was intentionally changed.

## Remaining Risks

None identified.
