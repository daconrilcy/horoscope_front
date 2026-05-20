# CONDAMAD Code Review

Date: 2026-05-20

## Review target

- Story: `CS-200-hellenistic-medieval-golden-cases`
- Capsule: `_condamad/stories/CS-200-hellenistic-medieval-golden-cases`
- Source type: brief, not audit-sourced.
- Closure class: full-closure for the finite G1-G12 golden-case scope.

## Inputs reviewed

- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md` (`RG-108`, `RG-112`, `RG-118` through `RG-127`)
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- `backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py`
- `backend/tests/unit/domain/astrology/fixtures/golden_snapshot.py`
- `backend/tests/factories/astrology_runtime_reference_factory.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- Persistent evidence under `evidence/`

## Diff summary

- Added the CS-200 golden-case test suite and compact evidence snapshots.
- Added test-local snapshot and traditional golden-case helpers.
- Updated the shared astrology runtime reference test factory to expose one planet sect rule fixture helper.
- Updated the existing dignity scoring test to consume that shared helper.
- Updated story evidence, review evidence and `story-status.md`.
- No production, frontend, API, migration, seed, dependency or LLM files changed.

## Review layers

- Subagents used: no. Review was performed in the main session.
- Diff integrity: CLEAN after review fixes.
- Acceptance audit: CLEAN.
- Validation audit: CLEAN.
- DRY / No Legacy audit: CLEAN after review fixes.
- Edge/security/data audit: CLEAN; test/evidence-only story with no runtime or data-access changes.

## Findings

### CR-1 Major - G12 snapshot was too broad

- Bucket: patch
- Location: `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-after.json`
- Source layer: acceptance / validation
- Evidence: the initial G12 snapshot captured full downstream public JSON payloads for `dominant_planets` and `interpretation_adapter`, exceeding AC8's compact curated snapshot policy.
- Impact: snapshot drift risk and harder maintenance for a golden suite intended to protect only contract fields.
- Suggested fix: keep only contract-level JSON fields for sect, first planet sect condition, advanced condition codes, dominance identifiers and adapter signal/pattern codes.
- Resolution: fixed before this final review; targeted golden test and JSON validation passed.

### CR-2 Medium - Planet sect runtime fixture was duplicated

- Bucket: patch
- Location: `backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py`
- Source layer: DRY / no-legacy
- Evidence: CS-200 redefined the same planet-to-sect runtime rule table already present in `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`.
- Impact: future fixture drift could make two tests disagree about runtime sect rules while both claim to be canonical.
- Suggested fix: move the setup into a shared test factory helper and consume it from both test modules.
- Resolution: fixed by adding `complete_reference_with_planet_sect_rules()` in `backend/tests/factories/astrology_runtime_reference_factory.py` and reusing it from both test surfaces.

### CR-3 Low - Final evidence preflight was stale

- Bucket: patch
- Location: `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/generated/10-final-evidence.md`
- Source layer: validation
- Evidence: final evidence claimed the initial worktree was clean, but this review/fix session began with story-scoped dirty files already present.
- Impact: reviewer could not distinguish pre-existing story implementation files from review-fix changes.
- Suggested fix: update preflight and file list evidence to reflect the real closure session.
- Resolution: fixed in final evidence.

### CR-4 Medium - G7 did not lock hayz profile and signal propagation

- Bucket: patch
- Location: `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`
- Source layer: acceptance
- Evidence: the brief requires G7 to prove hayz reaches condition profiles and governed signals when runtime thresholds match; the prior test only asserted the advanced condition code.
- Impact: a regression could preserve `advanced_conditions.hayz` while dropping the profile/signals propagation expected by CS-200.
- Suggested fix: include G7 profile breakdown and condition signal evidence in the curated snapshot, assert advanced `hayz` profile contribution, and assert G8 does not gain that contribution when only `in_sect` is true.
- Resolution: fixed in follow-up verification; targeted pytest, JSON validation and lint passed.

## Acceptance audit

| AC | Status | Evidence |
|---|---|---|
| AC1 | PASS | G1/G2 assert day/night `dignities.sect` fields and snapshot entries exist. |
| AC2 | PASS | G3-G6 assert `PlanetSectCondition` and `out_of_sect` propagation. |
| AC3 | PASS | G7/G8 distinguish complete hayz from in-sect-only, including profile/signals propagation for G7 and no advanced hayz profile contribution for G8. |
| AC4 | PASS | G9 asserts `planetary_joy` accidental and profile evidence. |
| AC5 | PASS | G10 asserts Mercury common/variable runtime classification. |
| AC6 | PASS | G11 asserts Sun domicile and score axes. |
| AC7 | PASS | G12 exercises `build_natal_result`, downstream surfaces and `build_chart_json`. |
| AC8 | PASS | Snapshot helper normalizes compact JSON; before/after JSON validates. |
| AC9 | PASS | Shared test factory prevents duplicate sect-rule fixture setup; scans classified. |
| AC10 | PASS | Diff remains test/evidence/governance scoped; forbidden runtime surfaces untouched. |
| AC11 | PASS | G12 JSON assertions and existing chart JSON tests passed. |
| AC12 | PASS | Evidence files exist and document G1-G12. |

## Validation audit

Python commands were run after `.\\.venv\\Scripts\\Activate.ps1`.

- `pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`: PASS, 9 passed.
- `pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py`: PASS, 5 passed.
- `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`: PASS, 4 passed.
- `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`: PASS, 6 passed.
- `pytest -q backend/tests/unit/domain/astrology/test_hayz_calculator.py`: PASS, 2 passed.
- `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`: PASS, 4 passed.
- `pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py`: PASS, 7 passed.
- `pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py`: PASS, 2 passed.
- `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`: PASS, 1 passed.
- `pytest -q backend/app/tests/unit/test_chart_json_builder.py`: PASS, 17 passed.
- `pytest -q backend/app/tests/unit/test_chart_result_service.py`: PASS, 7 passed.
- `ruff format .`: PASS, 1477 files left unchanged.
- `ruff check .`: PASS, all checks passed.
- `python -m json.tool ...golden-cases-before.json`: PASS.
- `python -m json.tool ...golden-cases-after.json`: PASS.
- `git diff --check`: PASS.

## DRY / No Legacy audit

- No production doctrine constants were added.
- No downstream imports of `SectCalculator` or `PlanetSectConditionCalculator` were added.
- Legacy sect-name scan hits are existing canonical runtime/test keys, not public JSON aliases.
- `prompt_hint` scan hits are existing CS-193 signal contract fields, not LLM prompt dependencies.
- The duplicated planet sect runtime fixture setup found in review was converged to a shared test factory helper.

## Commands run by reviewer

- `git status --short`
- `git diff --stat`
- `git diff --check`
- Targeted pytest, ruff, JSON validation and `rg` scans listed in `generated/10-final-evidence.md`.

## Residual risks

Aucun risque restant identifie.

## Verdict

CLEAN
