<!-- Plan de validation CS-083. -->

# Validation Plan

Run from `frontend/`:

- `npm run test -- design-system legacy-style AdminPromptsPage`
- `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke AdminPromptsPage`
- `npm run lint`
- `npm run build`
- `rg -n --glob "*.css" "--default_dropshadow|migration-only|compatibility|legacy|alias" src`

Run from repo root after venv activation:

- `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-083-fermer-garde-no-legacy-vocabulaire-css-actif/00-story.md`
- `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-083-fermer-garde-no-legacy-vocabulaire-css-actif/00-story.md`

