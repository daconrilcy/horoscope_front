# Story 45.4: Verrouiller QA, accessibilité et cohérence i18n du parcours dashboard

Status: ready-for-dev

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

- [ ] Task 1: Réaligner les tests de routing et navigation (AC: 1, 4, 5, 6)
  - [ ] Adapter `frontend/src/tests/router.test.tsx` au split `/dashboard` / `/dashboard/horoscope`
  - [ ] Ajouter la vérification du chemin retour vers `/dashboard`
  - [ ] Vérifier l'activation de l'item dashboard dans le bottom nav sur les deux routes
  - [ ] Vérifier les comportements du shell/header sur les deux routes

- [ ] Task 2: Verrouiller les états UI de la landing dashboard (AC: 2, 4, 6)
  - [ ] Ajouter/adapter les tests `success`
  - [ ] Ajouter/adapter les tests `loading`
  - [ ] Ajouter/adapter les tests `error`
  - [ ] Ajouter/adapter les tests `empty`
  - [ ] Vérifier que la section activités reste visible sur tous ces états

- [ ] Task 3: Verrouiller les états UI de la page détail (AC: 3, 4, 6, 8)
  - [ ] Réaligner `frontend/src/tests/TodayPage.test.tsx` sur la nouvelle route détail
  - [ ] Vérifier la présence continue des sections daily critiques
  - [ ] Vérifier l'absence de la section activités
  - [ ] Vérifier que les enrichissements moments clés/agendas des epics 43/44 sont toujours rendus

- [ ] Task 4: Encadrer la dette i18n du nouveau parcours (AC: 7)
  - [ ] Identifier toutes les nouvelles chaînes introduites par l'epic 45
  - [ ] Les centraliser dans les fichiers i18n appropriés ou, à défaut, dans un helper localisé testable
  - [ ] Éviter d'ajouter de nouveaux textes en dur dans les composants touchés
  - [ ] Ajouter des tests ciblés au minimum sur les nouveaux libellés critiques du parcours

- [ ] Task 5: Réaliser une passe de non-régression ciblée (AC: 5, 8)
  - [ ] Vérifier que les tests existants obsolètes sont mis à jour et non simplement supprimés
  - [ ] Vérifier que les assertions historiques sur `/dashboard` sont réécrites selon le nouveau produit attendu
  - [ ] Vérifier qu'aucune hypothèse de tests n'associe encore par erreur `/dashboard` à la page détail
  - [ ] Documenter clairement les points de couverture modifiés

## Dev Notes

### Intention de la story

- Cette story verrouille l'epic 45.
- Le risque principal n'est pas la complexité algorithmique, mais la régression silencieuse:
  - tests qui continuent d'asserter l'ancien comportement,
  - navigation cassée,
  - header incohérent,
  - hardcodes ajoutés lors du split.

### Contexte existant à ne pas casser

- `TodayPage.test.tsx` couvre déjà de nombreux cas du daily détaillé, y compris les enrichissements récents des moments clés.
- `DashboardPage.test.tsx` est actuellement centré sur un dashboard legacy et devra être réécrit, pas simplement retiré.
- `Header.test.tsx` encode aujourd'hui une hypothèse stricte sur `/dashboard` exact.
- `router.test.tsx` associe encore `/dashboard` à la vue daily détaillée actuelle.
- `ShortcutCard.test.tsx` couvre la section activités existante.

### Technical Requirements

- La validation de l'epic 45 reste frontend only.
- Ne pas créer de faux positifs en supprimant des assertions sans les remplacer.
- Priorité aux tests RTL/Vitest déjà présents dans le repo.
- Si un composant est rendu plus configurable pour i18n ou accessibilité, ajouter les tests ciblés correspondants.

### i18n Requirements

- Les composants déjà touchés par l'epic 45 ne doivent pas recevoir de nouvelles chaînes en dur si une centralisation raisonnable est possible.
- Les points les plus sensibles à couvrir:
  - libellé ou aria-label du résumé dashboard
  - bouton retour dashboard
  - messages d'état landing/détail si nouveaux
- Cette story ne doit pas devenir un refactor i18n global de tout le front; elle doit verrouiller le périmètre effectivement modifié.

### Accessibility Requirements

- Le résumé dashboard doit être focusable s'il est activable.
- L'activation clavier doit être testée.
- Le bouton retour doit exposer un nom accessible stable.
- Les états `error` et `empty` doivent rester lisibles au lecteur d'écran et ne pas piéger l'utilisateur.

### Architecture Compliance

- Garder les tests au plus proche des composants/pages/routes déjà existants.
- Ne pas déplacer arbitrairement les suites de tests si ce n'est pas nécessaire.
- Les ajustements i18n doivent rester localisés dans `frontend/src/i18n` ou dans des helpers dédiés, pas disséminés dans plusieurs composants.

### File Structure Requirements

- Tests principaux à toucher:
  - `frontend/src/tests/router.test.tsx`
  - `frontend/src/tests/DashboardPage.test.tsx`
  - `frontend/src/tests/TodayPage.test.tsx`
  - `frontend/src/tests/layout/Header.test.tsx`
  - `frontend/src/tests/ShortcutCard.test.tsx`
  - `frontend/src/tests/TodayHeader.test.tsx` si l'en-tête évolue
- Fichiers i18n potentiels:
  - `frontend/src/i18n/dashboard.tsx`
  - `frontend/src/utils/predictionI18n.ts`
  - ou nouveau helper ciblé si nécessaire

### Testing Requirements

- Exécuter les suites frontend ciblées du parcours dashboard après implémentation.
- Vérifier les cas positifs et négatifs.
- Vérifier le daily enrichi existant après déplacement de route.
- Vérifier que le parcours clavier est toujours utilisable.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic-45]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md]
- [Source: frontend/src/tests/router.test.tsx]
- [Source: frontend/src/tests/DashboardPage.test.tsx]
- [Source: frontend/src/tests/TodayPage.test.tsx]
- [Source: frontend/src/tests/layout/Header.test.tsx]
- [Source: frontend/src/tests/ShortcutCard.test.tsx]
- [Source: frontend/src/tests/TodayHeader.test.tsx]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story créée via le workflow BMAD `bmad-bmm-create-story` en mode autonome.

### Completion Notes List

- Story prête au dev.
- Le principal enjeu de QA est la réécriture propre des tests qui supposaient encore que `/dashboard` était la page daily détaillée.
- La centralisation des nouvelles chaînes est limitée au périmètre touché par l'epic 45 pour éviter un refactor i18n opportuniste.

### File List

- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `frontend/src/tests/router.test.tsx`
- `frontend/src/tests/DashboardPage.test.tsx`
- `frontend/src/tests/TodayPage.test.tsx`
- `frontend/src/tests/layout/Header.test.tsx`
- `frontend/src/tests/ShortcutCard.test.tsx`
- `frontend/src/tests/TodayHeader.test.tsx`
- `frontend/src/i18n/dashboard.tsx`
- `frontend/src/utils/predictionI18n.ts`
