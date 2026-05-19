# CONDAMAD Code Review

## Review target

- Story: `CS-193-planetary-condition-signals`
- Capsule: `_condamad/stories/CS-193-planetary-condition-signals`
- Review mode: main review plus three read-only subagent layers.

## Inputs reviewed

- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `evidence/**`
- `_condamad/stories/regression-guardrails.md`
- `git status --short`, `git diff --stat`, targeted `git diff`
- Validation command outputs from the main session

## Diff summary

CS-193 adds a DB-backed, runtime-loaded condition signal reference table,
immutable runtime and domain contracts, a pure `PlanetConditionSignalBuilder`,
`NatalResult.condition_signals`, and public JSON projection
`planet_condition_signals`. No frontend, prompt, LLM adapter, route or status
code was changed.

## Review layers

- Story Conformance Reviewer: found scope/evidence issues and the invalid axis
  risk.
- Technical Risk Reviewer: found validation evidence gaps, invalid axis risk
  and CS-194 worktree pollution risk.
- Source Finding Closure Reviewer: found invalid axis risk and non-final
  evidence; confirmed no recalculation in `json_builder.py` and no local
  threshold hits.
- Main review: accepted the invalid axis, evidence and global Ruff findings;
  classified CS-194 files as pre-existing out-of-scope worktree state.

## Findings

No open actionable finding remains for CS-193.

### Resolved CR-1 High - Runtime allowed `expression_quality`

- Bucket: patch
- Location: `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- Source layer: technical-risk, story-conformance, source-closure, main review
- Evidence: `_CONDITION_SIGNAL_AXES` previously allowed `expression_quality`,
  absent from `PlanetConditionProfile`; builder reads runtime axes with
  `getattr(profile, axis)`.
- Fix: removed `expression_quality` from allowed condition signal axes and added
  a repository integrity test rejecting `condition_axis="expression_quality"`.
- Validation: runtime repository/guard tests pass with 22 tests.

### Resolved CR-2 High - Final evidence and AC traceability were pending

- Bucket: patch
- Location: `generated/10-final-evidence.md`,
  `generated/03-acceptance-traceability.md`
- Source layer: story-conformance, validation, main review
- Evidence: previous files had `IN_PROGRESS`, `Ready for review: no`, and
  AC1-AC10 as `Pending`.
- Fix: replaced both files with command-backed evidence and AC mapping.
- Validation: final command matrix is recorded in `generated/10-final-evidence.md`.

### Resolved CR-3 Medium - Before/after evidence did not show contract stability clearly

- Bucket: patch
- Location: `evidence/natal-condition-signals-before.json`,
  `evidence/natal-condition-signals-after.json`
- Source layer: story-conformance, main review
- Evidence: previous snapshots listed only reduced shapes.
- Fix: added explicit contract diff, stable existing section list and validation
  references showing only `condition_signals` and `planet_condition_signals`
  were added.
- Validation: chart JSON/result tests pass with 20 tests.

### Resolved CR-4 High - Repository-level Ruff validation was not clean

- Bucket: patch
- Location: `ruff.toml`
- Source layer: validation, main review
- Evidence: `ruff check .` previously failed on tracked hidden skill/template
  bundles under `.agent`, `.agents`, `.claude`, `.gemini` and `.discord`, which
  blocked a clean story verdict under the repository checklist.
- Fix: added root Ruff configuration that excludes generated hidden tool
  bundles from repo-level application lint while preserving Python 3.13 and
  `E/F/I` rules.
- Validation: `ruff check .`, `ruff format --check .` and `ruff format .` now
  pass.

## Acceptance audit

AC1-AC10 are satisfied by implementation, passing tests, repository-level Ruff
validation and persisted guard evidence.

Worktree note: `_condamad/stories/CS-194-dominant-planets-engine/**` remains
visible as pre-existing out-of-scope work and is not part of the CS-193 review
target.

## Validation audit

- Unit and integration tests for changed backend surfaces pass.
- `pytest -q backend/app/tests/integration/test_reference_data_migrations.py`
  is deselected by marker policy; the executable migration proof is
  `pytest --long -q backend/app/tests/integration/test_reference_data_migrations.py`.
- Scoped backend lint and format checks pass.
- Repository-level `ruff check .`, `ruff format --check .` and `ruff format .`
  pass after excluding generated hidden tool bundles through `ruff.toml`.

## DRY / No Legacy audit

- No duplicate signal engine introduced.
- No DB/API/service/prediction imports in `backend/app/domain/astrology/condition/**`.
- No local signal thresholds or prompt/LLM/narration symbols in condition domain.
- JSON builder is projection-only.
- No frontend surface changed.

## Commands run by reviewer

All Python commands were run after `.\\.venv\\Scripts\\Activate.ps1`.

- `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_signal_builder.py backend/tests/unit/domain/astrology/test_natal_result_contract.py` -> 5 passed
- `pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` -> 20 passed
- `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py` -> 22 passed
- `pytest --long -q backend/app/tests/integration/test_reference_data_migrations.py` -> 5 passed
- `ruff format --check backend/app backend/tests` -> PASS
- `ruff check backend/app backend/tests` -> PASS
- `ruff check .` -> PASS
- `ruff format --check .` -> PASS, 1435 files already formatted
- `ruff format .` -> PASS, 1435 files left unchanged
- `git diff --check` -> PASS, CRLF warnings only
- Three RG-120 forbidden scans -> zero hits
- Projection scan -> expected integration/projection hits only
- Backend app import -> `horoscope-backend`

## Residual risks

- Aucun risque restant identifie pour CS-193.

## Verdict

CLEAN
