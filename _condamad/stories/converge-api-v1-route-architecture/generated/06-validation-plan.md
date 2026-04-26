# Validation Plan

## Targeted checks

```bash
# Replace with the smallest relevant test command after repository inspection.
pytest -q
```

## Architecture / negative scans

```bash
rg "legacy|compat|shim|fallback|deprecated|alias" .
```

## Lint / static checks

```bash
ruff check .
```

## Full regression checks

```bash
pytest -q
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
