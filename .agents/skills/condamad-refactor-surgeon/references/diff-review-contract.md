<!-- Contrat CONDAMAD de revue de diff apres refactorisation. -->

# Diff Review Contract

Diff review confirms that the internal structure changed without external
behavior change.

## Required Diff Evidence

Record:

- `git diff --stat`
- `git diff --name-status`
- `git diff --check`
- scoped `git diff` review summary
- untracked files review

## Review Questions

- Are all changed files inside the declared primary domain?
- Does the diff avoid new behavior?
- Does the diff avoid compatibility wrappers, shims, aliases, re-exports, silent fallbacks, and legacy paths?
- Is duplicated logic removed or consolidated without leaving two active paths?
- Do tests and scans map back to Behavior Invariants?
