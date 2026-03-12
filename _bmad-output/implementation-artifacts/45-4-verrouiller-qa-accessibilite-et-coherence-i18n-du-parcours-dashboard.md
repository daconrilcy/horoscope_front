# Story 45.4: Verrouiller QA, accessibilité et cohérence i18n du parcours dashboard

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a QA engineer,
I want verrouiller le nouveau parcours dashboard par des tests de routing, d'états UI et de navigation,
so that la séparation landing/détail n'introduise ni régression fonctionnelle, ni incohérence visuelle, ni dette i18n supplémentaire.

## Acceptance Criteria

1. Les tests couvrent explicitement le parcours utilisateur:
   - ouverture de `/dashboard`
   - ouverture du détail via le résumé
   - retour explicite vers `/dashboard`
2. Les suites frontend couvrent les états `loading`, `error`, `empty` et `success` sur la landing dashboard.
3. Les suites frontend couvrent les états `loading`, `error`, `empty` et `success` sur la page détail horoscope.
4. Les tests vérifient que:
   - la landing dashboard n'affiche pas les sections détaillées du daily
   - la page détail n'affiche pas le hub d'activités
5. Le header shell et le bottom nav restent cohérents sur les deux routes du parcours dashboard.
6. Les interactions critiques restent accessibles:
   - activation clavier du résumé dashboard
   - bouton retour utilisable au clavier
   - libellés accessibles présents
7. Toute nouvelle chaîne introduite dans l'epic 45 est centralisée de manière testable; aucune nouvelle dette de hardcode gratuit n'est introduite.
8. Les régressions sur le daily détaillé enrichi des epics 43/44 restent couvertes après le split de routes.

## Tasks / Subtasks

- [x] Task 1: Réaligner les tests de routing et navigation (AC: 1, 4, 5, 6)
  - [x] Adapter `frontend/src/tests/router.test.tsx` au split `/dashboard` / `/dashboard/horoscope`
  - [x] Ajouter la vérification du chemin retour vers `/dashboard`
  - [x] Vérifier l'activation de l'item dashboard dans le bottom nav sur les deux routes
  - [x] Vérifier les comportements du shell/header sur les deux routes

- [x] Task 2: Verrouiller les états UI de la landing dashboard (AC: 2, 4, 6)
  - [x] Ajouter/adapter les tests `success`
  - [x] Ajouter/adapter les tests `loading`
  - [x] Ajouter/adapter les tests `error`
  - [x] Ajouter/adapter les tests `empty`
  - [x] Vérifier que la section activités reste visible sur tous ces états

- [x] Task 3: Verrouiller les états UI de la page détail (AC: 3, 4, 6, 8)
  - [x] Réaligner `frontend/src/tests/DailyHoroscopePage.test.tsx` sur la nouvelle route détail
  - [x] Vérifier la présence continue des sections daily critiques
  - [x] Vérifier l'absence de la section activités
  - [x] Vérifier que les enrichissements moments clés/agendas des epics 43/44 sont toujours rendus

- [x] Task 4: Encadrer la dette i18n du nouveau parcours (AC: 7)
  - [x] Identifier toutes les nouvelles chaînes introduites par l'epic 45
  - [x] Les centraliser dans les fichiers i18n appropriés
  - [x] Éviter d'ajouter de nouveaux textes en dur dans les composants touchés
  - [x] Ajouter des tests ciblés au minimum sur les nouveaux libellés critiques du parcours

- [x] Task 5: Réaliser une passe de non-régression ciblée (AC: 5, 8)
  - [x] Vérifier que les tests existants obsolètes sont mis à jour et non simplement supprimés
  - [x] Vérifier que les assertions historiques sur `/dashboard` sont réécrites selon le nouveau produit attendu
  - [x] Vérifier qu'aucune hypothèse de tests n'associe encore par erreur `/dashboard` à la page détail
  - [x] Documenter clairement les points de couverture modifiés

## Dev Notes

- The targeted dashboard QA set now passes in `router.test.tsx`, `DashboardPage.test.tsx`, `DailyHoroscopePage.test.tsx`, `TodayHeader.test.tsx`, `Header.test.tsx` and `ShortcutCard.test.tsx` (92 assertions).
- `frontend/src/i18n/dashboard.tsx` now centralizes the landing, shortcuts and header strings introduced by epic 45.
- Accessibility is verified for the summary card (`Enter` and `Space`), the detail back button and localized accessible labels.
- A full `npm test` pass was rerun after the fixes; cross-suite redirect expectations impacted by the new landing were updated accordingly.
- A final cleanup pass removed noisy frontend test output by silencing dev-only analytics/store logs in test mode and aligning the remaining `MemoryRouter` tests with React Router future flags.

### Completion Notes List

- Verified full navigation flow: Dashboard -> Horoscope -> Dashboard.
- All UI states (loading, error, success) covered by tests for both landing and detail pages.
- Confirmed no regression on Epic 43/44 features.
- Clean i18n implementation without hardcoded strings in the epic 45 components.
- Updated legacy tests that still expected the old `/dashboard` detailed page.
- Test runs are now clean on the dashboard-related frontend suites, without analytics debug noise, consultation store warnings or React Router future-flag warnings.

### File List

- `frontend/src/tests/router.test.tsx`
- `frontend/src/tests/AdminPage.test.tsx`
- `frontend/src/tests/DashboardPage.test.tsx`
- `frontend/src/tests/DailyHoroscopePage.test.tsx`
- `frontend/src/tests/layout/Header.test.tsx`
- `frontend/src/tests/BottomNavPremium.test.tsx`
- `frontend/src/tests/ShortcutCard.test.tsx`
- `frontend/src/tests/TodayHeader.test.tsx`
- `frontend/src/tests/visual-smoke.test.tsx`
- `frontend/src/i18n/dashboard.tsx`
- `frontend/src/utils/analytics.ts`
- `frontend/src/state/consultationStore.tsx`
