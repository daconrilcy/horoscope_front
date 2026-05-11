# Execution Brief

- Story key: `CS-147-optimiser-conversion-mobile-landing`
- Objective: optimiser la conversion mobile de la landing en compactant le hero, en avançant une preuve forte, en réduisant les filtres landing et en verrouillant pricing/FAQ.
- Scope: `frontend/src/pages/landing/**`, tests frontend ciblés, preuves `_condamad/stories/CS-147-optimiser-conversion-mobile-landing/**`.
- Non-goals: backend, Stripe, auth, SEO/head, `App.css`, fond global, plans/prix/quotas, nouvelles dépendances.
- Guardrails applicables: `RG-058`, `RG-059`, `RG-060`, `RG-061`, `RG-068`, `RG-078`, `RG-082`, `RG-083`, `RG-084`, `RG-085`, `RG-086`, `RG-087`, `RG-088`.
- Write rules: aucun style inline, aucun nouveau filtre/motion non classé, pas de duplication de pricingConfig, `getActivePlans()` reste source unique.
- Completion: AC1-AC10 ont code et validation, preuves before/after produites, capsule finalisée, story status synchronisé.
- Halt conditions: besoin de changer plans/prix/routes/fond global, nouvelle dépendance, ou filtre conservé sans exception exacte.
