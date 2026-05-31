# Story Authoring Principles

<!-- Doctrine de redaction des stories CONDAMAD pour Codex. -->

## Core Principle

A CONDAMAD story is not background documentation. It is an execution contract
for a coding agent.

The story must be:

- mono-domain;
- bounded;
- testable;
- explicit about non-goals;
- grounded in repository evidence or clearly marked assumptions;
- strict about DRY and No Legacy.

## One Story, One Domain

Each story must belong to exactly one responsibility area. Use a canonical path
when possible, for example:

```text
backend/app/services/billing
frontend/src/api
frontend/src/pages/account
```

Do not combine backend service migration, frontend UX changes, and unrelated
test cleanup in one story. Split instead.

## No Vague Intent

Avoid broad verbs unless they have a measurable target. The following patterns
are not acceptable by themselves:

- improve;
- cleanup;
- refactor everything;
- as needed;
- where relevant;
- etc.

Replace them with observable outcomes, target files, forbidden paths, and
validation evidence.

## Evidence Over Confidence

Repo facts must come from files, commands, tests, or quoted user-provided
source material. If a fact is inferred, say so. If evidence is unavailable,
state the assumption risk in the story.

