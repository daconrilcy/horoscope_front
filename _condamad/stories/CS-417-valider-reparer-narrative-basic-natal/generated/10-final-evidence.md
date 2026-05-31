# Final Evidence - CS-417-valider-reparer-narrative-basic-natal

## Story status

- Validation outcome: targeted-pass-after-review-fix-with-full-suite-unrelated-failures
- Ready for review: yes
- Story key: CS-417-valider-reparer-narrative-basic-natal
- Source story: `00-story.md`
- Capsule path: `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal`
- Tracker row: `done`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: `_condamad/run-state.json` was already dirty.
- AGENTS.md: repository instructions provided in the user prompt; no scoped `backend/AGENTS.md` found.
- Story/status alignment: CS-417 path and source brief matched `_condamad/stories/story-status.md`.
- Capsule repair: required generated files were missing; repaired with `condamad_prepare.py --repair-generated-only`.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Status synchronized to `ready-to-review`. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | Fresh AC evidence recorded. |
| `generated/04-target-files.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Generated capsule file present. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Final evidence updated. |

## Implementation summary

- Added Basic plan-backed draft validation in `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`.
- Added structured Basic rejection metadata carrying `request_id`, `engine_version`, `schema_version`, `validation_errors`, and `fallback_used`.
- Added one-shot repair orchestration plus deterministic fallback generated only from `BasicNatalReadingPlan` public evidence.
- Review fix: malformed section entries are now rejected instead of being ignored when all requested sections are present.
- Added `backend/tests/unit/test_basic_natal_narrative_validator.py` covering missing/extra sections, unsupported facts, date-only surfaces, technical markers, person, advice, audit metadata, repair, fallback, limitations, disclaimers, sources, and vocation rejection.

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Basic validator compares requested plan section codes with draft sections. | validator pytest | PASS | Missing section is rejected. |
| AC2 | Basic validator rejects section codes absent from `BasicNatalReadingPlan` and malformed section entries. | validator pytest | PASS | Unauthorized or non-auditable section is rejected. |
| AC3 | Basic validator rejects draft fact ids and known astro terms absent from plan evidence. | validator pytest | PASS | Unsupported generated fact is rejected. |
| AC4 | Date-only plan limitations activate time-surface denylist. | validator pytest + VC11 scan | PASS | Ascendant/house/MC surfaces rejected. |
| AC5 | Basic denylist rejects score, raw audit and jargon markers. | validator pytest + VC10 scan | PASS | Expected scan hits are denylist constants only. |
| AC6 | Basic text check rejects mixed `tu` and `vous`. | validator pytest | PASS | Mixed person rejected. |
| AC7 | Prescriptive advice denylist rejects imperative advice. | validator pytest | PASS | Prescriptive advice rejected. |
| AC8 | Required plan limitations are mandatory in draft. | validator pytest | PASS | Valid draft keeps limitations. |
| AC9 | Basic rejection outcome includes structured metadata. | validator pytest | PASS | `request_id`, `engine_version`, `schema_version`, `validation_errors`. |
| AC10 | Repair orchestrator calls one constrained callback with plan and errors. | validator pytest | PASS | First invalid draft triggers repair. |
| AC11 | Second invalid draft validates deterministic fallback from plan evidence. | validator pytest + schema guard pytest | PASS | No padding fallback introduced. |
| AC12 | Existing rejected public boundary remains protected. | integration pytest with `--long` | PASS | Audit-only public boundary. |
| AC13 | Quota acceptance gate unchanged and tested. | quota-on-acceptance pytest | PASS | Consumption waits for accepted valid reading. |
| AC14 | Story evidence artifacts persisted. | evidence files + final capsule validation | PASS | Before/after/validation evidence present. |
| AC15 | RG-166 present in guardrail registry. | registry `rg` scan | PASS | Durable invariant already recorded. |
| AC16 | Vocation/carriere text is rejected when no `vocation` section is planned. | validator pytest | PASS | Unsupported vocation section invalid. |
| AC17 | Required plan disclaimers are mandatory in draft. | validator pytest | PASS | Valid draft keeps disclaimers. |
| AC18 | Public evidence ids/sources and section evidence ids are required and plan-scoped. | validator pytest | PASS | Valid draft keeps public sources. |

## Files changed

- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/tests/unit/test_basic_natal_narrative_validator.py`
- `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/generated/**`
- `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/evidence/**`
- `_condamad/stories/story-status.md`

## Files deleted

- None.

## Tests added or updated

- Added `backend/tests/unit/test_basic_natal_narrative_validator.py`.

## Commands run

| Command | Working directory | Result | Notes |
|---|---|---|---|
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --root . --repair-generated-only _condamad\stories\CS-417-valider-reparer-narrative-basic-natal` | repo root | PASS | Capsule generated files repaired. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-417-valider-reparer-narrative-basic-natal` | repo root | PASS | Capsule structure valid before implementation. |
| `ruff format app\services\llm_generation\natal\narrative_natal_reading_validator.py tests\unit\test_basic_natal_narrative_validator.py` | `backend` | PASS | Scoped Python formatting. |
| `ruff check .` | `backend` | PASS | Backend lint passes. |
| `python -B -m pytest -q tests\unit\test_basic_natal_narrative_validator.py --tb=short` | `backend` | PASS | 9 passed. |
| `python -B -m pytest -q tests\unit\test_narrative_natal_reading_v1.py --tb=short` | `backend` | PASS | 14 passed. |
| `python -B -m pytest -q tests\unit\test_natal_interpretation_service_v3_schema_guard.py --tb=short` | `backend` | PASS | 5 passed. |
| `python -B -m pytest -q tests\unit\test_natal_chart_long_quota_on_acceptance.py --tb=short` | `backend` | PASS | 4 passed. |
| `python -B -m pytest -q tests\integration\test_natal_interpretation_rejected_public_boundary.py --long --tb=short` | `backend` | PASS | 8 passed; `--long` required by project collection hook. |
| `python -B -m pytest -q tests\unit\test_narrative_natal_reading_v1.py tests\unit\test_natal_interpretation_service_v3_schema_guard.py tests\unit\test_natal_chart_long_quota_on_acceptance.py --tb=short` | `backend` | PASS | 23 passed. |
| `rg -n "fallback = response\.sections\[0\]\|ranking_score\|condition_axis\|audit_input" app\services\llm_generation\natal` | `backend` | PASS_WITH_EXPECTED_HITS | Hits are denylist constants in the validator only; zero fallback padding hit. |
| `rg -n "Ascendant\|MC\|maison\|maisons\|angularite" app\services\llm_generation\natal tests\unit\test_basic_natal_narrative_validator.py` | `backend` | PASS_WITH_EXPECTED_HITS | Hits are denylist constants, explicit rejection test, and pre-existing rejected workflow support. |
| `rg -n "RG-166\|Basic plan validation\|BasicNatalReadingPlan" ../_condamad/stories/regression-guardrails.md` | `backend` | PASS | RG-166 present. |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-417-valider-reparer-narrative-basic-natal` | repo root | PASS | CONDAMAD validation pass. |
| `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py _condamad\stories\CS-417-valider-reparer-narrative-basic-natal\00-story.md` | repo root | PASS | Story validation pass. |
| `python -B .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict _condamad\stories\CS-417-valider-reparer-narrative-basic-natal\00-story.md` | repo root | PASS | Strict story lint pass. |
| `python -B -m pytest -q --tb=short` | `backend` | FAIL_UNRELATED | 3667 passed, 2 skipped, 1253 deselected, 2 failed in pre-existing astrology governance guards outside changed files. |

## Full-suite failure classification

- `app/tests/unit/test_astrology_runtime_reference_guard.py::test_natal_flow_does_not_use_legacy_reference_service_or_symbols` fails on existing `natal_fact_graph_builder.py` true/mean node symbols.
- `tests/architecture/test_astrology_doctrine_governance_guardrails.py::test_rule_marker_surfaces_are_declared_in_doctrine_governance` fails on existing `natal_fact_graph_builder.py` and `basic_natal_contracts.py` surfaces.
- These files were not modified by CS-417; targeted story validations pass.

## Commands skipped or blocked

- App server startup: not launched; this backend domain validator story has no route or frontend runtime surface, and targeted/runtime tests covered the affected behavior.

## DRY / No Legacy evidence

- Canonical owner reused: `BasicNatalReadingPlan` from `app.domain.astrology.interpretation.basic_natal_reading_plan`.
- No frontend, migration, schema, quota, or public route changes.
- No compatibility shim, alias, duplicate active path, or fallback padding (`fallback = response.sections[0]`) introduced.
- `RG-166` already exists and remains the durable invariant for Basic plan-backed validation.

## Evidence artifacts

- `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/evidence/basic-validator-before.json`
- `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/evidence/basic-validator-after.json`
- `_condamad/stories/CS-417-valider-reparer-narrative-basic-natal/evidence/validation.txt`

## Final worktree status

- Initial dirty file observed: `_condamad/run-state.json`.
- Final dirty files are scoped to CS-417 plus pre-existing `_condamad/run-state.json`.

## Diff review

- `git diff --check -- <story paths>`: PASS; only line-ending warnings on existing markdown files.
- `git diff --stat -- <story paths>` reviewed; no frontend, migration, DB schema, quota owner or route churn.

## Remaining risks

- Full fast backend suite has unrelated guard failures listed above.

## Suggested reviewer focus

- Confirm only the unrelated full-suite governance failures if closing broader release health.
