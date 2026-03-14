# Story 51.2: Refactoriser AppShell → AppLayout + créer PageLayout avec slots

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux un `AppLayout` clairement délimité (navigation uniquement) et un `PageLayout` pour le contenu de chaque page,
afin que la navigation globale et la mise en page du contenu soient deux préoccupations séparées.

## Acceptance Criteria

1. `frontend/src/layouts/AppLayout.tsx` existe et contient exactement ce qu'`AppShell.tsx` contient (Header + Sidebar + BottomNav + main), sans la logique du fond (déplacée en RootLayout — story 51.1).
2. `AppShell.tsx` devient un alias de ré-export vers `AppLayout` pour la rétrocompatibilité — aucune rupture dans `routes.tsx`.
3. `frontend/src/layouts/PageLayout.tsx` existe avec les props `title?`, `header?` (slot ReactNode), `aside?` (slot ReactNode optionnel) et `children`.
4. `PageLayout` applique `max-width: var(--layout-page-max-width, 900px)`, padding et `margin: 0 auto` — les pages n'ont plus besoin de gérer ça.
5. Un token CSS `--layout-page-max-width` est ajouté dans `design-tokens.css`.
6. Les pages `DashboardPage`, `DailyHoroscopePage`, `NatalChartPage`, `BirthProfilePage` utilisent `PageLayout` comme conteneur racine.
7. Le rendu visuel de ces pages est identique avant/après.
8. Les tests existants passent sans modification.

## Tasks / Subtasks

- [ ] Tâche 1 : Créer `AppLayout.tsx` depuis `AppShell.tsx` (AC: 1, 2)
  - [ ] Lire `AppShell.tsx` entièrement
  - [ ] Créer `frontend/src/layouts/AppLayout.tsx` avec le même contenu, sans `StarfieldBackground` (déjà dans RootLayout)
  - [ ] Mettre à jour `AppShell.tsx` pour ré-exporter `AppLayout` : `export { AppLayout as AppShell } from '../layouts/AppLayout'`
  - [ ] Ajouter `AppLayout` au barrel `frontend/src/layouts/index.ts`

- [ ] Tâche 2 : Ajouter le token de layout dans `design-tokens.css` (AC: 5)
  - [ ] Ajouter dans `design-tokens.css` section `/* === LAYOUT === */` :
    - `--layout-page-max-width: 900px`
    - `--layout-page-padding: var(--space-6)` (24px)
    - `--layout-sidebar-width: 220px`

- [ ] Tâche 3 : Créer `PageLayout.tsx` et `PageLayout.css` (AC: 3, 4)
  - [ ] Interface : `{ title?: string; header?: ReactNode; aside?: ReactNode; children: ReactNode; className?: string }`
  - [ ] Rendu : wrapper `.page-layout` + section header optionnel + `<main>` + aside optionnel
  - [ ] CSS : max-width token, padding, margin auto, responsive

- [ ] Tâche 4 : Appliquer `PageLayout` aux 4 pages cibles (AC: 6, 7)
  - [ ] `DashboardPage.tsx` : wrapper racine → `<PageLayout>`
  - [ ] `DailyHoroscopePage.tsx` : wrapper racine → `<PageLayout>`
  - [ ] `NatalChartPage.tsx` : wrapper racine → `<PageLayout>`
  - [ ] `BirthProfilePage.tsx` : wrapper racine → `<PageLayout>`
  - [ ] Pour chaque page : vérifier qu'aucune règle CSS de max-width ou padding local n'entre en conflit

- [ ] Tâche 5 : Validation (AC: 7, 8)
  - [ ] Review visuelle des 4 pages migrées (desktop + mobile)
  - [ ] `npm run test` — tous les tests passent

## Dev Notes

### Contexte technique

**Prérequis** : Story 51.1 `done` (RootLayout — pour que AppLayout n'inclue plus StarfieldBackground).
Si 51.1 n'est pas terminée, `AppLayout` inclut toujours StarfieldBackground et la migration se fait séquentiellement.

### AppShell.tsx actuel (24 lignes)

```tsx
export function AppShell() {
  return (
    <div className="app-shell app-bg">
      <StarfieldBackground />
      <div className="app-bg-container">
        <Header />
        <div className="app-shell-body">
          <Sidebar />
          <main className="app-shell-main">
            <Outlet />
          </main>
        </div>
        <BottomNav />
      </div>
    </div>
  )
}
```

**AppLayout.tsx** (après extraction de StarfieldBackground vers RootLayout) :

```tsx
export function AppLayout() {
  return (
    <>
      <Header />
      <div className="app-shell-body">
        <Sidebar />
        <main className="app-shell-main">
          <Outlet />
        </main>
      </div>
      <BottomNav />
    </>
  )
}
```

Le wrapper `.app-shell.app-bg` et `.app-bg-container` appartiennent maintenant à `RootLayout`.

### Stratégie rétrocompatibilité AppShell

```typescript
// frontend/src/components/AppShell.tsx — après refacto
export { AppLayout as AppShell } from '../layouts/AppLayout'
```

Ainsi, `routes.tsx` (qui importe `AppShell`) continue de fonctionner sans modification.

### PageLayout

```tsx
interface PageLayoutProps {
  title?: string
  header?: React.ReactNode    // slot pour TodayHeader, titre personnalisé, etc.
  aside?: React.ReactNode     // slot pour un panneau latéral optionnel
  children: React.ReactNode
  className?: string
}

export function PageLayout({ title, header, aside, children, className }: PageLayoutProps) {
  return (
    <div className={`page-layout ${className ?? ''}`}>
      {(title || header) && (
        <div className="page-layout__header">
          {title && <h1 className="page-layout__title">{title}</h1>}
          {header}
        </div>
      )}
      <div className={`page-layout__body ${aside ? 'page-layout__body--with-aside' : ''}`}>
        <div className="page-layout__main">{children}</div>
        {aside && <aside className="page-layout__aside">{aside}</aside>}
      </div>
    </div>
  )
}
```

### CSS PageLayout

```css
.page-layout {
  max-width: var(--layout-page-max-width, 900px);
  margin: 0 auto;
  padding: var(--layout-page-padding, var(--space-6));
  width: 100%;
}

.page-layout__header {
  margin-bottom: var(--space-6);
}

.page-layout__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-headline);
}

.page-layout__body--with-aside {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: var(--space-6);
}

@media (max-width: 768px) {
  .page-layout__body--with-aside {
    grid-template-columns: 1fr;
  }
}
```

### Pages à migrer dans cette story

Migrer uniquement les 4 pages les plus simples (pas de layout spécialisé) :
- `DashboardPage` — contenu principal
- `DailyHoroscopePage` — contenu principal
- `NatalChartPage` — contenu principal
- `BirthProfilePage` — formulaire

**Ne pas migrer dans cette story** : ChatPage, ConsultationWizardPage, SettingsPage, AdminPage → ils auront leurs propres layouts en stories 51.3 et 51.4.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/layouts/AppLayout.tsx` |
| Créer | `frontend/src/layouts/PageLayout.tsx` |
| Créer | `frontend/src/layouts/PageLayout.css` |
| Modifier | `frontend/src/layouts/index.ts` (ajouter exports) |
| Modifier | `frontend/src/components/AppShell.tsx` (ré-export alias) |
| Modifier | `frontend/src/styles/design-tokens.css` (tokens layout) |
| Modifier | `frontend/src/pages/DashboardPage.tsx` |
| Modifier | `frontend/src/pages/DailyHoroscopePage.tsx` |
| Modifier | `frontend/src/pages/NatalChartPage.tsx` |
| Modifier | `frontend/src/pages/BirthProfilePage.tsx` |

### Project Structure Notes

- Les classes CSS `app-shell`, `app-shell-body`, `app-shell-main` dans `App.css` restent — ne pas les supprimer
- `AppLayout` utilise ces mêmes classes pour la rétrocompatibilité CSS
- `PageLayout.css` va dans `frontend/src/layouts/` — importer dans `PageLayout.tsx`

### References

- [Source: frontend/src/components/AppShell.tsx]
- [Source: frontend/src/app/routes.tsx]
- [Source: frontend/src/App.css] (classes .app-shell-*)
- [Source: frontend/src/styles/design-tokens.css]
- [Source: frontend/src/pages/DashboardPage.tsx]
- [Source: _bmad-output/planning-artifacts/epic-51-architecture-layouts.md]
- [Source: _bmad-output/implementation-artifacts/51-1-rootlayout-et-authlayout.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
