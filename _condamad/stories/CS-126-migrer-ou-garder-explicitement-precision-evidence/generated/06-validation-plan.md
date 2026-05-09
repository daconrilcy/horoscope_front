<!-- Plan de validation CONDAMAD pour CS-126. -->

# CS-126 Validation Plan

## Frontend Commands

```powershell
Push-Location frontend
npm run test -- ConsultationWizardPage ConsultationMigration natalInterpretation design-system visual-smoke
npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke
npm run lint
npm run build
rg -n "precision-|evidence-" src/App.css src -g "*.tsx"
rg -n "\.precision-badge|\.evidence-tags|\.evidence-pill" src -g "*.css"
rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css src/tests/design-system-allowlist.ts
Pop-Location
```

The precision/evidence scans may return only canonical non-`App.css` TSX hits
or exact retained decisions documented in `precision-evidence-after.md`; the
old selector CSS scan must return zero hits.

## Story Contract Commands

Python commands must run after activating the repository venv:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-126-migrer-ou-garder-explicitement-precision-evidence/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-126-migrer-ou-garder-explicitement-precision-evidence/00-story.md
```
