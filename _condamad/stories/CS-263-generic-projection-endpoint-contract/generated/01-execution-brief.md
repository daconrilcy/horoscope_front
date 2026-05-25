# Execution Brief — CS-263-generic-projection-endpoint-contract

## Primary objective

Define the canonical backend API contract document for future
`POST /v1/astrology/projections` without implementing any runtime route,
OpenAPI schema, persistence, frontend client, builder or service.

The implementation surface is documentation plus CONDAMAD evidence only:
`docs/architecture/generic-projection-endpoint-contract.md` and
`_condamad/stories/CS-263-generic-projection-endpoint-contract/**`.

## Execution rules

- Read `../00-story.md` completely before editing code.
- Load generated capsule summary before implementation; read a full generated file
  only on conflict or when editing it.
- Run `git status --short` before and after code changes.
- Preserve unrelated user changes.
- Implement only the current story.
- Run early guard scans before broad validation.
- Do not introduce compatibility wrappers, aliases, silent fallbacks, duplicate
  active paths, or legacy import routes unless explicitly required by the story.
- Record implementation and validation evidence in `10-final-evidence.md`.

## Done when

- Every AC in `03-acceptance-traceability.md` has code evidence and validation evidence.
- Commands in `06-validation-plan.md` have been run or explicitly documented as
  not run with reason and risk.
- `10-final-evidence.md` is complete.
- `_condamad/stories/story-status.md` marks CS-263 as `ready-to-review`.
