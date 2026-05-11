# Landing Conversion Before

Baseline capturé le 2026-05-11 sur `http://127.0.0.1:5173/` via Vite local et Playwright Chromium headless.

## Runtime Measurements

| Viewport | `.hero-section` | `.hero-ctas` | `.hero-visual` | `.hero-device` | `#social-proof` | `#pricing` | `#faq` | Overflow |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `390x844` | `y=98 h=1426 bottom=1524` | `y=602 h=129 bottom=731` | `y=886 h=600 bottom=1486` | `y=901 h=570 bottom=1471` | `y=1524 h=943 bottom=2467` | `y=4859 h=2049 bottom=6909` | `y=6909 h=1444 bottom=8353` | `0` |
| `768x1024` | `y=98 h=1351 bottom=1449` | `y=716 h=65 bottom=781` | `y=874 h=523 bottom=1397` | `y=895 h=481 bottom=1376` | `y=1449 h=795 bottom=2244` | `y=4187 h=2000 bottom=6186` | `y=6186 h=1115 bottom=7302` | `0` |
| `1440x1000` | `y=94 h=896 bottom=990` | `y=790 h=65 bottom=855` | `y=225 h=619 bottom=844` | `y=246 h=577 bottom=823` | `y=990 h=497 bottom=1487` | `y=2705 h=890 bottom=3595` | `y=3595 h=1166 bottom=4761` | `0` |

## Findings

- Sur `390x844`, le CTA primaire est visible (`.hero-ctas` bottom `731`) mais `.hero-device` commence à `y=901`, sous le premier viewport.
- `#social-proof` commence à `y=1524`, donc les preuves fortes complètes arrivent tard.
- Liens pricing détectés: `/register?plan=free`, `/register?plan=basic`, `/register?plan=premium`.

## Filter / Motion Inventory

Baseline source:

```powershell
rg -n "@keyframes|animation:|backdrop-filter|filter:" src/pages/landing src/layouts/LandingLayout.css
```

Hits attendus avant story:

- `LandingNavbar.css`: `.landing-navbar__shell` `backdrop-filter: blur(14px)`
- `LandingNavbar.css`: `.landing-navbar__lang` `backdrop-filter: blur(18px) saturate(135%)`
- `LandingNavbar.css`: `.landing-navbar__lang-dropdown` `backdrop-filter: blur(22px) saturate(145%)`
- `LandingNavbar.css`: `.landing-navbar__mobile-menu` `backdrop-filter: blur(6px)`
- `SocialProofSection.css`: `.social-proof__container` `backdrop-filter: blur(18px)`
- `TestimonialsSection.css`: `.testimonial-card` `backdrop-filter: blur(18px) saturate(140%)`
- `TestimonialsSection.css`: `.testimonial-card` `-webkit-backdrop-filter: blur(18px) saturate(140%)`
- `TestimonialsSection.css`: reduced motion `animation: none !important`
