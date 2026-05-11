<!-- Baseline pre-implementation CS-145. -->

# Landing Visual Complexity Before

- Source audit: `_condamad/audits/frontend-landing-page/2026-05-11-1841/02-finding-register.md#F-003`.
- Finding: current guards did not bound growth of landing `@keyframes`, `animation:`, `filter` and `backdrop-filter`.
- Current post-CS-143/CS-144 inventory before guard:
  - `@keyframes`: 0 under `src/pages/landing` and `src/layouts/LandingLayout.css`.
  - Active hero `animation:`: 0 in `LandingPage.css`.
  - Remaining inspectable effects: exact `backdrop-filter` declarations in navbar, social proof and testimonials, plus reduced-motion `animation: none !important`.

Guardrails consulted: `RG-083`, `RG-084`, `RG-085`, `RG-086`, `RG-087`.
