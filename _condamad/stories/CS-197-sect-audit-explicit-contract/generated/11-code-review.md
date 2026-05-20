# CONDAMAD Code Review - CS-197-sect-audit-explicit-contract

## Review target

- Story: `CS-197-sect-audit-explicit-contract`
- Source: `_condamad/stories/CS-197-sect-audit-explicit-contract/00-story.md`
- Scope reviewed: backend dignity sect contract, natal result propagation,
  chart JSON projection, persistence tests, story evidence and guardrails.
- Review date: 2026-05-20

## Inputs reviewed

- `00-story.md`
- `generated/03-acceptance-traceability.md`
- `generated/06-validation-plan.md`
- `generated/07-no-legacy-dry-guardrails.md`
- `generated/10-final-evidence.md`
- `evidence/sect-contract-before.json`
- `evidence/sect-contract-after.json`
- `evidence/sect-contract-validation.md`
- `_condamad/stories/regression-guardrails.md` (`RG-108`, `RG-112`,
  `RG-118`, `RG-119`, `RG-120`, `RG-122`, `RG-123`, `RG-124`)
- Current repository diff and changed implementation/tests.

## Diff summary

- Added `ChartSectResult` and strict validation in dignity contracts.
- `SectCalculator.calculate()` now returns the chart-level sect contract from
  runtime `above_horizon` / `below_horizon` rules.
- `PlanetDignityScoringService` calculates chart sect once and shares it across
  planet dignity results.
- `NatalResult` exposes `dignity_sect`.
- `json_builder.py` serializes the precomputed sect contract and raises when a
  dignity payload lacks the contract.
- Tests and persistent evidence were updated for AC1-AC8.
- `story-status.md` row for CS-197 is `done`.

## Review layers

### Acceptance audit

| AC | Result | Evidence |
|---|---|---|
| AC1 | PASS | `ChartSectResult`; sect calculator day/night tests. |
| AC2 | PASS | missing Sun and missing horizon runtime rule tests. |
| AC3 | PASS | scoring service asserts one shared `ChartSectResult` object. |
| AC4 | PASS | `NatalResult.dignity_sect` contract test. |
| AC5 | PASS | chart JSON test and zero `SectCalculator` hit in `json_builder.py`. |
| AC6 | PASS | chart result service persistence assertions. |
| AC7 | PASS | local horizon constant, per-planet condition and alias scans. |
| AC8 | PASS | before/after JSON evidence present with explicit sect object. |

### DRY / No Legacy audit

- No `SectCalculator` usage exists in `backend/app/services/chart/json_builder.py`.
- No local horizon house lists exist under
  `backend/app/domain/astrology/dignities` or `backend/app/services/chart`.
- No `PlanetSectCondition` / `planet_sect_condition` contract was introduced.
- `sect_code` / `chart_sect_code` hits are runtime reference internals or
  fixtures, not public compatibility aliases for `dignities.sect`.
- No infra/API/service/prediction/LLM imports were introduced in
  `backend/app/domain/astrology/dignities`.

### Edge and failure audit

- Missing Sun remains a hard failure.
- Missing `above_horizon` or `below_horizon` runtime rule is covered.
- Invalid or inconsistent public sect contracts raise `ValueError`.
- Chart JSON projection raises when dignity results exist without a precomputed
  sect contract instead of emitting `null`.

### Security and data audit

- No auth, secret, CORS, migration or external-call surface changed.
- Persistence stores the explicit sect contract through the existing chart
  result payload path.

## Findings

Aucun finding ouvert.

## Commands run by reviewer

| Command | Working directory | Result |
|---|---|---|
| `git diff --check` | repo root | PASS |
| `rg -n "SectCalculator" backend/app/services/chart/json_builder.py` | repo root | PASS, zero hits |
| `rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology/dignities backend/app/services/chart -g "*.py"` | repo root | PASS, zero hits |
| `rg -n "PlanetSectCondition|planet_sect_condition" backend/app backend/tests -g "*.py"` | repo root | PASS, zero hits |
| `rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code" backend/app backend/tests -g "*.py"` | repo root | PASS_WITH_CLASSIFIED_HITS |
| `$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt"; rg -n $forbidden backend/app/domain/astrology/dignities -g "*.py"` | repo root | PASS, zero hits |
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_dignity_contracts.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py` | repo root | PASS, 33 passed |
| `.\.venv\Scripts\Activate.ps1; ruff format --check .` | repo root | PASS, 1472 files already formatted |
| `.\.venv\Scripts\Activate.ps1; ruff check .` | repo root | PASS |
| `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` | repo root | PASS, 2748 passed, 1 skipped, 1177 deselected |
| `.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.main import app; print(app.title)"` | repo root | PASS, `horoscope-backend` |

## Review loop history

| Iteration | Verdict | Findings | Follow-up |
|---:|---|---|---|
| 1 | CLEAN | 0 | No fix required. |

## Residual risks

Aucun risque restant identifie.

## Verdict

CLEAN
