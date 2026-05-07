<!-- Plan de validation CONDAMAD pour la story CS-089. -->

# Validation Plan

Frontend commands from `frontend/`:

```powershell
npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke DailyHoroscopePage
npm run lint
npm run build
```

Static scans from repository root:

```powershell
rg -n -- "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" frontend/src/styles/backgrounds.css frontend/src/styles/glass.css frontend/src/pages/DailyHoroscopePage.css frontend/src/components/prediction/DailyAdviceCard.css
rg -n -- "font-size:|font-weight:|line-height:|letter-spacing:" frontend/src/styles/backgrounds.css frontend/src/styles/glass.css frontend/src/pages/DailyHoroscopePage.css frontend/src/components/prediction/DailyAdviceCard.css
rg -n -- "box-shadow:|border-radius:|linear-gradient|radial-gradient|var\(\s*--[a-zA-Z0-9_-]+\s*," frontend/src/styles/backgrounds.css frontend/src/styles/glass.css frontend/src/pages/DailyHoroscopePage.css frontend/src/components/prediction/DailyAdviceCard.css
rg -n -- "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" frontend/src/styles/backgrounds.css frontend/src/styles/glass.css frontend/src/pages/DailyHoroscopePage.css frontend/src/components/prediction/DailyAdviceCard.css
```

Story validation from repository root, after venv activation:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-089-converger-surfaces-premium-partagees-background-glass-daily-advice/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-089-converger-surfaces-premium-partagees-background-glass-daily-advice/00-story.md
```
