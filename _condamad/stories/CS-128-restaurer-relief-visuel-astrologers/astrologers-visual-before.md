# Astrologers Visual Before

<!-- Baseline visuelle avant restauration du relief compact /astrologers. -->

## Owner mapping

| Missing detail | Current selector/token | Target owner | Evidence | Decision |
|---|---|---|---|---|
| Surface translucide avec highlight radial | `.people-page .person-card` remplace `--app-person-card-background` par `--color-glass-bg` | `frontend/src/styles/app/cards.css` | Override compact lu avant modification | Restaurer `background` token-backed compact avec `--app-person-card-*`. |
| Ombre douce et relief interne | `.people-page .person-card` remplace `--app-person-card-box-shadow` par `--shadow-card` | `frontend/src/styles/app/cards.css` | Override compact lu avant modification | Restaurer `box-shadow` token-backed sans toucher `App.css`. |
| Bordure themee par persona | `.people-page .person-card` utilise `--color-glass-border` | `frontend/src/styles/app/cards.css` | `data-theme` et `--astro-accent` existent deja | Reconnecter `border-color` a `--app-person-card-border-color`. |
| Carte featured plus presente | `.people-page .person-card--featured` utilise `--color-glass-bg-2` et `--color-primary` | `frontend/src/styles/app/cards.css` | Override compact lu avant modification | Restaurer material featured distinct et garder `grid-column: span 2`. |
| Petite pastille logo | `.people-page .person-card-icon` reduit la taille mais garde la classe | `frontend/src/styles/app/cards.css` | Markup `person-card-icon` present dans `AstrologerCard.tsx` | Guarder affichage visible et material theme. |
| Avatar avec liseret/glow | `.people-page .person-card-avatar` ne retire pas les pseudo-elements mais compacte la taille | `frontend/src/styles/app/media.css` | `::before` et `::after` globaux existent | Guarder leur presence et ne pas les neutraliser. |
| Chips themees translucides | `.people-page .person-card-tag` reduit seulement taille/padding | `frontend/src/styles/app/cards.css` | Tokens `--app-person-card-tag-*` et `--astro-chip-*` existent | Guarder material token-backed et compact. |
| Badges provider/default/featured caches | `.people-page .person-card-provider-badge`, `.person-card-featured-badge`, `.person-default-badge` | `frontend/src/styles/app/cards.css` | Override compact `display: none` | Conserver la decision de visibilite. |

## Current visible state

- Route `/astrologers` conserve le layout compact centre et la grille deux colonnes.
- Les cartes compactes sont aplanies par des tokens generiques de glass/card.
- Les variables riches `--app-person-card-*` existent deja et peuvent etre reutilisees.
- Aucun changement React ou API n'est necessaire.

## Screenshots

- Screenshot before: non capture avant code change dans cette session; baseline textuelle persistante fournie par l'analyse visuelle et les selectors lus.
- Blocker note: le serveur local n'etait pas encore demarre au moment de capturer le baseline. La preuve before repose sur l'etat CSS versionne avant modification.
