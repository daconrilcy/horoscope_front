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
- current state evidence;
- target state;
- AC table with validation evidence;
- tasks mapped to ACs;
- mandatory reuse and DRY constraints;
- No Legacy / forbidden paths;
- files to inspect first;
- expected files to modify;
- dependency policy;
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

## Step 7 - Write Final Story

Persist the final story at the requested path or at:

```text
_condamad/stories/<story-key>/00-story.md
```

Report the story path and validation commands run.
