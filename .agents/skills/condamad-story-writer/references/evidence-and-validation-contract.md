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

## Validation Command Compiler

Compile validation commands from the source brief and story scope before the
story is marked `ready-to-dev`.

- If the brief names validation commands, preserve each named validation in the
  Validation Plan. Copy it textually when it is valid for the story type, or
  record the source command and justify the compiled replacement or out-of-scope
  decision.
- For audit-only or report-only stories, commands must be non-mutating. Use
  `ruff format --check` instead of `ruff format .`.
- If an audit-only or report-only brief names a mutating command, do not run it
  as validation. Record it as the source intent and compile the closest
  non-mutating command, or mark it out of scope with a reason.
- If a command starts with `cd backend`, paths inside the command must not be
  prefixed with `backend/`.
- If a command starts with `cd frontend`, paths inside the command must not be
  prefixed with `frontend/`.
- Validation commands must stay bounded to the story domain unless the brief
  explicitly requires a broader repository proof.

## Negative Scan Checklist

Every `rg` validation command must document:

- `forbidden_pattern`: the exact regex or token being rejected;
- `allowed_fixture_pattern`: fixtures, snapshots, or generated artifacts that
  may still contain the token;
- `roots`: the explicit directories or files scanned;
- `expected_false_positives`: known allowed hits and how the dev agent must
  classify them.

Do not use broad symbol bans when a narrower route, event, contract, or owner
surface is the real invariant.

Use this shape in the Validation Plan:

| Command | forbidden_pattern | allowed_fixture_pattern | roots | expected_false_positives |
|---|---|---|---|---|
| `rg -n "<pattern>" <roots>` | `<exact forbidden regex or token>` | `<allowed fixtures, snapshots, generated artifacts, or none>` | `<explicit files or directories>` | `<known allowed hits and classification rule>` |

## Audit And Report Archetype Completeness

For audit or report stories, preserve source completeness instead of converting
the work into generic cleanup:

- mandatory questions from the source audit/report brief;
- expected deliverables and artifact paths;
- upstream sources that must be inspected;
- required output formats;
- blocker conditions when a required source is missing or ambiguous.
