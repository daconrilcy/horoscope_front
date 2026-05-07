<!-- Baseline avant migration des valeurs premium partagees CS-089. -->

# Hardcoded Values Before

Baseline capturee avant implementation sur:

- `frontend/src/styles/backgrounds.css`
- `frontend/src/styles/glass.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/components/prediction/DailyAdviceCard.css`

## Findings initiaux

- `backgrounds.css`: gradients light/dark et atmospheres `rgba(...)` directement dans `.app-bg` et `.app-bg::before`; noise SVG inline.
- `glass.css`: rayons `26px`/`18px` et shadows `rgba(20,20,40,...)` directement dans les variantes glass.
- `DailyHoroscopePage.css`: aliases locaux `--glass-*`, gradients premium page, halos `rgba(...)`, background card literal et blur glass local.
- `DailyAdviceCard.css`: gradients/halos `rgba(...)` locaux pour la card et son badge.

## Classification cible

| Surface | Owner final |
|---|---|
| App background premium | `frontend/src/styles/premium-theme.css` via `--premium-app-*` |
| Noise premium | `frontend/src/styles/premium-theme.css` via `--premium-noise-image` |
| Glass surfaces/borders/card effects | `frontend/src/styles/glass.css` via `--glass-*` |
| Daily page background/halos | `frontend/src/styles/premium-theme.css` via `--premium-daily-*` |
| Daily advice halos/badge | `frontend/src/styles/premium-theme.css` via `--premium-daily-advice-*` |
