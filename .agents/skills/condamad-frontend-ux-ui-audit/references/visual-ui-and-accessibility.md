# Visual UI and Accessibility Rules

Use these rules when auditing visual hierarchy, readability, interaction
clarity, accessibility, touch targets, and motion.

## Visual UI

- Style must never reduce readability. Validate effects against text, icon,
  button, and state legibility across themes and resolutions.
- Every visual effect must have a function: guide attention, confirm action,
  create hierarchy, or improve understanding.
- Typography must be systematic: H1, H2, H3, body, caption, label, helper,
  error, with consistent size, weight, spacing, and usage.
- Colors must be semantic: primary, secondary, success, error, warning,
  information, background, border, text.
- Avoid purely decorative glass, blur, texture, gradients, shadows, or motion
  that increase cognitive load.

Classify as P0 when style blocks reading or state understanding. Classify as P1
when hierarchy, color, or typography weakens comprehension or confidence.

## Accessibility

Target WCAG 2.2 AA as the minimum.

Check:

- keyboard navigation with Tab, Shift+Tab, Enter, Space, and Escape;
- visible focus for every interactive element;
- contrast for text, icons, links, buttons, and component states;
- labels, helper text, and error messages for form fields;
- screen-reader-compatible form naming and error announcement;
- information not conveyed only by color;
- sufficient touch target size and spacing.

Block readiness when:

- the primary journey is not keyboard usable;
- focus is hidden, removed, or masked by sticky layers or overlays;
- text or control contrast is insufficient for critical content;
- placeholders are used as the only labels;
- errors are only visual;
- selection, error, success, or warning depends only on color;
- touch targets make mobile actions unreliable.

## Motion

- Motion must serve comprehension: transition, confirmation, or state change.
- Animations must be fast and non-blocking.
- Respect `prefers-reduced-motion`; reduce or remove non-essential animation.

Classify as P0 when motion blocks action or ignores reduced motion for intense
animation. Classify as P1 when motion slows tasks or distracts from state.

## Audit Questions

- Can the user identify primary, secondary, and tertiary content in seconds?
- Does any visual treatment make text or controls harder to understand?
- Are states visible without relying only on color?
- Can the full path be completed using only the keyboard?
- Is focus always visible?
- Are touch targets large enough on mobile?
- Do animations clarify or merely decorate?
