# Finding Register - frontend-landing-page - 2026-05-11-1841

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Medium | High | duplicate-responsibility | frontend-landing-page | E-008, E-009, E-015, E-016 | The prior JS loop is gone, but the hero remains an overbuilt decorative system: 995 CSS lines in `LandingPage.css`, 7 keyframes, 10 animated hero descendants at runtime and many layered panels/filters. This keeps first-viewport maintenance expensive. | Simplify the hero preview to one static or lightly animated product card model, reduce keyframes and filtered layers, and keep CTA/analytics unchanged. | yes |
| F-002 | Medium | High | missing-canonical-owner | frontend-landing-page | E-008, E-009, E-016, E-017 | Light/dark are now classified and guarded, but the visual style still reads as two different treatments: light mode is washed out by repeated pale glass, dark mode is more legible but much more dramatic, and the mobile menu adds a large blurred glow that weakens hierarchy. | Define a smaller shared visual contract for landing surfaces and mobile menu, then tune light/dark from the same semantic roles with current screenshots as before/after evidence. | yes |
| F-003 | Low | High | missing-test-coverage | frontend-landing-page | E-013, E-015, E-016 | Current guards prove ownership, no timers, no inline styles and no overflow, but no guard bounds the amount of CSS motion/filter complexity after CS-141. The same complexity can regrow while all current tests remain green. | Add a focused visual-complexity guard for landing hero/menu CSS, with exact allowlist counts or an owner map for animations and backdrop filters. | yes |
| F-004 | Info | High | architecture-guard-inventory | frontend-landing-page | E-001, E-003, E-005, E-006, E-007, E-010, E-011, E-012, E-013, E-014, E-018 | The original four remediation stories are materially closed: layout/background invariants hold, SEO/head ownership moved to `LandingHead`, JS timer is absent, and targeted tests/lint pass. | Preserve these guardrails as non-regression constraints for any further landing simplification. | no |

## Finding Details

### F-001 - Hero presentation remains over-complex after JS timer removal

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: frontend-landing-page
- Evidence: E-008, E-009, E-015, E-016
- Expected rule: first-viewport marketing preview should be cheap, readable and maintainable, with animation used sparingly and owned by a small visual contract.
- Actual state: `LandingPage.css` carries 995 lines, 73 landing declarations, 137 landing variable uses and 7 keyframes. Playwright observed 10 animated hero descendants on the current first viewport.
- Impact: The prior JS loop is gone, but the hero remains an overbuilt decorative system: 995 CSS lines in `LandingPage.css`, 7 keyframes, 10 animated hero descendants at runtime and many layered panels/filters. This keeps first-viewport maintenance expensive.
- Recommended action: Simplify the hero preview to one static or lightly animated product card model, reduce keyframes and filtered layers, and keep CTA/analytics unchanged.
- Suggested archetype: frontend-visual-simplification
- Story candidate: yes

### F-002 - Light/dark visual style is classified but still visually noisy

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-landing-page
- Evidence: E-008, E-009, E-016, E-017
- Expected rule: light and dark landing themes should share the same hierarchy, with paired surface/text/elevation roles and restrained page-level effects.
- Actual state: screenshots show a clean but washed light first viewport, a clearer dark first viewport, and a mobile menu whose blurred center glow dominates both themes. The implementation is token-backed, but the visual contract still permits too many local glass/gradient/filter decisions.
- Impact: Light/dark are now classified and guarded, but the visual style still reads as two different treatments: light mode is washed out by repeated pale glass, dark mode is more legible but much more dramatic, and the mobile menu adds a large blurred glow that weakens hierarchy.
- Recommended action: Define a smaller shared visual contract for landing surfaces and mobile menu, then tune light/dark from the same semantic roles with current screenshots as before/after evidence.
- Suggested archetype: design-system-convergence
- Story candidate: yes

### F-003 - No guard bounds visual-complexity regression

- Severity: Low
- Confidence: High
- Category: missing-test-coverage
- Domain: frontend-landing-page
- Evidence: E-013, E-015, E-016
- Expected rule: after simplifying the landing, guards should fail if keyframes, always-running animations or filtered glass layers grow again without an explicit owner.
- Actual state: current tests prove absence of JS timers and owner group classification, but not a maximum or allowlist for CSS animations/backdrop filters. A future change can add another infinite keyframe and still pass.
- Impact: Current guards prove ownership, no timers, no inline styles and no overflow, but no guard bounds the amount of CSS motion/filter complexity after CS-141. The same complexity can regrow while all current tests remain green.
- Recommended action: Add a focused visual-complexity guard for landing hero/menu CSS, with exact allowlist counts or an owner map for animations and backdrop filters.
- Suggested archetype: test-guard-hardening
- Story candidate: yes

### F-004 - Prior critical landing regressions are closed

- Severity: Info
- Confidence: High
- Category: architecture-guard-inventory
- Domain: frontend-landing-page
- Evidence: E-001, E-003, E-005, E-006, E-007, E-010, E-011, E-012, E-013, E-014, E-018
- Expected rule: new landing audit must not reopen closed work without current evidence.
- Actual state: `LandingPage` is composition-only for head, `LandingHead` owns document mutation, `HeroSection` has no timer, background class `app-bg--landing` is absent, inline style scan is clean, and tests/lint pass.
- Impact: The original four remediation stories are materially closed: layout/background invariants hold, SEO/head ownership moved to `LandingHead`, JS timer is absent, and targeted tests/lint pass.
- Recommended action: Preserve these guardrails as non-regression constraints for any further landing simplification.
- Suggested archetype: guardrail-preservation
- Story candidate: no
