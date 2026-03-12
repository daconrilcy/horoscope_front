# Story 45.3: Restaurer une page horoscope détaillée avec retour dashboard

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur curieux,
I want consulter l'intégralité de mon horoscope du jour sur une page dédiée,
so that je puisse explorer les moments clés, l'agenda et les thèmes en détail sans être distrait par les autres activités.

## Acceptance Criteria

1. La page `/dashboard/horoscope` affiche toutes les sections détaillées du daily:
   - `DayPredictionCard` (tonalité et résumé)
   - `TurningPointsList` (moments clés)
   - `DayAgenda` (agenda du jour)
   - `CategoryGrid` (détail par thèmes)
2. Un bouton de retour visible en haut de page renvoie explicitement vers `/dashboard`.
3. La page détaillée n'affiche plus le hub d'activités/raccourcis (`ShortcutsSection`) pour éviter la redondance avec la landing.
4. L'en-tête de page (`TodayHeader`) est mis à jour pour supporter le bouton de retour tout en conservant l'avatar et les infos utilisateur.
5. Les tests confirment que l'utilisateur peut naviguer du détail vers la landing via le bouton retour.
6. Le comportement de rafraîchissement (`RefreshCw`) reste fonctionnel et accessible sur la page détaillée.

## Tasks / Subtasks

- [x] Task 1: Finaliser le composant de page détaillée (AC: 1, 3, 6)
  - [x] Nettoyer `DailyHoroscopePage.tsx` pour ne garder que le flux daily complet
  - [x] Retirer l'affichage de `ShortcutsSection`
  - [x] Vérifier que toutes les sections (Agenda, Moments clés, Thèmes) sont correctement rendues
  - [x] S'assurer que le bouton de rafraîchissement est toujours présent et fonctionnel

- [x] Task 2: Ajouter le bouton de retour au dashboard (AC: 2, 4)
  - [x] Étendre `TodayHeader.tsx` pour accepter une prop `onBackClick`
  - [x] Afficher une icône de retour (type `ChevronLeft`) si `onBackClick` est présent
  - [x] Positionner le bouton de retour de façon ergonomique sur mobile et desktop
  - [x] Câbler l'action vers `navigate('/dashboard')` dans `DailyHoroscopePage`

- [x] Task 3: Verrouiller la navigation et le rendu par des tests (AC: 2, 5)
  - [x] Mettre à jour `frontend/src/tests/DailyHoroscopePage.test.tsx`
  - [x] Ajouter un test vérifiant que le clic sur le bouton retour change l'URL vers `/dashboard`
  - [x] Vérifier que le titre et les sections attendues sont bien présents sur la route détaillée
  - [x] Vérifier que `TodayHeader.test.tsx` couvre le nouveau bouton de retour

## Dev Notes

- Updated `TodayHeader` to support `onBackClick`.
- Added CSS for the back button in `App.css`.
- Removed `ShortcutsSection` from `DailyHoroscopePage`.
- All tests updated and passing.

### Completion Notes List

- Detailed horoscope page is now clean and focused.
- Back button implemented in `TodayHeader` and used in `DailyHoroscopePage`.
- UI consistency maintained between landing and detail.
- Verified navigation from detail to landing via tests.

### File List

- `frontend/src/components/TodayHeader.tsx`
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `frontend/src/App.css`
- `frontend/src/tests/TodayHeader.test.tsx`
- `frontend/src/tests/DailyHoroscopePage.test.tsx`
