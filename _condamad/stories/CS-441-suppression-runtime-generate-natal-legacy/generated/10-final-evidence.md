# Final Evidence - CS-441-suppression-runtime-generate-natal-legacy

## Story status

- Validation outcome: targeted-pass-with-full-suite-limitations
- Ready for review: yes
- Story key: CS-441-suppression-runtime-generate-natal-legacy
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy`
- Story registry: `CS-441` updated to `ready-to-review` on `2026-06-01`.

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- Initial `git status --short`: dirty worktree already contained CS-441 target files, generated capsule files, `_condamad/run-state.json`, and untracked source briefs.
- `_condamad/run-state.json`: pre-existing dirty file, out of scope and not intentionally edited.
- Source brief: `_story_briefs/cs-441-corriger-suppression-runtime-generate-natal-legacy.md` verified through `story-status.md`.
- AGENTS.md considered: repository root `AGENTS.md`.
- Guardrails classified:
  - Applicable: `RG-001`, `RG-018`, `RG-150`, `RG-164`, `RG-167`, `RG-173`, `RG-174`.
  - Boundary/non-applicable to edited code: `RG-002`, `RG-005`, `RG-006`, `RG-149`.

## Capsule validation

- Required generated files are present in `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/generated/`.
- Capsule summary was regenerated with `condamad_capsule_summary.py` after implementation evidence existed.
- Structural validation is recorded in `Commands run`.

## Implementation summary

- Deleted `AIEngineAdapter.generate_natal_interpretation` from `backend/app/domain/llm/runtime/adapter.py`.
- Removed provider-capable runtime construction from `NatalInterpretationService.interpret`: no `NatalExecutionInput`, no `use_case_key="natal_interpretation"` builder, no adapter call.
- Preserved historical readonly interpretation reads and changed legacy generation attempts to explicit `legacy_natal_generation_disabled` errors with `replacement="/v1/theme-natal/readings"`.
- Updated backend tests and architecture guards so positive legacy provider mocks are gone and reintroduction fails.

## AC validation

| AC | Implementation evidence | Validation evidence | Status |
|---|---|---|---|
| AC1 | `backend/app/domain/llm/runtime/adapter.py` deletes `AIEngineAdapter.generate_natal_interpretation`; `backend/tests/architecture/test_llm_legacy_extinction.py::test_natal_adapter_entry_point_is_removed` guards reintroduction. | `rg -n "generate_natal_interpretation" backend/app` -> `PASS: no matches`; targeted pytest `64 passed`. | PASS |
| AC2 | `NatalInterpretationService.interpret` rejects legacy generation before provider construction; service tests assert no gateway call. | AST/source guard in `test_natal_legacy_service_does_not_build_runtime_input`; targeted pytest `64 passed`. | PASS |
| AC3 | `interpretation_service.py` no longer imports or constructs `NatalExecutionInput` in the natal service path. | `rg -n "NatalExecutionInput\|use_case_key\s*=\s*['\"]natal_interpretation" backend/app/services/llm_generation/natal` -> `PASS: no matches`. | PASS |
| AC4 | Legacy `interpret` path now raises `legacy_natal_generation_disabled` before provider request construction. | `backend/tests/architecture/test_llm_legacy_extinction.py`; `backend/app/tests/unit/test_natal_interpretation_service*.py`; targeted pytest `64 passed`. | PASS |
| AC5 | `level` and `variant_code` remain only readonly lookup/rejection metadata in the removed path, not provider runtime selectors. | Bounded scans of natal service and adapter show no `NatalExecutionInput` or removed adapter call; targeted pytest `64 passed`. | PASS |
| AC6 | Positive provider mocks were removed or converted to absence/rejection assertions. | `rg -n "generate_natal_interpretation" backend/tests backend/app/tests` -> `PASS: no matches`. | PASS |
| AC7 | Readonly historical deserialization, list and get paths remain in `interpretation_service.py`. | `backend/tests/integration/test_theme_natal_public_reads.py` included in targeted pytest pass. | PASS |
| AC8 | `ThemeNatalBasicFullReadingRuntime` remains the Basic generation owner. | `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py` included in targeted pytest pass. | PASS |
| AC9 | CS-440 CR-4 runtime adapter portion is closed by method deletion and architecture guard coverage. | AST guard + bounded zero-hit scans + targeted pytest `64 passed`. | PASS |
| AC10 | Before/after scan and OpenAPI artifacts are persisted under `evidence/`. | `runtime-generate-natal-after.txt`, `positive-mocks-after.txt`, `openapi-after.json`, `route-openapi-after-check.txt`; artifact paths present. | PASS |
| AC11 | No public route was added to preserve the removed runtime path. | `route-openapi-after-check.txt`: `PASS: no public route/openapi legacy runtime hits`. | PASS |

## Files changed

- Backend app:
  - `backend/app/domain/llm/runtime/adapter.py`
  - `backend/app/services/llm_generation/natal/interpretation_service.py`
- Backend tests:
  - `backend/app/tests/unit/test_ai_engine_adapter.py`
  - `backend/app/tests/unit/test_natal_interpretation_service.py`
  - `backend/app/tests/unit/test_natal_interpretation_service_v2.py`
  - `backend/tests/architecture/test_llm_legacy_extinction.py`
  - `backend/tests/integration/test_basic_natal_v2_cache_invalidation.py`
  - `backend/tests/integration/test_basic_natal_v2_pipeline.py`
  - `backend/tests/integration/test_natal_basic_complete_v3_runtime.py`
  - `backend/tests/integration/test_theme_natal_basic_full_reading_runtime.py`
  - `backend/tests/unit/domain/llm/test_natal_llm_astrology_input.py`
  - `backend/tests/unit/test_basic_natal_narrative_validator.py`
- Story evidence:
  - `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/evidence/*`
  - `_condamad/stories/CS-441-suppression-runtime-generate-natal-legacy/generated/*`
  - `_condamad/stories/story-status.md`

## Files deleted

- No standalone file was deleted.
- In-file legacy runtime code was removed from `backend/app/domain/llm/runtime/adapter.py` and `backend/app/services/llm_generation/natal/interpretation_service.py`.

## Tests added or updated

- Updated adapter and natal service unit tests to assert removal/rejection rather than positive provider execution.
- Updated `backend/tests/architecture/test_llm_legacy_extinction.py` to guard the deleted adapter entry point and missing runtime input builder.
- Updated Basic/runtime integration tests touched by the legacy path so canonical `theme_natal` behavior remains covered.

## Evidence artifacts

- `evidence/runtime-generate-natal-before.txt`: before scan showed adapter method, service input builder and positive tests.
- `evidence/runtime-generate-natal-after.txt`: `PASS: no matches`.
- `evidence/positive-mocks-before.txt`: before scan showed positive mocks/calls.
- `evidence/positive-mocks-after.txt`: `PASS: no matches`.
- `evidence/openapi-before.json` and `evidence/openapi-after.json`: persisted OpenAPI snapshots.
- `evidence/route-openapi-after-check.txt`: `PASS: no public route/openapi legacy runtime hits`.
- `evidence/removal-audit.md`: deletion/keep decisions and risks.
- `evidence/validation.txt`: final command results and full-suite limitation details.

## Commands run

| Command | Result | Evidence summary |
|---|---|---|
| `ruff format <changed python files>` | PASS | 10 files unchanged, then 2 files unchanged after in-scope test updates. |
| `python -B -m pytest -q --tb=short <CS-441 targeted paths>` | PASS | `64 passed, 23 deselected in 1.93s`. |
| `python -B -c <app.routes/app.openapi legacy hit check>` | PASS | No route/OpenAPI hit for removed runtime strings. |
| `rg -n "generate_natal_interpretation" backend/app backend/tests backend/app/tests` | PASS | Exit 1 treated as `PASS: no matches` for zero-hit scan. |
| `rg -n "NatalExecutionInput|use_case_key=..." backend/app/services/llm_generation/natal backend/app/domain/llm/runtime/adapter.py` | PASS | Exit 1 treated as `PASS: no matches`. |
| `ruff check .` | PASS | `All checks passed!`. |
| `git diff --check` | PASS | CRLF normalization warnings only. |
| `python -B -m pytest -q --tb=short` | FAIL, out-of-scope | `9 failed, 3552 passed, 2 skipped, 1284 deselected`; failures are API router architecture debt, LLM DB model namespace debt, and prompt catalogue/seed checks excluded by CS-441 non-goals / CS-442 ownership. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-441-suppression-runtime-generate-natal-legacy` | PASS | Capsule structure and evidence sections validated after final-evidence repair. |

## Commands skipped or blocked

- No CS-441 capsule-required command was skipped.
- Repository-wide pytest was executed and recorded as a repository-level limitation because remaining failures are outside the CS-441 runtime deletion surface.

## Full-suite residual failures

- `backend/app/tests/unit/test_api_router_architecture.py::test_router_modules_do_not_define_private_helpers`
- `backend/app/tests/unit/test_api_router_architecture.py::test_api_sql_boundary_debt_matches_exact_allowlist`
- `backend/app/tests/unit/test_gateway_modes.py::test_catalog_schema_is_used_for_free_natal_fallback`
- `backend/app/tests/unit/test_seed_29_prompt_contract.py::test_seed_29_natal_short_requires_llm_astrology_input_v1`
- `backend/tests/unit/test_llm_model_namespace_guard.py::*` (3 failures)
- `backend/tests/unit/test_seed_66_20_taxonomy_basic_natal.py::*` (2 failures)

These failures are not fixed in this story because catalogues/seeds are explicit non-goals owned by CS-442, and router/model namespace debt is outside the CS-441 runtime adapter/service surface.

## DRY / No Legacy evidence

- No shim, alias, wrapper, re-export, fallback or compatibility method was added for `generate_natal_interpretation`.
- `backend/app` has zero exact hits for `generate_natal_interpretation`.
- Backend positive tests have zero exact hits for `generate_natal_interpretation`; remaining checks use absence/rejection behavior without preserving the old method name.
- Historical readonly rows are classified as `canonical-active`; provider-capable generation is classified as `historical-facade` and deleted.

## Diff review

- Scoped diff review covered backend adapter, natal service, architecture guards, targeted unit/integration tests, story status and CS-441 evidence files.
- No frontend, migration, catalogue, seed, script, auth, i18n, styling or `_condamad/run-state.json` change was introduced by this implementation.
- `generated/11-code-review.md` remains handoff-only because it predates implementation.

## Review artifacts

- `generated/11-code-review.md` existed before implementation and is classified as obsolete pre-implementation editorial review, not final code-review evidence.

## Final worktree status

- `git status --short` after implementation showed CS-441 code/test/evidence/status changes plus pre-existing `_condamad/run-state.json` and untracked source briefs.
- Known validation caches were removed from fixed workspace paths after test/lint runs.

## Remaining risks

- Full suite remains red on 9 out-of-scope failures; reviewer should not treat that as CS-441 closure evidence, but it is a repository-level risk.

## Suggested reviewer focus

- Verify that `NatalInterpretationService.interpret` preserves readonly historical reads while never constructing a provider request for legacy generation.
