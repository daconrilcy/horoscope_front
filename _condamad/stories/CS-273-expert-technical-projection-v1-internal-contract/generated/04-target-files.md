# Target Files

## Inspected before implementation

- `AGENTS.md`
- `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/00-story.md`
- `_story_briefs/cs-273-define-expert-technical-projection-v1-admin-astro-expert-only.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `docs/architecture/product-architecture-current-state-2026-05-24.md`
- CS-270, CS-271, CS-256, CS-266 and CS-272 story files via targeted searches
- `docs/architecture/structured-facts-v1-contract.md`
- `docs/architecture/evidence-refs-contract.md`
- Existing contract tests under `backend/tests/unit` and `backend/tests/architecture`

## Modified files

- `docs/architecture/expert-technical-projection-v1-contract.md`
- `docs/architecture/official-product-primitives-public-projections.md`
- `docs/architecture/product-architecture-current-state-2026-05-24.md`
- `backend/tests/unit/test_expert_technical_projection_contract.py`
- `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/00-story.md`
- `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/generated/**`
- `_condamad/stories/CS-273-expert-technical-projection-v1-internal-contract/evidence/**`
- `_condamad/stories/story-status.md`

## Forbidden or high-risk files kept untouched by CS-273

- `frontend/src/**`
- `backend/app/api/**`
- `backend/app/infra/db/**`
- `backend/migrations/**`
- generated OpenAPI clients
- public B2C projection contracts

## Required searches and checks

- Targeted `rg` for `expert_technical_projection_v1`, `ADMIN`, `ASTRO_EXPERT`, `non client`, `interne`, `B2C`.
- Targeted `rg` for data families, evidence links, raw payload exclusions and access-log fields.
- Expert registry row negative scan for public/client ownership wording.
- Current architecture synthesis negative scan for stale expert public projection wording.
- `git status --short -- backend/app frontend/src backend/migrations` to prove CS-273 did not edit app roots.
