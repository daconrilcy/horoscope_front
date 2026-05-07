<!-- Plan de validation CONDAMAD pour CS-087. -->

# CS-087 Validation Plan

Run from `frontend/`:

```powershell
npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke
npm run lint
npm run build
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/App.css
rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/App.css
rg -n "box-shadow:|border-radius:|linear-gradient|radial-gradient|var\(\s*--[a-zA-Z0-9_-]+\s*," src/App.css
rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/App.css
```

Run from repository root with venv activated for Python commands:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-087-converger-valeurs-visuelles-typographiques-app-css-restantes/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-087-converger-valeurs-visuelles-typographiques-app-css-restantes/00-story.md
```
