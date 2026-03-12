# Story 43.3: Refaire le rendu UI des moments clés

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur consultant le daily,
I want lire chaque moment clé comme une transition expliquée,
so that je comprenne la cause astrologique, le passage d’un état à un autre, et ce que cela implique pour la journée.

## Acceptance Criteria

1. Chaque carte `Moment clé` affiche trois sections lisibles: `Pourquoi ça bascule`, `Ce qui change`, `Implication`.
2. Le rendu explicite le passage `avant -> après` à partir des catégories dominantes, sans jargon technique brut.
3. Le driver astrologique principal est humanisé et affiché comme cause principale, avec un fallback sobre si aucun driver fort n’est disponible.
4. Les impacts restent visibles sous forme de catégories/pictogrammes et restent cohérents avec l’agenda du jour.
5. Le design mobile et desktop reste compact et ne réintroduit pas de bruit visuel excessif.
6. Le rendu reste compatible avec les payloads legacy qui ne possèdent pas encore l’enrichissement complet.

## Tasks / Subtasks

- [ ] Task 1: Repenser la hiérarchie visuelle de la carte (AC: 1, 5)
  - [ ] Ajouter trois sections explicites dans `TurningPointsList.tsx`
  - [ ] Conserver la fenêtre horaire et le badge de bascule
  - [ ] Garder une densité visuelle compatible mobile

- [ ] Task 2: Rendre le diff avant/après lisible (AC: 2, 4, 6)
  - [ ] Afficher `Avant` et `Après` à partir des catégories structurées
  - [ ] Gérer les cas d’apparition pure, disparition pure et recomposition
  - [ ] Prévoir un fallback legacy si seules les catégories impactées existent

- [ ] Task 3: Relier cause astrologique et implication produit (AC: 1, 3, 4)
  - [ ] Afficher la cause principale en tête de carte
  - [ ] Afficher une phrase d’implication courte sous la transition
  - [ ] Réutiliser les pictogrammes et labels de catégories déjà présents

- [ ] Task 4: Couvrir les rendus critiques (AC: 5, 6)
  - [ ] Mettre à jour les tests `TodayPage`
  - [ ] Ajouter des cas pour `emergence`, `recomposition`, `attenuation`
  - [ ] Vérifier le fallback legacy et l’absence de faux moment de minuit

## Dev Notes

- Cette story est purement orientée présentation et compréhension.
- Le composant ne doit pas recalculer la logique métier; il consomme la structure enrichie.
- Le rendu doit rester court: une carte dense mais lisible vaut mieux qu’un pavé.
- L’implication doit rester une phrase produit, pas un dump de drivers.

### Project Structure Notes

- Frontend principal:
  - `frontend/src/components/prediction/TurningPointsList.tsx`
  - `frontend/src/pages/TodayPage.tsx`
  - `frontend/src/tests/TodayPage.test.tsx`
  - `frontend/src/utils/predictionI18n.ts`
  - `frontend/src/types/dailyPrediction.ts`

### Technical Requirements

- Le composant doit accepter le contrat enrichi tout en restant compatible avec le payload actuel.
- Les sections `Pourquoi`, `Ce qui change`, `Implication` doivent être pilotées par i18n.
- Les catégories avant/après doivent réutiliser le mapping `getCategoryMeta`.

### Architecture Compliance

- Pas de logique astrologique lourde dans le composant React.
- Les helpers de composition restent hors JSX.
- L’UI doit rester alignée avec l’agenda du jour et les autres éléments du dashboard.

### Library / Framework Requirements

- React + TypeScript + styles inline/patterns existants uniquement.
- Pas de nouvelle librairie de layout ou de cartes.

### File Structure Requirements

- Concentrer le rendu dans `TurningPointsList.tsx`.
- Garder les helpers de texte dans `predictionI18n.ts`.
- Ajuster les types dans `dailyPrediction.ts` si le contrat public s’étend.

### Testing Requirements

- Ajouter au minimum:
  - un test d’affichage des trois sections
  - un test d’affichage du `Avant / Après`
  - un test fallback legacy
  - un test de cohérence avec les catégories impactées

### Previous Story Intelligence

- 41.6 a déjà imposé que `Moments clés du jour` représente des bascules ponctuelles et non des fenêtres longues. Cette story doit enrichir la lecture sans réintroduire de redondance ou de bruit. [Source: _bmad-output/implementation-artifacts/41-6-refactor-dashboard-moments-cles-et-agenda-du-jour.md]

### Git Intelligence Summary

- Le composant `TurningPointsList.tsx` est aujourd’hui simple et linéaire; il constitue le bon point d’extension sans refactor massif du dashboard.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.

### References

- [Source: user request 2026-03-12 — “on avait ça => ça devient ça”]
- [Source: frontend/src/components/prediction/TurningPointsList.tsx]
- [Source: frontend/src/pages/TodayPage.tsx]
- [Source: frontend/src/utils/predictionI18n.ts]
- [Source: frontend/src/tests/TodayPage.test.tsx]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de la demande utilisateur du 2026-03-12.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

- `_bmad-output/implementation-artifacts/43-3-refaire-le-rendu-ui-des-moments-cles.md`
