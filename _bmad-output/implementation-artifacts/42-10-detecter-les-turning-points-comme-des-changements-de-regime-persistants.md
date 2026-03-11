# Story 42.10: Détecter les turning points comme des changements de régime persistants

Status: ready-for-dev

## Story

As a QA engineer,
I want que les turning points représentent des bascules durables et non de simples événements,
so that le produit ne montre plus de faux pivots sur des journées faibles ou ambiguës.

## Acceptance Criteria

1. Un turning point requiert:
   - une amplitude minimale avant/après
   - une durée minimale du régime suivant
   - une confiance minimale
2. Les pivots sont déclenchés par changement de régime sur les courbes, pas par simple exactitude.
3. Le nombre de pivots publics baisse sur les journées faibles.
4. Le backend conserve des drivers explicatifs utiles pour le debug et l'evidence pack.
5. Les tests couvrent faux positif, vrai pivot et cas ambivalent.

## Tasks / Subtasks

- [ ] Task 1: Définir le contrat métier du pivot v3 (AC: 1, 2)
  - [ ] Définir fenêtres avant/après
  - [ ] Définir amplitude minimale
  - [ ] Définir durée minimale du régime suivant

- [ ] Task 2: Réimplémenter la détection de pivot (AC: 2, 4)
  - [ ] Refaire `turning_point_detector.py`
  - [ ] Conserver les drivers utiles
  - [ ] Éviter la dépendance directe à un `exact event`

- [ ] Task 3: Brancher la sortie sur les blocs et fenêtres v3 (AC: 3)
  - [ ] Utiliser les régimes segmentés comme entrée
  - [ ] Préparer une sortie publique plus sobre

- [ ] Task 4: Tests (AC: 5)
  - [ ] Tester journée faible sans faux pivot
  - [ ] Tester vrai basculement durable
  - [ ] Tester cas ambigu sans pivot public

## Dev Notes

- Cette story est centrale pour corriger le faux relief.
- Le pivot produit doit devenir rare, crédible et narrativement utile.
- Ne plus penser “event first”, mais “regime change first”.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/prediction/turning_point_detector.py`
  - `backend/app/prediction/block_generator.py`
  - `backend/app/prediction/engine_orchestrator.py`

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/prediction/turning_point_detector.py]
- [Source: backend/app/prediction/block_generator.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- Story prête pour refondre la logique de turning point autour des changements de régime.

### File List

- `_bmad-output/implementation-artifacts/42-10-detecter-les-turning-points-comme-des-changements-de-regime-persistants.md`

