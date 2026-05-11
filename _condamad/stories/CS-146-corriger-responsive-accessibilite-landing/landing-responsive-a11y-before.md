# CS-146 - Baseline responsive/a11y landing avant correction

Baseline capturee le 2026-05-11 sur le serveur Vite local `http://127.0.0.1:5176/`.

## Captures

- Desktop `1440x1000`: `landing-desktop-before.png`
- Tablette `768x1024`: `landing-tablet-before.png`
- Mobile `390x844`: `landing-mobile-before.png`
- Menu mobile ouvert `390x844`: `landing-mobile-menu-before.png`

## Mesures runtime

| Viewport | `scrollWidth` | `clientWidth` | `#social-proof` y | CTA hero y/bottom | H1 accessible |
|---|---:|---:|---:|---:|---|
| `1440x1000` | 1440 | 1440 | 990.375 | 796.375 / 855.375 | `Votre guide astrologique personnelToujours disponible` |
| `768x1024` | 850 | 768 | 1730.421875 | 743.234375 / 802.234375 | `Votre guide astrologique personnelToujours disponible` |
| `390x844` | 390 | 390 | 1802.484375 | 608.125 / 667.125 | `Votre guide astrologique personnelToujours disponible` |

## Constats

- La tablette `768x1024` presente un overflow horizontal de `82px`.
- Le H1 accessible concatene le lead et l'accent sans separateur textuel.
- Sur mobile, `#social-proof` commence a `y=1802.484375`, au-dela du seuil de sortie alternatif `y=1560`.
- Le menu mobile expose deja `role="dialog"` et `aria-modal="true"`, mais le code source ne contient pas de focus initial, focus trap, scroll lock ou restauration du focus.

## Sequence de focus menu mobile observee

Les neuf premieres tabulations restent dans `#landing-mobile-menu`, mais le focus initial n'est pas deplace par le composant a l'ouverture et aucun wrapping explicite n'est present dans le code avant correction.

