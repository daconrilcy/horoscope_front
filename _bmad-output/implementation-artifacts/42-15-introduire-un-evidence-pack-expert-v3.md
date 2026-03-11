# Story 42.15: Introduire un evidence pack expert v3

Status: ready-for-dev

## Story

As a backend architect,
I want produire un evidence pack expert indépendant du JSON public,
so that l'interprétation future et la projection publique consomment une structure cohérente, auditable et riche.

## Acceptance Criteria

1. Le backend produit un `evidence_pack` avec:
   - `day_profile`
   - `themes`
   - `time_windows`
   - `turning_points`
   - `drivers`
2. L'evidence pack distingue ce qui est structurel, ponctuel, favorable, tendu et fiable.
3. `evidence_pack_version` est explicite dans le contrat v3.
4. Le format est déterministe, typé et testable.
5. L'evidence pack n'impose pas encore l'usage d'un LLM.
6. Les tests couvrent au moins un cas complet nominal.

## Tasks / Subtasks

- [ ] Task 1: Définir le schéma de l'evidence pack (AC: 1, 2, 3, 4)
  - [ ] Ajouter `evidence_pack_version`
  - [ ] Ajouter les types dédiés
  - [ ] Définir le contenu minimal obligatoire

- [ ] Task 2: Introduire un builder dédié (AC: 1, 3)
  - [ ] Créer `daily_prediction_evidence_builder.py`
  - [ ] Brancher la construction depuis les sorties v3

- [ ] Task 3: Préparer l'usage downstream (AC: 2, 4)
  - [ ] Prévoir l'alimentation de `public_projection`
  - [ ] Préparer un futur usage LLM sans le rendre obligatoire ici

- [ ] Task 4: Tests (AC: 5)
  - [ ] Tester structure et contenu minimal
  - [ ] Vérifier le caractère déterministe

## Dev Notes

- L'evidence pack est une vraie frontière d'architecture.
- Il doit devenir la source de vérité interprétable, plus stable que le JSON public lui-même.
- Cette story prépare explicitement la suite 42.16.
- La version du contrat doit être explicite dès cette story pour sécuriser la transition et les futures évolutions prompt/public.

### Project Structure Notes

- Fichiers principaux:
  - nouveau fichier recommandé: `backend/app/prediction/daily_prediction_evidence_builder.py`
  - `backend/app/prediction/schemas.py`
  - `backend/app/prediction/engine_orchestrator.py`

### References

- [Source: _bmad-output/planning-artifacts/epic-42-daily-signal-driven-v3.md]
- [Source: backend/app/prediction/public_projection.py]
- [Source: backend/app/prediction/editorial_builder.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de l'Epic 42.

### Completion Notes List

- Story prête pour introduire la future source de vérité interprétable du moteur daily v3.

### File List

- `_bmad-output/implementation-artifacts/42-15-introduire-un-evidence-pack-expert-v3.md`
