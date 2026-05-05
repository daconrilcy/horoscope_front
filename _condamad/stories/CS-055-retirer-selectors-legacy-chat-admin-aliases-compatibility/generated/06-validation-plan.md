# Validation Plan - CS-055

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Legacy/theme/design guards | `npm run test -- legacy-style theme-tokens design-system` | `frontend` | yes | all tests pass |
| Frontend lint/typecheck | `npm run lint` | `frontend` | yes | no TypeScript errors |
| Local alias scan | `rg -n -e "var\(--glass" -e "var\(--success" -e "var\(--danger" -e "var\(--warning" frontend/src/pages/admin/AdminPromptsPage.css` | repo root | yes | zero token alias hits |
| Legacy/global scan | `rg -n -e "legacy" -e "--text-" -e "--glass" -e "--primary" src/styles src/App.css src/pages/admin/AdminPromptsPage.css` | `frontend` | yes | remaining hits classified |
| Story validate | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-055-retirer-selectors-legacy-chat-admin-aliases-compatibility/00-story.md` | repo root after venv activation | yes | PASS |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-055-retirer-selectors-legacy-chat-admin-aliases-compatibility/00-story.md` | repo root after venv activation | yes | PASS |
| Local startup | `npm run dev -- --host 127.0.0.1` | `frontend` | no | app starts on available Vite port |
| Diff whitespace | `git diff --check` | repo root | yes | no whitespace errors |
