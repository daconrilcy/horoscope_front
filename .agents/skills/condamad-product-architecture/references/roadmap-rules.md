# Roadmap Rules

## Ordering principle

Order stories by architecture dependency:

1. Decisions and registries that unblock naming and contracts.
2. Domain object/entity normalization.
3. Internal source-of-truth implementation.
4. Persistence, versioning, trace, cache, replay, and invalidation foundations.
5. Public/API/admin/debug contracts.
6. Automation, generated interpretation, or LLM integration.
7. Frontend/user workflows.
8. Migration, cleanup, and deprecation.
9. Observability and regression guardrails if not already covered.

## Story quality

Each story must be implementable by an agent without redoing the architecture synthesis.

Include:

- One clear goal.
- Explicit source audits.
- Concrete scope.
- Out of scope.
- Dependencies.
- Acceptance criteria.
- Validation evidence.
- Blockers or required decisions.

Avoid:

- Stories that only say "continue cleanup".
- Stories with mixed unrelated surfaces.
- Stories that depend on unnamed future architecture work.
- Stories whose validation is "manual review" only when automated or structural evidence is possible.

## Dependency rules

Do not schedule public API, frontend, or automation work before the canonical contracts it consumes.

Do not schedule cache/replay hardening before input identity and versioning rules exist.

Do not schedule migration cleanup before compatibility and deprecation rules exist.

## Acceptance criteria rules

Acceptance criteria should verify:

- Contract shape.
- Backward compatibility or intentional break.
- Traceability.
- Cache/replay behavior when relevant.
- Surface ownership.
- Removal or quarantine of legacy aliases when relevant.

## Validation evidence examples

Use project-appropriate evidence:

- Unit tests for object/entity rules.
- Contract tests for API/schema surfaces.
- Snapshot or golden tests for generated outputs.
- Integration tests for cache/replay/invalidation.
- Static scans for forbidden aliases or legacy paths.
- Observability checks for trace propagation.
