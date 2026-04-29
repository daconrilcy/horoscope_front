# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `?? _condamad/stories/replace-seed-validation-facade-test/`
- Existing dirty files: story capsule directory was untracked before implementation.
- AGENTS considered: `AGENTS.md`.

## Search evidence

- `rg -n "SeedValidationError|seed validation|required persona|persona" backend/app backend/scripts backend/tests`
- `rg -n "assert True|pass$" backend/app/tests backend/tests -g test_*.py`
- `rg -n "seed_30_5|PROMPTS_TO_SEED|seed validation|SeedValidationError|validate_seed|validate.*PROMPTS" backend/app/tests backend/tests backend/app backend/scripts -g *.py`

## Decisions made

- Classified the seed rule as `canonical-active`.
- Replaced the facade test instead of deleting it.
- Implemented pre-write seed contract validation in `use_cases_seed.py`.
- Added a durable regression guard `RG-014`.

## Validation

- Targeted tests passed.
- Ruff format/check passed.
- Pytest collection passed.
- Full pytest passed: 3474 passed, 12 skipped, 7 warnings.
- FastAPI app import smoke passed.

## Final `git status --short`

Recorded in `generated/10-final-evidence.md`.
