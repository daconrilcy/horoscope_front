# Story 45.2: Créer la landing dashboard avec résumé et hub d'activités

Status: ready-for-dev

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

- [ ] Task 1: Recomposer `DashboardPage` comme landing réelle (AC: 1, 4, 6)
  - [ ] Retirer la logique de dashboard legacy devenue hors sujet si elle ne correspond plus au parcours demandé
  - [ ] Conserver une structure simple: en-tête page, carte résumé, hub d'activités
  - [ ] Positionner le hub d'activités sous le résumé, sans éléments détaillés intermédiaires
  - [ ] Réutiliser `ShortcutsSection` plutôt que recréer une deuxième implémentation des activités

- [ ] Task 2: Brancher les données daily minimales sur la landing (AC: 1, 2, 5, 7)
  - [ ] Réutiliser `useDailyPrediction(accessToken)` existant
  - [ ] Utiliser `summary.overall_summary` comme source unique du texte résumé
  - [ ] Prévoir un rendu `loading`
  - [ ] Prévoir un rendu `error` avec message/action de récupération lisible
  - [ ] Prévoir un rendu `empty` ou setup manquant sans casser l'accès aux activités

- [ ] Task 3: Construire le composant de résumé dashboard avec activation vers le détail (AC: 2, 3, 8)
  - [ ] Créer un composant dédié si nécessaire au lieu de détourner lourdement `HeroHoroscopeCard`
  - [ ] Limiter visuellement le texte à 2 lignes sans tronquer la source métier
  - [ ] Rendre le conteneur cliquable et activable au clavier
  - [ ] Naviguer explicitement vers `/dashboard/horoscope`
  - [ ] Ajouter un nom accessible explicite du type `Voir l'horoscope du jour`

- [ ] Task 4: Gérer proprement les états de la landing (AC: 5, 8)
  - [ ] En `loading`, garder la section activités visible
  - [ ] En `error`, proposer une relance ciblée de récupération du daily
  - [ ] En `empty`, afficher un message d'absence de prédiction et une action de setup si nécessaire
  - [ ] Ne jamais remplacer toute la page par un état bloquant qui masque les autres activités

- [ ] Task 5: Couvrir la landing par des tests dédiés (AC: 2, 3, 4, 5, 6, 8)
  - [ ] Adapter ou réécrire `frontend/src/tests/DashboardPage.test.tsx`
  - [ ] Ajouter un test de navigation vers `/dashboard/horoscope`
  - [ ] Ajouter des tests `loading/error/empty`
  - [ ] Vérifier l'absence de sections détaillées (`Moments clés`, `Agenda`) sur `/dashboard`
  - [ ] Vérifier que les raccourcis restent présents quel que soit l'état du daily

## Dev Notes

### Intention de la story

- Cette story transforme `/dashboard` en véritable point d'entrée léger.
- Le dashboard doit devenir une page de synthèse et d'orientation, pas la page daily complète.
- Le produit demande explicitement:
  - 1 cadre résumé 2 lignes,
  - puis les autres activités.

### Contexte existant à réutiliser

- `ShortcutsSection` existe déjà et contient le hub d'activités.
- `useDailyPrediction` expose déjà la donnée dont on a besoin pour le résumé.
- `TodayHeader` est déjà utilisé comme en-tête premium de la zone dashboard.
- `DashboardPage` legacy n'est plus branchée, mais son nom et son emplacement conviennent au nouveau besoin.

### Contexte existant à ne pas détourner sans raison

- `HeroHoroscopeCard` est visuellement proche du besoin mais n'est pas un fit direct:
  - il impose `signName`,
  - ses CTA sont hardcodés en français,
  - il est pensé comme hero premium, pas comme simple résumé 2 lignes.
- Sauf refactor explicite et propre, il est préférable de créer un composant plus sobre ou de le généraliser proprement au lieu de le forcer.

### Technical Requirements

- Aucun changement backend.
- Réutiliser la query React existante pour profiter du cache et éviter les doubles appels inutiles.
- Le résumé doit être une contrainte de présentation, pas une troncature métier irréversible.
- Ne pas dupliquer les cartes d'activité; réutiliser `ShortcutsSection`.
- La page doit rester utile si le daily n'est pas disponible.

### UX Requirements

- La hiérarchie visuelle doit être immédiate:
  - résumé horoscope en premier,
  - activités ensuite.
- Le résumé doit être perçu comme un point d'entrée vers plus de détail.
- Les activités doivent rester directement accessibles, y compris si le daily charge encore ou échoue.
- L'écran doit rester mobile-first:
  - pas de scroll inutile avant de voir au moins le résumé et le début du hub
  - pas d'empilement de sections détaillées entre les deux

### Architecture Compliance

- Respecter les responsabilités existantes:
  - données via `frontend/src/api`
  - orchestration légère dans la page
  - composants réutilisables dans `frontend/src/components`
- Pas de logique métier importante dans le composant visuel de résumé.
- Les textes nouveaux doivent éviter les hardcodes gratuits et suivre les patterns i18n déjà présents dans l'app dès que le composant est touché.

### File Structure Requirements

- Fichiers principaux pressentis:
  - `frontend/src/pages/DashboardPage.tsx`
  - `frontend/src/components/ShortcutsSection.tsx`
  - nouveau composant possible: `frontend/src/components/dashboard/DashboardHoroscopeSummaryCard.tsx`
  - styles associés si nécessaire
- Tests à réaligner:
  - `frontend/src/tests/DashboardPage.test.tsx`
  - éventuellement `frontend/src/tests/ShortcutCard.test.tsx`
  - `frontend/src/tests/router.test.tsx` si le contenu visible de `/dashboard` change dans les assertions

### Testing Requirements

- Tester les états `loading`, `error`, `empty`, `success`.
- Tester la navigation par clic et clavier sur la carte résumé.
- Vérifier que le hub d'activités reste visible sur tous les états.
- Vérifier que les sections du daily détaillé ne sont pas présentes sur la landing.
- Exécuter les suites frontend ciblées après implémentation.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic-45]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md]
- [Source: frontend/src/pages/DashboardPage.tsx]
- [Source: frontend/src/components/ShortcutsSection.tsx]
- [Source: frontend/src/components/ShortcutCard.tsx]
- [Source: frontend/src/api/useDailyPrediction.ts]
- [Source: frontend/src/types/dailyPrediction.ts]
- [Source: frontend/src/tests/DashboardPage.test.tsx]
- [Source: frontend/src/tests/ShortcutCard.test.tsx]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story créée via le workflow BMAD `bmad-bmm-create-story` en mode autonome.

### Completion Notes List

- Story prête au dev.
- Le résumé dashboard doit rester un consommateur léger du contrat daily existant.
- Le hub d'activités reste visible sur tous les états du résumé, conformément à la demande produit.

### File List

- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/components/ShortcutsSection.tsx`
- `frontend/src/components/ShortcutCard.tsx`
- `frontend/src/components/dashboard/`
- `frontend/src/api/useDailyPrediction.ts`
- `frontend/src/types/dailyPrediction.ts`
- `frontend/src/tests/DashboardPage.test.tsx`
- `frontend/src/tests/ShortcutCard.test.tsx`
