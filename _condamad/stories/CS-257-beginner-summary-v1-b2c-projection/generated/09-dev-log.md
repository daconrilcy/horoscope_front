# Dev Log

- Preflight: `.git` present; initial dirty worktree already included CS-256 files and `story-status.md`.
- Capsule: generated files were missing; ran `condamad_prepare.py` with explicit CS-257 key after the first inference attempt refused multiple CS identifiers; `condamad_validate.py` PASS.
- Implementation: added the canonical `beginner_summary_v1` contract and aligned the existing product primitive registry. No frontend, API, DB, migration or runtime source was changed.
- Validation: targeted `rg` scans PASS; app OpenAPI/routes neutrality checks PASS; `ruff check .` PASS; full backend pytest PASS after one shorter timeout.
- Cleanup: removed known generated caches under `backend/.ruff_cache`, `backend/app/__pycache__`, and `backend/tests/__pycache__`.
- Feedback loop: no-propagation; no reusable skill or AGENTS.md learning found beyond story-local evidence.
