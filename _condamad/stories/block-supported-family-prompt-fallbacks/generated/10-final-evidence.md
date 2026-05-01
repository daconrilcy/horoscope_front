# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: block-supported-family-prompt-fallbacks
- Source story: `_condamad/stories/block-supported-family-prompt-fallbacks/00-story.md`
- Capsule path: `_condamad/stories/block-supported-family-prompt-fallbacks`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: pre-existing dirty `_condamad/stories/regression-guardrails.md`; untracked `_condamad/audits/prompt-generation/`, `_condamad/stories/block-supported-family-prompt-fallbacks/`, `_condamad/stories/converge-horoscope-daily-narration-assembly/`, `_condamad/stories/formalize-consultation-guidance-prompt-ownership/`.
- AGENTS.md files considered: root `AGENTS.md`.
- Capsule generated: yes, under requested story folder after correcting helper output path.
- Regression guardrails considered: `RG-004`, `RG-006`, `RG-018`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story unchanged. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Rewritten with story-specific scope. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC4 mapped. |
| `generated/04-target-files.md` | yes | yes | PASS | Target files and searches recorded. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands and timeout handling recorded. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Exact forbidden keys and exceptions listed. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Removed forbidden keys from `backend/app/domain/llm/prompting/catalog.py`; added `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`. | `pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py` PASS; forbidden key scan classified. | PASS | Runtime fallback builder returns `None` for each forbidden key. |
| AC2 | Added `test_production_rejects_missing_assembly_for_supported_families` in `test_assembly_resolution.py`. | `pytest -q tests/llm_orchestration/test_assembly_resolution.py` PASS. | PASS | Covers chat, guidance, natal, horoscope_daily. |
| AC3 | Added exact allowlist test in `test_prompt_governance_registry.py`; added `fallback-exception-audit.md`. | `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py` PASS. | PASS | New fallback keys require explicit audit/test update. |
| AC4 | Did not modify QA routes; existing integration guard kept passing. | `pytest -q tests/integration/test_llm_legacy_extinction.py` PASS; combined targeted suite PASS. | PASS | Canonical pipeline guards remain active. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/domain/llm/prompting/catalog.py` | modified | Removed supported prompt fallback entries. | AC1 |
| `backend/app/domain/llm/runtime/gateway.py` | modified | Decoupled DB/profile runtime metadata from fallback prompt ownership. | AC2, AC4 |
| `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` | added | Reintroduction guard for forbidden fallback keys. | AC1, AC4 |
| `backend/tests/llm_orchestration/test_assembly_resolution.py` | modified | Production missing assembly coverage and DB prompt non-regression coverage. | AC2, AC4 |
| `backend/tests/llm_orchestration/test_prompt_governance_registry.py` | modified | Exact fallback exception allowlist guard. | AC3 |
| `_condamad/stories/block-supported-family-prompt-fallbacks/fallback-exception-audit.md` | added | Persistent audit of fallback exceptions. | AC3 |
| `_condamad/stories/block-supported-family-prompt-fallbacks/generated/*` | generated/modified | CONDAMAD evidence. | AC1-AC4 |

## Files deleted

- None.

## Tests added or updated

- Added `test_supported_use_cases_are_absent_from_prompt_fallback_configs`.
- Added `test_supported_use_cases_do_not_build_fallback_config`.
- Added `test_production_rejects_missing_assembly_for_supported_families`.
- Added `test_db_prompt_resolution_does_not_require_supported_fallback_prompt`.
- Added `test_prompt_fallback_config_exceptions_are_exact`.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\block-supported-family-prompt-fallbacks\00-story.md` | `backend/` | PASS | 0 | Story validation PASS. |
| `python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\block-supported-family-prompt-fallbacks\00-story.md` | `backend/` | PASS | 0 | Story lint PASS. |
| `pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py` | `backend/` | PASS | 0 | 6 passed. |
| `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py` | `backend/` | PASS | 0 | 19 passed. |
| `pytest -q tests/llm_orchestration/test_assembly_resolution.py` | `backend/` | PASS | 0 | Covered by combined targeted suite after adding DB prompt non-regression coverage. |
| `pytest -q tests/integration/test_llm_legacy_extinction.py` | `backend/` | PASS | 0 | 4 passed. |
| `pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_assembly_resolution.py tests/llm_orchestration/test_stable_profiles.py tests/llm_orchestration/test_execution_profiles.py tests/llm_orchestration/test_resolved_execution_plan.py tests/integration/test_llm_legacy_extinction.py` | `backend/` | PASS | 0 | 58 passed. |
| `pytest -q app/tests/integration/test_consultation_catalogue.py app/tests/integration/test_consultation_third_party.py app/tests/integration/test_consultations_router.py app/tests/integration/test_ops_monitoring_api.py` | `backend/` | PASS | 0 | 31 passed. |
| `pytest -q` | `backend/` | PASS | 0 | 3491 passed, 12 skipped. |
| `rg -n "PROMPT_FALLBACK_CONFIGS\|legacy_use_case_fallback" app tests` | `backend/` | PASS | 0 | Hits classified in DRY / No Legacy evidence. |
| `ruff format .` | `backend/` | PASS | 0 | 1 file reformatted. |
| `ruff check . --fix` | `backend/` | PASS | 0 | 2 import-order issues fixed. |
| `ruff check .` | `backend/` | PASS | 0 | All checks passed. |
| `ruff format --check .` | `backend/` | PASS | 0 | 1243 files already formatted. |
| `python -B -c "from app.main import app; print(app.title)"` | `backend/` | PASS | 0 | Printed `horoscope-backend`. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\block-supported-family-prompt-fallbacks` | repo root | PASS | 0 | CONDAMAD validation PASS. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; line-ending warnings only. |

## Commands skipped or blocked

- None.

## DRY / No Legacy evidence

| Pattern | File | Classification | Action | Status |
|---|---|---|---|---|
| `PROMPT_FALLBACK_CONFIGS` | `app/domain/llm/prompting/catalog.py` | allowed bounded registry | Removed forbidden entries and exact-allowlisted remaining entries. | PASS |
| `PROMPT_FALLBACK_CONFIGS` | `tests/llm_orchestration/test_llm_legacy_extinction.py` | test_guard_expected_hit | Guard asserts forbidden keys absent and builder returns `None`. | PASS |
| `PROMPT_FALLBACK_CONFIGS` | `tests/llm_orchestration/test_prompt_governance_registry.py` | test_guard_expected_hit | Guard asserts exact exception set. | PASS |
| `legacy_use_case_fallback` | `app/domain/llm/runtime/contracts.py` | out_of_scope_with_justification | Existing enum/observability contract, not prompt fallback ownership. | PASS |
| `legacy_use_case_fallback` | `app/tests/integration/test_ops_monitoring_llm_api.py` | allowed_historical_reference | Existing observability fixture outside story scope. | PASS |

## Diff review

- `git diff --stat`: tracked diff limited to LLM catalog/tests plus pre-existing dirty registry not edited by this implementation; untracked story artifacts are expected.
- `git diff --check`: PASS, line-ending warnings only.
- No frontend, API routes, prompt seed content, dependency files, or DB migrations changed.

## Final worktree status

```text
 M _condamad/stories/regression-guardrails.md
 M backend/app/domain/llm/prompting/catalog.py
 M backend/app/domain/llm/runtime/gateway.py
 M backend/tests/llm_orchestration/test_assembly_resolution.py
 M backend/tests/llm_orchestration/test_prompt_governance_registry.py
?? _condamad/audits/prompt-generation/
?? _condamad/stories/block-supported-family-prompt-fallbacks/
?? _condamad/stories/converge-horoscope-daily-narration-assembly/
?? _condamad/stories/formalize-consultation-guidance-prompt-ownership/
?? backend/tests/llm_orchestration/test_llm_legacy_extinction.py
```

`_condamad/stories/regression-guardrails.md` and the unrelated `_condamad` untracked folders were already dirty at preflight.

## Remaining risks

- `_condamad/stories/regression-guardrails.md` was dirty before implementation and remains outside this change set.
- The gateway now permits non-prod empty-assembly bootstrap to use runtime metadata with an empty developer prompt for supported families; production still rejects missing assemblies with `missing_assembly`.

## Suggested reviewer focus

- Confirm the exact fallback exception list is acceptable.
- Confirm supported production paths fail on missing assembly rather than falling through to fallback prompt ownership.
