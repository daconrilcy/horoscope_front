# CONDAMAD Code Review

## Review target

- Story: `CS-199-advanced-sect-scoring-integration`
- Capsule: `_condamad/stories/CS-199-advanced-sect-scoring-integration`
- Review/fix iterations: 2 review rounds, 2 fix rounds.

## Inputs reviewed

- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- Current `git diff`
- Targeted tests, full pytest, Ruff and static scans

## Diff summary

- `AdvancedConditionEngine` now passes the runtime reference into `HayzCalculator`.
- `HayzCalculator` now derives `out_of_sect` from `PlanetSectCondition.is_out_of_sect` and uses `PlanetSectCondition.is_in_sect` only as the hayz sect precondition.
- Hayz non-sect factors remain evaluated inside `advanced_conditions` through runtime accidental rules, with horizon rules constrained to the same runtime system.
- Downstream condition profile, dominance and interpretation adapter tests include no-recalculation guards.
- The stale seed-count validation blocker was corrected in `backend/app/tests/unit/test_dignity_reference_seed.py`.
- Capsule evidence records before/after snapshots, required case coverage, scans, validation and final review.

## Findings

### CR-1 High - Hayz ownership leaked into dignity calculator

- Bucket: patch
- Source layer: technical risk review
- Evidence: an earlier implementation imported `AccidentalDignityCalculator` from `HayzCalculator` and used a newly added `hayz_non_sect_factors_match` helper.
- Impact: duplicated hayz ownership outside `advanced_conditions`, contrary to CS-199.
- Fix applied: removed the helper from `AccidentalDignityCalculator`; moved non-sect hayz factor evaluation into `HayzCalculator` using `runtime_reference`.
- Status: RESOLVED.

### CR-2 High - Required before/after snapshot evidence was incomplete

- Bucket: patch
- Source layer: story conformance and technical risk review
- Evidence: before/after snapshots initially lacked `planet_condition_profiles`, `planet_condition_signals`, `dominant_planets`, `interpretation_adapter` and later lacked explicit coverage for all brief-required cases.
- Impact: AC12 and RG-119..RG-126 evidence was incomplete.
- Fix applied: regenerated snapshot artifacts with all required sections, added the missing night-diurnal out-of-sect and incomplete-hayz coverage, and validated both JSON files.
- Status: RESOLVED.

### CR-3 Medium - Evidence was stale and used forbidden limited-pass wording

- Bucket: patch
- Source layer: story conformance and technical risk review
- Evidence: final evidence recorded `PASS_WITH_LIMITATIONS` and referred to accidental `hayz` breakdown after the implementation moved to runtime non-sect factor evaluation.
- Impact: closure artifact contradicted the story and current code.
- Fix applied: updated validation and final evidence to the final code state and removed limited-pass wording.
- Status: RESOLVED.

### CR-4 High - Full pytest validation failed on stale seed-count guard

- Bucket: patch
- Source layer: validation
- Evidence: `pytest -q` and isolated `pytest -q backend/app/tests/unit/test_dignity_reference_seed.py::test_reference_seed_populates_astral_dignity_tables` failed because the canonical seed data contains 42 accidental dignity rules while the test expected 41.
- Impact: repository-level final validation was not clean, so CS-199 could not be marked `done`.
- Fix applied: aligned the test expectation with the canonical 42-rule seed and reran full validation.
- Status: RESOLVED.

## Acceptance audit

- AC1: PASS. `out_of_sect` is emitted from `PlanetSectCondition.is_out_of_sect`.
- AC2: PASS. Hayz is gated by `PlanetSectCondition.is_in_sect`.
- AC3: PASS. Hayz still requires non-sect runtime factors and is not reduced to `in_sect`.
- AC4: PASS. Missing `PlanetSectCondition` fails explicitly.
- AC5: PASS. Condition profiles consume facts and do not import/recalculate sect.
- AC6: PASS. Dominance consumes profiles/advanced conditions and does not import/recalculate sect.
- AC7: PASS. Interpretation adapter consumes semantic facts and does not import/recalculate sect.
- AC8: PASS. Equivalent score outputs remain stable in snapshots; the incomplete-hayz correction is explicitly documented.
- AC9: PASS. Score deltas are documented.
- AC10: PASS. Forbidden sect patterns remain absent or classified as runtime/test terminology.
- AC11: PASS. Public JSON shape remains CS-197/CS-198 compatible.
- AC12: PASS. Persistent evidence files are complete, including required case coverage.

## Validation audit

- Targeted CS-199 tests: PASS, 50 passed.
- Ruff format/check: PASS.
- Full repository tests: PASS, 2765 passed, 1 skipped, 1177 deselected.
- Static scans: PASS; zero hits for downstream sect calculators, local sect constants and local horizon tuples.
- Guardrail `RG-126`: PASS.

## DRY / No Legacy audit

- No compatibility wrapper, alias, local sect constants, downstream sect calculator imports or public legacy sect fields were introduced.
- Existing `sect_code` / `chart_sect_code` hits are runtime-reference and test terminology.
- Existing `prompt_hint` hits are runtime-backed signal fields, not LLM ownership.
- No frontend, API, DB, migration, seed JSON, OpenAPI or dependency file was changed.

## Commands run by reviewer

| Command | Result |
|---|---|
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/tests/unit/domain/astrology/test_hayz_calculator.py backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_dignity_reference_seed.py::test_reference_seed_populates_astral_dignity_tables` | PASS, 50 passed |
| `.\.venv\Scripts\Activate.ps1; ruff check --fix backend/app/tests/unit/test_dignity_reference_seed.py; ruff format .; ruff check .` | PASS |
| `.\.venv\Scripts\Activate.ps1; pytest -q` | PASS, 2766 passed, 1 skipped, 1177 deselected |
| `rg` guard scans listed in `evidence/advanced-sect-validation.md` | PASS or classified expected hits |

## Residual risks

Aucun risque restant identifie.

## Verdict

CLEAN.
