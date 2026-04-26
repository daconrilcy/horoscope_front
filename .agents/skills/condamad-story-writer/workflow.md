# CONDAMAD Story Writer Workflow

<!-- Workflow de generation d'une story CONDAMAD mono-domaine. -->

## Step 1 - Resolve Input

Identify the source type:

- brief;
- audit;
- code-review;
- architecture-decision;
- bug;
- refactor;
- existing story.

If the user provides only a broad goal, infer the smallest single-domain story
that can be implemented and validated independently. Split only when the user
explicitly asks for multiple stories or when one story would cross domains.

## Step 2 - Define Domain Boundary

Select exactly one domain and make the boundary visible:

- canonical path or package;
- in-scope behavior;
- out-of-scope behavior;
- explicit non-goals;
- forbidden adjacent domains.

## Step 2b - Select Story Archetype

Select exactly one primary archetype from
`references/story-archetypes.md`.

The archetype determines mandatory sections, AC patterns, validation evidence,
and anti-drift rules.

If the operation type is `remove`, or the story mentions route/module/field/API
deletion, legacy facade removal, compatibility surface removal, or dead-code
removal, load and apply `references/removal-story-contract.md`.

Do not write the final story until the archetype-specific contract has been
applied.

## Step 3 - Evidence Pass

Collect enough evidence to avoid invented repo facts:

- source brief or audit;
- applicable `AGENTS.md`;
- repository structure;
- existing implementation;
- relevant tests;
- forbidden legacy patterns;
- validation commands.

If repository evidence is unavailable, state that explicitly and record the
assumption risk.

## Step 4 - Draft Implementation Contract

Use `templates/story-template.md`.

The draft must include:

- objective;
- trigger/source;
- domain boundary;
- operation contract;
- current state evidence;
- target state;
- AC table with validation evidence;
- tasks mapped to ACs;
- mandatory reuse and DRY constraints;
- No Legacy / forbidden paths;
- files to inspect first;
- expected files to modify;
- dependency policy;
- removal contract when the operation or archetype requires it;
- validation plan;
- regression risks;
- dev agent instructions.

## Step 5 - Anti-Drift Validation

Before writing the final story, check:

- every task maps to at least one AC;
- every AC maps to validation evidence;
- no vague task language remains;
- no global refactor or broad cleanup is hidden in the scope;
- no new dependency is permitted without explicit justification;
- no compatibility shim, alias, fallback, or re-export is listed as acceptable.

## Step 6 - Story Lint

Run:

```bash
python -B scripts/condamad_story_validate.py <story_path>
python -B scripts/condamad_story_lint.py <story_path>
```

Fix the story until both pass. A story must not be marked `ready-for-dev` while
the validator fails.

## Step 6b - Adversarial Story Review

Before finalizing, review the generated story as if you were the dev agent
trying to misinterpret it.

Check:

- Can an agent choose between two valid implementation paths?
- Can an agent keep a legacy path and still claim success?
- Can an agent skip a route, file, field, type, or import because the
  classification is unclear?
- Can an agent pass ACs with grep-only evidence while behavior remains?
- Can an agent avoid deletion through repointing or soft-delete?
- Can an agent create a new route, wrapper, alias, or fallback?
- Can an agent mark `ready-for-dev` while user decision is needed?

If yes, tighten the story before writing final output.

## Step 7 - Write Final Story

Persist the final story at the requested path or at:

```text
_condamad/stories/<story-key>/00-story.md
```

Report the story path and validation commands run.
