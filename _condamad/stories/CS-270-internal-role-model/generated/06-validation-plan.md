# Validation Plan

## Targeted checks

```bash
# Replace with the smallest relevant test command after repository inspection.
python -B -m pytest -q --tb=short
```

## Early guard scans

Run these before expensive test suites and fix failures first.

```bash
rg "legacy|compat|shim|fallback|deprecated|alias" .
rg "<<forbidden symbol/import patterns from story guardrails>>" .
git diff --check
```

## Lint / static checks

```bash
ruff check .
```

## Full regression checks

```bash
python -B -m pytest -q --tb=short
```

## Rule for skipped commands

If a command cannot be run, record:

- exact command;
- reason not run;
- risk created;
- compensating evidence, if any.
