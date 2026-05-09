<!-- Brief d'execution CONDAMAD pour CS-125. -->

# CS-125 Execution Brief

## Objective

Close `F-001` by turning every active `--app-*` prefix in
`frontend/src/App.css` into an explicit, deterministic taxonomy.

## Scope

- In scope: `frontend/src/App.css`, exact frontend consumers required by the
  story scans, `frontend/src/tests/design-system-guards.test.ts`,
  `frontend/src/tests/design-system-allowlist.ts`,
  `frontend/src/styles/token-namespace-registry.md`, and story evidence files.
- Out of scope: backend, API behavior, broad page decomposition, dependency
  changes, and any user-visible behavior change.

## Required Guardrails

- `RG-044`, `RG-045`, `RG-046`, `RG-047`, `RG-048`, `RG-049`, `RG-050`,
  `RG-059`, `RG-061`, `RG-075`, `RG-076`.

## Done Conditions

- Baseline and after taxonomy artifacts exist.
- Every active `--app-*` prefix has a final owner decision.
- The design-system guard fails on unknown App prefixes.
- Validation commands from the story are run or honestly recorded.
- Story status is synchronized with `_condamad/stories/story-status.md`.

## Halt Conditions

- A prefix needs to remain a public CSS contract without source-backed owner.
- Validation repeatedly fails with no safe scoped fix.
- A requested correction would broaden scope outside `CS-125`.
