# Design System, UX Writing, Handoff, QA, and Measurement Rules

Use these rules when auditing component consistency, content quality, state
coverage, delivery readiness, QA, analytics, and post-launch learning.

## Design System

- Check existing components before proposing a new component.
- Every component must define relevant states: default, hover, focus, active,
  disabled, loading, error, success, empty.
- Tokens should replace hardcoded values for color, typography, spacing,
  radius, shadow, z-index, and motion.
- Component documentation must explain usage, behavior, accessibility, and when
  not to use the component.
- Any exception to the design system must be justified by product, technical,
  or contextual need.

Classify as P0 when a critical component lacks required states. Classify as P1
when hardcoded values, local variants, or undocumented usage create drift.

## UX Writing

- Titles must help the user understand the page or task.
- Error messages must offer a solution.
- Empty states must explain why the state is empty and what to do next.
- Language must be concrete and avoid unexplained jargon, acronyms, and
  internal terms.

Block readiness when:

- an error cannot be repaired from the message;
- an empty critical screen gives no next step;
- titles or labels prevent task understanding.

## Handoff Design to Development

- No screen should enter development without state specifications.
- Tickets should include testable UX acceptance criteria.
- Breakpoints should define layout, visibility, and interaction behavior.
- Final or realistic content must be used before delivery, including long
  content and empty cases.

Classify as P0 when a developer cannot know critical behavior for loading,
error, success, empty, disabled, focus, or responsive states. Classify as P1
when content or breakpoint specs are incomplete but recoverable.

## QA UX/UI

Test journeys, not only screens. Include:

- signup;
- purchase;
- search;
- edit;
- cancellation;
- error recovery;
- back navigation.

Test edge cases:

- long content;
- zero result;
- missing data;
- server/network error;
- low connection;
- expired session;
- denied permissions;
- browser zoom;
- varied screen sizes.

## Measurement

- Each launch should have a measurement plan: events, funnels, goals, and alert
  thresholds.
- Post-launch decisions should use analytics, user feedback, support, heatmaps
  when appropriate, and qualitative tests.
- Recurring support irritants should feed the UX roadmap.

Block readiness when a critical journey launches with no way to measure
completion, failure, or abandonment.

## Audit Questions

- Does a matching component already exist?
- Are all relevant states designed and implemented?
- Are tokens used instead of one-off visual values?
- Do titles, labels, errors, and empty states help action?
- Can QA test the full journey and edge cases?
- Are realistic contents represented?
- Is success measurable after launch?
