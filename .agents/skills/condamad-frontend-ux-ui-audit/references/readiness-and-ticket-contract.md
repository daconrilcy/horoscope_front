# Readiness and Ticket Contract

Use this reference for production readiness audits, launch gates, handoff
reviews, and requests to turn audit findings into tickets.

## Definition of Ready UX/UI

A subject is ready to be designed only when these elements are known or
explicitly marked as missing:

- user problem;
- affected user segment or behavior;
- concerned journey;
- success metric;
- business, legal, technical, and brand constraints;
- required content, or owner for missing content;
- main product, UX, and business hypotheses;
- accessibility, performance, privacy, or compliance risks.

If one of these elements is missing, do not invent it. Mark the subject as
partially ready and name the decision or evidence required.

## Definition of Done UX/UI

An interface is ready for development or release only when the relevant items
are complete:

- complete journey is represented;
- desktop, tablet, and mobile behavior are defined when relevant;
- components exist or are documented;
- default, hover, focus, active, disabled, loading, error, success, and empty
  states are covered when applicable;
- error messages are written;
- empty states are planned;
- accessibility rules are integrated;
- contrasts are checked;
- keyboard behavior is specified and testable;
- edge cases are documented;
- realistic data and content were tested;
- developer acceptance criteria are written;
- analytics tracking is defined for critical journeys;
- QA can test the complete journey.

For release readiness, classify missing Done items as P0 when they block
critical task completion, accessibility, trust, data preservation, or
measurement. Otherwise classify as P1 or P2 according to impact.

## Ticket-Ready Remediation Format

When the user asks for tickets or an implementation-ready correction plan,
produce one ticket per coherent remediation. Do not create one ticket per tiny
visual symptom when a single user-visible outcome should own the fix.

Use this format:

```md
### <Ticket title>

**Problem:** <user friction or product risk>
**Objective:** Enable <user segment> to <action/result> with less <friction>.
**UX/UI rules:** <rule families or specific violated rules>
**Priority:** P0/P1/P2
**Owner:** Product / Design / Frontend / QA / Analytics
**Scope:** <screen, section, journey step, component, or file area>
**Acceptance criteria:**
- <testable condition>
- <testable condition>
**Validation:**
- <manual, automated, visual, accessibility, analytics, or browser check>
**Success metric:** <conversion/completion/activation/error/support metric, or "N/A" with reason>
```

## Ticket Quality Gate

A remediation ticket is not ready if:

- it only says "improve", "modernize", "clean up", or "fix UX";
- it lacks a user-visible outcome;
- it has no acceptance criteria;
- it does not identify the affected surface;
- it assigns ownership vaguely when multiple roles are involved;
- it cannot be verified by QA or analytics;
- it hides a product decision as an implementation task.

## Launch Checklist

Before recommending release, confirm:

- user understands the page without explanation;
- primary action is visible;
- final or realistic text is present;
- errors are useful;
- empty states are useful;
- loading states are present;
- back navigation works;
- entered data is not lost;
- mobile is usable;
- keyboard can complete the journey;
- focus is visible;
- contrast is acceptable;
- CTAs are explicit;
- edge cases were tested;
- costs and conditions are transparent;
- consent is clear and non-manipulative;
- sensitive actions require confirmation;
- performance is acceptable;
- tracking is in place;
- help or support appears where needed.
