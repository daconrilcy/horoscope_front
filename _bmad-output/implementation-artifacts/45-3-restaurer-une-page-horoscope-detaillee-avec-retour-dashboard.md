# Story 45.3: Restaurer une page horoscope détaillée avec retour dashboard

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur consultant l'horoscope du jour,
I want ouvrir une page dédiée au daily complet avec un bouton retour clair vers le dashboard,
so that je retrouve tout le détail utile sans perdre mon point d'entrée principal.

## Acceptance Criteria

1. La route `/dashboard/horoscope` affiche la vue daily détaillée actuellement implémentée, avec au minimum:
   - le résumé du jour
   - les moments clés du jour
   - l'agenda du jour
2. Un bouton de retour visible en haut de page renvoie explicitement vers `/dashboard`.
3. La page détail n'affiche plus la section des autres activités, qui appartient désormais à la landing dashboard.
4. La page détail continue à utiliser les données du daily existantes via `useDailyPrediction`, sans changement de contrat backend.
5. Si l'utilisateur ouvre le détail après la landing, le cache React Query existant est réutilisé quand la donnée est déjà disponible.
6. Les états `loading`, `error` et `empty` restent cohérents sur la page détail, et aucun de ces états n'empêche de revenir au dashboard.
7. Les interactions déjà en place sur le daily détaillé ne sont pas régressées sans arbitrage explicite:
   - refresh manuel
   - tracking analytics existant
   - rendu des moments clés et de l'agenda
8. Les tests vérifient la présence du bouton retour, l'absence de la section activités sur la page détail et la stabilité des sections daily critiques.

## Tasks / Subtasks

- [ ] Task 1: Isoler la page daily détaillée du nouveau dashboard (AC: 1, 3, 4)
  - [ ] Réutiliser la logique actuelle de `TodayPage` comme base de la page détail
  - [ ] Supprimer de cette page la section `ShortcutsSection`
  - [ ] Préserver les sections daily critiques déjà live
  - [ ] Vérifier si `CategoryGrid` reste dans le périmètre ou doit être explicitement retirée selon le cadrage produit final

- [ ] Task 2: Introduire un contrôle de retour explicite vers `/dashboard` (AC: 2, 6, 8)
  - [ ] Ajouter un bouton ou lien retour visible au-dessus du contenu détaillé
  - [ ] Utiliser une navigation explicite vers `/dashboard`, pas un simple `navigate(-1)`
  - [ ] Garder ce contrôle disponible même en `error` ou `empty`
  - [ ] Vérifier l'accessibilité clavier et le nom accessible du bouton retour

- [ ] Task 3: Préserver les comportements utiles de la page daily existante (AC: 1, 4, 5, 7)
  - [ ] Conserver `useDailyPrediction`
  - [ ] Conserver la logique de normalisation des `turning_points`
  - [ ] Conserver l'agenda calculé à partir des données existantes
  - [ ] Préserver le tracking analytics déjà présent
  - [ ] Préserver le refresh manuel existant sauf arbitrage produit explicite

- [ ] Task 4: Recaler l'en-tête et la hiérarchie visuelle du détail (AC: 1, 2, 3, 7)
  - [ ] Vérifier l'articulation entre `Header` du shell et `TodayHeader`
  - [ ] Empêcher un double titre ou une hiérarchie confuse
  - [ ] Positionner proprement le bouton retour par rapport au header de page et au bouton refresh
  - [ ] Valider le rendu mobile-first

- [ ] Task 5: Sécuriser le détail par des tests ciblés (AC: 2, 3, 6, 7, 8)
  - [ ] Adapter `frontend/src/tests/TodayPage.test.tsx` pour viser la route `/dashboard/horoscope`
  - [ ] Ajouter un test de retour vers `/dashboard`
  - [ ] Vérifier l'absence de `ShortcutsSection` sur la page détail
  - [ ] Vérifier que les sections daily critiques restent présentes
  - [ ] Vérifier que les états `loading/error/empty` laissent une voie de retour

## Dev Notes

### Intention de la story

- Cette story transforme l'actuelle page daily détaillée en écran explicitement secondaire dans le parcours dashboard.
- Le but n'est pas de réinventer le daily, mais de le déplacer et de le clarifier.
- Le bon réflexe est de partir de l'existant de `TodayPage` et de retirer ce qui appartient désormais à la landing dashboard.

### Contexte existant à réutiliser

- `TodayPage` contient déjà:
  - récupération user + daily
  - refresh
  - normalisation des moments clés
  - agenda dérivé
  - tracking analytics
- Les récents epics 43 et 44 ont enrichi le rendu des moments clés; cette story ne doit pas le casser.
- Le calcul du détail daily est déjà couvert par de nombreux tests frontend.

### Risques connus à prévenir

- Régression de routing si des tests ou composants continuent d'associer `/dashboard` à la page détail.
- Double titre `Horoscope` entre le shell et `TodayHeader`.
- Perte involontaire du bouton refresh ou du tracking existant.
- Régression sur les fallbacks `loading/error/empty` déjà présents dans `TodayPage`.
- Réintroduction des activités dans la page détail par simple duplication.

### Technical Requirements

- Frontend only.
- Réutiliser la query `useDailyPrediction` actuelle; aucun nouvel endpoint.
- Garder la logique de normalisation métier là où elle se trouve aujourd'hui, ou l'extraire proprement si la séparation landing/détail le justifie.
- Si une extraction technique est nécessaire pour éviter la duplication entre landing et détail, privilégier:
  - un hook commun léger pour la récupération des données,
  - ou une extraction de sections de rendu,
  - mais ne pas lancer un refactor transversal inutile.

### Scope Boundaries

- In scope:
  - route détail
  - bouton retour
  - retrait du hub d'activités
  - maintien du daily détaillé
- Out of scope:
  - nouveau contrat backend
  - redesign complet des composants moments clés/agendas
  - refonte graphique hors besoin direct du parcours

### Architecture Compliance

- Rester dans la structure actuelle:
  - pages dans `frontend/src/pages`
  - composants daily dans `frontend/src/components/prediction`
  - hooks de données dans `frontend/src/api`
- Ne pas déplacer la logique de transformation daily dans un composant purement visuel.
- Respecter les patterns de l'app:
  - loading/error/empty explicites
  - navigation React Router
  - server state via React Query

### File Structure Requirements

- Fichiers principaux pressentis:
  - `frontend/src/pages/TodayPage.tsx` ou nouveau `frontend/src/pages/DailyHoroscopePage.tsx`
  - `frontend/src/components/TodayHeader.tsx` si le bouton retour y est intégré
  - `frontend/src/components/layout/Header.tsx`
  - `frontend/src/components/prediction/*`
- Tests principaux:
  - `frontend/src/tests/TodayPage.test.tsx`
  - `frontend/src/tests/router.test.tsx`
  - `frontend/src/tests/TodayHeader.test.tsx` si l'en-tête est étendu

### Testing Requirements

- Tester le rendu détaillé sur `/dashboard/horoscope`.
- Tester le bouton retour vers `/dashboard`.
- Vérifier l'absence de `ShortcutsSection`.
- Vérifier la présence continue de:
  - résumé daily
  - moments clés
  - agenda
- Vérifier que les cas `error` et `empty` conservent une sortie de navigation claire.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic-45]
- [Source: _bmad-output/planning-artifacts/architecture.md]
- [Source: frontend/src/pages/TodayPage.tsx]
- [Source: frontend/src/components/TodayHeader.tsx]
- [Source: frontend/src/components/prediction/DayPredictionCard.tsx]
- [Source: frontend/src/components/prediction/TurningPointsList.tsx]
- [Source: frontend/src/components/prediction/DayAgenda.tsx]
- [Source: frontend/src/api/useDailyPrediction.ts]
- [Source: frontend/src/tests/TodayPage.test.tsx]
- [Source: frontend/src/tests/TodayHeader.test.tsx]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story créée via le workflow BMAD `bmad-bmm-create-story` en mode autonome.

### Completion Notes List

- Story prête au dev.
- Le daily détaillé doit rester un dérivé direct de `TodayPage` pour préserver les enrichissements récents des epics 43/44.
- Le bouton retour doit être explicite et stable, sans dépendre de l'historique navigateur.

### File List

- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `frontend/src/pages/TodayPage.tsx`
- `frontend/src/components/TodayHeader.tsx`
- `frontend/src/components/layout/Header.tsx`
- `frontend/src/components/prediction/DayPredictionCard.tsx`
- `frontend/src/components/prediction/TurningPointsList.tsx`
- `frontend/src/components/prediction/DayAgenda.tsx`
- `frontend/src/api/useDailyPrediction.ts`
- `frontend/src/tests/TodayPage.test.tsx`
- `frontend/src/tests/TodayHeader.test.tsx`
- `frontend/src/tests/router.test.tsx`
