# Target Files

## Must read

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/portable-llm-release-readiness/00-story.md`
- `_condamad/audits/scripts-ops/2026-05-02-1847/01-evidence-log.md`
- `scripts/llm-release-readiness.ps1`
- `backend/app/tests/unit/test_start_dev_stack_script.py`
- `backend/app/tests/unit/test_scripts_ownership.py`

## Must search

- `rg -n "llm-release-readiness|PytestCache|pytest_cache_runtime|C:\\\\dev\\\\horoscope_front" backend app tests scripts _condamad`
- `rg -n "cache_dir=|pytest_cache_runtime|\\.pytest_cache_runtime|PytestCachePath" .`
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" scripts/llm-release-readiness.ps1 backend/app/tests/unit/test_llm_release_readiness_script.py`

## Likely modified

- `scripts/llm-release-readiness.ps1`
- `backend/app/tests/unit/test_llm_release_readiness_script.py`
- `_condamad/stories/portable-llm-release-readiness/path-baseline.txt`
- `_condamad/stories/portable-llm-release-readiness/path-after.txt`
- `_condamad/stories/portable-llm-release-readiness/readiness-run-evidence.md`
- `_condamad/stories/portable-llm-release-readiness/generated/*.md`

## Forbidden unless justified

- `backend/app/domain/llm/prompting/**`
- `frontend/**`
- API contracts and generated clients
- LLM provider implementations

## Delete or move candidates

- None.
