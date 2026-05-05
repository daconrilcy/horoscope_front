<!-- Inventaire final du cluster visuel et typographique CS-046. -->

# CS-046 Hardcoded Values After

## Resultat

- 299 declarations hardcodees non ambigues ont ete migrees vers tokens ou roles canoniques existants.
- 567 declarations du cluster consomment maintenant explicitement `--font-weight-*`, `--font-size-*`, `--line-height-*`, `--space-*` ou `--radius-*`.
- Aucun nouveau namespace token et aucun nouveau role typographique n'a ete cree.

## Compteurs apres migration

```text
frontend/src/App.css colors=317 type=236 spacing=384 radius=106 shadow=47
frontend/src/pages/admin/AdminPromptsPage.css colors=8 type=111 spacing=289 radius=51 shadow=0
frontend/src/pages/HelpPage.css colors=246 type=82 spacing=148 radius=36 shadow=33
frontend/src/pages/settings/Settings.css colors=144 type=97 spacing=118 radius=30 shadow=23
frontend/src/pages/AstrologerProfilePage.css colors=129 type=86 spacing=111 radius=26 shadow=24
```

## Exceptions finales

- Couleurs et gradients editoriaux: conserves car ils portent des compositions locales et necessitent une decision produit avant tokenisation.
- Shadows locales: conservees sauf usage deja tokenise par `--shadow-*` ou `--profile-card-shadow*`.
- Tailles typographiques expressives `clamp(...)`, `rem` editoriaux et tailles non couvertes par les tokens existants: conservees pour eviter un mapping near-equivalent non prouve.
- Spacing hors liste canonique ou compose sur plusieurs axes: conserve tant que le mapping n'est pas strictement equivalent.

Zero `unclassified`, `TODO` ou `TBD`.
