# Story 44.1: Étendre le contrat public des moments clés avec des indicateurs de mouvement

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend maintainer,
I want enrichir les turning points publics avec un bloc `movement` et des `category_deltas`,
so that le frontend puisse expliquer l'amplitude et la direction d'une bascule sans recalcul fragile côté client.

## Acceptance Criteria

1. Le contrat public des moments clés expose de manière additive un bloc `movement` incluant au minimum `strength`, `previous_composite`, `next_composite`, `delta_composite` et `direction`.
2. Le contrat public expose une liste `category_deltas` structurée, avec au minimum `code`, `direction`, `delta_score`, `delta_intensity` et `delta_rank` si disponible.
3. Les nouveaux champs restent optionnels et backward compatibles pour les consommateurs qui ne les utilisent pas encore.
4. Le schéma distingue explicitement un changement global (`movement.direction`) d'une variation locale par catégorie.
5. Les types backend et frontend partagés restent cohérents et documentés.

## Tasks / Subtasks

- [x] Task 1: Étendre les schémas backend des turning points publics (AC: 1, 2, 3, 4)
  - [x] Ajouter les nouveaux champs optionnels aux schémas Pydantic des moments clés publics
  - [x] Introduire des sous-objets dédiés pour `movement` et `category_deltas` plutôt que des champs plats dispersés
  - [x] Préserver les champs existants pour éviter toute rupture de contrat

- [x] Task 2: Aligner les types frontend et DTO consommés (AC: 3, 5)
  - [x] Étendre les types TypeScript des turning points publics
  - [x] Documenter le caractère optionnel des nouveaux champs
  - [x] Vérifier la cohérence de nommage backend/frontend

- [x] Task 3: Documenter le contrat et ses garde-fous (AC: 2, 4, 5)
  - [x] Décrire clairement le sens métier de `direction`, `strength` et `delta`
  - [x] Documenter la différence entre mouvement global et variations de catégories
  - [x] Référencer les stories suivantes qui calculeront puis afficheront ces données

## Dev Notes

- Cette story ne calcule pas encore les valeurs métier; elle prépare le contrat additif.
- Le contrat doit rester compatible avec les payloads actuels de `/v1/predictions/daily`.
- Les noms doivent rester alignés avec Epic 43 pour éviter une seconde taxonomie de bascules.
- `movement`: Amplitude et direction globale de la bascule.
- `category_deltas`: Détail des variations par axe thématique.

### Project Structure Notes

- Backend principal:
  - `backend/app/prediction/schemas.py`
  - `backend/app/prediction/public_projection.py`
- Frontend principal:
  - `frontend/src/types/dailyPrediction.ts`

### Technical Requirements

- `movement` et `category_deltas` sont optionnels dans les schémas publics.
- Les champs numériques sont typés explicitement.
- Le contrat autorise une liste `category_deltas`, mais le tri, les seuils et la limitation d'affichage sont traités en 44.2.

### Architecture Compliance

- Le backend expose des données structurées et non des phrases finalisées.
- La localisation et la formulation restent côté frontend.

### Testing Requirements

- Ajouter des tests de contrat sur la sérialisation backend.
- Ajouter des tests de types/fallback frontend si le projet en dispose déjà.

### Previous Story Intelligence

- Epic 43 a déjà introduit `change_type`, `primary_driver`, `previous_categories`, `next_categories` et `impacted_categories`.
- Les régressions récentes ont montré qu'un contrat partiel pousse le frontend à reconstruire des transitions incohérentes.

### Git Intelligence Summary

- Les derniers correctifs sur les moments clés ont surtout porté sur le fallback frontend et la cohérence des transitions.
- Cette story doit éviter d'ajouter un second niveau de logique implicite côté UI.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic-43-Moments-clés-du-jour-explicables-et-localisés]
- [Source: backend/app/prediction/schemas.py]
- [Source: backend/app/prediction/public_projection.py]
- [Source: frontend/src/types/dailyPrediction.ts]
- [Source: user request 2026-03-12 — “enrichir ces moments clefs avec des valeurs qui justifie le mouvement ?”]

## Dev Agent Record

### Agent Model Used

GPT-4o

### Debug Log References

- Added `V3Movement` and `V3CategoryDelta` to `schemas.py`.
- Updated `V3TurningPoint` and `V3EvidenceTurningPoint` in `schemas.py`.
- Updated `PublicTurningPointPolicy` and `_deserialize_evidence_pack` in `public_projection.py`.
- Updated `DailyPredictionTurningPoint` and added related interfaces in `dailyPrediction.ts`.

### Completion Notes List

- Contract extended with `movement` and `category_deltas`.
- Backward compatibility preserved.
- Unit tests added for backend serialization.

### File List

- `backend/app/prediction/schemas.py`
- `backend/app/prediction/public_projection.py`
- `frontend/src/types/dailyPrediction.ts`
- `backend/app/tests/unit/prediction/test_public_projection_evidence.py`
