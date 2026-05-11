<!-- Baseline pre-implementation CS-143. -->

# Hero Complexity Before

- Source audit: `_condamad/audits/frontend-landing-page/2026-05-11-1841/02-finding-register.md#F-001`.
- Audit baseline: `LandingPage.css` 995 lines, 7 keyframes, 10 descendants hero animes au runtime.
- Worktree note: `HeroSection.tsx` and `LandingPage.css` were already dirty before this execution; the diff showed partial hero simplification already present.
- Regression guardrails consulted: `RG-083`, `RG-084`, `RG-085`, `RG-086`, `RG-087`.

Pre-implementation risk retained from audit:

- Always-running hero motion and filtered decorative layers were too costly to maintain.
- CTA analytics and accessible labels had to remain unchanged.
