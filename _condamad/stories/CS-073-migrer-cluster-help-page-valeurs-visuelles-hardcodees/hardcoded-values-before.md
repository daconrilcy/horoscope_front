<!-- Baseline du cluster HelpPage avant migration CS-073. -->

# Hardcoded Values Before

## Scope

- File: `frontend/src/pages/HelpPage.css`
- Bounded cluster: main help page styles from `.help-page` through `.help-placeholder-card__text`, before the `Help Subscriptions Page` block.
- Out of scope: subscription-specific styles in the same file.

## Baseline scans

Commands run from repository root before implementation:

```powershell
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" frontend/src/pages/HelpPage.css
rg -n "font-size:|font-weight:|line-height:|letter-spacing:" frontend/src/pages/HelpPage.css
rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," frontend/src/pages/HelpPage.css
rg -n "legacy|Legacy|alias|compat|shim|fallback|migration-only" frontend/src/pages/HelpPage.css
```

The cluster contains repeated hardcoded colors, glass surfaces, borders, shadows,
radii and typographic values. The forbidden namespace scan returned zero hits.

## Initial decisions

| Category | Representative literals | Initial decision |
|---|---|---|
| Help page glass surfaces | `rgba(255, 255, 255, 0.48)`, `rgba(255, 255, 255, 0.58)`, `rgba(255, 255, 255, 0.66)` | migrate to page-scoped `--help-*` semantic variables |
| Help page ink | `#2f2345`, `rgba(47, 35, 69, 0.74)`, `#6d56bf` | migrate to page-scoped `--help-*` semantic variables |
| Repeated accent borders | `rgba(138, 114, 217, 0.16)`, `rgba(138, 114, 217, 0.2)`, `rgba(138, 114, 217, 0.32)` | migrate to page-scoped `--help-*` semantic variables |
| Repeated shadows | `0 18px 34px rgba(87, 63, 144, 0.1)`, CTA purple shadow | migrate to page-scoped `--help-*` semantic variables |
| Repeated radii | `18px`, `22px`, `24px`, `26px`, `32px`, `40px` | migrate repeated page roles to local variables; keep one-off geometry where semantic |
| Typography repetitions | eyebrow, body-muted, metadata and section/card titles | migrate to existing `--type-*`, `--font-*` and `--line-height-*` tokens where applicable |
