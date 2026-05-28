# Dev Log — CS-364

## Preflight

- Initial `git status --short`: `_condamad/run-state.json` already untracked.
- Story-status row matched `CS-364`, target `Path`, and source brief.
- Capsule generated files were missing and were repaired with `condamad_prepare.py --repair-generated-only`; validation PASS.
- CS-363 architecture report found at `_condamad/architecture/theme-astral-prompt-contract/2026-05-28-1217/archi-theme-astral-prompt-contract-v1.md`.

## Implementation Notes

- No Alembic migration was added: existing `llm_use_case_configs`, `llm_prompt_versions`, `llm_output_schemas`, `llm_personas`, `llm_execution_profiles`, and `llm_assembly_configs` cover the required persistence.
- Added the `theme_astral` family to the existing prompt governance registry instead of creating a parallel registry.
- Added a backend-only delivery depth model (`essential`, `deep`) so provider-visible read models do not expose commercial plan names.
- Generated evidence:
  - `evidence/baseline-llm-contracts.txt`
  - `evidence/theme-astral-contract-manifest.json`

## Validation Summary

- `ruff format <modified python files>` PASS.
- `ruff check .` PASS.
- `python -B -m pytest -q tests --tb=short` PASS: 1217 passed, 227 deselected.
- `python -B -c "from app.main import app; print(app.title)"` PASS: `horoscope-backend`.
- Parallel-registry negative scan PASS with no matches.

## Feedback Loop

- `no-propagation`: no reusable process correction beyond story-local evidence. The transient Windows case-collision mistake was corrected by restoring the tracked story file and using `--repair-generated-only`.
