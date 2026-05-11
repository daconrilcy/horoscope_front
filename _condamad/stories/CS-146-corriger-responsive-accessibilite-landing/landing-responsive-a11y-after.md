# CS-146 - Preuve responsive/a11y landing apres correction

Preuve capturee le 2026-05-11 sur le serveur Vite local `http://127.0.0.1:5176/`.

## Captures

- Desktop `1440x1000`: `landing-desktop-after.png`
- Tablette `768x1024`: `landing-tablet-after.png`
- Mobile `390x844`: `landing-mobile-after.png`
- Menu mobile ouvert `390x844`: `landing-mobile-menu-after.png`

## Mesures runtime

| Viewport | `scrollWidth` | `clientWidth` | `#social-proof` y | CTA hero y/bottom | H1 accessible |
|---|---:|---:|---:|---:|---|
| `1440x1000` | 1440 | 1440 | 990.375 | 796.375 / 855.375 | `Votre guide astrologique personnel - Toujours disponible` |
| `768x1024` | 768 | 768 | 1449.203125 | 721.734375 / 780.734375 | `Votre guide astrologique personnel - Toujours disponible` |
| `390x844` | 390 | 390 | 1524.234375 | 604.125 / 663.125 | `Votre guide astrologique personnel - Toujours disponible` |

## Differences validees

- Overflow tablette corrige: `scrollWidth` passe de `850` a `768` pour `clientWidth=768`.
- `#social-proof` mobile passe de `y=1802.484375` a `y=1524.234375`, soit `278.25px` plus haut et sous le seuil alternatif `y=1560`.
- CTA hero mobile reste visible dans le premier viewport: bottom `663.125` pour une hauteur viewport de `844`.
- H1 conserve un seul `h1` et expose un nom accessible avec separateur.
- Menu mobile: les treize tabulations observees restent dans `#landing-mobile-menu`; Escape ferme le menu, restaure le focus au bouton `Ouvrir le menu` et remet `document.body.style.overflow` a vide.

## Validation executee

| Commande | Resultat |
|---|---|
| `npm run test -- LandingPage` | PASS - 7 tests |
| `npm run test -- LandingPage visual-smoke design-system AppBgStyles page-architecture` | PASS - 135 tests |
| `npm run lint` | PASS |
| `rg -n "app-bg--landing\|style=" src/pages/landing src/layouts` | PASS - zero hit |
| `rg -n -- "--landing-(misc\|common\|temp\|shared\|base\|general\|global)-" src/pages/landing src/layouts` | PASS - zero hit |
| `rg -n "\bfetch\(\|axios\." src` | PASS_WITH_CLASSIFICATION - hit unique `src/api/client.ts`, client HTTP central |
| `rg -n "\bany\b" src/pages/landing src/tests/LandingPage.test.tsx` | PASS - zero hit |
| `rg -n "style=\{\{" src/pages/landing src/layouts` | PASS - zero hit |
| `rg -n "@keyframes\|animation:\|backdrop-filter\|filter:" src/pages/landing src/layouts/LandingLayout.css` | PASS_WITH_CLASSIFICATION - hits existants couverts par `RG-088` et `design-system-guards.test.ts` |

## Guardrails

- `RG-083`: PASS via tests `theme-tokens/design-system/visual-smoke` inclus dans la commande cible et absence de style inline landing.
- `RG-084`: PASS via `design-system` et absence de fond page-level ajoute.
- `RG-085`: PASS via `AppBgStyles`, `visual-smoke`, `design-system`; aucun changement starfield/fond global.
- `RG-086`: PASS via `AppBgStyles`, `design-system` et scan zero-hit `app-bg--landing`.
- `RG-087`: PASS via `AppBgStyles` et `design-system`; aucun changement de peinture globale.
- `RG-088`: PASS via `design-system-guards.test.ts`; les hits `backdrop-filter`/`animation: none !important` restent les exceptions exactes deja classees.

