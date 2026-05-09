<!-- Plan de validation CONDAMAD pour CS-125. -->

# CS-125 Validation Plan

## Frontend Commands

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke
npm run lint
npm run build
rg -n "OLD|legacy|alias|compat|compatibility|shim|migration-only" src/App.css
rg -n -- "--app-(person|people|activity|premium|flow|summary|precision|evidence|chat|usage)-" src/App.css
Pop-Location
```

The audited-prefix scan may return only entries documented in
`app-prefix-taxonomy-after.md`.

## Story Contract Commands

Python commands must run after activating the repository venv:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-125-fermer-taxonomie-variables-app-restantes/00-story.md
```
