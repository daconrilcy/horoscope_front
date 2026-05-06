<!-- Baseline avant migration du cluster App. -->

# CS-082 Hardcoded Values Before

Scope: `frontend/src/App.css` uniquement.

## Commandes baseline

- `rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/App.css`
- `rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/App.css`
- `rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/App.css`

## Constats avant implementation

`App.css` contenait des literals visuels repetes dans plusieurs sous-surfaces:

- shell et navigation mobile: offsets, rayons, padding et ombres de bouton;
- etats feedback: surfaces loading, empty, success et danger;
- catalogue astrologues: fonds radiaux, couleurs de titres et texte;
- carte resume dashboard: fonds radiaux, ombres, ligne decor et action CTA.

Le fichier contenait aussi de nombreuses valeurs one-off historiques hors du lot
migre ici. Elles restent documentees comme dette hors lot lorsque non touchees
par les sous-surfaces ci-dessus.

