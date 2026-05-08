<!-- Plan de validation CS-111. -->

# Validation Plan CS-111

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Consumer inventory | `rg -n "TwoColumnLayout|sidebarWidth|--sidebar-width|style=" frontend/src` | repo root | yes | no unclassified layout inline style or `--sidebar-width` |
| Allowlist removal scan | `rg -n "TwoColumnLayout|--sidebar-width" frontend/src/tests/design-system-allowlist.ts frontend/src/tests/inline-style-allowlist.ts` | repo root | yes | zero hits |
| Inline/design-system guards | `npm run test -- inline-style design-system` | `frontend/` | yes | all tests pass |
| Token guard | `npm run test -- theme-tokens` | `frontend/` | yes | all tests pass |
| Layout architecture guard | `npm run test -- page-architecture layout` | `frontend/` | yes | all tests pass |
| Frontend lint | `npm run lint` | `frontend/` | yes | exit 0 |
| Frontend regression suite | `npm run test` | `frontend/` | yes | all tests pass |
| Story validate/lint | `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py ...; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict ...` | repo root | yes | PASS |
