# Output Contract

## Executive Architecture Decision Summary

Include:

- Product architecture direction in 5-10 bullets.
- Decisions already safe to take.
- Decisions blocked by missing evidence or owner validation.
- Highest-risk implementation dependencies.

## Audit Source Map

Use a table:

| Audit | Scope | Closure status | Key architecture inputs | Evidence IDs | Findings used | Blockers | Deferred context | Used for |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

If the audit contains source-label caveats or tracker conflicts, add a short paragraph below the table named `Story label caveats`.

## Capability Matrix

Use a table:

| Capability / family | Inputs | Objects required | Canonical contracts required | Surfaces required | Status | Blockers | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |

If the domain uses graph/model terminology, name the contract column accordingly, for example `Graph required` or `Model required`.

## Surface Matrix

Use a table:

| Surface | Current contract | Expected contract | Capabilities exposed | Consumers | Risks | Blockers | Required changes | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Default surface taxonomy:

- `internal`
- `public_api`
- `admin_debug`
- `automation_or_llm`
- `frontend`
- `data_storage`
- `observability`

## Canonical Registry Decisions

Use one subsection per registry:

```markdown
### <registry_name>

Decision: <adopt / defer / reject / replace>
Owner: <role or team>
Canonical entries:

| ID | Version | Inputs | Output contract | Compatibility | Deprecation | Trace fields | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

## Object / Entity Decisions

Use a table:

| Object | Kind | Lifecycle owner | Persistence | Serialization | Versioning | Surfaces | Decision | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Allowed kinds:

- `core_entity`
- `value_object`
- `derived_object`
- `external_reference`
- `presentation_model`
- `debug_artifact`

## Operational Rules

Use a table:

| Rule area | Rule | Applies to | Invalidated by | Trace requirement | Owner | Sources |
| --- | --- | --- | --- | --- | --- | --- |

Required areas:

- Versioning.
- Trace.
- Cache.
- Replay.
- Invalidation.
- Migration.
- Observability.

## Roadmap

Use ordered story cards:

```markdown
### Story <n>: <title>

Story ID: <actual ID / next-available-id / needs-tracker-remap>
Source label: <optional audit-provided candidate label>
Goal: ...
Source audits: ...
Source findings: ...
Scope: ...
Out of scope: ...
Dependencies: ...
Acceptance criteria:
- ...
Validation evidence:
- ...
Blockers / decisions:
- ...
Stop condition: ...
```

## Open Questions

Use a table:

| Question | Why it matters | Owner | Blocks | Suggested default | Sources |
| --- | --- | --- | --- | --- | --- |
