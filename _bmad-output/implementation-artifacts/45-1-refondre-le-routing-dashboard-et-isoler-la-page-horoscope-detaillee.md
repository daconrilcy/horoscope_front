# Story 45.1: Refondre le routing dashboard et isoler la page horoscope détaillée

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a frontend architect,
I want séparer explicitement la landing `/dashboard` du détail horoscope `/dashboard/horoscope`,
so that le menu dashboard ouvre une page d'accueil légère sans perdre la continuité de navigation vers l'horoscope complet.

## Acceptance Criteria

1. La route authentifiée `/dashboard` ne rend plus directement `TodayPage` ni l'équivalent de la page daily détaillée actuelle.
2. Une route authentifiée dédiée `/dashboard/horoscope` est introduite pour le détail complet du daily, sous le même shell applicatif.
3. Le bottom nav garde l'item dashboard actif sur `/dashboard` et `/dashboard/horoscope`, sans régression sur les autres routes.
4. Le header shell ne crée pas de double titre ni de comportement incohérent sur les routes du sous-parcours dashboard.
5. `RootRedirect`, `AuthGuard` et les redirections existantes continuent d'envoyer l'utilisateur authentifié vers `/dashboard`.
6. Les deep links vers `/chat`, `/consultations`, `/settings`, `/astrologers` et les autres pages ne changent pas.
7. Les tests de routing couvrent explicitement l'existence des deux routes et la cohérence des états actifs de navigation.

## Tasks / Subtasks

- [x] Task 1: Rebrancher le contrat de routing dashboard (AC: 1, 2, 5, 6)
  - [x] Remplacer le binding actuel `/dashboard -> TodayPage` dans `frontend/src/app/routes.tsx`
  - [x] Introduire explicitement la route `/dashboard/horoscope`
  - [x] Garder la redirection racine vers `/dashboard` inchangée
  - [x] Vérifier que les routes existantes non liées au dashboard ne changent pas

- [x] Task 2: Clarifier les responsabilités des pages du parcours dashboard (AC: 1, 2, 4)
  - [x] Réaffecter la page de landing dashboard à un composant dédié `DashboardPage`
  - [x] Réaffecter la page détaillée du daily à un composant dédié `DailyHoroscopePage` (renommé depuis `TodayPage`)
  - [x] Éviter toute logique de page hybride qui continuerait à afficher landing et détail sur la même route
  - [x] Préserver un delta minimal en réutilisant les composants et hooks déjà présents

- [x] Task 3: Recaler les règles de header et de navigation (AC: 3, 4)
  - [x] Mettre à jour `frontend/src/components/layout/Header.tsx` pour traiter le sous-arbre dashboard de façon cohérente
  - [x] Conserver la logique d'activation du bottom nav sur les sous-routes dashboard
  - [x] Vérifier qu'aucun double `Horoscope` n'apparaît entre le shell et l'en-tête de page
  - [x] Vérifier les comportements mobile et desktop

- [x] Task 4: Sécuriser le contrat de routing par des tests (AC: 3, 4, 5, 7)
  - [x] Mettre à jour `frontend/src/tests/router.test.tsx`
  - [x] Mettre à jour `frontend/src/tests/layout/Header.test.tsx`
  - [x] Ajouter ou adapter un test sur l'activation du bottom nav pour une sous-route dashboard
  - [x] Vérifier que `/dashboard/horoscope` reste sous `AuthGuard`

## Dev Notes

- Renamed `TodayPage.tsx` to `DailyHoroscopePage.tsx`.
- Updated `routes.tsx` with nested dashboard routes.
- Updated `Header.tsx` to handle the new dashboard structure.
- All tests updated and passing.

### Completion Notes List

- Implemented nested routing for dashboard.
- Restored `DashboardPage` as the main landing.
- Isolated daily horoscope to `DailyHoroscopePage`.
- Updated `BottomNav` and `Header` logic for both routes.
- Renamed and fixed all relevant tests.

### File List

- `frontend/src/app/routes.tsx`
- `frontend/src/components/layout/Header.tsx`
- `frontend/src/components/layout/BottomNav.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `frontend/src/tests/router.test.tsx`
- `frontend/src/tests/DailyHoroscopePage.test.tsx`
- `frontend/src/tests/layout/Header.test.tsx`
