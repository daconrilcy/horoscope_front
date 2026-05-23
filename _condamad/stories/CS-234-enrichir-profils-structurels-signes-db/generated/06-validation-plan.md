# Validation Plan

## Targeted checks

```bash
python -B -m pytest -q app/tests/integration/test_reference_data_migrations.py app/tests/unit/test_prediction_reference_repository.py
```

## Architecture / negative scans

```bash
rg -n "\b(seasonal_quadrant|fertility|voice|humane|bestial|fruitful|barren|mute)\b" backend/app/domain/astrology backend/app/services/natal -g "*.py"
rg -n "sect|gender" "docs/recherches astro" docs/db_seeder/astrology
```

## Lint / static checks

```bash
ruff check .
```

## Full regression checks

```bash
python -B -m pytest -q
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
