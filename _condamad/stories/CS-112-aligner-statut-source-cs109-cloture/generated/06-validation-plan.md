<!-- Plan de validation CS-112. -->

# Validation Plan CS-112

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Stale status scan | `rg -n "ready-to-dev" _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout` | repo root | yes | zero hits |
| Status parity scan | `rg -n "CS-109|Status:" _condamad/stories/story-status.md _condamad/stories/CS-109-fermer-decisions-residuelles-pages-layout/00-story.md` | repo root | yes | CS-109 registry and source show `done` |
| Frontend diff isolation | `git diff --name-only -- frontend/src` | repo root | yes | no CS-112-owned frontend files |
| Story validate/lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py ...; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict ...` | repo root | yes | PASS |
