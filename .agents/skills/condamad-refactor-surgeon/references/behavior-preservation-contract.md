<!-- Contrat CONDAMAD de preservation du comportement externe. -->

# Behavior Preservation Contract

A refactor is behavior-preserving. It may change internal structure but must not
change public contracts, data semantics, user-visible outcomes, HTTP status
codes, validation rules, side effects, or error behavior unless a separate story
explicitly authorizes that behavior change.

## Required Behavior Invariants

Behavior Invariants must name observable behavior that remains unchanged, such
as:

- inputs and outputs;
- public API surface;
- error messages or status codes;
- persistence side effects;
- ordering and filtering semantics;
- security or authorization decisions.

## Forbidden During Refactor

- no new behavior;
- no feature changes;
- no silent fallback behavior;
- no test weakening;
- no unrecorded public API change.

If invariants cannot be proven, stop and gather characterization evidence before
editing.
