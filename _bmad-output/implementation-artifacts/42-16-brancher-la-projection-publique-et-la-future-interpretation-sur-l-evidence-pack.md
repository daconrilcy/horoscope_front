# Story 42.16: Brancher la projection publique et la future interprétation sur l'evidence pack

Status: ready-for-dev

## Story

As a product platform team,
I want faire de l'evidence pack la source de vérité interprétable,
so that le JSON public et un futur prompt expert ne dérivent plus directement d'une agrégation fragile de signaux.

## Acceptance Criteria

1. `public_projection` dérive ses résumés structurants de l'evidence pack.
2. L'éditorialisation ne peut plus inventer du relief absent du moteur.
3. Le backend prépare un contrat propre pour une future couche LLM.
4. Les tests verrouillent la cohérence entre evidence pack et payload public.
5. Le routeur public reste découplé du détail du moteur v3.

## Tasks / Subtasks

- [ ] Task 1: Brancher la projection publique sur l'evidence pack (AC: 1, 4, 5)
  - [ ] Adapter `public_projection.py`
  - [ ] Conserver un contrat public lisible

- [ ] Task 2: Refaire la couche éditoriale autour de l'evidence pack (AC: 2, 3)
  - [ ] Adapter `editorial_builder.py`
  - [ ] Adapter `editorial_service.py`
  - [ ] Préparer le pont vers un futur prompt expert

- [ ] Task 3: Tests de cohérence (AC: 4)
  - [ ] Vérifier que le payload public ne sur-interprète pas
  - [ ] Vérifier l'alignement evidence pack / résumé public

## Dev Notes

- Le bon flux cible est:
  - moteur -> evidence pack -> projection publique
  - moteur -> evidence pack -> interprétation experte
- Cette story est le point de découplage final entre signal métier et wording produit.

### Project Structure Notes

- Fichiers principaux:
  - `backend/app/prediction/public_projection.py`
  - `backend/app/prediction/editorial_builder.py`
  - `backend/app/prediction/editorial_service.py`
  - `backend/app/prediction/daily_prediction_evidence_builder.py`

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/prediction/public_projection.py]
- [Source: backend/app/prediction/editorial_builder.py]
- [Source: backend/app/prediction/editorial_service.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- Story prête pour faire de l'evidence pack la base de la projection et de l'interprétation future.

### File List

- `_bmad-output/implementation-artifacts/42-16-brancher-la-projection-publique-et-la-future-interpretation-sur-l-evidence-pack.md`

