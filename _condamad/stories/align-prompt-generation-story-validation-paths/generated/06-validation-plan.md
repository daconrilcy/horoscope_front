# Validation Plan

## Environment assumptions

- Commands run on Windows PowerShell.
- Every Python command must activate `.\.venv\Scripts\Activate.ps1` first.
- Backend commands run from `backend/`.
- `rg` scans run from the repository root unless stated otherwise.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story structure validation | `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\align-prompt-generation-story-validation-paths\00-story.md` | `backend/` | yes | PASS |
| Story strict lint | `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\align-prompt-generation-story-validation-paths\00-story.md` | `backend/` | yes | PASS |
| Corrected validation paths | `pytest -q app/tests/unit/test_seed_horoscope_narrator_assembly.py app/tests/unit/test_guidance_service.py app/tests/unit/test_consultation_generation_service.py` | `backend/` | yes | PASS with at least one collected test per file |

## Unit tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend topology guard | `pytest -q app/tests/unit/test_backend_pytest_collection.py app/tests/unit/test_backend_test_topology.py` | `backend/` | yes | PASS |

## Integration tests

- Not applicable: this story changes documentary validation paths only.

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Active obsolete path scan | `rg -n "pytest -q tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py|pytest -q tests/unit/test_guidance_service.py|pytest -q tests/unit/test_consultation_generation_service.py" _condamad\stories` | repo root | yes | no active validation-plan hits outside classified historical or forbidden-example references |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Obsolete path inventory | `rg -n "tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py|tests/unit/test_guidance_service.py|tests/unit/test_consultation_generation_service.py" _condamad\stories` | repo root | yes | all hits classified in `validation-path-audit.md` |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Lint | `ruff check .` | `backend/` | yes | PASS |
| Diff whitespace | `git diff --check` | repo root | yes | PASS |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Backend regression suite | `pytest -q` | `backend/` | conditional | PASS or documented limitation if too expensive |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | only story-scope files changed plus pre-existing dirty files |
| Worktree status | `git status --short` | repo root | yes | expected files only |

## Commands that may be skipped only with justification

- Full backend `pytest -q` may be skipped only if targeted checks and topology guards pass and runtime is prohibitive.
