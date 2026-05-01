# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/block-supported-family-prompt-fallbacks/00-story.md`
- Review pass: fresh review after fixing the prior blocking finding.
- Verdict: `CLEAN`

## Inputs reviewed

- `_condamad/stories/block-supported-family-prompt-fallbacks/00-story.md`
- `_condamad/stories/block-supported-family-prompt-fallbacks/generated/10-final-evidence.md`
- `_condamad/stories/block-supported-family-prompt-fallbacks/fallback-exception-audit.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/llm/prompting/catalog.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`

## Diff summary

- Supported keys were removed from `PROMPT_FALLBACK_CONFIGS`.
- Runtime metadata for DB/profile resolution was decoupled from fallback prompt ownership.
- Production missing assembly is explicitly rejected for supported families.
- Remaining fallback exceptions are documented and exact-allowlisted.
- Reintroduction guards cover both direct catalog keys and `build_fallback_use_case_config`.

## Findings

- No actionable findings.

## Acceptance audit

- AC1 supported fallback keys absent: PASS. `PROMPT_FALLBACK_CONFIGS` no longer contains `chat`, `chat_astrologer`, `guidance_contextual`, `natal_interpretation`, or `horoscope_daily`.
- AC2 production missing assembly rejected: PASS. `test_production_rejects_missing_assembly_for_supported_families` covers `chat`, `guidance`, `natal`, and `horoscope_daily`.
- AC3 bootstrap exceptions exact: PASS. `test_prompt_fallback_config_exceptions_are_exact` matches `fallback-exception-audit.md`.
- AC4 QA pipeline remains canonical: PASS. Targeted LLM and integration guards pass; full-suite evidence is recorded in `generated/10-final-evidence.md`.

Applicable guardrails:

- `RG-004`: no API error-envelope changes introduced.
- `RG-006`: no non-API import of `app.api` introduced.
- `RG-018`: supported fallback prompt ownership is blocked by tests and scan.

## Validation audit

Commands rerun during this review:

- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_assembly_resolution.py tests/llm_orchestration/test_stable_profiles.py tests/llm_orchestration/test_execution_profiles.py tests/llm_orchestration/test_resolved_execution_plan.py tests/integration/test_llm_legacy_extinction.py` -> PASS, 58 passed.
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check .; ruff format --check .` -> PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\block-supported-family-prompt-fallbacks\00-story.md; python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\block-supported-family-prompt-fallbacks\00-story.md` -> PASS.
- `.\.venv\Scripts\Activate.ps1; cd backend; python -B -c "from app.main import app; print(app.title)"` -> PASS, `horoscope-backend`.
- `git diff --check` -> PASS with line-ending warnings only.
- `cd backend; rg -n "PROMPT_FALLBACK_CONFIGS|legacy_use_case_fallback" app tests` -> PASS, hits classified below.

Full-suite evidence reviewed but not rerun in this fresh pass:

- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` -> PASS, 3491 passed, 12 skipped, recorded in `generated/10-final-evidence.md`.

## DRY / No Legacy audit

- `PROMPT_FALLBACK_CONFIGS` in `catalog.py`: allowed bounded registry; supported prompt owners removed.
- `PROMPT_FALLBACK_CONFIGS` in tests: expected guard hits.
- `legacy_use_case_fallback` in `runtime/contracts.py`: existing observability enum, not prompt ownership.
- `legacy_use_case_fallback` in `test_ops_monitoring_llm_api.py`: existing observability fixture.
- Gateway bootstrap fallback now uses runtime metadata with an empty developer prompt only when `_allows_nominal_bootstrap_fallback` permits the non-prod empty-assembly case; production still raises `missing_assembly`.

## Residual risks

- Worktree contains unrelated dirty/untracked CONDAMAD story material outside this review target.
- Non-prod empty-assembly bootstrap remains an intentional exception; it is observable and does not reintroduce prompt text into `PROMPT_FALLBACK_CONFIGS`.

## Verdict

`CLEAN`
