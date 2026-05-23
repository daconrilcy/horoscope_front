# Baseline Snapshot Contract

<!-- Contrat transverse pour capturer un etat avant/apres testable. -->

Use this contract for refactors, convergences, migrations, route restructuring,
API contract changes, generated contract changes, and behavior-preserving
changes.

## Rule

If the story claims no regression or behavior preservation, it must capture a
baseline before implementation and compare it after implementation.

## Required Story Content

The story must state:

- baseline artifact path or command before implementation;
- after artifact path or command after implementation;
- comparison command or test;
- expected invariant;
- allowed differences, if any.

## Examples

- OpenAPI before/after snapshot;
- runtime route inventory before/after;
- import inventory before/after;
- generated contract diff;
- DB schema before/after;
- migration mapping before/after.
