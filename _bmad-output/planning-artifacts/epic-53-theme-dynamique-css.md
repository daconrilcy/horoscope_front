# Epic 53: Supprimer toute logique de thème conditionnelle du JSX

Status: split-into-stories

## Contexte

Malgré le système de tokens CSS de l'Epic 49, certains composants calculent encore des couleurs dynamiquement en JSX selon le thème :
- `DayPredictionCard.tsx` : `const textColor = isAstro && theme === 'dark' ? "white" : "var(--text-1)"`
- `DashboardHoroscopeSummaryCard.tsx` : `style={{ color: theme === 'dark' ? 'white' : undefined }}`
- Possibles occurrences similaires dans d'autres composants utilisant `useTheme()`

Ce pattern est problématique : il duplique la logique que CSS gère nativement, crée des dépendances inutiles sur le contexte de thème dans des composants de présentation, et rend les tests plus complexes.

## Objectif Produit

Éliminer toute logique `theme === 'dark'` dans le JSX des composants de présentation en déléguant cette adaptation aux variables CSS auto-adaptatives définies dans `design-tokens.css`.

## Non-objectifs

- Ne pas modifier `ThemeProvider.tsx` ou le mécanisme de détection du thème
- Ne pas supprimer `useTheme()` des composants qui en ont besoin pour des raisons non-CSS (ex: passer le thème à une API Canvas/WebGL)
- Ne pas refondre `AstroMoodBackground` — son Canvas a besoin du thème

## Découpage en stories

- 53.1 Variables CSS adaptatives pour le mode dark dans les composants de texte
- 53.2 Variables CSS contextuelles pour les surfaces AstroTheme (fond clair/sombre)
- 53.3 Audit et nettoyage des `useTheme()` résiduels dans les composants de présentation

## Références

- [Source: frontend/src/components/prediction/DayPredictionCard.tsx]
- [Source: frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx]
- [Source: frontend/src/state/ThemeProvider.tsx]
- [Source: frontend/src/styles/design-tokens.css]
- [Source: _bmad-output/planning-artifacts/epic-49-design-tokens-css-centralises.md]
