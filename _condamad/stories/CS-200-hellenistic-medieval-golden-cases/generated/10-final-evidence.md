# Final Evidence

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: `CS-200-hellenistic-medieval-golden-cases`
- Source story: `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/00-story.md`
- Capsule path: `_condamad/stories/CS-200-hellenistic-medieval-golden-cases`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial `git status --short`: story-scoped dirty files were present before this review/fix session.
- Pre-existing dirty files: `_condamad/stories/story-status.md`, CS-200 generated/evidence files, `backend/tests/unit/domain/astrology/fixtures/`, `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`.
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes, missing required generated files were created.
- Story sufficiency gate: PASS; finite G1-G12 scope, persistent evidence and deterministic guards are defined.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Source story exists. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created for implementation. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC12 mapped and completed. |
| `generated/04-target-files.md` | yes | yes | PASS | Target map created. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Commands listed. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Story-specific guardrails created. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Completed. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | G1/G2 in `test_traditional_golden_cases.py` and snapshot. | Golden pytest PASS. | PASS | Day/night chart sect locked. |
| AC2 | G3-G6 runtime dignity cases. | Golden pytest PASS. | PASS | In-sect/out-of-sect locked. |
| AC3 | G7/G8 advanced condition, profile and signal cases. | Golden pytest PASS. | PASS | Hayz requires non-sect factors and propagates to profile/signals only when complete. |
| AC4 | G9 rejoicing case. | Golden pytest PASS. | PASS | `planetary_joy` profile contribution locked. |
| AC5 | G10 Mercury case. | Golden pytest PASS. | PASS | Mercury common/variable runtime classification locked. |
| AC6 | G11 essential dignity case. | Golden pytest PASS. | PASS | Sun domicile and score axes locked. |
| AC7 | G12 integrated pipeline case. | Golden pytest PASS. | PASS | NatalResult and JSON propagation covered. |
| AC8 | `golden_snapshot.py`, before/after JSON. | `python -m json.tool` PASS. | PASS | Snapshot compacted after review fix. |
| AC9 | Runtime-backed helpers, shared test factory `complete_reference_with_planet_sect_rules`, no production doctrine edits. | Scans PASS with classified hits. | PASS | Duplicated local sect-rule fixture converged during review fix. |
| AC10 | Diff limited to backend tests, shared test factory, story evidence/capsule files and status registry. | Diff review PASS. | PASS | No forbidden path/dependency changes. |
| AC11 | G12 JSON assertions and existing JSON tests. | `test_chart_json_builder.py` PASS. | PASS | CS-197/CS-198 public projection stable. |
| AC12 | Evidence directory, index, before, after, validation. | `Test-Path` and case-ID `rg` PASS. | PASS | G1-G12 documented. |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | added | Targeted golden assertions G1-G12. | AC1-AC12 |
| `backend/tests/unit/domain/astrology/fixtures/__init__.py` | added | Test fixture package marker. | AC1-AC12 |
| `backend/tests/unit/domain/astrology/fixtures/golden_snapshot.py` | added | Snapshot normalization. | AC8 |
| `backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py` | added | Runtime-backed case builders and curated summaries. | AC1-AC12 |
| `backend/tests/factories/astrology_runtime_reference_factory.py` | modified | Shared runtime fixture for planet sect rules, avoiding duplicated test-local doctrine setup. | AC9 |
| `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` | modified | Reuses shared runtime fixture instead of a local duplicate. | AC9 |
| `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-index.md` | added | Case provenance and invariants. | AC12 |
| `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-before.json` | added | Baseline absence marker. | AC8, AC12 |
| `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-after.json` | added | Curated runtime snapshot. | AC1-AC12 |
| `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-validation.md` | added | Validation and scan classification. | AC8-AC12 |
| `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/generated/01-execution-brief.md` | added | Capsule execution brief. | All |
| `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/generated/03-acceptance-traceability.md` | added | AC traceability. | All |
| `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/generated/04-target-files.md` | added | Target file map. | All |
| `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/generated/06-validation-plan.md` | added | Validation plan. | All |
| `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/generated/07-no-legacy-dry-guardrails.md` | added | No Legacy / DRY guardrails. | AC9, AC10 |
| `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/generated/10-final-evidence.md` | added | Final implementation evidence. | All |
| `_condamad/stories/CS-200-hellenistic-medieval-golden-cases/generated/11-code-review.md` | added | Final review evidence after fix loop. | All |
| `_condamad/stories/story-status.md` | modified | Marks CS-200 as `done` after clean review. | All |

## Files deleted

None.

## Tests added or updated

- Added `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`.
- Added test helpers under `backend/tests/unit/domain/astrology/fixtures/`.
- Updated `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` to reuse the shared planet sect runtime fixture.
- Expanded G7/G8 golden assertions and snapshot evidence for hayz profile/signals propagation.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\\.venv\\Scripts\\Activate.ps1; ruff format .` | repo root | PASS | 0 | Final run: 1477 files left unchanged. |
| `.\\.venv\\Scripts\\Activate.ps1; ruff check .` | repo root | PASS | 0 | All checks passed. |
| `.\\.venv\\Scripts\\Activate.ps1; ruff check backend/tests/factories/astrology_runtime_reference_factory.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py` | repo root | PASS | 0 | Targeted lint for review fix passed after import-order correction. |
| `.\\.venv\\Scripts\\Activate.ps1; ruff check backend/tests/unit/domain/astrology/test_traditional_golden_cases.py backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py` | repo root | PASS | 0 | Targeted lint for G7/G8 follow-up fix passed. |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_traditional_golden_cases.py` | repo root | PASS | 0 | 9 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py` | repo root | PASS | 0 | 5 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` | repo root | PASS | 0 | 4 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py` | repo root | PASS | 0 | 6 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_hayz_calculator.py` | repo root | PASS | 0 | 2 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py` | repo root | PASS | 0 | 4 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py` | repo root | PASS | 0 | 7 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py` | repo root | PASS | 0 | 2 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py` | repo root | PASS | 0 | 1 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/app/tests/unit/test_chart_json_builder.py` | repo root | PASS | 0 | 17 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; pytest -q backend/app/tests/unit/test_chart_result_service.py` | repo root | PASS | 0 | 7 passed. |
| `.\\.venv\\Scripts\\Activate.ps1; python -m json.tool ...golden-cases-before.json` | repo root | PASS | 0 | Valid JSON. |
| `.\\.venv\\Scripts\\Activate.ps1; python -m json.tool ...golden-cases-after.json` | repo root | PASS | 0 | Valid JSON. |
| `git diff --check` | repo root | PASS | 0 | No whitespace/conflict marker errors. |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Local app server startup | no | Story is test/evidence-only and changed no app runtime path. | Low. | Targeted backend tests, JSON projection tests and chart result tests passed. |

## DRY / No Legacy evidence

- No production code changed.
- No frontend, API, migration, seed, DB model, dependency or LLM file changed.
- No local doctrine constants found.
- Planet sect runtime fixture setup is centralized in `complete_reference_with_planet_sect_rules`; CS-200 and the existing dignity scoring tests reuse the same helper.
- G7 now proves `hayz` reaches the enriched condition profile and governed condition signal output; G8 proves `in_sect` alone does not add the advanced `hayz` profile contribution.
- `SectCalculator` / `PlanetSectConditionCalculator` were not imported into downstream condition, advanced, dominance, adapter or JSON builder modules.
- Scan hits for `sect_code` / `chart_sect_code` are existing canonical runtime reference fields or explicit test fixture input keys, not public JSON aliases.
- `prompt_hint` scan hits are existing CS-193 signal contract fields, not prompt/LLM dependencies.

## Diff review

- Scope review: expected additions are backend tests, story capsule files and story evidence.
- Production diff: none.
- Snapshot review finding fixed: G12 public JSON snapshot was reduced to contract fields instead of full downstream payloads.
- Follow-up brief verification fixed: G7/G8 now prove hayz profile/signals propagation boundaries.

## Final worktree status

Final `git status --short`:

```text
 M _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-after.json
 M _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-index.md
 M _condamad/stories/CS-200-hellenistic-medieval-golden-cases/evidence/golden-cases-validation.md
 M _condamad/stories/CS-200-hellenistic-medieval-golden-cases/generated/03-acceptance-traceability.md
 M _condamad/stories/CS-200-hellenistic-medieval-golden-cases/generated/10-final-evidence.md
 M _condamad/stories/CS-200-hellenistic-medieval-golden-cases/generated/11-code-review.md
 M backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py
 M backend/tests/unit/domain/astrology/test_traditional_golden_cases.py
```

## Remaining risks

Aucun risque restant identifie.

## Suggested reviewer focus

Review that G7/G8 lock hayz propagation without introducing a local doctrine engine, and that the G12 curated projection remains compact while covering dominance, interpretation adapter and public JSON contracts.
