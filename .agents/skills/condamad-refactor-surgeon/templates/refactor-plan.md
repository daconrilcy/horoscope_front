<!-- Modele CONDAMAD de plan de refactorisation avant edition. -->

# CONDAMAD Refactor Plan

## Refactor Type

`extract-function`

## Primary Domain

- Domain: `<repo-relative/domain-path>`

## Current State Evidence

- Evidence 1: `<command or file reference>` - `<observed current structure>`

## Target State

- `<desired internal structure after refactor>`

## Behavior Invariants

- `<observable behavior that must remain unchanged>`

## Scope Boundary

In scope:

- `<repo-relative path or symbol>`

Out of scope:

- `<explicit non-goal>`

## No Legacy / DRY Constraints

- No compatibility wrappers, shims, aliases, re-exports, silent fallbacks, or legacy paths.
- One canonical implementation path after the refactor.
- No broad cleanup outside the selected refactor.

## Validation Plan

### Targeted Tests

```bash
<test command>
```

### Static Checks

```bash
<static check command>
```

### Negative Legacy Scans

```bash
python -B .agents/skills/condamad-refactor-surgeon/scripts/condamad_refactor_scan.py <target-path> --fail-on-hit
```

### Diff Review

```bash
git diff --check
git diff --stat
git diff --name-status
```

## Diff Review Plan

- Confirm only declared domain files changed.
- Confirm behavior-preserving diff.
- Confirm no forbidden No Legacy markers were introduced.
