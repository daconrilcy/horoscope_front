# Story 56.3: Déployer les error boundaries sur toutes les pages et sections critiques

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux que les `PageErrorBoundary` et `SectionErrorBoundary` soient déployés sur toutes les pages et sections critiques,
afin qu'une erreur JavaScript dans un composant affiche une UI de fallback utile plutôt que de faire planter l'app entière.

## Acceptance Criteria

1. Toutes les pages dans `AppShell` sont enveloppées dans un `PageErrorBoundary` au niveau du router ou du layout.
2. Les sections critiques (dashboard, chat, prediction) sont enveloppées dans des `SectionErrorBoundary`.
3. Les erreurs API visibles à l'utilisateur utilisent `<ErrorState>` au lieu de spans inline ou de rien.
4. L'app ne crashe plus entièrement si un composant lève une exception JavaScript.
5. Les tests existants passent sans modification.

## Tasks / Subtasks

- [ ] Tâche 1 : Déployer `PageErrorBoundary` au niveau router/layout (AC: 1)
  - [ ] Lire `frontend/src/app/routes.tsx` et `frontend/src/components/AppShell.tsx`
  - [ ] Envelopper `<Outlet />` dans `AppShell` avec `PageErrorBoundary`
  - [ ] Ou envelopper chaque route dans `routes.tsx` — choisir l'approche la plus simple

- [ ] Tâche 2 : Identifier les sections critiques (AC: 2)
  - [ ] Lire les pages : `DashboardPage`, `ChatPage` (ou équivalent), page prédiction
  - [ ] Identifier les blocs qui peuvent lever des erreurs JS indépendamment

- [ ] Tâche 3 : Déployer `SectionErrorBoundary` sur les sections critiques (AC: 2)
  - [ ] Envelopper `DashboardHoroscopeSummaryCard` (ou Container)
  - [ ] Envelopper la section chat si isolable
  - [ ] Envelopper `DayPredictionCard` (ou Container)

- [ ] Tâche 4 : Remplacer les affichages d'erreur hétérogènes (AC: 3)
  - [ ] Grep `chat-error`, erreurs inline dans les pages
  - [ ] Remplacer par `<ErrorState message={...} onRetry={...} />`

- [ ] Tâche 5 : Validation (AC: 4, 5)
  - [ ] Simuler une erreur JS dans un composant (throw dans render) — vérifier le fallback
  - [ ] `npm run test`

## Dev Notes

### Contexte technique

**Prérequis** : Stories 56.1 et 56.2 `done`.

**Stratégie de déploiement** :

Option A — Boundary au niveau AppShell (minimum) :
```tsx
// AppShell.tsx
<main className="app-shell-main">
  <PageErrorBoundary>
    <Outlet />
  </PageErrorBoundary>
</main>
```

Option B — Boundary par route dans routes.tsx :
```tsx
{
  element: <PageErrorBoundary><DashboardPage /></PageErrorBoundary>
}
```

Recommandation : Option A pour la couverture minimale, puis Option B pour les pages complexes si nécessaire.

**Sections à prioriser** :
1. Dashboard — plusieurs cartes indépendantes
2. Chat — récupération d'historique peut échouer
3. Page prédiction — rendu de données astrologiques complexes

**Ne pas over-enginer** : Toutes les sections n'ont pas besoin d'un SectionErrorBoundary. Prioriser les sections qui font du fetching asynchrone ou qui rendent des données dynamiques complexes.

**Simulation d'erreur pour test** (temporaire, à supprimer) :
```tsx
// Dans un composant pour tester
if (Math.random() < 0.5) throw new Error('Test error')
```

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Lire/modifier | `frontend/src/components/AppShell.tsx` |
| Lire | `frontend/src/app/routes.tsx` |
| Lire/modifier | `frontend/src/pages/DashboardPage.tsx` |
| Modifier | Pages avec erreurs hétérogènes identifiées |

### References

- [Source: frontend/src/components/AppShell.tsx]
- [Source: frontend/src/app/routes.tsx]
- [Source: frontend/src/pages/DashboardPage.tsx]
- [Source: _bmad-output/implementation-artifacts/56-1-page-et-section-error-boundaries.md]
- [Source: _bmad-output/implementation-artifacts/56-2-composant-errorstate-unifie.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
