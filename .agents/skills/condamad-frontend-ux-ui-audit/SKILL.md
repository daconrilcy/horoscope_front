---
name: condamad-frontend-ux-ui-audit
description: >
  Orchestrate a complete UX/UI audit of a frontend page, screen, route,
  screenshot, design, or user journey and produce a prioritized correction
  plan. Use when the user asks to analyze frontend quality, usability,
  accessibility, conversion, responsive behavior, trust, content, design-system
  consistency, AI UX, anti-dark-pattern risks, or production readiness. The
  skill loads specialized references only as needed and returns P0/P1/P2
  findings with acceptance criteria, QA checks, and implementation guidance.
---

<!-- Skill CONDAMAD d'orchestration pour audit UX/UI frontend. -->

# CONDAMAD Frontend UX/UI Audit

Use this skill to audit a frontend page or journey against CONDAMAD UX/UI
governance rules, then produce an actionable correction plan. The output must
connect every important issue to evidence, user impact, priority, concrete
correction, acceptance criteria, and validation.

Do not modify application code by default. Produce the audit and correction
plan first unless the user explicitly asks for implementation.

## Core Principle

Do not deliver aesthetic opinions. Deliver operational product quality
judgment.

Every finding must answer:

- what is wrong;
- where it appears;
- why it matters for the user or business;
- which rule family it violates;
- how to fix it;
- how to verify that the fix is done.

## Required References

Load only the references that match the page and request. Always load:

- `references/priority-and-gates.md`
- `references/output-contract.md`

Load additional references by audit surface:

- Product framing, journey, metrics, information architecture:
  `references/product-and-information-architecture.md`
- Visual hierarchy, UI craft, accessibility:
  `references/visual-ui-and-accessibility.md`
- Forms, conversion, performance, responsive:
  `references/forms-conversion-performance-responsive.md`
- AI UX, ethics, trust, privacy, safety:
  `references/trust-ethics-ai-privacy.md`
- Design system, UX writing, handoff, QA, measurement:
  `references/design-system-content-handoff.md`
- Definition of Ready, Definition of Done, ticket-ready remediation output:
  `references/readiness-and-ticket-contract.md`

For full audits, production readiness audits, or broad requests without a
narrowly named surface, load all references. For narrow audits, load only the
always-required references plus the matching specialist references.

If the audit targets an existing repository page, also apply relevant local
instructions such as `AGENTS.md`, `_condamad/stories/regression-guardrails.md`
when present, and neighboring page/design-system conventions.

## Scope Control

Use this skill for:

- full UX/UI audit of a page, route, screenshot, or design;
- production readiness review before launch;
- prioritized correction plan for a frontend page;
- conversion, form, checkout, onboarding, pricing, landing, dashboard, or
  settings review;
- mobile/responsive, accessibility, trust, content, and state QA;
- AI feature UX review;
- anti-dark-pattern and privacy/confidence review.

Do not use this skill for:

- isolated CSS fixes with an obvious local cause;
- pure implementation tasks where the plan is already approved;
- generic React development without UX/UI audit;
- copy-only edits unless the request is specifically about UX writing quality.

For narrow requests, return a narrow audit. For launch readiness, critical
journeys, or high-risk flows, run the full orchestration.

## Audit Modes

Infer the mode from the request:

- **Quick screen audit**: screenshot, single visible page, or narrow UI concern.
- **Full page audit**: rendered page plus code or enough context to assess the
  page end to end.
- **Journey audit**: multi-step flow such as signup, checkout, onboarding,
  search, cancellation, payment, upload, or AI generation.
- **Production readiness audit**: launch gate review using P0 blockers and
  definition of done.
- **Correction plan handoff**: convert findings into implementation tasks for
  design, React, styling, QA, and measurement.
- **Ticketization mode**: convert the correction plan into product/design/dev
  tickets with problem, objective, UX/UI rules, acceptance criteria, metric,
  owner, and validation.

Ask a clarification question only when the missing answer would materially
change risk classification or correction strategy. Otherwise infer and label
assumptions.

## Evidence Workflow

For existing frontend pages:

1. Inspect applicable instructions and guardrails.
2. Identify page type, route, primary user goal, primary action, and risk level.
3. Review rendered evidence when available or easy to obtain.
4. Inspect directly relevant components, styles, tokens, states, forms, and
   neighboring pages.
5. Test or reason through desktop, mobile, keyboard, focus, loading, empty,
   error, success, and edge states.
6. Label any finding based on incomplete evidence as a hypothesis and name the
   validation needed.

For screenshot or design-only audits:

1. Audit visible hierarchy, IA, content, controls, trust, accessibility risks,
   mobile implications, and missing states.
2. Do not invent implementation details. Express implementation guidance as
   likely areas: layout, tokens, component states, form behavior, tracking.
3. Mark non-visible behavior as "to verify".

For journey audits:

1. Map the start, user objective, steps, decision points, risks of abandonment,
   error states, and success metric.
2. Audit the complete task, not isolated screens.
3. Treat data loss, hidden cost, inaccessible step, blocked mobile completion,
   or irreversible action without confirmation as P0.

## Specialist Lanes

Run the audit through these internal lanes, then consolidate. Do not show
separate transcripts unless useful.

### Product and Journey

Check objective clarity, user intent, flow, metric, critical path, decision
order, navigation, location cues, CTA priority, and abandonment risks.

### Visual UI and Accessibility

Check readability, hierarchy, contrast, focus, keyboard, typography, semantic
color, touch targets, motion, responsive visual stability, and whether visual
effects serve comprehension.

### Forms, Conversion, and Performance UX

Check field clarity, labels, errors, data preservation, CTA wording, loading
feedback, perceived speed, server/network failures, and conversion friction.

### Trust, Ethics, AI, Privacy, and Safety

Check transparency of costs, consent symmetry, cancellation, data collection
justification, sensitive action confirmation, AI explainability, human control,
and personalization control.

### Design System, Content, Handoff, QA, and Measurement

Check component reuse, complete states, tokens, hardcoded values, UX writing,
empty states, realistic content, acceptance criteria, analytics, QA coverage,
and post-launch measurement.

## Prioritization

Use P0/P1/P2 from `references/priority-and-gates.md`.

Default escalation:

- P0 for anything that blocks task completion, accessibility, trust, safety,
  data preservation, transparency, or production readiness.
- P1 for strong degradation of comprehension, conversion, coherence,
  maintainability, perceived quality, or confidence.
- P2 for refinements that improve polish, consistency, or perception without
  blocking launch.

Never downgrade a P0 because it is expensive to fix. Cost affects the plan, not
the severity.

## Scoring

For full audits, score these criteria from 1 to 5:

- Clarity
- Utility
- Hierarchy
- Accessibility
- Performance UX
- Coherence
- Trust
- Control
- Content
- Measurement

Any score below 4 in clarity, hierarchy, accessibility, trust, or control means
the page should not be considered ready without correction. Any score below 3
in accessibility, trust, or control on a critical journey is normally P0.

## Output Rules

Use `references/output-contract.md` for final structure.

The final audit must include:

- executive verdict;
- score table when scope is full audit or launch readiness;
- prioritized P0/P1/P2 findings;
- correction plan by phase;
- acceptance criteria;
- QA and validation plan;
- implementation guidance if repository context exists;
- unresolved decisions or assumptions.

For production readiness or handoff requests, also include Definition of Ready,
Definition of Done, and ticket-ready remediation items from
`references/readiness-and-ticket-contract.md`.

Do not include generic advice. Replace vague recommendations with concrete
actions.

Bad:

- "Improve spacing."
- "Make the UI more modern."
- "Add better error handling."

Good:

- "Make the primary CTA visually dominant in the pricing footer; the current
  three equal-weight buttons create decision ambiguity. Acceptance: one primary
  action is identifiable within 3 seconds at desktop and mobile widths."
- "Replace placeholder-only labels with persistent labels for email and
  password. Acceptance: each input has an accessible name and the label remains
  visible after typing."
- "Add a retryable network error state for the upload step. Acceptance: timeout
  shows cause, next action, and preserves selected files."

## Non-Negotiables

Before returning, check whether any non-negotiable is present:

- critical action without confirmation;
- user form data can be lost;
- error does not explain how to fix the issue;
- primary journey is not keyboard usable;
- focus is invisible;
- contrast makes critical content hard to read;
- mobile prevents task completion;
- cost or commitment is hidden until the final step;
- refusing consent is harder than accepting;
- AI performs important actions without user control;
- critical page is slow, unstable, or lacks loading feedback;
- key journey has no success measurement.

If yes, report it as P0 and make it visible in the executive verdict.

## Final Self-Review

Before answering, verify:

- every P0 has a concrete remediation and acceptance criterion;
- findings are ordered by user risk, not by page order;
- each recommendation names the affected surface;
- code-level guidance is not invented when code was not inspected;
- accessibility issues are not softened into polish issues;
- mobile and keyboard risks are explicitly covered;
- unresolved assumptions are labeled;
- the correction plan can be handed to design/dev/QA without reinterpretation.
- production-readiness audits explicitly cover Definition of Ready and
  Definition of Done;
- ticketization requests produce self-contained tickets, not only findings.
