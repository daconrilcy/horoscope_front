# Product and Information Architecture Rules

Use these rules when auditing page purpose, journey structure, navigation,
decision flow, and metrics.

## Product Framing

- Each screen must have one dominant objective: inform, convert, compare,
  configure, buy, register, confirm, or solve a problem.
- Critical journeys must be documented or reconstructable: start point, user
  goal, steps, abandonment risks, metrics, and error states.
- Each UX decision must answer a real friction or opportunity: confusion,
  abandonment, slowness, error, low trust, excess effort, or low conversion.
- Each critical journey must have at least one success metric: conversion,
  completion, task time, error rate, activation, retention, satisfaction, or
  support ticket reduction.

Block readiness when:

- an important page mixes goals without hierarchy;
- a critical path cannot be described end to end;
- no success metric exists for a key journey.

## User Research and Assumptions

- For major journeys, prefer evidence from representative users or serious
  quantitative validation.
- State hypotheses explicitly: "We believe [change] helps [user] achieve
  [result], measured by [metric]."
- Prefer behavioral segments over decorative personas: new user, hurried
  expert, anxious buyer, comparing buyer, advanced admin, etc.

If evidence is absent, do not block by default unless the flow is high-risk;
label the assumption and propose validation.

## Information Architecture

- Navigation labels must match user vocabulary, not internal team names,
  acronyms, or organization structure.
- The user must always know where they are, what they can do, and how to go
  back.
- Use page titles, active navigation, breadcrumbs, step indicators, or progress
  markers when needed.
- The primary action must be visually prioritized by placement, label, and
  style.
- Content must be ordered according to the user's decision path. Critical
  information must appear before secondary detail.

Block readiness when:

- the user cannot locate themselves or recover orientation;
- several equal-weight CTAs compete on one decision point;
- critical information needed for the decision is hidden after marketing copy.

## Audit Questions

- What is the one thing this screen must help the user do?
- What is the next action the user should take?
- What decision must the user make before acting?
- What information is missing before that decision?
- What could make the user abandon the path?
- What metric proves the screen works?
- Does the page structure match that decision order?
