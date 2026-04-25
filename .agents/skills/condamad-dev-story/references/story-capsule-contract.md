# CONDAMAD Story Capsule Contract

## 1. Purpose

A CONDAMAD story capsule is the execution envelope for one development story.

It exists to transform one human-readable story into a Codex-ready implementation package with explicit context, traceability, validation, and final evidence.

The capsule is not a second story format and must not become a parallel product backlog. It is an execution artifact generated from a source story so Codex can implement the work with minimal ambiguity, strong DRY discipline, and strict No Legacy enforcement.

## 2. Core Principle

One story has one human-owned source of truth and one generated execution capsule.

The user should not be required to manually create every capsule file. If only a story markdown file is provided, the CONDAMAD skill must generate the missing capsule structure before implementation.

```text
Human story source
        ↓
CONDAMAD capsule generation
        ↓
Codex implementation
        ↓
Final evidence and review handoff
```

## 3. Accepted Inputs

The CONDAMAD skill accepts either:

1. A path to a single story markdown file.
2. A path to an existing CONDAMAD story capsule directory.
3. A prompt containing a story body directly, when no file path is available.

When the input is a single story markdown file, the skill must create a capsule directory and copy or reference the source story as `00-story.md`.

When the input is already a capsule directory, the skill must validate the capsule structure before implementation.

When the input is a story body in the prompt, the skill must create a new capsule directory using an inferred story key and persist the story body as `00-story.md`.

## 4. Canonical Capsule Location

The default generated capsule location is:

```text
_condamad/stories/<story-key>/
```

The `<story-key>` must be stable, filesystem-safe, and derived in this order:

1. Explicit story key in metadata, if present.
2. Story filename without extension, if a story file path is provided.
3. Story title normalized to lowercase kebab-case.
4. Timestamp-prefixed fallback only if no stable key can be inferred.

Examples:

```text
_condamad/stories/70-23-services-dry-zero-legacy/
_condamad/stories/70-20-ai-engine-adapter-cleanup/
_condamad/stories/2026-04-25-generated-story/
```

## 5. Capsule Structure

The canonical capsule structure is:

```text
_condamad/stories/<story-key>/
  00-story.md
  generated/
    01-execution-brief.md
    03-acceptance-traceability.md
    04-target-files.md
    06-validation-plan.md
    07-no-legacy-dry-guardrails.md
    10-final-evidence.md
```

Optional files may be added when useful:

```text
  generated/
    02-context-map.md
    05-implementation-plan.md
    08-subagent-briefs.md
    09-dev-log.md
```

The required files are enough to implement a story. Optional files should be generated only when they materially improve safety, traceability, or reviewer usefulness.

## 6. File Responsibilities

### 6.1 `00-story.md`

`00-story.md` is the human-owned story source inside the capsule.

It must contain the original story content or a faithful copy of the original story file. It may include:

- Story title
- Goal
- Context
- Acceptance Criteria
- Tasks or scope
- Constraints
- Definition of Done
- Explicit non-goals

Codex must not rewrite business intent, acceptance criteria, or scope in this file unless the user explicitly asks for story editing.

Allowed edits during implementation are limited to status or completion metadata only when the original story format requires it and the story instructions allow it.

### 6.2 `generated/01-execution-brief.md`

This file translates the story into concise Codex execution instructions.

It must include:

- Story key
- Primary objective
- Implementation boundaries
- Non-goals
- Required preflight checks
- Write rules
- Completion definition
- Halt conditions

It must be short, direct, imperative, and implementation-oriented.

It must not restate the entire story.

### 6.3 `generated/03-acceptance-traceability.md`

This file maps every acceptance criterion to expected implementation and validation evidence.

It must contain a table with at least these columns:

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|

Rules:

- Every AC from `00-story.md` must appear exactly once.
- No AC may be merged with another AC unless the story itself defines them as combined.
- Each AC must have a validation strategy before implementation begins.
- The final status must be `Passed`, `Failed`, `Blocked`, or `Not applicable with justification`.
- A story cannot be marked complete while any AC is `Pending`.

### 6.4 `generated/04-target-files.md`

This file guides repo exploration and limits unnecessary edits.

It must include:

- Files and directories that must be read before implementation
- Required `rg` searches
- Files likely to be modified
- Files likely to be deleted or moved
- Files forbidden to modify unless directly justified
- Existing tests to inspect first

This file may start as an initial hypothesis, but Codex must update it after repository inspection.

It must distinguish between:

- Must read
- Must search
- Likely modified
- Forbidden unless justified

### 6.5 `generated/06-validation-plan.md`

This file defines the validation commands and evidence expected for the story.

It must include:

- Targeted tests
- Architecture or import guard checks
- Static checks
- Full regression commands when feasible
- Legacy-negative searches
- Handling rules for commands that cannot be executed

Each command must be documented with:

- Command
- Purpose
- Expected success condition
- Whether it is mandatory or conditional

If a command cannot be run, Codex must record:

- The exact command
- Why it was not run
- The risk created by not running it
- The fallback evidence used, if any

### 6.6 `generated/07-no-legacy-dry-guardrails.md`

This file applies the No Legacy and DRY contract to the specific story.

It must include:

- Forbidden legacy patterns relevant to the story
- Canonical destinations or namespaces
- Legacy symbols, imports, files, or concepts to search for
- Required negative evidence
- Exceptions, if explicitly allowed by the story
- Review checklist

It must be derived from the stable reference file:

```text
.agents/skills/condamad-dev-story/references/no-legacy-contract.md
```

When the story is explicitly about cleanup, refactoring, canonicalization, LLM runtime hardening, backend namespace convergence, service cleanup, DB cleanup, or architecture enforcement, this file is mandatory and must be story-specific.

### 6.7 `generated/10-final-evidence.md`

This file is the final review handoff.

It must include:

- Final story status
- AC-by-AC validation table
- Files changed
- Files deleted
- Tests added or updated
- Commands run and results
- Commands not run and reasons
- Legacy / DRY evidence
- Final `git status --short`
- Known limitations
- Suggested reviewer focus

A story is not complete until this file is filled with concrete evidence.

## 7. Optional Files

### 7.1 `generated/02-context-map.md`

Use when the story depends on prior architecture decisions, existing canonical paths, deprecated paths, or cross-module relationships.

Recommended for:

- Backend architecture stories
- LLM runtime stories
- Service namespace cleanup
- DB model cleanup
- Entitlement or canonical pipeline stories

### 7.2 `generated/05-implementation-plan.md`

Use when the implementation requires multiple coordinated edits, moves, deletions, migrations, or test updates.

It should include:

- Initial findings
- Proposed changes
- Files to modify
- Files to delete
- Tests to add or update
- Risk assessment
- Rollback strategy

Codex should generate or update this file before writing code for complex stories.

### 7.3 `generated/08-subagent-briefs.md`

Use only for large stories where parallel read-only exploration helps.

Subagents must be read-only unless the user explicitly authorizes parallel writes.

Recommended subagent roles:

- DRY / duplication scan
- No Legacy scan
- Test coverage scan
- Documentation / reference scan

The main agent remains responsible for all writes and final decisions.

### 7.4 `generated/09-dev-log.md`

Use when the implementation is long, risky, or likely to require reviewer traceability.

It should include:

- Preflight status
- Search evidence
- Implementation notes
- Commands run
- Decisions made
- Issues encountered
- Final status

## 8. Capsule Generation Rules

When a capsule does not exist, Codex must:

1. Infer the story key.
2. Create the capsule directory.
3. Create `00-story.md` from the source story.
4. Generate the required files under `generated/`.
5. Validate that every AC has a traceability row.
6. Validate that a validation plan exists before implementation.
7. Validate that No Legacy / DRY guardrails exist when the story touches architecture, refactoring, cleanup, canonical namespaces, services, DB models, or LLM runtime.
8. Continue implementation only after the capsule is complete.

The user must not be asked to manually create the capsule files unless generation is impossible due to missing story content or filesystem access.

## 9. Capsule Validation Rules

Before implementation, Codex must verify:

- `00-story.md` exists and is readable.
- `generated/01-execution-brief.md` exists.
- `generated/03-acceptance-traceability.md` exists and covers all ACs.
- `generated/04-target-files.md` exists.
- `generated/06-validation-plan.md` exists.
- `generated/07-no-legacy-dry-guardrails.md` exists when required.
- There is no contradiction between story scope and execution brief.
- The validation plan includes at least one objective test or check.

If validation fails, Codex must repair the capsule before coding.

## 10. Implementation Rules

During implementation, Codex must:

- Run preflight repository checks.
- Protect unrelated user changes.
- Read the target files before editing.
- Search for existing patterns before adding new abstractions.
- Prefer canonical paths and existing architecture.
- Avoid compatibility wrappers, shims, aliases, and duplicate paths.
- Update traceability as evidence becomes available.
- Update final evidence before declaring completion.

Codex must not:

- Treat generated capsule files as more authoritative than `00-story.md` for business intent.
- Mark an AC as passed without code and validation evidence.
- Hide skipped tests.
- Preserve legacy paths for convenience.
- Create additional architecture variants unless explicitly required.

## 11. Evidence Standard

Evidence must be concrete and reviewable.

Acceptable evidence includes:

- File paths and symbols changed
- Test names and test command output summaries
- Static check command summaries
- `rg` command summaries for negative legacy evidence
- `git diff --stat`
- Final `git status --short`
- Explicit reviewer notes

Unacceptable evidence includes:

- “Looks good”
- “Should pass”
- “Implemented as requested” without test or code reference
- Hidden assumptions
- Silent skipped commands

## 12. Completion Criteria

A CONDAMAD story capsule is complete when:

- Every required capsule file exists.
- Every AC has final status and evidence.
- Required commands have passed or skipped commands are justified.
- No forbidden legacy pattern remains unless explicitly allowed.
- File changes are listed.
- Final evidence is complete.
- The story is ready for review.

The final answer to the user must summarize:

- Story key
- Final status
- Files changed
- Tests and checks run
- Remaining risks, if any
- Path to `generated/10-final-evidence.md`

## 13. Review Handoff

The reviewer should be able to inspect only:

1. `00-story.md`
2. `generated/03-acceptance-traceability.md`
3. `generated/06-validation-plan.md`
4. `generated/07-no-legacy-dry-guardrails.md`
5. `generated/10-final-evidence.md`
6. The git diff

and understand whether the story is complete.

If this is not possible, the capsule is insufficient.

## 14. Anti-Pattern Checklist

Reject or repair the capsule if it contains any of these patterns:

- Generated files that contradict the source story
- ACs missing from traceability
- Validation plan with only vague manual checks
- No final evidence file
- No negative legacy search for cleanup/refactor stories
- Broad “read the whole repo” instructions without target files or searches
- No explicit non-goals
- No halt conditions
- No reviewer focus
- Evidence written before implementation and not updated after changes

## 15. Minimal Capsule Template

Use this when generating a capsule quickly:

```text
_condamad/stories/<story-key>/
  00-story.md
  generated/
    01-execution-brief.md
    03-acceptance-traceability.md
    04-target-files.md
    06-validation-plan.md
    07-no-legacy-dry-guardrails.md
    10-final-evidence.md
```

The user provides or references `00-story.md`.

Codex generates everything else.
