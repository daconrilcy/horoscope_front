---
name: condamad-regression-guardrails
description: >
  Manage the shared CONDAMAD regression guardrail registry under
  _condamad/stories/regression-guardrails.md. Use when creating, updating,
  implementing, auditing, reviewing, or refactoring CONDAMAD stories so the
  agent creates the registry if missing, reads applicable invariants, enforces
  non-regression evidence, and updates the registry when a story creates a new
  durable invariant.
---

<!-- Skill CONDAMAD de gestion du registre anti-regression inter-stories. -->

# CONDAMAD Regression Guardrails

## Purpose

Maintain a single shared registry of durable invariants produced by CONDAMAD
stories. The registry prevents a new story, refactor, audit recommendation, or
review fix from regressing behavior or architecture already protected by prior
stories.

Canonical registry path:

`_condamad/stories/regression-guardrails.md`

## Non-negotiable rules

- Ensure the registry exists before writing, implementing, reviewing, auditing,
  or refactoring a CONDAMAD story.
- If the registry is missing, create it from
  `templates/regression-guardrails-template.md`.
- Read the registry before defining scope, changing code, producing audit story
  candidates, or returning a review verdict.
- A story that touches a protected surface must cite applicable guardrail IDs,
  include non-regression ACs, and define executable evidence.
- A story that creates a new durable invariant must update the registry with a
  new `RG-XXX` row.
- Do not add vague invariants. Name the concrete route, module, contract,
  owner, behavior, import boundary, or forbidden legacy surface.
- Do not remove or weaken an invariant unless the current user explicitly asks
  for that governance change and the reason is recorded in the registry.

## Workflow

1. Locate the repository root.
2. Check whether `_condamad/stories/regression-guardrails.md` exists.
3. If missing:
   - create `_condamad/stories/` if needed;
   - copy the structure from `templates/regression-guardrails-template.md`;
   - seed known invariants only from repository evidence, not assumptions.
4. Read the registry.
5. Classify guardrails as:
   - applicable: the current work touches or depends on the protected surface;
   - non-applicable: the work is outside that surface;
   - needs-investigation: the scope may overlap and requires repository search.
6. Inject the result into the active CONDAMAD artifact:
   - story: `Current State Evidence`, `Explicit non-goals`, `Acceptance Criteria`,
     `Validation Plan`, and a `Regression Guardrails` section;
   - dev capsule: generated validation and No Legacy guardrail files;
   - review: acceptance/validation audit and verdict;
   - audit: story candidates and risk matrix;
   - refactor plan: behavior invariants and validation evidence.
7. After completion, update the registry if the work created a stable new
   invariant or changed the expected guard for an existing invariant.

## Required story snippet

Use this section in each new or materially updated story:

```md
## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-XXX` - <why this invariant applies>
- Non-applicable invariants:
  - `RG-YYY` - <why this story does not touch the protected surface>
- Required regression evidence:
  - <test, scan, snapshot, diff, audit, or runtime inventory>
- Allowed differences:
  - <explicit allowed differences, or "none">
```

## Registry row format

Add rows to `## Invariants actifs` using this shape:

```md
| RG-XXX | `<source-story-key>` | <protected surface> | <durable invariant> | <deterministic guard> |
```

The guard must be executable or objectively reviewable: AST test, runtime route
inventory, OpenAPI diff, import scan, targeted forbidden symbol scan, generated
manifest diff, or persisted audit.

## Validation

This skill is mostly procedural. Validation is done by checking that:

- the registry file exists;
- the active story/capsule/review/audit/refactor artifact cites the registry;
- applicable invariants are mapped to evidence;
- new durable invariants are added with a concrete guard.

