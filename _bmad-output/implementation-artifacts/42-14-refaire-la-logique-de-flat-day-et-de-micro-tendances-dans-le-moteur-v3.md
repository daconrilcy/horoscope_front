# Story 42.14: Refaire la logique de flat day et de micro-tendances dans le moteur v3

Status: ready-for-dev

## Story

As a product owner,
I want distinguer une journée plate, une journée faible et une journée intense mais neutre,
so that les micro-tendances et les signaux publics restent honnêtes et réellement utiles.

## Acceptance Criteria

1. `flat_day` dépend des métriques v3 et non d'un simple manque de pivots.
2. Les micro-tendances ne sont exposées que si le relatif apporte une vraie nuance.
3. Une journée intense mais neutre n'est plus traitée comme plate.
4. Les journées réellement plates restent sobres côté fenêtres, pivots et wording.
5. Les tests couvrent les trois familles:
   - plat
   - faible mais non plat
   - intense mais neutre

## Tasks / Subtasks

- [ ] Task 1: Définir la nouvelle logique de flat day (AC: 1, 3)
  - [ ] Définir les seuils à partir des métriques v3
  - [ ] Éviter un simple proxy “pas de windows”

- [ ] Task 2: Revoir l'exposition des micro-tendances (AC: 2, 4)
  - [ ] Adapter `public_projection.py`
  - [ ] Garder une hiérarchie claire entre absolu et relatif

- [ ] Task 3: Tester les cas produits clés (AC: 5)
  - [ ] Cas plat
  - [ ] Cas faible mais non plat
  - [ ] Cas neutre intense

## Dev Notes

- Cette story traite directement une faiblesse du système actuel: la confusion entre neutralité, platitude et faible intensité.
- Le mot d'ordre reste `honesty first`.
- Le relatif ne doit exister que pour aider à lire la journée, pas pour requalifier artificiellement le fond de signal.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/prediction/public_projection.py`
  - `backend/app/services/relative_scoring_service.py`
  - `backend/app/tests/integration/test_daily_prediction_qa.py`

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/prediction/public_projection.py]
- [Source: backend/app/tests/integration/test_daily_prediction_qa.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- Story prête pour refaire la notion de journée plate dans le cadre du moteur v3.

### File List

- `_bmad-output/implementation-artifacts/42-14-refaire-la-logique-de-flat-day-et-de-micro-tendances-dans-le-moteur-v3.md`

