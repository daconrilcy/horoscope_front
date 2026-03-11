# Story 42.15: Introduire un evidence pack expert v3

Status: completed

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

- [x] Task 1: Définir le schéma de l'evidence pack (AC: 1, 2, 3, 4)
  - [x] Ajouter `evidence_pack_version`
  - [x] Ajouter les types dédiés
  - [x] Définir le contenu minimal obligatoire

- [x] Task 2: Introduire un builder dédié (AC: 1, 3)
  - [x] Créer `daily_prediction_evidence_builder.py`
  - [x] Brancher la construction depuis les sorties v3

- [x] Task 3: Préparer l'usage downstream (AC: 2, 4)
  - [x] Prévoir l'alimentation de `public_projection`
  - [x] Préparer un futur usage LLM sans le rendre obligatoire ici

- [x] Task 4: Tests (AC: 5)
  - [x] Tester structure et contenu minimal
  - [x] Vérifier le caractère déterministe

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

Gemini CLI Agent

### Debug Log References

- Story complétée avec enrichissement du schéma V3EvidencePack (natal_structural, layer_diagnostics) et correction de l'injection de dépendances dans EngineOrchestrator.

### Completion Notes List

- Story complétée. L'evidence pack est désormais une source de vérité complète incluant les diagnostics de couches (T, A, E) et la structure natale.
- Dependency injection corrigée dans `EngineOrchestrator.with_context_loader`.
- Schéma enrichi dans `schemas.py`.
- Builder mis à jour pour mapper les nouvelles données.
- Tests unitaires validant l'intégralité du pack.

### File List

- `backend/app/prediction/daily_prediction_evidence_builder.py`
- `backend/app/prediction/schemas.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/tests/unit/test_evidence_pack_v3.py`
- `_bmad-output/implementation-artifacts/42-15-introduire-un-evidence-pack-expert-v3.md`
