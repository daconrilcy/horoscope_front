<!-- Contrat CONDAMAD de validation et politique de commandes. -->

# Validation Contract

Validation must prove behavior preservation and scope control. A final refactor
requires targeted tests, static checks when relevant, negative legacy scans, and
diff review evidence.

## Required Validation Sections

- Targeted Tests
- Static Checks
- Negative Legacy Scans
- Diff Review

At least one test or static command is required. At least one negative scan
command is required.

Weak evidence is invalid:

- "manual review"
- "looks good"
- "covered by tests"
- "not needed"

## Review-safe Command Policy

Allowed:

- `git status --short`
- `git diff --check`
- `git diff --stat`
- `git diff --name-status`
- `rg ...`
- targeted tests;
- check-only lint/static checks;
- this skill's helper scripts.

Forbidden mutating examples unless explicitly authorized:

- formatters without check mode, such as `ruff format .`
- `npm run format`
- code generators;
- dependency updates;
- migrations;
- destructive git commands;
- cleanup scripts.
