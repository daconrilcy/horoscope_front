# Story <story-key>: <title>

Status: ready-for-dev

<!-- Keep contract headings and markers in English. Story content may be written in French. -->

## 1. Objective

One clear paragraph explaining the implementation outcome.

## 2. Trigger / Source

- Source type: brief | audit | code-review | architecture-decision | bug | refactor
- Source reference: <path, pasted brief, issue, review, or audit>
- Reason for change: <why this story exists>

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: <backend/app/services/... or equivalent>
- In scope:
  - ...
- Out of scope:
  - ...
- Explicit non-goals:
  - ...

## 4. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `<relative/path.py>` - <what exists today>
- Evidence 2: `<relative/path.py>` - <what must change>

If repository evidence was not available, state:

- Repository evidence: not available
- Assumption risk: <risk>

## 5. Target State

After implementation:

- ...
- ...
- ...

## 6. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | ... | test / guard / grep / command |
| AC2 | ... | test / guard / grep / command |

## 7. Implementation Tasks

- [ ] Task 1 - <action> (AC: AC1)
  - [ ] Subtask 1.1 - <specific step>
  - [ ] Subtask 1.2 - <specific step>

- [ ] Task 2 - <action> (AC: AC2)
  - [ ] Subtask 2.1 - <specific step>

## 8. Mandatory Reuse / DRY Constraints

- Reuse:
  - `<existing module/class/function>` for <purpose>
- Do not recreate:
  - ...
- Shared abstraction allowed only if:
  - ...

## 9. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `<path or import>`
- `<symbol>`

## 10. Files to Inspect First

Codex must inspect before editing:

- `<relative/path>`
- `<relative/path>`

## 11. Expected Files to Modify

Likely files:

- `<relative/path>` - <expected change>

Likely tests:

- `<relative/test_path>` - <expected coverage>

Files not expected to change:

- `<relative/path>` - <reason>

## 12. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 13. Validation Plan

Run or justify why skipped:

```bash
<targeted tests>
<architecture guard tests>
<lint/type checks>
<negative rg scans>
```

## 14. Regression Risks

- Risk: ...
  - Guardrail: ...
- Risk: ...
  - Guardrail: ...

## 15. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.

## 16. References

- `<source>` - <why relevant>
