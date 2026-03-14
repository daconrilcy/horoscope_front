# Epic 49: Centraliser tous les design tokens CSS pour une modifiabilité maximale

Status: split-into-stories

## Contexte

Les epics 16 et 17 ont posé les fondations visuelles du produit : variables CSS dans `index.css` et `theme.css`, système de glassmorphism, gradients premium, mode sombre. Ces bases sont fonctionnelles mais incomplètes :

- Les valeurs de couleur, espacement, rayon, ombre et animation sont dispersées entre `index.css`, `theme.css`, `App.css`, et des valeurs hardcodées dans des fichiers CSS de composants individuels (`HeroHoroscopeCard.css`, `MiniInsightCard.css`, `ShortcutCard.css`)
- De nombreux composants React (`DayPredictionCard`, `DashboardHoroscopeSummaryCard`) utilisent des styles inline avec des valeurs magiques (`1.5rem`, `1.125rem`, `rgba(255,255,255,0.7)`)
- La logique de couleur thème-dépendante est dupliquée en JSX (`theme === 'dark' ? 'white' : 'var(--text-1)'`) dans plusieurs composants
- Le pattern glassmorphism (blur, background, border, pseudo-éléments) est recodé de manière légèrement différente dans au moins 3 fichiers CSS distincts

Cette dispersion rend toute modification visuelle risquée : changer un rayon de bordure ou une couleur nécessite de toucher 5 à 10 fichiers différents.

## Objectif Produit

Créer un système de design tokens CSS exhaustif et centralisé qui :

1. Regroupe **toutes** les valeurs visuelles (couleurs, typographie, espacement, rayons, ombres, animations) en un seul fichier source `design-tokens.css`
2. Rend le passage light/dark entièrement géré par les tokens, sans aucune logique conditionnelle en JSX
3. Expose des classes CSS utilitaires dérivées des tokens pour couvrir les patterns répétés
4. Fournit un système `.glass-card` unique avec modificateurs, remplaçant le glassmorphism dupliqué
5. Migre tous les styles inline et valeurs magiques existants vers les nouveaux tokens

## Non-objectifs

- Ne pas introduire de CSS-in-JS, Tailwind, ou librairie de composants externe
- Ne pas refondre la logique applicative des composants (changements CSS uniquement sauf suppressions inline)
- Ne pas modifier la structure HTML/JSX des composants au-delà de ce qui est nécessaire pour supprimer les styles inline
- Ne pas créer de tokens pour des patterns qui n'existent qu'une seule fois dans le codebase

## Diagnostic Technique

### CSS actuel à consolider

**`frontend/src/index.css`** (37 lignes) :
- Variables root : `--bg-base`, `--bg-sheen`, `--text-1`, `--text-2`, `--line`, `--primary`, `--primary-strong`, `--danger`, `--success`
- Font family et base typographie

**`frontend/src/styles/theme.css`** (197 lignes) :
- Système dual-thème `.dark` avec override
- Text : `--text-1`, `--text-2`, `--text-3`, `--text-headline`
- Backgrounds : `--bg-top`, `--bg-mid`, `--bg-bot` (gradients)
- Surfaces glass : `--glass`, `--glass-2`, `--glass-border`
- CTA : `--cta-l`, `--cta-r`
- Sémantiques : `--success`, `--error`, `--btn-text`
- Badges : `--badge-chat`, `--badge-consultation`, `--badge-amour`, `--badge-travail`, `--badge-energie`
- Ombres : hero, card, nav, CTA (light & dark variants)
- Mini-card gradients : `--love-g1/g2`, `--work-g1/g2`, `--energy-g1/g2`
- `--constellation-color`

**`frontend/src/styles/backgrounds.css`** (61 lignes) :
- `.app-bg` avec gradient premium + noise SVG
- `.app-bg-container` (max-width 1100px)
- `.starfield-bg`

**CSS de composants individuels** (patterns glassmorphism dupliqués) :
- `HeroHoroscopeCard.css` : glass hero, pseudo-éléments, CTA button
- `MiniInsightCard.css` : glass mini, gradients thématiques
- `ShortcutCard.css` : glass shortcut

### Styles inline à éliminer (exemples prioritaires)

`DayPredictionCard.tsx` : 20+ objets `style={}` avec valeurs magiques
`DashboardHoroscopeSummaryCard.tsx` : `theme === 'dark' ? 'white' : undefined`

## Principe de mise en oeuvre

- Créer `frontend/src/styles/design-tokens.css` comme fichier source unique
- Organiser par sections : couleurs, typographie, espacement, rayons, ombres, animations
- Créer `frontend/src/styles/utilities.css` pour les classes utilitaires
- Créer `frontend/src/styles/glass.css` pour le système glassmorphism unifié
- Importer ces fichiers dans `main.tsx` ou `App.tsx` au bon ordre
- Migrer progressivement en story par story sans casser le rendu existant

## Découpage en stories

### Chapitre 1 — Fondation tokens couleurs

- 49.1 Créer `design-tokens.css` : variables de couleurs sémantiques, surfaces et status

### Chapitre 2 — Fondation tokens layout

- 49.2 Étendre `design-tokens.css` : typographie, espacement, rayons, ombres et animations

### Chapitre 3 — Classes utilitaires

- 49.3 Créer les classes CSS utilitaires dérivées des tokens

### Chapitre 4 — Glassmorphism unifié

- 49.4 Créer le système `.glass-card` mutualisé et supprimer les doublons

### Chapitre 5 — Migration composants

- 49.5 Migrer les styles inline et valeurs magiques des composants vers les tokens

## Risques et mitigations

### Risque 1 : Régression visuelle lors de la migration

Mitigation :
- Conserver l'ancien `theme.css` en parallèle pendant la migration (alias ou import)
- Migrer composant par composant avec review visuelle entre chaque story
- Les tests Vitest existants couvrent le comportement, pas le rendu → accepter

### Risque 2 : Conflits de spécificité CSS

Mitigation :
- Garder les variables sur `:root` et `.dark` uniquement
- Pas de classes utilitaires avec `!important`
- Documenter l'ordre d'import dans `main.tsx`

### Risque 3 : Renommage cassant de variables existantes

Mitigation :
- En story 49.1, créer les nouveaux tokens **en plus** des anciens (pas en remplacement)
- Alias les anciens noms vers les nouveaux si nécessaire
- Supprimer les anciens uniquement après migration complète (story 49.5)

## Ordre recommandé d'implémentation

- 49.1 → 49.2 → 49.3 → 49.4 → 49.5

Chemin critique : les stories 49.1 et 49.2 sont des prérequis bloquants pour toutes les stories de l'Epic 50 (composants UI primitifs).

## Références

- [Source: frontend/src/index.css]
- [Source: frontend/src/styles/theme.css]
- [Source: frontend/src/styles/backgrounds.css]
- [Source: frontend/src/styles/App.css]
- [Source: frontend/src/components/HeroHoroscopeCard.css]
- [Source: frontend/src/components/MiniInsightCard.css]
- [Source: frontend/src/components/ShortcutCard.css]
- [Source: frontend/src/components/prediction/DayPredictionCard.tsx]
- [Source: frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx]
- [Source: _bmad-output/planning-artifacts/epics.md]
