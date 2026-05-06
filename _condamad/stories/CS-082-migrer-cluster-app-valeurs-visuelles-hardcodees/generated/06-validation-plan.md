<!-- Plan de validation CS-082. -->

# Validation Plan

Run from `frontend/`:

- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke AdminPromptsPage`
- `npm run lint`
- `npm run build`
- `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/App.css`
- `rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/App.css`
- `rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/App.css`

Run from repo root after venv activation:

- `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/00-story.md`
- `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-082-migrer-cluster-app-valeurs-visuelles-hardcodees/00-story.md`

