# Epic 56: Standardiser les Error Boundaries et les états d'erreur

Status: split-into-stories

## Contexte

Un composant `ErrorBoundary.tsx` existe dans le projet mais est peu ou pas utilisé autour des pages. Les erreurs JavaScript non gérées dans un composant React font planter l'ensemble de l'arbre de rendu sans afficher d'état d'erreur utilisable.

De plus, les états d'erreur dans les pages (erreur API, données absentes) sont gérés de façon incohérente : certaines pages affichent un `<span className="chat-error">`, d'autres n'affichent rien, d'autres encore ont leur propre UI d'erreur.

## Objectif Produit

Fournir une couverture systématique des erreurs à deux niveaux :
1. **Error Boundaries React** : capturer les erreurs de rendu JS et afficher une UI de fallback
2. **États d'erreur API** : composant `<ErrorState>` unifié pour les erreurs de chargement

## Non-objectifs

- Ne pas gérer le logging des erreurs vers un service externe (Sentry etc.)
- Ne pas refondre la gestion des erreurs API dans les hooks de données

## Découpage en stories

- 56.1 Créer `<PageErrorBoundary>` et `<SectionErrorBoundary>` à partir du ErrorBoundary existant
- 56.2 Créer le composant `<ErrorState>` unifié (icône + message + bouton retry)
- 56.3 Déployer les error boundaries sur toutes les pages et sections critiques

## Références

- [Source: frontend/src/components/ErrorBoundary.tsx]
- [Source: frontend/src/components/ui/EmptyState/EmptyState.tsx] (Epic 50 — pattern similaire)
- [Source: frontend/src/pages/DashboardPage.tsx]
- [Source: frontend/src/App.css]
