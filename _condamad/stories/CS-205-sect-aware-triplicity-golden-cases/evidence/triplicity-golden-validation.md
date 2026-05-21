<!-- Validation CS-205 des cas golden de triplicite. -->

# CS-205 Triplicity Golden Validation

## Summary

- Dedicated CS-205 suite added:
  `backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py`.
- Persistent before snapshot records that no dedicated CS-205 suite existed.
- Persistent after snapshot captures G1-G6 in a curated, non-volatile shape.
- Participant status: supported and applied through runtime `sect_code == "all"`.
- No score change: production scoring files were not modified.
- No public payload change: `json_builder.py` was not modified.

## Commands

All Python commands were run after `.\.venv\Scripts\Activate.ps1`.

| Command | Result | Summary |
|---|---|---|
| `pytest -q backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py` | PASS | 8 tests passed. |
| `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py` | PASS | 13 tests passed. |
| `pytest -q backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_traditional_golden_cases.py backend/tests/unit/domain/astrology/test_dignity_contracts.py backend/tests/unit/domain/astrology/test_sect_calculator.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py` | PASS | 57 tests passed. |
| `ruff format .` | PASS | 1 file reformatted. |
| `ruff check .` | FAIL then PASS | Import order fixed with targeted `ruff check ... --fix`; final full lint passed. |
| Anti-constant scan over `backend/app` | PASS | Zero hits. |
| Local doctrine pattern scan over `backend/app/domain/astrology/dignities` | PASS | Zero hits. |
| Forbidden import scan over `backend/app/domain/astrology/dignities` | PASS | Zero hits. |
| `python -m json.tool` for before/after snapshots | PASS | Both JSON files valid. |
| Forbidden path diff | PASS | Empty diff for API, infra, prediction, migrations, seeds and frontend. |

## Scan exception register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py` | `triplicity` | Dedicated CS-205 seed-backed fixture/test evidence. | permanent fixture-only |
| `backend/tests/unit/domain/astrology/fixtures/triplicity_seed_cases.py` | `seed_backed_triplicity_reference` | Maps canonical seed rows into runtime contracts for CS-205. | permanent fixture-only |

## Forbidden path confirmation

- No `backend/app/api/**` change.
- No `backend/app/infra/**` change.
- No `backend/app/domain/prediction/**` change.
- No `backend/migrations/**` change.
- No `docs/db_seeder/**` change.
- No `frontend/**` change.
