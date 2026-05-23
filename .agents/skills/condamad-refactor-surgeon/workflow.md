<!-- Workflow CONDAMAD pour refactorisation chirurgicale sans changement de comportement. -->

# CONDAMAD Refactor Surgeon Workflow

## Goal

Execute exactly one bounded, mono-domain, behavior-preserving refactor. The
workflow changes internal structure only: no new behavior, no feature work, no
compatibility debt, no unrelated cleanup.

## Source-of-truth precedence

1. System/developer safety rules and tool constraints.
2. Repository `AGENTS.md`.
3. Current user instruction, only within the requested refactor scope.
4. `refactor-plan.md` validated for this run.
5. Existing tests, public APIs, and observed behavior.
6. This skill's reference contracts.

## Stop Conditions

Stop before editing when any of these are insufficient:

- scope is vague or broader than one surgical refactor;
- primary domain is missing or multiple primary domains are requested;
- allowed refactor type is missing or unmapped;
- Behavior Invariants are missing, placeholders only, or unverifiable;
- Current State Evidence or Target State is missing;
- validation evidence cannot be produced;
- requested work needs new behavior, a feature change, compatibility wrapper, shim, alias, re-export, silent fallback, or legacy path without a separate authorizing story;
- command policy would require mutating formatters, generators, dependency updates, migrations, or destructive git commands without explicit authorization.

## Workflow Steps

### Step 0 - Preflight

Run and record:

```bash
git status --short
```

Resolve:

- target files and symbols;
- exactly one primary domain;
- one allowed refactor type;
- current-state evidence;
- target-state evidence;
- explicit behavior invariants.

### Step 1 - Plan before edits

Create or update `refactor-plan.md` from `templates/refactor-plan.md`.

The plan must include:

- Refactor Type;
- Primary Domain;
- Current State Evidence;
- Target State;
- Behavior Invariants;
- Scope Boundary;
- No Legacy / DRY constraints;
- Validation Plan;
- Diff Review Plan.

Validate the plan when the helper is available:

```bash
python -B scripts/condamad_refactor_validate.py --plan refactor-plan.md
```

### Step 2 - Characterize behavior

Before risky transformations, identify existing tests or add characterization
tests that prove the Behavior Invariants. Do not proceed on assumptions such as
"covered by tests" without command, path, and expected result.

### Step 3 - Implement the smallest coherent refactor

Only edit files in the declared primary domain and target list. Preserve
external behavior. Do not introduce feature work, unrelated cleanup, broad
formatting, compatibility wrappers, shims, aliases, re-exports, silent
fallbacks, or legacy paths.

### Step 4 - Validate

Run targeted tests, static checks, negative legacy scans, and diff checks from
the plan. Validation evidence must include at least one test or static command
and at least one negative scan command.

Recommended checks:

```bash
git diff --check
python -B scripts/condamad_refactor_scan.py <target-path> --fail-on-hit
```

### Step 5 - Diff review

Review:

```bash
git diff --stat
git diff --name-status
git diff
```

Confirm:

- no unrelated files changed;
- no behavior changes are visible at public boundaries;
- no duplicate active path remains;
- no compatibility or legacy path was introduced;
- tests and scans match the Behavior Invariants.

### Step 6 - Evidence

Create or update `refactor-evidence.md` from
`templates/refactor-evidence.md`. Capture exact command results. The evidence
collector may be used because it does not mutate application code:

```bash
python -B scripts/condamad_refactor_collect_evidence.py --root . --output refactor-evidence.md
```

Validate final evidence:

```bash
python -B scripts/condamad_refactor_validate.py --evidence refactor-evidence.md
```

## Review-safe command policy

Allowed without extra authorization:

- `git status --short`
- `git diff ...`
- `git diff --check`
- `git ls-files --others --exclude-standard`
- `rg ...`
- targeted tests
- check-only lint or static checks
- this skill's helper scripts

Forbidden unless explicitly authorized:

- formatters without check mode;
- generators;
- dependency updates;
- migrations;
- cleanup scripts;
- destructive git commands;
- commands that write outside the approved refactor domain.
