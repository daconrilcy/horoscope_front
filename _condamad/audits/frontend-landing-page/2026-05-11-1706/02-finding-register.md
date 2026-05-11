# Finding Register - frontend-landing-page

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | missing-canonical-owner | frontend-landing-page | E-004, E-005, E-006, E-010 | The landing visual system is concentrated in one large semantic variable block. It is token-backed but too broad to refactor precisely, and light/dark decisions are coupled to component-specific names. | Split landing visual ownership into finite, documented semantic groups and reduce `LandingLayout.css` to stable theme primitives consumed by section CSS. | yes |
| F-002 | Medium | High | missing-canonical-owner | frontend-landing-page | E-008, E-009 | Light and dark modes do not behave as two theme variants of the same composition. Light mode stacks pale glass surfaces; dark mode relies on starfield and translucent panels, producing different hierarchy and contrast. | Define one shared landing composition model, then tune light/dark through paired surface/text/elevation tokens and visual snapshots. | yes |
| F-003 | Medium | High | missing-guard | frontend-landing-page | E-007, E-008 | `HeroSection` owns a custom live typewriter/state loop for a decorative preview. It adds runtime complexity to the first viewport and is not disabled by the CSS reduced-motion guard. | Replace the live interval with a simpler CSS-only or static preview, or gate it with reduced-motion and visibility. | yes |
| F-004 | Medium | Medium | missing-canonical-owner | frontend-landing-page | E-007 | `LandingPage.tsx` owns SEO meta, Open Graph, canonical and JSON-LD head mutation directly inside the page component, with incomplete cleanup branches and story-era comments. | Extract a small landing head/SEO owner or central head utility, remove story-era comments, and make cleanup behavior deterministic. | yes |
| F-005 | Info | High | architecture-guard-inventory | frontend-landing-page | E-001, E-002, E-003, E-010, E-011 | The prior landing layout and token migrations remain guarded and passing; no active layout bypass, landing-specific background class, inline style, or horizontal overflow was found in the audited runtime. | Keep these guardrails as non-regression constraints for any refactor story. | no |

## Finding Details

### F-001 - Landing visual ownership is too broad

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-landing-page
- Evidence: E-004, E-005, E-006, E-010
- Expected rule: the landing domain should have clear owners for theme primitives, component surfaces and section layout so a refactor can be scoped safely.
- Actual state: `LandingLayout.css` declares 256 `--landing-*` variables, including low-level colors, shadows, radii, type scale, navbar, language selector, mobile menu, hero device, cards and dark overrides.
- Impact: The landing visual system is concentrated in one large semantic variable block. It is token-backed but too broad to refactor precisely, and light/dark decisions are coupled to component-specific names.
- Recommended action: Split landing visual ownership into finite, documented semantic groups and reduce `LandingLayout.css` to stable theme primitives consumed by section CSS.
- Story candidate: yes
- Suggested archetype: design-system-convergence

### F-002 - Light and dark visual systems diverge

- Severity: Medium
- Confidence: High
- Category: missing-canonical-owner
- Domain: frontend-landing-page
- Evidence: E-008, E-009
- Expected rule: dark and light variants should preserve the same hierarchy, spacing and component roles while changing surface/color values.
- Actual state: screenshots show light mode as pale glass-on-pale-glass, while dark mode uses a much more dramatic astral background and many translucent panels. Mid-page cards lose definition in dark and over-blend in light.
- Impact: Light and dark modes do not behave as two theme variants of the same composition. Light mode stacks pale glass surfaces; dark mode relies on starfield and translucent panels, producing different hierarchy and contrast.
- Recommended action: Define one shared landing composition model, then tune light/dark through paired surface/text/elevation tokens and visual snapshots.
- Story candidate: yes
- Suggested archetype: design-system-convergence

### F-003 - Hero live preview is overbuilt for its value

- Severity: Medium
- Confidence: High
- Category: missing-guard
- Domain: frontend-landing-page
- Evidence: E-007, E-008
- Expected rule: first-viewport decorative behavior should be cheap, predictable and easy to disable.
- Actual state: `HeroSection.tsx` updates state every 80ms for typewriter/tool/trend animation while CSS reduced-motion only suppresses CSS transitions/animations.
- Impact: `HeroSection` owns a custom live typewriter/state loop for a decorative preview. It adds runtime complexity to the first viewport and is not disabled by the CSS reduced-motion guard.
- Recommended action: Replace the live interval with a simpler CSS-only or static preview, or gate it with reduced-motion and visibility.
- Story candidate: yes
- Suggested archetype: runtime-simplification

### F-004 - Landing page owns head mutations directly

- Severity: Medium
- Confidence: Medium
- Category: missing-canonical-owner
- Domain: frontend-landing-page
- Evidence: E-007
- Expected rule: route/page components should compose content; non-visual document head behavior should have a small canonical owner.
- Actual state: `LandingPage.tsx` mutates document title, meta description, OG tags, canonical link and JSON-LD scripts inside one `useEffect`, with comments such as `AC1`/`AC2` and an incomplete cleanup branch.
- Impact: `LandingPage.tsx` owns SEO meta, Open Graph, canonical and JSON-LD head mutation directly inside the page component, with incomplete cleanup branches and story-era comments.
- Recommended action: Extract a small landing head/SEO owner or central head utility, remove story-era comments, and make cleanup behavior deterministic.
- Story candidate: yes
- Suggested archetype: ownership-routing-refactor

### F-005 - Existing guards remain effective

- Severity: Info
- Confidence: High
- Category: architecture-guard-inventory
- Domain: frontend-landing-page
- Evidence: E-001, E-002, E-003, E-010, E-011
- Expected rule: prior CONDAMAD frontend guardrails should remain green before new visual refactors.
- Actual state: targeted tests and lint pass; route hierarchy and background guardrails are still in place.
- Impact: The prior landing layout and token migrations remain guarded and passing; no active layout bypass, landing-specific background class, inline style, or horizontal overflow was found in the audited runtime.
- Recommended action: Keep these guardrails as non-regression constraints for any refactor story.
- Story candidate: no
- Suggested archetype: guardrail-preservation
