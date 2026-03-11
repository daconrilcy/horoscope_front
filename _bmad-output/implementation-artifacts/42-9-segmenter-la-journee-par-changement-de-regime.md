# Story 42.9: Segmenter la journée par changement de régime

Status: ready-for-dev

## Story

As a prediction engine designer,
I want découper la journée en régimes cohérents dérivés des courbes,
so that les blocs horaires soient les résumés d'un signal continu et non la simple conséquence d'un pivot ou d'une grille artificielle.

## Acceptance Criteria

1. La segmentation part des courbes lissées et non d'une grille fixe ou des seuls turning points.
2. Les blocs sont fusionnés ensuite pour produire 4 à 8 segments lisibles maximum.
3. Chaque bloc expose orientation, intensité et confiance.
4. La segmentation reste déterministe et testable.
5. Les blocs deviennent la base des fenêtres et pivots v3.

## Tasks / Subtasks

- [ ] Task 1: Définir la logique de segmentation de régime (AC: 1, 4)
  - [ ] Définir les critères de changement de régime
  - [ ] Définir les critères de fusion minimale

- [ ] Task 2: Introduire un segmenter dédié (AC: 2, 3)
  - [ ] Créer un module dédié si nécessaire
  - [ ] Produire des blocs riches et typés

- [ ] Task 3: Brancher la sortie sur la chaîne v3 (AC: 5)
  - [ ] Préparer l'alimentation des fenêtres et pivots
  - [ ] Garder la compatibilité du debug

- [ ] Task 4: Tests (AC: 4)
  - [ ] Tester journée calme
  - [ ] Tester journée avec deux régimes contrastés
  - [ ] Tester fusion pour éviter la fragmentation

## Dev Notes

- Le moteur actuel découpe encore trop à partir des pivots; cette story inverse la dépendance.
- Les blocs doivent devenir des résumés de courbe, pas des boîtes techniques.
- Une bonne cible produit est 4 à 8 blocs lisibles par jour.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/prediction/block_generator.py`
  - nouveau fichier recommandé: `backend/app/prediction/regime_segmenter.py`
  - `backend/app/prediction/engine_orchestrator.py`

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/prediction/block_generator.py]
- [Source: backend/app/prediction/decision_window_builder.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- Story prête pour faire des blocs v3 la représentation de régimes cohérents.

### File List

- `_bmad-output/implementation-artifacts/42-9-segmenter-la-journee-par-changement-de-regime.md`
