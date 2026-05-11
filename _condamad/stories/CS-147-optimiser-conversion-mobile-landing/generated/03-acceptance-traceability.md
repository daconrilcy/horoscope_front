# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `.hero-device` commence avant `y=844px` sur `390x844`. | `LandingPage.css` compact mobile et reassurance masquee sur mobile. | After runtime: `.hero-device y=833`; `npm run test -- LandingPage visual-smoke ...` PASS. | Passed |
| AC2 | CTA primaire hero visible sur `390x844`. | CTA préservé dans `HeroSection.tsx`. | After runtime: `.hero-ctas y=586 bottom=711`; `LandingPage` PASS. | Passed |
| AC3 | Preuve forte compacte visible sur `390x844`. | `HeroSection.tsx` ajoute `.hero-proof-strip`. | After runtime: `.hero-proof-strip y=723 bottom=816`; `LandingPage` PASS. | Passed |
| AC4 | Preuve hero utilise une source landing owned. | Réutilisation `t.socialProof.badges.swiss` et `t.socialProof.proofs.swiss`. | Test DOM `LandingPage` vérifie libellé et preuve. | Passed |
| AC5 | Filtres landing restants ont décision exacte. | Filtres lang/social/testimonials retirés; allowlist `RG-088` réduite à navbar shell/menu. | `npm run test -- design-system` PASS + scan filtres classifié. | Passed |
| AC6 | Plan Free reste visible dans pricing mobile. | `PricingSection.tsx` conserve `getActivePlans()`. | Test DOM pricing vérifie Free/Basic/Premium. | Passed |
| AC7 | Liens plan gardent `free`, `basic`, `premium`. | `to={/register?plan=${plan.planCode}}` inchangé. | Test DOM pricing vérifie les trois hrefs. | Passed |
| AC8 | Tracking pricing garde `pricing_plan_select`. | Handler analytics inchangé. | Test interaction Basic vérifie `pricing_plan_select`. | Passed |
| AC9 | CTA final FAQ garde `/register`. | `FaqSection.tsx` inchangé fonctionnellement. | Test DOM FAQ vérifie href `/register`. | Passed |
| AC10 | Aucun guard landing/fond/design-system ne régresse. | Tests/guards et scans exécutés. | Lint PASS, suite Vitest complète PASS, scans RG PASS/classifiés. | Passed |
