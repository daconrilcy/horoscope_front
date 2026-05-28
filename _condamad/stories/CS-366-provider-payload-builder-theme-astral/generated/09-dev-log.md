# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- Initial `git status --short`: tracked backend changes and generated CS-366 files already present for this story; no unrelated revert performed.
- Story registry row matched `CS-366`, capsule path, and source brief.
- Capsule validation before implementation: PASS.

## Search evidence

- Scoped story and capsule summary loaded.
- Existing runtime/config/material owners inspected with targeted `rg`.
- Legacy scan target: `ThemeAstralLLMInputV1Builder`, `theme_astral_llm_input_v1_builder`, local `_DELIVERY_PROFILES`, legacy resolver name.

## Implementation notes

- Added canonical runtime provider payload builder under `backend/app/domain/llm/runtime/`.
- Moved provider delivery profile resolution to `backend/app/domain/llm/configuration/theme_astral_contracts.py`.
- Deleted legacy internal `theme_astral_llm_input_v1_builder.py`.
- Wired `LLMGateway.build_user_payload` to use the built `theme_astral_llm_input_v1` provider payload.
- Updated targeted tests and persisted story evidence artifacts.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-366-provider-payload-builder-theme-astral` | PASS | Capsule structure. |
| `ruff format <changed files>` | PASS | Scoped format only. |
| `python -B -m pytest -q backend\tests\llm_orchestration\test_theme_astral_provider_payload_builder.py backend\tests\integration\llm\test_theme_astral_provider_payload_handoff.py --tb=short` | PASS | 7 passed, 1 deselected. |
| `python -B -m pytest -q backend\tests\unit\domain\astrology\test_llm_astrology_input_v1.py backend\tests\integration\llm\test_natal_llm_astrology_input_audit.py backend\tests\integration\astrology\test_theme_astral_interpretation_material_input.py backend\tests\unit\infra\db\repositories\test_interpretation_material_source_repository.py --tb=short` | PASS | 10 passed, 3 deselected. |
| `Set-Location backend; ruff check .` | PASS | All checks passed. |
| `Set-Location backend; python -B -m pytest -q tests\llm_orchestration tests\unit\domain\astrology tests\integration\llm --tb=short` | PASS | 845 passed, 3 deselected. |
| Protected-surface `git diff --quiet` checks | PASS | Frontend, migrations, DB models, app repositories unchanged. |
| `git diff --check` | PASS | Only line-ending warnings. |
| `Set-Location backend; python -B -c "from app.main import app; print(app.title)"` | PASS | App import/start smoke: `horoscope-backend`. |

## Issues encountered

- Two checks were first started from `backend` with a root-relative activation path that failed; those outputs were excluded and equivalent checks were rerun from the repository root after venv activation.
- `VC15` failed before `evidence/validation.txt` existed; it passed after evidence creation.

## Decisions made

- The old `ThemeAstralLLMInputV1Builder` was deleted instead of retained as a shim.
- Provider delivery profiles are resolved in configuration, not duplicated inside the runtime builder.
- No regression guardrail registry update: story explicitly records a registry gap but keeps registry changes out of scope.

