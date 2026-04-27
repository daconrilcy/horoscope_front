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

## Step 2c - Select Required Contracts

After selecting the primary archetype, select all required contracts:

- Runtime Source of Truth Contract
- Baseline Snapshot Contract
- Ownership Routing Contract
- Allowlist Exception Contract
- Contract Shape Contract
- Batch Migration Contract
- Reintroduction Guard Contract
- Persistent Evidence Contract

Do not draft the story until required contracts are selected.

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
For conditional transverse sections, choose exactly one matching active or
not-applicable snippet from `templates/snippets/` and inline it into the story.

The draft must include:

- objective;
- trigger/source;
- domain boundary;
- operation contract;
- required contracts table;
- selected transverse contract snippets;
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

From the skill directory:

```bash
python -B scripts/condamad_story_validate.py <story_path>
python -B scripts/condamad_story_validate.py --explain-contracts <story_path>
python -B scripts/condamad_story_lint.py <story_path>
```

From the repository root:

```bash
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py <story_path>
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts <story_path>
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py <story_path>
```

For release-grade checks, run lint in strict mode:

```bash
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict <story_path>
```

Fix the story until all required validation commands pass. A story must not be
marked `ready-for-dev` while the validator or strict lint fails.

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
- Can the story pass with `rg` only while runtime behavior is wrong?
- Can the story change a contract while `Behavior change allowed: no`?
- Can the agent keep an exception without expiry?
- Can a broad allowlist hide a future regression?
- Can the agent skip baseline capture?
- Can the agent skip persistent evidence?
- Can one AC be partially implemented and still look complete?
- Can an internal test import be mistaken for external usage?

If yes, tighten the story before writing final output.

## Step 7 - Write Final Story

Persist the final story at the requested path or at:

```text
_condamad/stories/<story-key>/00-story.md
```

Report the story path and validation commands run.

Before packaging the skill, remove generated Python artifacts and verify none
remain under `condamad-story-writer`:

```bash
find .agents/skills/condamad-story-writer -type d -name "__pycache__" -prune -exec rm -rf {} +
find .agents/skills/condamad-story-writer -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
```
