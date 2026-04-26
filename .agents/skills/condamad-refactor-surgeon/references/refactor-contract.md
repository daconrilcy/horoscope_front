<!-- Contrat CONDAMAD de refactorisation bornee. -->

# Refactor Contract

A CONDAMAD refactor is a bounded internal restructuring that preserves external
behavior. It must be planned, scoped, validated, and reviewed as one surgical
change.

## Required Inputs

- one allowed Refactor Type;
- exactly one Primary Domain;
- Current State Evidence;
- Target State;
- Behavior Invariants;
- files expected to change;
- validation commands;
- negative legacy scans.

## Rejection Rules

Reject or stop when:

- the request is vague;
- the refactor type is not in the taxonomy;
- domain boundaries are missing or multiple primary domains are requested;
- behavior invariants are absent;
- validation evidence is not possible;
- the plan permits compatibility wrappers, shims, aliases, re-exports, silent fallbacks, or legacy paths without a separate story;
- the implementation would change observable behavior without a separate authorizing story.

## Completion Rule

The refactor is complete only when exact command evidence, negative scan
evidence, and diff review evidence are recorded.
