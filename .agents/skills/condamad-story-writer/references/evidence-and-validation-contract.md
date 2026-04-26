# Evidence And Validation Contract

<!-- Contrat de preuves et de commandes de validation pour les stories CONDAMAD. -->

## Evidence Types

Accepted evidence sources:

- repository file path and observed behavior;
- test file or failing test;
- audit or review finding;
- user-provided brief;
- command output;
- architecture document;
- explicit assumption with risk.

Do not present assumptions as facts.

## Current State Evidence

The story must include at least one current-state evidence item or an explicit
statement that repository evidence is unavailable.

Evidence items should use this shape:

```md
- Evidence 1: `relative/path.py` - what exists today.
```

## Validation Plan

The validation plan must include at least one command. Prefer commands that the
dev agent can run directly:

```bash
pytest -q backend/app/tests/unit/test_target.py
ruff check .
rg "legacy_import" backend/app backend/tests
```

If a command is intentionally skipped, the story must require the dev agent to
record why it was skipped and the risk.

