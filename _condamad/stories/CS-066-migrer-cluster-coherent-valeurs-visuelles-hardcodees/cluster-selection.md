<!-- Decision de cluster pour CS-066. -->

# Cluster Selection

Cluster choisi: `ui Badge`.

Fichiers inclus:

- `frontend/src/components/ui/Badge/Badge.css`
- `frontend/src/components/ui/Badge/Badge.tsx`
- tests consommateurs verifiant la couleur badge

Fichiers exclus:

- autres composants UI primitives
- pages admin
- shell chat, landing, natal et prediction cards

Raison:

- le cluster est coherent, borne et deja couvert par des tests Vitest;
- les couleurs, bordures et ombres peuvent utiliser les tokens existants `--color-badge-*`, `--color-primary`, `--color-glass-border` et `--shadow-card`;
- aucun nouveau token, role typographique ou namespace n'est introduit.

Non-goals:

- ne pas migrer les dimensions uniques `36px`, `40px`, `44px` dans cette story;
- ne pas modifier les autres clusters hardcoded listes par l'audit;
- ne pas changer les registres de tokens puisque seuls des tokens existants sont consommes.
