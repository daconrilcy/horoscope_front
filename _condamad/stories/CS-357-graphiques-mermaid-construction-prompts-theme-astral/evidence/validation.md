# Validation Evidence

- `python -B -c` path and Mermaid count: PASS, `mermaid_blocks 8`.
- Combined `rg` over `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`: PASS for plans, global pipeline, injected data, persona, safety, provider order, exclusions and no-call boundary.
- `rg -n "natal-prompt-construction-mermaid\.md" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`: PASS.
- `git status --short -- backend/app backend/tests frontend/src`: PASS, no entries.
- `git diff --check -- _condamad/docs/prompt-generation-cartography _condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral _condamad/stories/story-status.md`: PASS with CRLF warning only.
- `ruff check .` from `backend` with venv active: PASS.
- `python -B -m pytest -q --tb=short` from `backend` with venv active: PASS, 3487 passed, 1 skipped, 1222 deselected in 234.30 s.
- `python -B .agents/skills/condamad-dev-story/scripts/condamad_validate.py _condamad/stories/CS-357-graphiques-mermaid-construction-prompts-theme-astral`: PASS after final evidence table correction.
