<!-- Revue CONDAMAD finale pour CS-032. -->

# Code Review CS-032

Verdict: CLEAN

Findings fixed:

- `npm run test -- design-system` now includes hardcoded literal, inline-style
  and CSS fallback assertions, not only marker checks.
- `frontend/src/tests/design-system-allowlist.ts` was added as the central exact
  exception source.
