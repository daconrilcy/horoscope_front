# Validation Plan

## Targeted Checks

```bash
python -B -m pytest -q app/tests/unit/test_astrology_runtime_reference_repository.py tests/unit/domain/astrology/test_sign_runtime_builder.py app/tests/unit/test_chart_json_builder.py app/tests/unit/test_astrology_runtime_reference_guard.py tests/unit/domain/astrology/test_sign_runtime_data.py tests/unit/domain/astrology/test_chart_signature.py
```

## Architecture / Negative Scans

```bash
rg -n "SEASONAL_QUADRANT_BY_SIGN|FERTILITY_BY_SIGN|VOICE_BY_SIGN|FORM_BY_SIGN|HUMANE_BY_SIGN|BESTIAL_BY_SIGN" app/domain/astrology app/services/natal -g "*.py"
```

## Lint / Static Checks

```bash
ruff check .
```

## Runtime Smoke Check

```bash
python -B -c "from app.main import app; assert hasattr(app, 'routes'); assert callable(app.openapi)"
```

## Rule For Skipped Commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
