# Story 43.2: Introduire un wording i18n pour les moments clés

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a frontend architect,
I want composer le wording des moments clés via i18n à partir de données structurées,
so that le français, l’anglais et les futures langues restent cohérents sans figer des phrases métier dans le backend.

## Acceptance Criteria

1. Le backend ne fournit plus le wording final comme source primaire pour les moments clés enrichis.
2. Le frontend introduit des clés i18n dédiées pour les causes astrologiques, les transitions `avant/après`, les libellés d’impact et les implications.
3. Le wording distingue au minimum les cas `emergence`, `recomposition` et `attenuation`.
4. Les règles de formulation couvrent l’absence d’un driver principal, un driver unique et plusieurs drivers secondaires.
5. Les helpers i18n restent centralisés, testables et sans duplication FR/EN hors du dictionnaire de traduction.
6. Les tests frontend couvrent le rendu FR et EN à partir des mêmes données structurées.

## Tasks / Subtasks

- [ ] Task 1: Définir les clés i18n dédiées aux moments clés enrichis (AC: 2, 3)
  - [ ] Ajouter les clés de labels de sections `why`, `before_after`, `implication`
  - [ ] Ajouter les clés de causes astrologiques par type de driver
  - [ ] Ajouter les variantes de wording pour `emergence`, `recomposition`, `attenuation`

- [ ] Task 2: Centraliser la composition textuelle (AC: 1, 4, 5)
  - [ ] Étendre `predictionI18n.ts` avec des helpers purs pour les moments clés enrichis
  - [ ] Utiliser des fonctions de composition paramétrées par `change_type` et `primary_driver`
  - [ ] Prévoir des fallbacks propres quand certaines données manquent

- [ ] Task 3: Garantir la cohérence multilingue (AC: 2, 4, 6)
  - [ ] Vérifier que FR et EN couvrent les mêmes cas métier
  - [ ] Interdire les chaînes backend brutes dans le rendu final
  - [ ] Ajouter des tests ciblés sur les compositions linguistiques

## Dev Notes

- Cette story porte sur la couche linguistique, pas sur la détection métier.
- Le backend doit fournir un contrat structuré; la phrase finale appartient au frontend.
- Le wording doit rester bref, naturel, et compréhensible sans jargon astro excessif.
- Les helpers doivent éviter la duplication des variantes linguistiques dans les composants React.

### Project Structure Notes

- Frontend principal:
  - `frontend/src/utils/predictionI18n.ts`
  - `frontend/src/i18n/predictions.ts`
  - `frontend/src/types/dailyPrediction.ts`
  - `frontend/src/tests/TodayPage.test.tsx`

### Technical Requirements

- Les nouvelles clés i18n doivent être stables et regroupées logiquement.
- Les fonctions de composition doivent prendre des données structurées, jamais parser une phrase backend.
- Les fallbacks doivent préserver une phrase lisible si `primary_driver` ou `previous_categories` sont absents.

### Architecture Compliance

- La localisation reste côté frontend.
- Les composants UI consomment des helpers déjà composés plutôt que d’assembler des phrases inline.
- Ne pas multiplier les dictionnaires parallèles hors `predictions.ts`.

### Library / Framework Requirements

- React + TypeScript existants uniquement.
- Aucun ajout de dépendance i18n supplémentaire.

### File Structure Requirements

- Ajouter les nouvelles clés dans `frontend/src/i18n/predictions.ts`.
- Ajouter la logique de composition dans `frontend/src/utils/predictionI18n.ts`.
- Ne pas disperser de texte dur dans `TurningPointsList.tsx`.

### Testing Requirements

- Ajouter au minimum:
  - un test FR `emergence`
  - un test EN `recomposition`
  - un test fallback sans driver
  - un test garantissant qu’aucune chaîne backend brute n’est reprise telle quelle

### Previous Story Intelligence

- 41.6 a déjà centralisé une partie du wording daily via `predictionI18n.ts`; cette story doit prolonger ce pattern au lieu de créer un nouveau système. [Source: _bmad-output/implementation-artifacts/41-6-refactor-dashboard-moments-cles-et-agenda-du-jour.md]

### Git Intelligence Summary

- Le rendu actuel des moments clés vit encore dans `TurningPointsList.tsx` avec des chaînes inline. Cette story doit déplacer cette responsabilité dans la couche i18n pour éviter la duplication et préparer d’autres langues.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.

### References

- [Source: user request 2026-03-12 — “le wording doit etre gerer avec i18n”]
- [Source: frontend/src/utils/predictionI18n.ts]
- [Source: frontend/src/i18n/predictions.ts]
- [Source: frontend/src/components/prediction/TurningPointsList.tsx]
- [Source: frontend/src/types/dailyPrediction.ts]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de la demande utilisateur du 2026-03-12.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

- `_bmad-output/implementation-artifacts/43-2-introduire-un-wording-i18n-pour-les-moments-cles.md`
