# Final Evidence - CS-197-sect-audit-explicit-contract

## Story status

- Validation outcome: PASS
- Review outcome: CLEAN
- Story key: CS-197-sect-audit-explicit-contract
- Source story: `_condamad/stories/CS-197-sect-audit-explicit-contract/00-story.md`
- Capsule path: `_condamad/stories/CS-197-sect-audit-explicit-contract/`

## Preflight

- Repository root: `C:\dev\horoscope_front`
- Initial `git status --short`: clean
- Pre-existing dirty files: none
- AGENTS.md files considered: `AGENTS.md`
- Capsule generated: yes
- Story sufficiency gate: pass

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | source story present |
| `generated/01-execution-brief.md` | yes | yes | PASS | story-specific |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | AC1-AC8 covered |
| `generated/04-target-files.md` | yes | yes | PASS | scoped target map |
| `generated/06-validation-plan.md` | yes | yes | PASS | executable commands listed |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | story-specific |
| `generated/10-final-evidence.md` | yes | yes | PASS | completed |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | `ChartSectResult`; `SectCalculator.calculate()` returns explicit contract | targeted sect tests passed | PASS | day/night fields asserted |
| AC2 | missing Sun and missing `above_horizon` / `below_horizon` runtime rules raise `ValueError` | targeted sect tests passed | PASS | no fallback |
| AC3 | `PlanetDignityScoringService` shares one `ChartSectResult` across planet results | scoring service test passed | PASS | object identity asserted |
| AC4 | `NatalResult.dignity_sect` added; old fields preserved | natal contract test passed | PASS | `PlanetDignityResult.sect` remains |
| AC5 | `json_builder.py` serializes precomputed object and fails closed when dignity results lack a sect contract | projection test and `SectCalculator` scan passed | PASS | no projection recalculation |
| AC6 | persistence stores `dignity_sect` and per-result `chart_sect` | chart result service test passed | PASS | payload shape asserted |
| AC7 | local horizon constants removed; no per-planet sect condition introduced | guard scans passed/classified | PASS | `sect_code` hits classified as runtime internals |
| AC8 | before/after snapshots added | evidence files present and contain new fields | PASS | public delta documented |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `backend/app/domain/astrology/dignities/contracts.py` | modified | add strict `ChartSectResult`; attach to `PlanetDignityResult` | AC1, AC3 |
| `backend/app/domain/astrology/dignities/sect_calculator.py` | modified | return explicit chart-level contract | AC1, AC2 |
| `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` | modified | calculate sect once and share result | AC3 |
| `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py` | modified | remove local horizon constants and read runtime horizon rules | AC7 |
| `backend/app/domain/astrology/dignities/__init__.py` | modified | export `ChartSectResult` | AC1 |
| `backend/app/domain/astrology/natal_calculation.py` | modified | expose `dignity_sect` | AC4 |
| `backend/app/services/chart/json_builder.py` | modified | serialize precomputed `dignities.sect` object and fail closed on missing contract | AC5 |
| `backend/app/tests/unit/test_chart_json_builder.py` | modified | assert public sect object | AC5 |
| `backend/app/tests/unit/test_chart_result_service.py` | modified | assert persisted sect contract | AC6 |
| `backend/tests/unit/domain/astrology/test_sect_calculator.py` | modified | assert contract fields and missing rules | AC1, AC2 |
| `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` | modified | assert shared chart sect object | AC3 |
| `backend/tests/unit/domain/astrology/test_dignity_contracts.py` | modified | assert DTO shape and immutability | AC1 |
| `backend/tests/unit/domain/astrology/test_natal_result_contract.py` | modified | assert `NatalResult.dignity_sect` | AC4 |
| `backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py` | modified | update fixture contract | AC3 |
| `backend/tests/unit/domain/astrology/advanced_condition_test_helpers.py` | modified | update helper contract | AC3 |
| `_condamad/stories/CS-197-sect-audit-explicit-contract/evidence/*` | added | before/after and validation evidence | AC8 |
| `_condamad/stories/CS-197-sect-audit-explicit-contract/generated/*` | added/modified | CONDAMAD capsule evidence | AC1-AC8 |

## Files deleted

- None.

## Tests added or updated

- `backend/tests/unit/domain/astrology/test_sect_calculator.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `backend/tests/unit/domain/astrology/test_dignity_contracts.py`
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_dignity_contracts.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | repo root | PASS | 0 | 33 passed |
| `.\.venv\Scripts\Activate.ps1; ruff check . --fix; ruff format .; ruff check .` | repo root | PASS | 0 | 1 import ordering issue fixed, format unchanged after fix, all checks passed |
| `.\.venv\Scripts\Activate.ps1; ruff format --check .` | repo root | PASS | 0 | 1472 files already formatted |
| `.\.venv\Scripts\Activate.ps1; ruff check .` | repo root | PASS | 0 | all checks passed |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | PASS | 0 | 2748 passed, 1 skipped, 1177 deselected |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.main import app; print(app.title)"` | repo root | PASS | 0 | backend app imports and reports `horoscope-backend` |
| `rg -n "SectCalculator" backend/app/services/chart/json_builder.py` | repo root | PASS | 1 | zero hits expected |
| `rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology/dignities backend/app/services/chart -g "*.py"` | repo root | PASS | 1 | zero hits expected |
| `rg -n "PlanetSectCondition|planet_sect_condition" backend/app backend/tests -g "*.py"` | repo root | PASS | 1 | zero hits expected |
| `rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code" backend/app backend/tests -g "*.py"` | repo root | PASS | 0 | hits classified as runtime internals |
| `$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt"; rg -n $forbidden backend/app/domain/astrology/dignities -g "*.py"` | repo root | PASS | 1 | zero hits expected |
| `git diff --check` | repo root | PASS | 0 | no whitespace errors; line-ending warnings only |

## Commands skipped or blocked

| Command | Required | Reason | Risk | Compensating evidence |
|---|---:|---|---|---|
| Local app server start | no | Backend contract story; no route or frontend runtime was changed. | Low: startup-specific integration not exercised here. | Full backend pytest suite and chart persistence/projection tests passed. |

## DRY / No Legacy evidence

- No `SectCalculator` in `json_builder.py`.
- No local horizon house constants remain under `backend/app/domain/astrology/dignities` or `backend/app/services/chart`.
- No `PlanetSectCondition` / `planet_sect_condition` introduced.
- `sect_code` / `chart_sect_code` hits are existing runtime reference internals, classified in `evidence/sect-contract-validation.md`.
- No forbidden infra/API/service/prediction/LLM imports in `backend/app/domain/astrology/dignities`.
- `ChartSectResult` rejects invalid values and inconsistent day/night horizon booleans.
- `json_builder.py` raises `ValueError` instead of emitting `dignities.sect: null` when dignity results exist without a precomputed sect contract.

## Diff review

- `git diff --stat`: scoped to backend dignity contract/calculation/projection tests and CONDAMAD evidence.
- `git diff --check`: PASS.
- Frontend files changed: none.
- Latest review evidence: `generated/11-code-review.md` verdict `CLEAN`.

## Final worktree status

- `git status --short`: expected CS-197 additions under `evidence/` and `generated/`, story status update, and scoped backend/test modifications only.

## Remaining risks

- No runtime risk identified after tests and scans.

## Suggested reviewer focus

- Confirm public JSON contract change from string to object at `dignities.sect`.
- Confirm `AccidentalDignityCalculator` horizon checks correctly use runtime rules and preserve hayz behavior.
