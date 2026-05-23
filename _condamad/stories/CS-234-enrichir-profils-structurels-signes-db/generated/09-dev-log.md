# Dev Log

## 2026-05-23

- Initial dirty worktree had unrelated deleted `_condamad/codex-runs/**`, `.gitignore`, `story-status.md`, transformed briefs, local skill folders and future CS-235/CS-236 artifacts.
- Prepared missing capsule files with `condamad_prepare.py`; helper created a duplicate inferred capsule path, then generated files were copied into the requested CS-234 capsule and the duplicate helper capsule was removed.
- Implemented sign structural taxonomies and profile FKs.
- Updated seed catalog and seed service to use `astral_structural_reference_catalog.json` for the new attributes.
- Added migration and test coverage.
- Full backend pytest has one unrelated failure in aspect ruleset schema validation; targeted CS-234 tests pass.
- Feedback-loop routing: no-propagation. The full-suite failure is outside this story surface and was not introduced or corrected here.
