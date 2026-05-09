<!-- Brief d'execution CONDAMAD pour CS-126. -->

# CS-126 Execution Brief

## Objective

Close `F-002` by making the `precision` and `evidence` visual families in
`frontend/src/App.css` explicitly migrated or explicitly retained with exact
source-backed ownership.

## Scope

- In scope: `frontend/src/App.css`, exact precision/evidence TSX consumers,
  existing owner CSS files when migration requires them,
  `frontend/src/tests/design-system-guards.test.ts`,
  `frontend/src/tests/design-system-allowlist.ts`, and story evidence files.
- Out of scope: backend, business data semantics, broad component architecture,
  unrelated CSS pages.

## Required Guardrails

- `RG-044`, `RG-047`, `RG-048`, `RG-049`, `RG-050`, `RG-061`, `RG-075`,
  `RG-077`.
- Preserve `RG-076` introduced by `CS-125`.

## Done Conditions

- Before and after precision/evidence artifacts exist.
- App.css has zero unclassified `precision/evidence` class or variable hits.
- Consumers use the final canonical class names.
- Validation commands from the story are run or honestly recorded.
- Story status is synchronized with `_condamad/stories/story-status.md`.
