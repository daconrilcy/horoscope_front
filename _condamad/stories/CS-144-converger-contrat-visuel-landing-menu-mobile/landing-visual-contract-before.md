<!-- Baseline pre-implementation CS-144. -->

# Landing Visual Contract Before

- Source audit: `_condamad/audits/frontend-landing-page/2026-05-11-1841/02-finding-register.md#F-002`.
- Audit finding: light/dark landing hierarchy still read as divergent, and mobile menu glow was visually dominant.
- Existing owners: `LandingLayout.css` for roles, `LandingPage.css` for hero/card consumption, `LandingNavbar.css` for mobile menu.
- Regression guardrails consulted: `RG-083`, `RG-084`, `RG-085`, `RG-086`, `RG-087`.

Known pre-change risks:

- Visual corrections could bypass the global background owner.
- New `--landing-*` roles could become vague or unconsumed.
