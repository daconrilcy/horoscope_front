<!-- Preuve finale du guard visual-smoke tokenise. -->

# CS-047 Visual Smoke After

| Item | Resultat |
|---|---|
| Assertions typographiques legacy | supprimees du test |
| Nouveau contrat `.section-header__title` | `font-size: var(--font-size-lg)` |
| Nouveau contrat `.bottom-nav__label` | `font-size: var(--font-size-xs)`, `font-weight: var(--font-weight-medium)` |
| Preuve de resolution token | chaque token attendu doit etre declare dans `design-tokens.css` |
| Assertions `opacity` | conservees |
| Validation | `npm run test -- visual-smoke css-fallback design-system inline-style theme-tokens legacy-style` PASS |
