# CONDAMAD No Legacy Contract

## Purpose

This contract defines the non-negotiable rules that a CONDAMAD implementation agent must enforce whenever a story has a DRY, cleanup, canonicalization, migration, namespace convergence, or legacy-removal objective.

The goal is not to make legacy code quieter. The goal is to remove ambiguity from the executable system.

A story is not complete when the new path works. A story is complete only when the old competing path can no longer be used as an active, nominal, tolerated, or silently preserved execution path.

## Core doctrine

CONDAMAD follows five rules:

1. One responsibility has one canonical implementation path.
2. Canonical configuration or canonical structure must fail explicitly when missing.
3. Compatibility must never be preserved by inertia.
4. Deletion is preferred over passive backward compatibility when the story intent is cleanup or convergence.
5. Completion requires negative evidence: the removed legacy path must be searched for and proven absent from active code, tests, docs, and registries relevant to the story scope.

## Definitions

### Canonical path

A canonical path is the single authoritative module, service, namespace, registry, configuration entry, or runtime route that the project intentionally supports for a responsibility.

A canonical path is not simply the newest path. It must be the path validated by the story, architecture notes, AGENTS.md, project context, or existing code doctrine.

### Legacy path

A legacy path is any older, transitional, duplicated, tolerated, deprecated, compatibility-oriented, or ambiguous path that provides the same or overlapping responsibility as the canonical path.

Legacy includes code, imports, registry aliases, configuration keys, tests, docs, comments, fixtures, scripts, and compatibility helpers.

### Shim

A shim is a thin layer that preserves an old API, import path, class name, function name, route, configuration key, or behavior by delegating to a newer implementation.

For CONDAMAD cleanup stories, a shim is legacy unless explicitly authorized by the story.

### Compatibility wrapper

A compatibility wrapper is any object, function, module, route, registry entry, or alias whose purpose is to keep an old consumer working without moving that consumer to the canonical path.

### Silent fallback

A silent fallback is any behavior that continues execution through an alternate, legacy, inferred, default, or compatibility path when canonical data, configuration, implementation, or routing is missing.

A silent fallback is forbidden on canonical paths.

### Duplicate active implementation

A duplicate active implementation exists when two or more code paths can perform the same responsibility in production or nominal test execution.

The duplicate may be obvious, such as two services with similar names, or indirect, such as a registry that can route to both canonical and old handlers.

## Absolute prohibitions

The implementation agent must not introduce or preserve any of the following unless the story explicitly authorizes it and defines a bounded removal plan:

- Compatibility shim.
- Re-export module preserving an old import path.
- Alias from old class/function/module names to new names.
- Fallback from canonical path to legacy path.
- Dual-read logic from both legacy and canonical configuration.
- Dual-write logic to both legacy and canonical persistence targets.
- Transitional registry key that maps an old identifier to a new implementation.
- Deprecated route kept active for convenience.
- Old import path kept alive to avoid touching consumers.
- Test fixture that validates legacy behavior as nominal behavior.
- Documentation that presents legacy behavior as supported.
- TODO comment that defers legacy removal without a dated, tracked, story-bound removal criterion.
- Broad exception handler that hides missing canonical configuration and continues with defaults.
- Environment-variable fallback that revives a removed behavior.
- “Temporary” compatibility retained without an explicit AC and expiry condition.

## Required behavior

### Canonical-only routing

All nominal consumers must call the canonical path directly.

If a consumer still imports, references, or executes a legacy path, the story is not done.

### Explicit failure over fallback

When canonical configuration, canonical registry data, canonical release snapshot, canonical assembly, canonical namespace, or canonical service wiring is missing, the implementation must fail explicitly with the project’s expected exception type.

The implementation must not:

- infer a replacement from legacy fields;
- retry through an older service;
- default to a generic behavior;
- silently continue with partial configuration;
- convert a canonical failure into a success path.

### Deletion over preservation

If the story is about cleanup, refactor, namespace convergence, or legacy elimination, the implementation should delete obsolete paths instead of keeping compatibility layers.

If deletion is unsafe, the implementation agent must document the blocker in final evidence and must not mark the relevant AC as fully satisfied.

### Tests must lock the new invariant

Tests must prove the canonical path works and the legacy path cannot silently return.

Preferred tests:

- import regression tests for canonical imports;
- negative import tests for removed modules when appropriate;
- architecture guard tests scanning forbidden paths or symbols;
- registry tests proving old keys are absent;
- configuration validation tests proving missing canonical config fails explicitly;
- regression tests proving consumers no longer use legacy imports;
- golden or snapshot tests when the story changes runtime observability or structural outputs.

### Search evidence is mandatory

Every No Legacy story must include search evidence.

Searches must be adapted to the story, but typical patterns include:

```bash
rg "legacy|compat|shim|fallback|deprecated|alias" backend/app backend/tests
rg "from app\.services" backend/app backend/tests
rg "import app\.services" backend/app backend/tests
rg "<removed_symbol>|<old_module>|<old_registry_key>" backend/app backend/tests docs scripts
```

If a search returns hits, each hit must be classified as one of:

- allowed historical reference;
- comment/doc requiring update;
- active legacy to remove;
- false positive;
- out-of-scope with justification.

Unclassified hits are not acceptable final evidence.

## Allowed exceptions

Exceptions are allowed only when all conditions below are true:

1. The story explicitly authorizes a temporary compatibility behavior.
2. The compatibility behavior has a named owner or follow-up story.
3. The behavior is isolated behind a clearly named transitional module or flag.
4. Tests prove the compatibility behavior is bounded and does not become nominal.
5. Final evidence records the sunset condition.

If any of these conditions is missing, the exception is forbidden.

## Required implementation sequence

### 1. Identify canonical truth

Before editing, the implementation agent must identify:

- the canonical namespace;
- the canonical service or module;
- the canonical configuration source;
- the canonical registry or routing mechanism if any;
- the consumers that must be migrated;
- the legacy paths that must disappear.

The result must be reflected in the generated acceptance traceability file or final evidence.

### 2. Search before creating

Before adding a helper, class, service, registry, guard, validator, or script, the implementation agent must search for existing equivalents.

Creating a new abstraction is allowed only when:

- no suitable canonical abstraction already exists;
- the new abstraction has a single clear responsibility;
- the new abstraction does not duplicate active behavior;
- the new abstraction is placed in the canonical namespace.

### 3. Migrate consumers

All active consumers must be updated to the canonical path.

This includes:

- application code;
- tests;
- fixtures;
- scripts;
- registries;
- seed/bootstrap code;
- docs that define supported usage;
- CI or quality-gate checks when relevant.

### 4. Remove legacy path

After consumers are migrated, the obsolete path must be removed.

Removal may include:

- deleting modules;
- deleting imports;
- deleting registry entries;
- deleting compatibility flags;
- deleting old config keys;
- deleting stale tests;
- deleting stale docs;
- updating package exports.

### 5. Add regression guards

The implementation must add or update guardrails that make legacy reintroduction difficult.

Examples:

- a pytest guard that fails if forbidden imports reappear;
- a static check in the project quality gate;
- a test that validates there is only one active canonical registration;
- a test that validates canonical failure is explicit;
- a doc-conformity check if the story affects project doctrine.

### 6. Produce final evidence

The implementation agent must update final evidence with:

- changed files;
- deleted files;
- commands run;
- commands not run and why;
- search commands and classification summary;
- AC-by-AC validation;
- remaining risks;
- reviewer focus points.

## Acceptance standard

A No Legacy AC is satisfied only when all of the following are true:

- canonical behavior is implemented;
- all nominal consumers use the canonical path;
- legacy path is removed or explicitly blocked;
- no active compatibility wrapper remains;
- no silent fallback remains;
- tests pass;
- negative search evidence is recorded;
- final evidence maps the AC to code and validation.

If any of these is missing, the AC is not done.

## Red flags during review

The reviewer must challenge the implementation if any of the following appears:

- “Kept for backward compatibility.”
- “Temporary alias.”
- “Fallback to old behavior.”
- “Preserved to avoid breaking tests.”
- “Deprecated but still supported.”
- “No consumers should use it, but it remains available.”
- “We can remove it later.”
- “Existing tests still import the old path.”
- “The old config field is still read if the new one is missing.”
- “The new implementation delegates to the old one.”
- “The old implementation delegates to the new one.”
- “Both namespaces exist but one is preferred.”

Each of these phrases usually means the story is not truly No Legacy.

## Severity classification

### Blocking

A blocking finding prevents the story from being marked ready for review.

Blocking examples:

- active fallback remains;
- compatibility wrapper remains;
- old import path still works;
- duplicate active implementation remains;
- missing canonical config does not fail explicitly;
- tests validate legacy behavior as supported;
- acceptance criteria are not mapped to evidence.

### Major

A major finding should be fixed before merge unless explicitly accepted by the reviewer.

Major examples:

- docs still reference legacy path as supported;
- search hits are not classified;
- guard tests are missing for a structural cleanup;
- deleted legacy path lacks regression coverage;
- final evidence does not list commands run.

### Minor

A minor finding does not usually block review but should be cleaned up.

Minor examples:

- stale comments mentioning old terminology;
- non-executable historical note not clearly marked historical;
- overly broad final evidence wording;
- missing reviewer focus note.

## Final reviewer checklist

Before marking a CONDAMAD No Legacy story as complete, verify:

- There is one canonical path for the responsibility.
- All active consumers use that path.
- Removed symbols, modules, routes, registry keys, and config keys are searched for.
- Every search hit is classified.
- No shim, alias, wrapper, or re-export preserves the old path.
- Missing canonical data fails explicitly.
- Tests protect both positive canonical behavior and negative legacy reintroduction.
- Final evidence maps each AC to code evidence and validation evidence.
- The story did not create a new parallel namespace while removing an old one.

## Final rule

Do not confuse migration with convergence.

Migration means the new path exists.
Convergence means the old competing path is gone, blocked, or explicitly outside the supported perimeter.

CONDAMAD requires convergence.
