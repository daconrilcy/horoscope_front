# CONDAMAD Code Review

## Review Target

- Story: `_condamad/stories/converge-horoscope-daily-narration-assembly/00-story.md`
- Review run: post-fix verification after DB restoration and evidence refresh
- Verdict: `CLEAN`

## Inputs Reviewed

- `_condamad/stories/converge-horoscope-daily-narration-assembly/00-story.md`
- `_condamad/stories/converge-horoscope-daily-narration-assembly/generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- Diff for changed backend code, tests, guardrails, and capsule evidence.

## Diff Summary

The implementation moves durable daily narration instructions out of
`AstrologerPromptBuilder` and into governed assembly-owned prompt/plan-rule
surfaces. The admin resolved-detail test now restores original published rows,
and AC2 now executes the seed and verifies persisted plan-rule wiring.

The previously modified tracked SQLite artifact `backend/horoscope.db` has been
restored to its committed baseline and is no longer part of the diff.

## Findings

No open findings.

Resolved findings from the previous review:

- CR-1: `backend/horoscope.db` remained modified. Fixed by restoring the tracked DB file; `git status --short -- backend/horoscope.db` now returns no output.
- CR-2: `generated/10-final-evidence.md` was stale. Fixed by updating the targeted pytest result to `23 passed`, the seed test result to `5 passed`, and recording the DB restoration check.

## Acceptance Audit

- AC1: PASS. Builder emits contextual daily payload and user parameters only. Forbidden markers are absent from `AstrologerPromptBuilder`.
- AC2: PASS. Seed execution test verifies migrated prompt text plus persisted free/premium `plan_rules_ref` and enabled `plan_rules_state`.
- AC3: PASS. Admin resolved detail exposes migrated prompt and plan-rule text, while restoring any original published rows after the test.
- AC4: PASS. Narration behavior remains routed through the daily narration service and gateway; adapter non-ownership guard is present.

## Validation Audit

Reviewer commands run in the venv:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q tests/unit/prediction/test_astrologer_prompt_builder.py app/tests/unit/test_seed_horoscope_narrator_assembly.py tests/llm_orchestration/test_narrator_migration.py tests/integration/test_admin_llm_catalog.py::test_admin_llm_catalog_resolved_detail_exposes_horoscope_daily_narration_assembly tests/unit/prediction/test_llm_narrator_deprecation_guard.py
```

Result: `23 passed in 6.54s`.

```powershell
ruff format --check .
ruff check .
python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\converge-horoscope-daily-narration-assembly\00-story.md
python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\converge-horoscope-daily-narration-assembly\00-story.md
git diff --check
```

Result: all passed.

Other reviewer checks:

- Builder forbidden marker scan: zero hits.
- Adapter / horoscope daily forbidden marker scan: zero hits.
- Positive migrated-text scan: hits only in assembly-owned files.
- RG-006 `app.api` import scan in non-API layers: zero hits.
- RG-016 nominal `LLMNarrator` test consumption scan: zero hits.
- RG-017 direct provider / `LLMNarrator` runtime scan: zero hits.
- `git status --short -- backend/horoscope.db`: no output.

## DRY / No Legacy Audit

- No duplicate prompt ownership remains in `AstrologerPromptBuilder`.
- No new `AIEngineAdapter` narrative ownership was found.
- No legacy `app.services.ai_engine_adapter` path was introduced.
- `RG-019` is a valid durable invariant for this story.

## Residual Risks

- Full pytest suite was not rerun during this final review; targeted regression coverage plus full Ruff checks passed.
- Product wording of the migrated narration prompt was not reviewed for tone beyond ownership and regression constraints.

## Verdict

`CLEAN`: no actionable findings remain. Required targeted validations, scans,
format/lint checks, story validation, and DB diff check pass.
