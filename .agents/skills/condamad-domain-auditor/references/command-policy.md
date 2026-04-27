# Command Policy

## Allowed by default

- `rg`
- `git status --short`
- `git grep`
- read-only Python scripts
- targeted `pytest` commands when they do not mutate application code
- lint or typecheck commands in check-only mode
- explicit `--runtime-command` evidence commands only when they are read-only and requested by the audit operator

## Forbidden unless explicitly requested

- formatters such as `ruff format`, `black`, or `eslint --fix`
- migrations
- generators that rewrite application code
- dependency install, update, or lockfile rewrite
- destructive git commands
- application code edits
- report writes outside `_condamad/audits/**`
- runtime commands that format, migrate, generate, install, update, delete, rewrite, or mutate application state

## Python execution in this repository

Follow the repository rule: activate `.\.venv\Scripts\Activate.ps1` before any Python command.

If `.venv` is missing or dependencies are unavailable, do not install dependencies automatically. Record the skipped command, reason, and residual risk in `01-evidence-log.md`. Only create or install environment dependencies if the user explicitly authorizes it.
