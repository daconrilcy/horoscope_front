# Validation Plan

## Environment assumptions

- Repository root: `C:\dev\horoscope_front`
- OS target: Windows / PowerShell
- Python commands require `.\\.venv\\Scripts\\Activate.ps1`.
- No new dependency is allowed.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Script path scan | `rg -n "C:\\dev\\horoscope_front|pytest_cache_runtime|PytestCachePath" scripts/llm-release-readiness.ps1` | repo root | yes | No absolute local path; cache variable and override visible. |
| Script guard test | `pytest -q app/tests/unit/test_llm_release_readiness_script.py` | `backend` | yes | Tests pass. |
| Script ownership guards | `pytest -q app/tests/unit/test_backend_quality_test_ownership.py app/tests/unit/test_scripts_ownership.py` | `backend` | yes | Ownership registries include the new script guard and the updated script decision. |
| Full readiness script | `scripts\llm-release-readiness.ps1` | repo root | yes | Script exits 0 only when the aggregate report decision is `go`; a `no-go` report must stop the script. |

## Unit tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| RG-016 guard | `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` | `backend` | yes | Tests pass. |
| LLM governance subset | `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py tests/llm_orchestration/test_assembly_resolution.py` | `backend` | yes | Tests pass. |

## Integration tests

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Release lifecycle tests | `pytest -q tests/integration/test_llm_release.py` | `backend` | yes | Tests pass repeatedly without snapshot version collisions. |

## Supporting backend release checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Release snapshot repeatability | `pytest -q tests/integration/test_llm_release.py` | `backend` | yes | Release snapshots use unique versions and eagerly loaded serialized relations. |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Forbidden absolute path | `rg -n "C:\\dev\\horoscope_front" scripts/llm-release-readiness.ps1` | repo root | yes | Zero hits. |
| No-go readiness decision | `pytest -q app/tests/unit/test_llm_release_readiness_script.py` | `backend` | yes | Guard verifies the script parses `llm-release-readiness.json` and rejects `decision != "go"`. |

## DRY / No Legacy scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Legacy terms in touched script/test | `rg -n "legacy|compat|shim|fallback|deprecated|alias" scripts/llm-release-readiness.ps1 backend/app/tests/unit/test_llm_release_readiness_script.py` | repo root | yes | No active compatibility or fallback introduced. |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Ruff format check | `ruff format --check app/tests/unit/test_llm_release_readiness_script.py` | `backend` | yes | No formatting changes needed. |
| Ruff lint | `ruff check app/tests/unit/test_llm_release_readiness_script.py` | `backend` | yes | No lint errors. |

## Regression checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Story validate | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/portable-llm-release-readiness/00-story.md` | repo root | yes | Story validates. |
| Story lint | `python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/portable-llm-release-readiness/00-story.md` | repo root | yes | Story lint passes. |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Diff summary | `git diff --stat` | repo root | yes | Only story-scoped files changed. |
| Whitespace check | `git diff --check` | repo root | yes | No whitespace errors. |
| Worktree status | `git status --short` | repo root | yes | Expected dirty files only. |

## Commands that may be skipped only with justification

- Full readiness script execution is required after the user-reported false-success failure.
- Full `pytest -q` may be skipped only if runtime is prohibitive; this implementation ran it successfully.
