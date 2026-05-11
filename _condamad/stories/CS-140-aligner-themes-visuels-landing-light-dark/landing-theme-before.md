# Baseline CS-140 - theme landing light/dark

Baseline issue de l'audit et des scans avant patch.

- Source audit: `_condamad/audits/frontend-landing-page/2026-05-11-1706/00-audit-report.md#F-002`.
- Etat initial: light mode avec surfaces glass pales sur fond pale; dark mode avec separation locale moins marquee.
- Dependence CS-139: les roles owner after sont disponibles dans `_condamad/stories/CS-139-refactoriser-ownership-css-landing/landing-css-ownership-after.md`.

## Roles concernes

- Surfaces et bordures: `--landing-surface-*`, `--landing-accent-border-*`.
- Hero: `--landing-hero-*`.
- Navigation mobile: `--landing-navbar-*`, `--landing-language-*`, `--landing-mobile-*`.

## Risque initial

Les corrections theme auraient pu repartir dans `App.css`, un fond dedie landing ou des styles inline sans owner exact.
