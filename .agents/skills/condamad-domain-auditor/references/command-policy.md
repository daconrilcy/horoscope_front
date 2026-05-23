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
- report writes outside `_condamad/audits/**` unless the user, story brief, or
  governing task contract explicitly names another audit deliverable path
- runtime commands that format, migrate, generate, install, update, delete, rewrite, or mutate application state

## Python execution in this repository

Follow the repository rule: verify `.\.venv\Scripts\Activate.ps1` exists and
activate it before any Python command.

Use this PowerShell prelude before validation, diagnostics, targeted tests, or
read-only Python evidence scripts:

```powershell
if (-not (Test-Path -LiteralPath .\.venv\Scripts\Activate.ps1)) { throw "Missing virtual environment: .\.venv" }
. .\.venv\Scripts\Activate.ps1
```

Never run `python`, `pip`, `pytest`, `ruff`, or Python-based tools without this
activation. If `.venv` is missing or dependencies are unavailable, stop before
the Python command and record the skipped command, reason, and residual risk in
`01-evidence-log.md`. Only create or install environment dependencies if the
user explicitly authorizes it.
