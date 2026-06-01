# Dev Log - CS-441

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- `.git`: present.
- Initial dirty files included CS-441 target files, generated capsule files, `_condamad/run-state.json`, and untracked source briefs. `_condamad/run-state.json` and source briefs were not modified by this implementation run.
- Story status row verified for `CS-441`: path and brief source matched the request.
- Scoped guardrails resolved from story/capsule: `RG-001`, `RG-002`, `RG-005`, `RG-006`, `RG-018`, `RG-149`, `RG-150`, `RG-164`, `RG-167`, `RG-173`, `RG-174`.

## Implementation notes

- Removed `AIEngineAdapter.generate_natal_interpretation` from `backend/app/domain/llm/runtime/adapter.py`.
- Removed `AIEngineAdapter` and `NatalExecutionInput` usage from `NatalInterpretationService.interpret`.
- Kept readonly historical interpretation projection/list/get behavior in `interpretation_service.py`.
- Converted positive legacy provider tests into deletion, rejection, readonly, and `theme_natal` runtime guards.
- Marked the pre-implementation editorial review artifact as obsolete for final implementation evidence.

## Validation log

- `ruff format` on changed Python files: PASS.
- Targeted pytest for CS-441 surfaces: `64 passed, 23 deselected`.
- `ruff check .`: PASS.
- `git diff --check`: PASS, with CRLF normalization warnings only.
- `python -B -m pytest -q --tb=short`: FAIL with 9 out-of-scope failures after CS-441 fixes; see final evidence.

## Feedback loop

- No-propagation: no reusable skill/process issue was identified. The remaining red full-suite checks map to existing unrelated debt or non-goal catalogue/seed cleanup.
