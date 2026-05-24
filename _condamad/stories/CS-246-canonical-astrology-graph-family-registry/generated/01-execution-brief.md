# Execution Brief — CS-246-canonical-astrology-graph-family-registry

## Primary objective

Implement story `CS-246-canonical-astrology-graph-family-registry` exactly as defined in `../00-story.md`.

Create one canonical backend-domain registry for astrology graph families under
`backend/app/domain/astrology/runtime`, with typed metadata, deterministic
duplicate and unknown-code rejection, a read-only natal graph definition link,
and no public API/frontend/DB/migration behavior delta.

## Execution rules

- Read `../00-story.md` completely before editing code.
- Read all required generated capsule files before implementation.
- Run `git status --short` before and after code changes.
- Preserve unrelated user changes.
- Implement only the current story.
- Do not introduce compatibility wrappers, aliases, silent fallbacks, duplicate active paths, or legacy import routes unless explicitly required by the story.
- Record implementation and validation evidence in `10-final-evidence.md`.
- Preserve the source brief `_story_briefs/cs-246-canonical-astrology-graph-family-registry.md`.
- Do not touch frontend, API routers, DB models, migrations, auth, i18n, styles, or build tooling.

## Done when

- Every AC in `03-acceptance-traceability.md` has code evidence and validation evidence.
- Commands in `06-validation-plan.md` have been run or explicitly documented as not run with reason and risk.
- `10-final-evidence.md` is complete.
- `_condamad/stories/story-status.md` marks CS-246 as `ready-to-review`.
