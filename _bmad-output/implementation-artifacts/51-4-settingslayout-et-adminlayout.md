# Story 51.4: Créer SettingsLayout et AdminLayout

Status: done

## Story

En tant que développeur frontend,
je veux des layouts `SettingsLayout` et `AdminLayout` extrayant la structure de leurs pages respectives,
afin que la mise en page des onglets de Settings et du hub Admin soit réutilisable indépendamment du contenu.

## Acceptance Criteria

1. `frontend/src/layouts/SettingsLayout.tsx` existe avec les props `title`, `tabs` (intégré ou slot), `children`.
2. `frontend/src/layouts/AdminLayout.tsx` existe avec les props `title`, `sections` (config de navigation), `backToHubLabel`, `children`.
3. `SettingsPage.tsx` est simplifié pour utiliser `SettingsLayout`.
4. `AdminPage.tsx` est simplifié pour utiliser `AdminLayout`.
5. Le rendu visuel de Settings et Admin est identique avant/après.
6. Les onglets de Settings (Account, Subscription, Usage) et les sections Admin (Pricing, Monitoring, Personas, Reconciliation) fonctionnent correctement.
7. Les tests existants passent sans modification.

## Tasks / Subtasks

- [x] Tâche 1 : Lire `SettingsPage.tsx` et `SettingsTabs.tsx` (AC: 1, 3)
  - [x] Identification de la structure : titre + onglets + contenu.

- [x] Tâche 2 : Lire `AdminPage.tsx` et `AdminPage.css` (AC: 2, 4)
  - [x] Extraction des styles vers `AdminLayout.css`.

- [x] Tâche 3 : Créer `SettingsLayout.tsx` (AC: 1)
  - [x] Intégration de `SettingsTabs` pour centraliser le layout du module.

- [x] Tâche 4 : Créer `AdminLayout.tsx` et `AdminLayout.css` (AC: 2)
  - [x] Implémentation de la logique Hub (grille) vs Détail (Outlet).
  - [x] Utilisation des tokens de design dans le nouveau CSS.

- [x] Tâche 5 : Simplifier `SettingsPage.tsx` (AC: 3)
  - [x] Remplacement du wrapper par `SettingsLayout`.

- [x] Tâche 6 : Simplifier `AdminPage.tsx` (AC: 4)
  - [x] Remplacement du hub/détail par `AdminLayout` en passant la config des sections.

- [x] Tâche 7 : Validation (AC: 5, 6, 7)
  - [x] `npm run test` — 1079 tests réussis.

## Dev Notes

### Standardisation des layouts de modules

Les modules `Settings` et `Admin` disposent désormais de leurs propres layouts structurels. Cela permet de garantir une cohérence visuelle parfaite entre les différentes sous-pages de ces modules (ex: tous les onglets de settings partagent exactement le même positionnement de titre et d'onglets via le layout).

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List
- Création de `SettingsLayout` intégrant les onglets.
- Création de `AdminLayout` gérant dynamiquement le hub et les vues détaillées.
- Migration de `SettingsPage` et `AdminPage` vers ces layouts.
- Nettoyage du CSS obsolète (`AdminPage.css`).
- Validation via 1079 tests réussis.

### File List
- `frontend/src/layouts/SettingsLayout.tsx`
- `frontend/src/layouts/AdminLayout.tsx`
- `frontend/src/layouts/AdminLayout.css`
- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/pages/AdminPage.tsx`
