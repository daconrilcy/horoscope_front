# Dev Log — CS-335

- Preflight: `.git` present; initial dirty context was only `_condamad/run-state.json` untracked.
- Capsule repair: required `generated/*.md` files were missing and were created with `condamad_prepare.py`; capsule validation passed.
- Implementation: restricted gateway prompt serialization to the prompt-visible `llm_astrology_input_v1` blocks and added orchestration plus AST guards.
- Validation: targeted tests, architecture guards, `ruff check .`, OpenAPI non-exposure check and full backend pytest suite passed.
- Note: an early validation attempt from `backend` used the wrong venv activation path; all evidence-closing Python commands were rerun from repo root with `.\\.venv\\Scripts\\Activate.ps1` before `Set-Location backend`.
