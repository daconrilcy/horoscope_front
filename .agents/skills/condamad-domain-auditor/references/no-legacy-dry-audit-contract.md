# No Legacy / DRY Audit Contract

Audit must identify:

- duplicate active implementations;
- compatibility wrappers;
- aliases;
- shims;
- fallback paths;
- legacy route surfaces;
- old import paths;
- re-exports preserving old paths;
- duplicated business rules.

Every legacy finding must classify:

- remove candidate;
- canonical replacement;
- blocker;
- story candidate.
