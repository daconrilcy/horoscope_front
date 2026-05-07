# Hardcoded Values Before - CS-085

## Scope

- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/pages/landing/**/*.css`

## Scan commands

| Category | Command | Result |
|---|---|---|
| Visual values | `rg -n "#[0-9A-Fa-f]{3,8}\|rgba?\(\|hsla?\(" frontend/src/layouts/LandingLayout.css frontend/src/pages/landing --glob "*.css"` | Hits found across landing layout, landing page and landing sections. |
| Typography values | `rg -n "font-size:\|font-weight:\|line-height:\|letter-spacing:" frontend/src/layouts/LandingLayout.css frontend/src/pages/landing --glob "*.css"` | Hits found across landing page and section typography roles. |
| Elevation/radius/fallback candidates | `rg -n "box-shadow:\|border-radius:\|var\(\s*--[a-zA-Z0-9_-]+\s*," frontend/src/layouts/LandingLayout.css frontend/src/pages/landing --glob "*.css"` | Hits found for repeated shadows, radius literals and tokenized radius/elevation usage. |
| No Legacy vocabulary | `rg -n "legacy\|Legacy\|alias\|compat\|compatibility\|shim\|fallback\|migration-only" frontend/src/layouts/LandingLayout.css frontend/src/pages/landing --glob "*.css"` | Zero hits. |
| Page-scoped namespaces | corrected final command in validation plan | Pending final corrected run. |

## Initial classification

| Surface | Before finding | Required final decision |
|---|---|---|
| `LandingLayout.css` | Landing shell gradients and translucent surfaces use rgba literals. | `registered-semantic-owner` under `--landing-*` or existing token. |
| `LandingPage.css` | Repeated glass surfaces, premium shadows, CTA shadows, dark hero overlays, pill radii and expressive typography. | Migrate repeated values to documented `--landing-*`, premium/global tokens or typography roles; classify rare one-offs. |
| `sections/FaqSection.css` | Repeated section eyebrow/headline/body typography, glass cards, CTA shadow. | Reuse section typography and landing surface/elevation owners. |
| `sections/LandingFooter.css` | Dark footer rgba text and border tones. | Document footer tone owners or classify final one-offs. |
| `sections/LandingNavbar.css` | Navigation glass surfaces, dropdown overlays, text tones, shadows and radii. | Migrate repeated values to landing navbar owners and existing tokens. |
| `sections/PricingSection.css` | Pricing cards, badges, CTA shadows and plan typography. | Reuse landing/premium owners and typography roles. |
| `sections/ProblemSection.css` | Problem card surfaces and two semantic accent colors. | Use documented semantic owner or final one-off classification. |
| `sections/SocialProofSection.css` | Social proof surfaces and compact typography. | Reuse landing section owners. |
| `sections/SolutionSection.css` | Solution card surfaces, step pills and typography. | Reuse landing section owners. |
| `sections/TestimonialsSection.css` | Premium card tokens already used; star color and typography literals remain. | Use premium/landing owner or final local decision. |

## Baseline conclusion

The cluster is bounded to landing CSS. There are many repeated visual and typography literals to migrate or classify, and no initial active No Legacy vocabulary hit in the landing CSS cluster.
