# No Legacy / DRY Guardrails

## Forbidden unless explicitly required by the story

- Compatibility wrappers
- Transitional aliases
- Legacy import paths
- Duplicate active implementations
- Re-export modules preserving old imports
- Silent fallback behavior
- Tests that preserve legacy paths as nominal behavior

## Required when relevant

- One canonical path per responsibility
- Negative search evidence for removed symbols or imports
- Tests or architecture guards that fail if a legacy path is reintroduced
- Explicit errors instead of silent fallback for missing canonical configuration

## CS-287 scoped decisions

- The canonical implementation path is `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`.
- The builder must consume `structured_facts_v1` payloads and must not recalculate natal runtime data.
- The builder may reuse application-controlled disclaimer codes; it must not create disclaimer prose.
- The builder may return `plan_insufficient`; it must not silently downgrade to a lower-plan payload.
- API routers, DB, migrations, frontend, provider calls and prompt templates remain forbidden for this story.

## Reviewer questions

- Did we delete the legacy path or only move the problem?
- Did we preserve an old path “temporarily”?
- Did any test import the old namespace?
- Did any doc, registry, or config still reference the old path?
