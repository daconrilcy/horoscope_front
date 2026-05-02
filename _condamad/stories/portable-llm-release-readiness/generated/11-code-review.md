# CONDAMAD Code Review

## Review Target

- Story: `_condamad/stories/portable-llm-release-readiness/00-story.md`
- Status reviewed: `ready-for-review`
- Verdict: `CLEAN`

## Inputs Reviewed

- `_condamad/stories/portable-llm-release-readiness/00-story.md`
- Capsule evidence under `_condamad/stories/portable-llm-release-readiness/generated/`
- `_condamad/stories/regression-guardrails.md`
- Current diff for `scripts/llm-release-readiness.ps1`, backend release files,
  ownership registers, and generated evidence artifacts

## Diff Summary

The script now uses a repo-relative pytest cache by default, exposes
`-PytestCachePath`, runs backend pytest steps from `backend/`, rejects native
command failures, and refuses to print `llm_release_readiness_ok` while the
aggregate readiness report is `no-go`.

The supporting backend diff is now explicitly governed by the story: release
snapshot tests use unique versions, snapshot serialization preloads relations
already present in the manifest contract, and ownership registries cover the new
script guard.

## Findings

No actionable findings.

## Acceptance Audit

- AC1: satisfied; forbidden absolute local path is absent from the active script.
- AC2: satisfied; cache resolution and override are covered by the script guard.
- AC3: satisfied; baseline, after-scan, and run evidence are present.
- AC4: satisfied; applicable LLM guardrails were validated and no prompt/provider
  behavior changed.
- AC5: satisfied; story validate and strict lint pass.
- AC6: satisfied; runtime no-go behavior stops before false success.
- AC7: satisfied; supporting backend release and ownership preconditions are now
  explicitly scoped and covered.

## Validation Audit

Reviewer validation commands run for this review:

```powershell
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_llm_release_readiness_script.py app/tests/unit/test_backend_quality_test_ownership.py app/tests/unit/test_scripts_ownership.py
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/integration/test_llm_release.py
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py tests/llm_orchestration/test_assembly_resolution.py
.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check app/tests/unit/test_llm_release_readiness_script.py
.\.venv\Scripts\Activate.ps1; cd backend; ruff check app/tests/unit/test_llm_release_readiness_script.py
.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\portable-llm-release-readiness\00-story.md
.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\portable-llm-release-readiness\00-story.md
rg -n "C:\\dev\\horoscope_front" scripts/llm-release-readiness.ps1
rg -n "legacy|compat|shim|fallback|deprecated|alias" scripts/llm-release-readiness.ps1 backend/app/tests/unit/test_llm_release_readiness_script.py
try { .\scripts\llm-release-readiness.ps1 -SkipStartupSmoke; Write-Error 'Expected readiness script to fail on no-go report'; exit 1 } catch { if ($_.Exception.Message -notlike '*LLM release readiness decision is*') { throw }; Write-Host $_.Exception.Message; exit 0 }
git diff --check
```

Results:

- 15 script/ownership tests passed.
- 11 release integration tests passed.
- 62 LLM guardrail tests passed.
- Ruff format/check passed for the new guard test.
- Story validate and strict lint passed.
- Runtime no-go behavior was verified in this review: the script stops with
  `LLM release readiness decision is 'no-go'` and does not print false success.
- Forbidden absolute-path scan returned zero hits in the active script.
- The only `legacy` scan hit is the expected residual-report artifact name in
  the release readiness script.
- `git diff --check` reported no whitespace errors, only LF-to-CRLF warnings.

## DRY / No Legacy Audit

No fallback to `C:\dev\horoscope_front` remains in the active script. No second
readiness script was introduced. Obsolete pytest paths are retained only as
historical baseline evidence and replaced by active collected paths in runtime.

## Residual Risks

The local aggregate readiness artifact remains `no-go` until qualification,
golden, and smoke evidence are supplied or correlated. That is now expected and
correctly surfaced as a script failure.

## Verdict

`CLEAN`
