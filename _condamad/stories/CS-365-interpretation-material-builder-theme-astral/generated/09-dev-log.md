# CS-365 - Dev Log

- 2026-05-28: Preflight found existing untracked `_condamad/run-state.json`; left untouched as unrelated dirty worktree context.
- 2026-05-28: Generated missing capsule files with `condamad_prepare.py --story-key CS-365-interpretation-material-builder-theme-astral` and validated capsule.
- 2026-05-28: Implemented backend domain builder, theme astral LLM input handoff, unit tests, and integration test.
- 2026-05-28: Integration tests under `tests/integration/**` are deselected unless pytest receives `--long`; final evidence uses `--long`.
