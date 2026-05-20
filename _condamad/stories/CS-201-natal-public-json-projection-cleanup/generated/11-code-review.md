# CONDAMAD Code Review

## Review Target

- Story: `CS-201-natal-public-json-projection-cleanup`
- Capsule: `_condamad/stories/CS-201-natal-public-json-projection-cleanup`
- Review iteration: 4
- Reviewer result: CLEAN

## Inputs Reviewed

- `AGENTS.md`
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md`
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/generated/03-acceptance-traceability.md`
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/generated/06-validation-plan.md`
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/generated/07-no-legacy-dry-guardrails.md`
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/generated/10-final-evidence.md`
- `_condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/*`
- `_condamad/stories/regression-guardrails.md`
- `git status --short`, `git diff --stat`, `git diff --check`
- Fresh targeted tests, lint, OpenAPI import and RG-128 scans run on 2026-05-20.
- Changed application and test files.

## Diff Summary

- `backend/app/services/chart/json_builder.py`: adds projection-only `astral_points` and `signs_runtime`; converges condition profiles, condition signals, advanced conditions and dominant planets to the public shapes from the initial brief; keeps no-time neutralization.
- `backend/app/tests/unit/test_chart_json_builder.py`: covers direct maps, signal-list maps, public advanced/dominance field names, empty advanced blocks and nested no-time neutralization.
- `backend/app/tests/unit/test_chart_result_service.py`: covers old persisted payload gaps without backfill.
- `backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py` and CS-200 golden evidence: align the locked public projection summary with the corrected dominant planet public field names.
- CONDAMAD evidence and story status updated.

## Findings

No actionable findings found in the fresh review pass.

## Prior Review Findings

| Finding | Source layers | Decision | Resolution |
|---|---|---|---|
| Public map contract was not implemented for `planet_condition_profiles` and `planet_condition_signals`. | Story conformance, source closure | Accepted | Serializers now return direct maps keyed by planet; empty computed maps return `{}`; tests and snapshots updated. |
| Initial brief target shapes were not implemented for `planet_condition_signals`, `advanced_conditions` and `dominant_planets`. | User brief conformance, public payload stability | Accepted | `planet_condition_signals` now maps planet code to signal lists; `advanced_conditions` exposes `planet_code`, `condition_type`, `score_effect`, `axis_weights`, `evidence`; `dominant_planets` exposes `_code` fields and `planets[*].planet_code/score`. Tests, snapshots and validation evidence updated. |
| Legacy alias scan evidence was broad/contradictory. | Story conformance, technical risk, source closure | Accepted | `public-json-validation.md` now records exact hit classification for each `sect_code` / `chart_sect_code` hit. |
| Python validation environment was not evidenced. | Story conformance, technical risk | Accepted | Final evidence commands now include explicit `.\.venv\Scripts\Activate.ps1; ...` prefixes. |
| Snapshot evidence contained prose placeholders. | Technical risk | Accepted | JSON snapshots now contain JSON values only; explanatory labels remain in markdown audit/validation. |
| Evidence/generated files were untracked. | Source closure | Dismissed for closure | The files are present in the worktree and listed by final `git status --short`; no commit/push was requested, so they remain untracked until the user chooses staging/commit. |
| `houses[*].sign` remains historical. | Source closure | Dismissed as out of scope | CS-201 forbids public field removal/rename without user decision; validation now classifies this retained field explicitly. |

## Acceptance Audit

All AC1-AC14 have implementation and validation evidence in `generated/03-acceptance-traceability.md` and `generated/10-final-evidence.md`.

Key checks:

- AC1/AC2: CS-197 sect and CS-198 planet sect condition object contracts remain asserted.
- AC3: condition profiles are direct maps, condition signals are direct maps of signal lists, advanced conditions and dominants use the public names from the initial brief, and empty maps are `{}`.
- AC4/AC7: `astral_points` and `signs_runtime` are projected from `NatalResult`; nested `house` fields are neutralized in no-time mode.
- AC8: old persisted payload gaps are not backfilled.
- AC9/AC12: OpenAPI/app import still succeeds and no adjacent frontend/API/DB/migration/seed surfaces changed.
- AC13/AC14: evidence records no-change score and no-change astrology facts.

## Validation Audit

Python commands were run after venv activation. Recorded passing commands include:

- targeted projection/persistence/natal/golden tests: 36 passed;
- domain regression tests: 23 passed;
- `ruff format .`;
- `ruff check .`;
- FastAPI app import/OpenAPI generation;
- story validation and strict lint;
- CS-201 scans and diff checks.

No required validation remains skipped.

## DRY / No Legacy Audit

- No forbidden projection engine imports in `json_builder.py`.
- No public sect compatibility aliases were added.
- `sect_code` / `chart_sect_code` hits are canonical runtime/reference internals and are classified in `public-json-validation.md`.
- No frontend/API/DB/migration/seed changes were made.
- No fallback or recalculation path was added for missing persisted facts.

## Commands Run By Reviewer

- `git status --short`
- `git diff --stat`
- `git diff --check`
- `.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py`
- `.\.venv\Scripts\Activate.ps1; ruff check .`
- `.\.venv\Scripts\Activate.ps1; ruff format --check .`
- `.\.venv\Scripts\Activate.ps1; python -c "from backend.app.main import app; app.openapi()"`
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md`
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts _condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md`
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py _condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md`
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-201-natal-public-json-projection-cleanup/00-story.md`
- `.\.venv\Scripts\Activate.ps1; python -m json.tool _condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-before.json`
- `.\.venv\Scripts\Activate.ps1; python -m json.tool _condamad/stories/CS-201-natal-public-json-projection-cleanup/evidence/public-json-after.json`
- `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-code-review/scripts/condamad_review_validate.py .agents/skills/condamad-code-review`
- Targeted `rg` scans from CS-201 validation plan

## Residual Risks

- None identified. CONDAMAD evidence/generated files are story-scoped and must be included in the closure commit.

## Verdict

CLEAN
