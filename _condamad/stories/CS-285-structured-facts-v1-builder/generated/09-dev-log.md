# Dev Log

## 2026-05-25

- Preflight: repository root `C:\dev\horoscope_front`; `.git` present; initial worktree already had many unrelated modified/untracked files from prior stories and backend work.
- Capsule: required `generated/*.md` files were missing; ran `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py ...` with venv active, then `condamad_validate.py`; validation PASS.
- Registry: confirmed row `CS-285` points to `_condamad/stories/CS-285-structured-facts-v1-builder/00-story.md` and `_story_briefs/cs-285-implement-structured-facts-v1-builder.md`.
- Implementation: added canonical backend-domain builder adjacent to interpretation owners; added unit/architecture guards.
- Validation: targeted tests PASS; `ruff check .` PASS; full backend pytest PASS.
- Note: broad forbidden-term scan over all backend tests contains historical test fixtures/assertion lists; story-owned files have a clean targeted scan.
- Review/fix iteration 1: implementation review found forbidden text-like labels in `excluded_surfaces`; replaced them with neutral category names, updated the unit guard, sample payload and evidence.
