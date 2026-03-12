# Story 45.2: Créer la landing dashboard avec résumé et hub d'activités

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur authentifié,
I want voir sur `/dashboard` uniquement un résumé très court de mon horoscope du jour puis mes autres activités,
so that j'accède immédiatement à l'essentiel avant de choisir d'aller plus loin ou d'ouvrir un autre parcours.

## Acceptance Criteria

1. La page `/dashboard` affiche un cadre horoscope dédié contenant uniquement le résumé du jour et non la version détaillée actuelle.
2. Le résumé affiché provient du daily existant (`summary.overall_summary`) et est limité visuellement à 2 lignes maximum sur mobile et desktop.
3. Le cadre résumé est entièrement cliquable ou activable au clavier et ouvre `/dashboard/horoscope`.
4. Sous le cadre résumé, la page affiche la section des autres activités disponibles, en s'appuyant sur les raccourcis déjà présents (`chat`, `tirage`, etc.).
5. Les états `loading`, `error` et `empty` de la donnée daily sont gérés dans la landing sans faire disparaître le hub d'activités.
6. La landing dashboard n'affiche plus `Moments clés du jour`, `Agenda du jour`, ni les autres sections du détail daily.
7. Le frontend réutilise le hook `useDailyPrediction` existant et ne demande aucun endpoint backend supplémentaire.
8. Les interactions restent accessibles:
   - activation clavier du cadre résumé
   - nom explicite du lien/bouton
   - feedback lisible en cas d'erreur ou d'absence de prédiction

## Tasks / Subtasks

- [x] Task 1: Recomposer `DashboardPage` comme landing réelle (AC: 1, 4, 6)
  - [x] Retirer la logique de dashboard legacy devenue hors sujet si elle ne correspond plus au parcours demandé
  - [x] Conserver une structure simple: en-tête page, carte résumé, hub d'activités
  - [x] Positionner le hub d'activités sous le résumé, sans éléments détaillés intermédiaires
  - [x] Réutiliser `ShortcutsSection` plutôt que recréer une deuxième implémentation des activités

- [x] Task 2: Brancher les données daily minimales sur la landing (AC: 1, 2, 5, 7)
  - [x] Réutiliser `useDailyPrediction(accessToken)` existant
  - [x] Utiliser `summary.overall_summary` comme source unique du texte résumé
  - [x] Prévoir un rendu `loading`
  - [x] Prévoir un rendu `error` avec message/action de récupération lisible
  - [x] Prévoir un rendu `empty` ou setup manquant sans casser l'accès aux activités

- [x] Task 3: Construire le composant de résumé dashboard avec activation vers le détail (AC: 2, 3, 8)
  - [x] Créer un composant dédié `DashboardHoroscopeSummaryCard`
  - [x] Limiter visuellement le texte à 2 lignes sans tronquer la source métier
  - [x] Rendre le conteneur cliquable et activable au clavier
  - [x] Naviguer explicitement vers `/dashboard/horoscope`
  - [x] Ajouter un nom accessible explicite du type `Voir l'horoscope du jour`

- [x] Task 4: Gérer proprement les états de la landing (AC: 5, 8)
  - [x] En `loading`, garder la section activités visible
  - [x] En `error`, proposer une relance ciblée de récupération du daily
  - [x] En `empty`, afficher un message d'absence de prédiction et une action de setup si nécessaire
  - [x] Ne jamais remplacer toute la page par un état bloquant qui masque les autres activités

- [x] Task 5: Couvrir la landing par des tests dédiés (AC: 2, 3, 4, 5, 6, 8)
  - [x] Réécrire `frontend/src/tests/DashboardPage.test.tsx`
  - [x] Ajouter un test de navigation vers `/dashboard/horoscope`
  - [x] Ajouter des tests `loading/error/empty`
  - [x] Vérifier l'absence de sections détaillées (`Moments clés`, `Agenda`) sur `/dashboard`
  - [x] Vérifier que les raccourcis restent présents quel que soit l'état du daily

## Dev Notes

- Created `DashboardHoroscopeSummaryCard` component.
- Updated `DashboardPage` to use the new summary card and `ShortcutsSection`.
- Added CSS for the summary card and skeletons.
- Centralized landing strings and shortcut labels in `frontend/src/i18n/dashboard.tsx`.
- Added an explicit retry action for landing error state and keyboard support for both `Enter` and `Space`.
- Updated `DashboardPage.test.tsx` with landing-specific scenarios and i18n coverage.

### Completion Notes List

- Dashboard landing now shows a 2-line summary of the daily horoscope.
- Summary card links to the detailed horoscope page.
- Shortcuts section is always visible below the summary.
- Loading, empty and error states are handled without masking activities.
- Error state now offers a targeted retry instead of a dead-end message.
- Accessibility is preserved for mouse and keyboard activation, including `Space`.
- Shortcut labels are localized from the same dashboard translation catalog.

### File List

- `frontend/src/i18n/dashboard.tsx`
- `frontend/src/components/ShortcutsSection.tsx`
- `frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/App.css`
- `frontend/src/tests/DashboardPage.test.tsx`
- `frontend/src/tests/ShortcutCard.test.tsx`
