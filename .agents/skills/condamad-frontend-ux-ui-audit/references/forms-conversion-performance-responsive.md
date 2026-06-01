# Forms, Conversion, Performance UX, and Responsive Rules

Use these rules when auditing forms, checkout, signup, onboarding, search,
pricing, loading, network states, and mobile behavior.

## Forms and Conversion

- A field must ask one question only.
- Labels must remain visible during and after input.
- Errors must be specific, natural-language, and repairable: what is wrong,
  why if useful, and what to do next.
- Minimize input. Remove non-essential fields, prefill when possible, use
  autocomplete, suggestions, scanning, wallets, or selection controls.
- User data must not be lost after back navigation, refresh, server error, or
  validation error on long or important forms.
- CTA labels must describe the real action, especially for important actions.

Block readiness when:

- placeholder is the only label;
- critical form data can be lost;
- an error says only "Error", "Invalid", or "Something went wrong";
- a payment, signup, subscription, deletion, or submission CTA is vague;
- the user cannot know what to correct.

## Performance UX

- Perceived speed must be designed: loading states, skeletons, immediate
  feedback, and latency messages.
- Track Core Web Vitals or equivalent page performance for key pages: LCP, INP,
  CLS or team-defined thresholds.
- Every click, tap, save, submit, or mutation must show immediate feedback.
- Network and server failures must be anticipated: offline, timeout, service
  unavailable, payment failed, save failed.

Block readiness when:

- the page can show a blank screen without feedback;
- a button gives no visible reaction after click;
- a loader can run indefinitely without explanation;
- server/network failure does not explain what happened or what to do.

## Mobile and Responsive

- Mobile must not be a mechanically compressed desktop page.
- Reorder content, interactions, density, and controls for small screens.
- Frequent actions must be reachable and comfortably tappable.
- Complex tables must adapt into cards, prioritized columns, filtered views, or
  comparison-friendly layouts.
- Avoid long manual mobile input where autocomplete, selection, scanning,
  wallets, or prefilled data are possible.

Block readiness when:

- mobile prevents the critical task;
- primary controls are too small, too high, or too close;
- horizontal table scrolling prevents understanding or action;
- content is clipped, overlapped, or unusable at zoom or small widths.

## Edge Case QA

Check:

- long names;
- long translations;
- no results;
- absent data;
- network error;
- slow connection;
- expired session;
- permission denied;
- browser zoom;
- small mobile viewport.

## Audit Questions

- Does every field have a durable, accessible label?
- Does every error tell the user how to fix it?
- Can the user recover without losing work?
- Does every action produce feedback quickly?
- What happens offline, on timeout, or on server failure?
- Can mobile users complete the same critical task?
