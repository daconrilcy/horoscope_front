# CONDAMAD Principles

## Purpose

CONDAMAD is a Codex-native development method for implementing one story with maximum architectural discipline, minimum ceremony, and verifiable evidence.

CONDAMAD replaces a heavy BMAD-style procedural workflow with a smaller execution capsule that Codex can generate, follow, validate, and complete. The method is optimized for repository work: read the actual code, preserve the worktree, implement narrowly, run checks, and produce reviewable evidence.

## Definition

CONDAMAD means:

**CO**dex **N**ative **D**evelopment **A**gent **M**ethod for **A**rchitecture **D**iscipline.

Its goal is not to create more documentation. Its goal is to convert one story into an executable, traceable, testable implementation plan.

## Core model

A CONDAMAD story has one human source input:

```text
00-story.md
```

All other capsule files are generated or completed by Codex:

```text
generated/
  01-execution-brief.md
  03-acceptance-traceability.md
  04-target-files.md
  06-validation-plan.md
  07-no-legacy-dry-guardrails.md
  10-final-evidence.md
```

The user must not be asked to manually create the generated capsule files.

If only a story markdown file is provided, Codex must generate the missing capsule before implementation.

## Operating principles

### 1. The story defines scope, not process

The story is the source of functional and architectural intent.

Do not copy a large generic workflow into every story. Convert the story into a compact execution capsule and execute from that capsule.

### 2. Repository truth beats assumptions

Before modifying code, inspect the real repository.

Use existing code, imports, tests, configuration, and architecture as the source of truth. Never implement from the story alone when the repository can prove the actual structure.

### 3. One story, one capsule, one evidence trail

Each story must have a dedicated capsule directory.

The capsule must show:

- what Codex understood;
- what files Codex inspected;
- how each acceptance criterion maps to code and tests;
- what validations were run;
- what changed;
- what risks remain.

### 4. Traceability is mandatory

Every acceptance criterion must map to implementation evidence and validation evidence.

A story is not complete because code was changed. It is complete only when every AC can be traced to:

- changed or intentionally unchanged files;
- tests, guardrails, or checks;
- final evidence.

### 5. DRY is structural, not cosmetic

Do not create duplicate active paths for the same responsibility.

Before adding a helper, service, facade, registry, mapper, or guard, search for existing equivalents. Refactor or converge existing code when possible.

Duplication is allowed only when explicitly justified by different responsibilities, not because it is faster.

### 6. No Legacy means no tolerated compatibility by inertia

Do not preserve old behavior through wrappers, aliases, re-exports, compatibility imports, fallback branches, or transitional modules unless the story explicitly authorizes it.

When a canonical path exists, update consumers to the canonical path and remove the legacy path.

If removing a legacy path is unsafe within the story scope, record it as a blocker or residual risk. Do not silently keep it.

### 7. Canonical path wins

There must be one nominal path per responsibility.

If multiple modules, folders, services, registries, or models compete for the same responsibility, the implementation must converge toward the canonical path defined by repository rules, story context, or architecture docs.

### 8. Fail explicitly rather than fallback silently

When canonical configuration, registry entries, execution profiles, routes, mappings, or dependencies are missing, prefer explicit errors over silent fallback.

A fallback is acceptable only when the story says it is part of the nominal behavior and tests prove its boundaries.

### 9. Preserve the user's worktree

Before editing, inspect the current worktree state.

Do not overwrite unrelated changes. Do not revert user changes unless explicitly asked. Do not use destructive Git commands unless the user explicitly instructs it.

### 10. Small patches beat large rewrites

Prefer focused, reviewable changes.

Do not perform broad rewrites, renames, or formatting-only changes unless they are required by the story or validation tooling.

### 11. Tests are evidence, not decoration

Add or update tests where behavior, architecture boundaries, imports, configuration, or structural contracts change.

For behavior changes, prefer test-first or characterization tests.

For structural refactors, use import tests, architecture guard tests, negative search checks, and regression suites.

### 12. Validation must be explicit

Every completed story must list the exact commands run and their result.

If a command cannot be run, document:

- the exact command;
- why it was not run;
- the risk created by not running it.

### 13. Final evidence is required before completion

Do not mark a story as complete or ready for review until `generated/10-final-evidence.md` is filled.

The final evidence must include:

- story status;
- AC validation table;
- files changed;
- files deleted;
- tests added or updated;
- commands run;
- commands not run;
- DRY / No Legacy evidence;
- remaining risks;
- suggested reviewer focus.

### 14. Subagents are read-only by default

Subagents may be used for exploration, search, duplication analysis, legacy detection, or test discovery.

The main agent owns all writes.

Do not allow multiple agents to edit the same repository concurrently unless the user explicitly requests a parallel worktree strategy.

### 15. Prefer automation for repeatable checks

Use scripts for deterministic, repeated checks such as:

- capsule validation;
- acceptance traceability completeness;
- changed-file collection;
- forbidden legacy pattern scanning;
- final evidence consistency.

Do not rely only on prose when a repeatable check can be scripted.

## CONDAMAD lifecycle

### Phase 0 — Preflight

Before doing any work:

- identify the repository root;
- run or inspect `git status --short`;
- locate the story file;
- load relevant `AGENTS.md` instructions;
- identify whether a capsule already exists.

### Phase 1 — Capsule generation

If the capsule does not exist, create it.

Generate at minimum:

- `generated/01-execution-brief.md`;
- `generated/03-acceptance-traceability.md`;
- `generated/04-target-files.md`;
- `generated/06-validation-plan.md`;
- `generated/07-no-legacy-dry-guardrails.md`.

Do not start implementation until the capsule is coherent.

### Phase 2 — Repository reconnaissance

Search before editing.

Use repository-native search and inspect likely consumers, tests, registries, imports, and configuration.

Update the target-file map if the initial story assumptions are incomplete.

### Phase 3 — Implementation plan

Write or update the implementation plan before code changes.

The plan must include:

- proposed changes;
- expected files to modify;
- files to delete if relevant;
- tests to add or update;
- risks;
- rollback strategy.

### Phase 4 — Implementation

Implement the smallest change that satisfies the story.

Respect repository style and existing architecture.

Do not introduce unrelated improvements.

### Phase 5 — Validation

Run targeted tests first, then broader checks when feasible.

Use architecture guard checks when the story changes structure.

Use negative searches when the story removes legacy, fallback, alias, shim, or duplicate paths.

### Phase 6 — Evidence completion

Update `generated/10-final-evidence.md`.

Every AC must have a clear status and evidence.

### Phase 7 — Final response

Return a concise implementation report.

Include:

- story key;
- status;
- files changed;
- tests and commands run;
- commands skipped;
- remaining risks;
- suggested reviewer focus.

## Capsule file responsibilities

### `00-story.md`

Human-authored or copied source story.

It should contain the goal, context, acceptance criteria, constraints, non-goals, and definition of done.

### `generated/01-execution-brief.md`

Codex-generated operational brief.

It must reduce the story into precise execution instructions and stop conditions.

### `generated/03-acceptance-traceability.md`

Codex-generated AC matrix.

It must map each AC to expected code impact and validation evidence.

### `generated/04-target-files.md`

Codex-generated file map.

It must include files and directories to read, search terms to run, likely modified files, and forbidden or risky areas.

### `generated/06-validation-plan.md`

Codex-generated validation contract.

It must list targeted checks, architecture checks, full checks, and skipped-command reporting rules.

### `generated/07-no-legacy-dry-guardrails.md`

Codex-generated or template-based guardrail file.

It must make forbidden compatibility, duplication, fallback, shim, alias, and legacy behaviors explicit.

### `generated/10-final-evidence.md`

Codex-completed proof file.

It is the authoritative completion report for the story.

## Non-negotiable prohibitions

Do not:

- ask the user to manually create generated capsule files;
- edit unrelated files;
- hide skipped tests;
- mark completion without evidence;
- keep compatibility wrappers by inertia;
- create a new namespace when a canonical namespace exists;
- add fallback logic to avoid fixing configuration or imports;
- change acceptance criteria to match the implementation;
- modify story scope without explicit user instruction;
- use destructive Git commands without explicit user instruction.

## Completion standard

A CONDAMAD story is ready for review only when all of the following are true:

- every AC has implementation evidence;
- every AC has validation evidence;
- changed files are listed;
- deleted files are listed if applicable;
- tests or guardrails were added or justified;
- commands run are listed with results;
- commands not run are listed with reasons;
- DRY / No Legacy checks were performed when relevant;
- final worktree state is recorded;
- remaining risks are explicit.

## Glossary

### Canonical

The authoritative implementation path, namespace, registry, configuration, or runtime flow that the repository intends to support nominally.

### Legacy

Any obsolete, transitional, duplicated, backward-compatible, or deprecated path that remains only because older code once depended on it.

### Shim

A thin compatibility layer that preserves an old API, import path, or behavior while delegating to a new implementation.

### Silent fallback

A branch that hides missing or invalid canonical configuration by choosing another behavior without explicit failure.

### Duplicate active path

Two or more implementations, namespaces, registries, services, or entrypoints that can actively perform the same responsibility.

### Evidence

A concrete proof item such as a changed file, test, command output, guardrail, negative search result, or final validation note.

## Final rule

CONDAMAD exists to make Codex more autonomous, not to make the user maintain more paperwork.

One human story in. One generated capsule. One focused implementation. One evidence-backed result.
