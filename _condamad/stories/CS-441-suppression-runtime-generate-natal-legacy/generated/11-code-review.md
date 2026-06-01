# Review CS-441 - suppression-runtime-generate-natal-legacy

Verdict: CLEAN

## Scope

- Story reviewed: `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/00-story.md`
- Source brief: `_story_briefs/cs-441-corriger-suppression-runtime-generate-natal-legacy.md`
- Tracker row: `CS-441`, status `done`, last update `2026-06-01`
- Review mode: implementation review after CS-441 code, tests, guardrails and evidence were produced.

## Brief And Tracker Alignment

- The tracker `Path` matches the target story path.
- The tracker `Source` matches the source brief path.
- The story objective matches the brief: delete the provider-capable legacy runtime entry point
  `AIEngineAdapter.generate_natal_interpretation`.
- The implementation preserves the explicit non-goals: no catalogue, seed, script, frontend,
  migration, public historical API deletion, or `_condamad/run-state.json` change is required.

## Implementation Review

- `backend/app/domain/llm/runtime/adapter.py` no longer defines
  `AIEngineAdapter.generate_natal_interpretation`.
- `backend/app/services/llm_generation/natal/interpretation_service.py` no longer builds
  `NatalExecutionInput` for legacy natal generation and rejects legacy generation before provider
  request construction.
- Historical readonly reads are still served through persisted interpretation projection.
- Basic generation remains owned by the `theme_natal` runtime and public slot contract.
- Positive tests no longer mock the removed adapter method.
- Architecture guards reject reintroduction of the removed method and legacy runtime input builder.

## Guardrail Review

Applicable guardrails remain covered by executable evidence:

- `RG-001`, `RG-018`, `RG-150`, `RG-164`, `RG-167`, `RG-173`, `RG-174`.

Boundary guardrails remain non-applicable or indirectly preserved for this backend-only deletion:

- `RG-005`, `RG-006`, `RG-149`.

No new durable invariant was created; no registry update is required.

## Validation Evidence

Executed from repository root with `.\.venv\Scripts\Activate.ps1` active.

```powershell
Push-Location backend
ruff check .
python -B -m pytest -q tests/unit/domain/theme_natal `
  tests/integration/test_theme_natal_basic_full_reading_runtime.py `
  tests/integration/test_theme_natal_public_api_product_actions.py `
  tests/integration/test_theme_natal_public_reads.py `
  tests/architecture/test_legacy_natal_generation_inventory_guard.py `
  tests/architecture/test_llm_legacy_extinction.py `
  ..\backend\app\tests\unit\test_ai_engine_adapter.py `
  ..\backend\app\tests\unit\test_natal_interpretation_service.py `
  ..\backend\app\tests\unit\test_natal_interpretation_service_v2.py --tb=short
Pop-Location
```

Result: `ruff check` PASS; targeted tests PASS, `80 passed, 22 deselected`.

```powershell
python -B -c "<app.routes/app.openapi legacy runtime check>"
rg -n 'generate_natal_interpretation' backend/app backend/tests backend/app/tests
rg -n 'NatalExecutionInput\(|use_case_key=.*natal_interpretation' `
  backend/app/services/llm_generation/natal backend/app/domain/llm/runtime/adapter.py
```

Result: route/OpenAPI PASS; both zero-hit scans PASS.

```powershell
python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py `
  _condamad\stories\CS-441-suppression-runtime-generate-natal-legacy --final
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py `
  _condamad\stories\CS-441-suppression-runtime-generate-natal-legacy\00-story.md
python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict `
  _condamad\stories\CS-441-suppression-runtime-generate-natal-legacy\00-story.md
```

Result: capsule validation PASS; story validation PASS; strict lint PASS.

## Findings

No actionable implementation issue found.

## Issues Fixed During Review Loop

- Closure artifacts still described an intermediate review state after implementation review:
  `00-story.md`, `generated/10-final-evidence.md`, `generated/11-code-review.md` and
  `_condamad/stories/story-status.md` still described an intermediate review state.
- Fix applied: updated those artifacts to `done` / final `CLEAN` review without changing ACs,
  scope, source brief or application behavior.

## Propagation

No-propagation: the correction was local closure evidence only and does not reveal reusable
learning requiring guardrail, AGENTS or skill changes.

## Residual Risk

Repository-wide pytest remains known red outside CS-441, as documented in `generated/10-final-evidence.md`.
The failures concern router/model namespace debt and catalogue/seed checks outside this story scope.
