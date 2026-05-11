# Baseline before - catalogue `/astrologers`

Date: 2026-05-11

## Etat constate avant correction

- Desktop `1440x1000`: `AstrologerGrid.tsx` applique `featured={index === 0}` a la premiere carte. Le CSS `.people-page .person-card--featured` force `grid-column: span 2`, ce qui cree une carte pleine largeur dans une grille catalogue compacte.
- Mobile `390x844`: `.people-page .person-grid` force `grid-template-columns: repeat(2, minmax(0, 1fr))` sans override mobile plus specifique. Le catalogue reste donc en deux colonnes compressees.
- Tablette `768x1024`: la grille reste gouvernee par le meme repeat fixe a deux colonnes.
- DOM signaux visibles: `AstrologerCard.tsx` rend les badges provider, default et featured dans le DOM, mais `cards.css` les cache sous `.people-page`.
- Affordance conversion: la carte entiere est un `button`, mais aucun CTA visuel localise n'est rendu dans la carte.
- Hauteur carte: `.people-page .person-card` force `height: 256px` et `.people-page .person-card--featured` force `height: 244px`.
- Dette CSS: `media.css` contient `mix-alend-mode: multiply`.

## Scans avant

```text
frontend/src/features/astrologers/components/AstrologerGrid.tsx: featured={index === 0}
frontend/src/styles/app/cards.css: .people-page .person-grid repeat(2, minmax(0, 1fr))
frontend/src/styles/app/cards.css: .people-page .person-card height: 256px
frontend/src/styles/app/cards.css: .people-page .person-card--featured grid-column: span 2
frontend/src/styles/app/cards.css: .people-page .person-card--featured height: 244px
frontend/src/styles/app/cards.css: badges provider/default/featured display: none
frontend/src/styles/app/media.css: mix-alend-mode: multiply
```

## Decision d'implementation

La story recommande de neutraliser le layout featured pleine largeur plutot que
de creer une vraie carte editoriale horizontale. Le correctif retenu aligne donc
toutes les cartes du catalogue sur une grille egale et conserve les signaux de
choix dans chaque carte.
