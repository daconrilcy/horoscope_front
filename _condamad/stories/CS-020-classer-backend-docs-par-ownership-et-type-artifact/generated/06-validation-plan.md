# Validation Plan

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Docs ownership guard | `pytest -q app/tests/unit/test_backend_docs_ownership.py` | `backend` | yes | pass |
| Ops quality ownership guard | `pytest -q app/tests/unit/test_backend_quality_test_ownership.py` | `backend` | yes | pass |
| Backend lint | `ruff check .` | `backend` | yes | pass |
| Full backend regression | `pytest -q` | `backend` | yes | pass |
| Story validation | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-020-classer-backend-docs-par-ownership-et-type-artifact/00-story.md` | repo root | yes | pass |
