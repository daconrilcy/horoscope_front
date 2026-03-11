# Story 42.11: Refaire les fenêtres décisionnelles à partir des blocs v3

Status: ready-for-dev

## Story

As a utilisateur consultant le daily,
I want voir des créneaux vraiment utiles parce qu'ils résument des régimes cohérents,
so that les fenêtres proposées aient une personnalité propre et une valeur décisionnelle crédible.

## Acceptance Criteria

1. Les `decision_windows` sont dérivées des blocs de régime v3.
2. Chaque fenêtre expose au minimum:
   - orientation
   - intensité
   - confiance
   - thèmes dominants
3. `best_window` n'émerge que si une fenêtre est réellement exploitable.
4. Les journées faibles ne génèrent plus de fenêtres artificiellement riches.
5. Les tests couvrent la cohérence entre blocs, fenêtres et projection publique.

## Tasks / Subtasks

- [ ] Task 1: Reconcevoir la logique de fenêtre métier (AC: 1, 2)
  - [ ] Définir la dérivation depuis les blocs v3
  - [ ] Définir les types de fenêtres utiles

- [ ] Task 2: Refaire le builder de fenêtres (AC: 2, 3)
  - [ ] Adapter `decision_window_builder.py`
  - [ ] Ajouter score et confiance v3 si nécessaire

- [ ] Task 3: Brancher les fenêtres dans la projection publique (AC: 3, 4)
  - [ ] Revoir `best_window`
  - [ ] Garder une projection sobre sur journée faible

- [ ] Task 4: Tests (AC: 5)
  - [ ] Tester cohérence blocs -> fenêtres
  - [ ] Tester absence de `best_window` artificiel

## Dev Notes

- Les fenêtres ne doivent plus être un artefact dérivé des seuls pivots.
- L'utilisateur doit percevoir un créneau comme un régime exploitable, pas comme un instant magique.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/prediction/decision_window_builder.py`
  - `backend/app/prediction/public_projection.py`
  - `backend/app/prediction/block_generator.py`

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/prediction/decision_window_builder.py]
- [Source: backend/app/prediction/public_projection.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- Story prête pour refaire les fenêtres décisionnelles sur les blocs de régime v3.

### File List

- `_bmad-output/implementation-artifacts/42-11-refaire-les-fenetres-decisionnelles-a-partir-des-blocs-v3.md`

