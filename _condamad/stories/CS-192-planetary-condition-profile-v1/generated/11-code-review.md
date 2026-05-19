<!-- Revue CONDAMAD CS-192. -->

# CONDAMAD Code Review

## Review target

- Story: `CS-192-planetary-condition-profile-v1`
- Capsule: `_condamad/stories/CS-192-planetary-condition-profile-v1`
- Closure class: `not applicable`; story source is an architecture decision,
  not an audit finding.

## Inputs reviewed

- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- Current git diff and untracked story files.

## Diff summary

CS-192 adds condition axes to dignity score weights, transports those axes into
the runtime reference, creates the pure domain package
`backend/app/domain/astrology/condition`, integrates `condition_profiles` into
`NatalResult`, and projects `planet_condition_profiles` in
`build_chart_json`. The diff also adds targeted backend tests, migration
coverage, RG-119 guard evidence, story evidence, and the registry row.

## Findings

No remaining actionable findings after the documentation and snapshot coherence
fixes from the final review pass.

Previously fixed issues verified during this review:

- Public `planet_condition_profiles.planets.<code>` now includes the required
  per-planet metadata and profile fields.
- `AstrologyRuntimeReferenceMapper` now fails when the five condition axes are
  absent instead of silently neutralizing missing runtime data.
- `DignityScoreWeightReferenceData` no longer exposes `visibility_weight` inside
  `domain/astrology`; the infra mapper translates DB columns to
  `condition_visibility` and sibling condition-axis attributes, preserving the
  existing astrology/prediction boundary guard.
- The story status and task checkboxes in `00-story.md` now match
  `story-status.md`.
- The before/after snapshots now include the surrounding chart payload fields
  used as stability evidence, and the condition profile breakdown includes both
  essential and accidental contributions consistently with the source
  dignities.

## Acceptance audit

| AC | Review result |
|---|---|
| AC1 | PASS - migration and SQLAlchemy models expose the five axes with neutral defaults. |
| AC2 | PASS - runtime repository and mapper transport the axes under typed contracts. |
| AC3 | PASS - condition contracts are immutable dataclasses without narrative payloads. |
| AC4 | PASS - service derives axes from `PlanetDignityResult` plus runtime weights. |
| AC5 | PASS - `NatalResult.condition_profiles` is present and `dignities` remains intact. |
| AC6 | PASS - JSON projection serializes precomputed profiles without recalculating axes. |
| AC7 | PASS - RG-119 architecture guard covers forbidden imports, mappings, LLM and dedicated table. |
| AC8 | PASS with scoped lint limitation - story-target lint passes; global lint fails outside CS-192 on skill templates. |
| AC9 | PASS - deterministic ranking covered by tests. |

## Validation audit

Commands run from repository root after `.\.venv\Scripts\Activate.ps1` during
the fresh review requested on 2026-05-19:

| Command | Result | Evidence |
|---|---|---|
| `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py backend/app/tests/integration/test_reference_data_migrations.py` | PASS | 43 passed, 5 deselected |
| `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py backend/app/tests/integration/test_reference_data_migrations.py backend/app/tests/unit/test_astrology_prediction_boundary.py::test_astrology_domain_does_not_carry_product_symbols` | PASS | 44 passed, 5 deselected |
| `pytest -q` | PASS | 2693 passed, 1 skipped, 1177 deselected |
| `ruff check <fichiers CS-192>` | PASS | All checks passed |
| `ruff format --check <fichiers CS-192>` | PASS | 19 files already formatted |
| `ruff check backend _condamad/stories/CS-192-planetary-condition-profile-v1/00-story.md` | PASS | All checks passed |
| `git diff --check` | PASS | no whitespace/conflict issues |
| `ruff check .` | FAIL outside scope | 28 pre-existing errors under `.agent/.agents/.claude/.gemini` skill templates |

RG-119 scans:

| Scan | Result |
|---|---|
| Forbidden DB/API/services/prediction imports under `backend/app/domain/astrology/condition` | PASS, zero hit |
| Forbidden LLM/prompt/interpretation terms under `backend/app/domain/astrology/condition` | PASS, zero hit |
| Forbidden condition mappings and `astral_chart_planet_condition_profiles` under backend code/migrations/tests | PASS, zero hit |

## DRY / No Legacy audit

- No DB, API, services, prediction or LLM import is present in the condition
  domain package.
- No forbidden product symbol `visibility_weight` remains under
  `backend/app/domain/astrology`.
- No dedicated `astral_chart_planet_condition_profiles` table or model is
  introduced.
- No compatibility wrapper, alias, fallback path, or duplicate condition engine
  is present in the reviewed implementation.
- The serializer projects `condition_profiles` and does not recalculate the
  ranking or axes.

## Residual risks

- `ruff check .` remains blocked outside CS-192 by pre-existing placeholder
  skill templates under `.agent/.agents/.claude/.gemini`; story-target lint,
  formatting checks, tests and RG-119 scans pass.

## Verdict

CLEAN
