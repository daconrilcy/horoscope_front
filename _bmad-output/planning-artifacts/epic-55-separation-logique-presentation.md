# Epic 55: Séparer la logique métier de la présentation (Container/Presenter pattern)

Status: split-into-stories

## Contexte

Plusieurs composants mélangent la récupération de données, la logique métier et le rendu visuel dans un seul fichier. Exemple : `DashboardHoroscopeSummaryCard.tsx` fait un appel API, gère les états loading/error et rend la carte en même temps.

Ce mélange rend les composants difficiles à tester unitairement, difficiles à réutiliser avec des données différentes, et difficiles à lire.

Un hook `useDashboardAstroSummary.ts` existe déjà pour ce composant — c'est le bon pattern, il faut le généraliser.

## Objectif Produit

Séparer systématiquement les composants complexes en :
- **Hook** (`useXxx.ts`) : fetching, état, logique métier
- **Composant présentationnel** (`Xxx.tsx`) : reçoit des props, rend du JSX, pas de logique

## Non-objectifs

- Ne pas séparer les composants simples qui n'ont pas de logique de données
- Ne pas créer une couche Redux ou un state management global
- Ne pas déplacer les hooks déjà bien séparés (les hooks existants sont en majorité corrects)

## Découpage en stories

- 55.1 Séparer les composants dashboard complexes (DashboardHoroscopeSummaryCard, DailyInsightsSection)
- 55.2 Séparer les composants de prédiction (DayPredictionCard, CategoryGrid)
- 55.3 Séparer les pages-composants qui font du fetching (AstrologersPage, ConsultationsPage)

## Références

- [Source: frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx]
- [Source: frontend/src/components/dashboard/useDashboardAstroSummary.ts]
- [Source: frontend/src/components/DailyInsightsSection.tsx]
- [Source: frontend/src/components/prediction/DayPredictionCard.tsx]
