# Baseline specificite App avant CS-124

- Source: `_condamad/audits/frontend-app-css-standardization/2026-05-09-1145/01-evidence-log.md#E-010` et `#E-011`.
- Probleme initial: les guards existants bloquaient des valeurs visuelles, mais pas les noms App page-specific.
- Reliquats a bloquer: vocabulaire `astrologer`, `consultation`, `dashboard`, `settings`, `wizard` dans les selectors et variables `--app-*` de `App.css`.

