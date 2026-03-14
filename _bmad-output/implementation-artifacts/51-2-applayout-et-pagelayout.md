# Story 51.2: Refactoriser AppShell → AppLayout + créer PageLayout avec slots

Status: done

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

- [x] Tâche 1 : Créer `AppLayout.tsx` depuis `AppShell.tsx` (AC: 1, 2)
  - [x] Lire `AppShell.tsx` entièrement
  - [x] Créer `frontend/src/layouts/AppLayout.tsx` avec le même contenu, sans `StarfieldBackground` (déjà dans RootLayout)
  - [x] Mettre à jour `AppShell.tsx` pour ré-exporter `AppLayout` : `export { AppLayout as AppShell } from '../layouts/AppLayout'`
  - [x] Ajouter `AppLayout` au barrel `frontend/src/layouts/index.ts`

- [x] Tâche 2 : Ajouter le token de layout dans `design-tokens.css` (AC: 5)
  - [x] Ajouter dans `design-tokens.css` section `/* === LAYOUT === */` :
    - `--layout-page-max-width: 900px`
    - `--layout-page-padding: var(--space-6)` (24px)
    - `--layout-sidebar-width: 220px`

- [x] Tâche 3 : Créer `PageLayout.tsx` et `PageLayout.css` (AC: 3, 4)
  - [x] Interface : `{ title?: string; header?: ReactNode; aside?: ReactNode; children: ReactNode; className?: string }`
  - [x] Rendu : wrapper `.page-layout` + section header optionnel + `<main>` + aside optionnel
  - [x] CSS : max-width token, padding, margin auto, responsive

- [x] Tâche 4 : Appliquer `PageLayout` aux 4 pages cibles (AC: 6, 7)
  - [x] `DashboardPage.tsx` : wrapper racine → `<PageLayout>`
  - [x] `DailyHoroscopePage.tsx` : wrapper racine → `<PageLayout>`
  - [x] `NatalChartPage.tsx` : wrapper racine → `<PageLayout>`
  - [x] `BirthProfilePage.tsx` : wrapper racine → `<PageLayout>`
  - [x] Pour chaque page : vérifier qu'aucune règle CSS de max-width ou padding local n'entre en conflit

- [x] Tâche 5 : Validation (AC: 7, 8)
  - [x] Review visuelle des 4 pages migrées (desktop + mobile)
  - [x] `npm run test` — tous les tests passent

## Dev Notes

...

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Création d' `AppLayout` et refactorisation d'`AppShell` en alias.
- Ajout des tokens de layout dans `design-tokens.css`.
- Création de `PageLayout` avec support des slots (title, header, aside).
- Migration réussie de `DashboardPage`, `DailyHoroscopePage`, `NatalChartPage` et `BirthProfilePage`.
- Validation via 1079 tests réussis.

### File List
- `frontend/src/layouts/AppLayout.tsx`
- `frontend/src/layouts/PageLayout.tsx`
- `frontend/src/layouts/PageLayout.css`
- `frontend/src/layouts/index.ts`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/styles/design-tokens.css`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/pages/BirthProfilePage.tsx`
