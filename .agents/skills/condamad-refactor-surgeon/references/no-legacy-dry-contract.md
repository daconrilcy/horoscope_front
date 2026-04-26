<!-- Contrat CONDAMAD No Legacy et DRY pour les refactorisations. -->

# No Legacy / DRY Contract

The refactor must converge on one canonical implementation path. It must reduce
or preserve duplication; it must not create parallel active paths.

## Forbidden Unless Separately Authorized

- compatibility wrappers;
- shims;
- aliases;
- re-exports;
- silent fallbacks;
- legacy paths;
- duplicate active implementations;
- deprecated paths kept as default behavior;
- broad cleanup unrelated to the selected refactor.

## Required Evidence

- negative scan command and result;
- explanation for any remaining findings;
- diff review confirming no duplicate active path;
- tests or static checks proving the canonical path still works.

Any plan that allows a shim, fallback, alias, re-export, compatibility wrapper,
or legacy path without separate authorization must fail validation.
