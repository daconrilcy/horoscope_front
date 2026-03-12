# Story 43.1: Structurer une sémantique explicable des bascules

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a backend maintainer,
I want enrichir les turning points publics avec une sémantique structurée de changement,
so that le frontend puisse afficher pourquoi une bascule existe sans reconstruire la logique métier à partir de phrases fragiles.

## Acceptance Criteria

1. Le backend expose de manière additive, pour chaque moment clé public, un `change_type` explicite au minimum parmi `emergence`, `recomposition`, `attenuation`.
2. Le backend expose un diff structuré entre `previous_categories`, `next_categories` et `impacted_categories`, sans imposer de phrase localisée.
3. Le backend expose un `primary_driver` structuré dérivé des drivers existants, avec type d’événement, corps, aspect, cible et métadonnées utiles filtrées.
4. Les frontières synthétiques de début/fin de journée ne sont jamais publiées comme bascules explicables.
5. Le contrat reste backward compatible avec le payload actuel de `/v1/predictions/daily`.
6. Les tests backend couvrent au minimum un cas `emergence`, un cas `recomposition`, un cas `attenuation` et l’absence de faux pivot de minuit.

## Tasks / Subtasks

- [x] Task 1: Définir le contrat additif des moments clés enrichis (AC: 1, 2, 5)
  - [x] Introduire un schéma typed pour la sémantique de bascule publique
  - [x] Ajouter `change_type`, `previous_categories`, `next_categories`, `impacted_categories`
  - [x] Prévoir des champs optionnels pour préserver la compatibilité du DTO existant

- [x] Task 2: Déterminer et exposer le `primary_driver` (AC: 3, 5)
  - [x] Définir une règle de sélection stable du driver principal
  - [x] Filtrer les métadonnées techniques non utiles au produit
  - [x] Prévoir un fallback propre en absence de driver dominant

- [x] Task 3: Produire la sémantique de changement dans la projection publique (AC: 1, 2, 4)
  - [x] Distinguer `emergence`, `recomposition`, `attenuation`
  - [x] Exclure explicitement `00:00` et `24:00` des bascules explicables
  - [x] Garder les vraies transitions tardives comme `22:45` ou `23:15`

- [x] Task 4: Verrouiller la non-régression backend (AC: 4, 5, 6)
  - [x] Mettre à jour les tests de projection publique
  - [x] Ajouter des tests d’intégration daily prediction pour le contrat additif
  - [x] Vérifier que les consommateurs existants continuent à fonctionner sans le nouveau rendu

## Dev Notes

- Cette story ne doit pas produire les phrases finales de l’UI.
- Le backend doit livrer une structure sémantique stable, pas un wording FR/EN.
- Le plus petit delta cohérent est dans `public_projection`, pas dans le moteur v3 profond.
- La logique de sélection du driver principal doit rester simple et explicable:
  - prioriser un exact event public
  - sinon un ingress significatif
  - sinon un driver de fallback neutre

### Project Structure Notes

- Backend principal:
  - `backend/app/prediction/public_projection.py`
  - `backend/app/prediction/schemas.py`
  - `backend/app/api/v1/routers/predictions.py`
  - `backend/app/tests/unit/prediction/test_public_projection_evidence.py`
  - `backend/app/tests/integration/test_daily_prediction_api.py`

### Technical Requirements

- Le nouveau contrat doit être additif et optionnel.
- Les catégories exposées doivent rester des codes canoniques déjà compris par le frontend.
- `primary_driver` doit être sérialisable, stable et découplé de métadonnées brutes inutiles.
- Aucun wording final ne doit être stocké dans ce nouveau contrat.

### Architecture Compliance

- La vérité métier reste côté backend.
- La composition linguistique finale reste côté frontend/i18n.
- Ne pas introduire de seconde logique parallèle de détection de bascule en dehors de la projection publique existante.

### Library / Framework Requirements

- Python 3.13, FastAPI, Pydantic et la stack existante uniquement.
- Aucun ajout de dépendance requis.

### File Structure Requirements

- Étendre les schémas existants dans `backend/app/prediction/schemas.py` avant toute logique ad hoc dans le routeur.
- Centraliser la fabrication du moment clé enrichi dans `public_projection.py`.

### Testing Requirements

- Ajouter au minimum:
  - un test `emergence`
  - un test `recomposition`
  - un test `attenuation`
  - un test de non-publication du faux pivot `00:00`
  - un test de compatibilité du payload legacy

### Previous Story Intelligence

- 41.6 a déjà déplacé les `Moments clés du jour` vers une logique de bascule courte et lisible; cette story doit enrichir la structure, pas revenir aux longues fenêtres ambiguës. [Source: _bmad-output/implementation-artifacts/41-6-refactor-dashboard-moments-cles-et-agenda-du-jour.md]
- 42.16 a fait de l’evidence pack la source de vérité publique; l’enrichissement des bascules doit donc rester aligné avec la projection publique existante. [Source: _bmad-output/implementation-artifacts/42-16-brancher-la-projection-publique-et-la-future-interpretation-sur-l-evidence-pack.md]

### Git Intelligence Summary

- `7d1548b fix(daily): stabilize v3 projection and dashboard moments` a déjà supprimé les faux pivots de minuit côté frontend; le backend doit maintenant exposer une sémantique de changement cohérente avec cette stabilisation.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.
- Les règles actives viennent de `AGENTS.md`, des artefacts Epic 41/42 et du contrat daily prediction existant.

### References

- [Source: user request 2026-03-12 — “expliquer pourquoi ce sont des bascules”]
- [Source: backend/app/prediction/public_projection.py]
- [Source: backend/app/prediction/schemas.py]
- [Source: backend/app/api/v1/routers/predictions.py]
- [Source: _bmad-output/implementation-artifacts/41-6-refactor-dashboard-moments-cles-et-agenda-du-jour.md]
- [Source: _bmad-output/implementation-artifacts/42-16-brancher-la-projection-publique-et-la-future-interpretation-sur-l-evidence-pack.md]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story générée en mode BMAD YOLO à partir de la demande utilisateur du 2026-03-12.

### Completion Notes List

- Implemented enriched semantic fields for turning points: change_type, previous_categories, next_categories, primary_driver.
- Updated TurningPointDetector to compute these fields and exclude midnight pivots.
- Updated DailyPredictionEvidenceBuilder to propagate fields to Evidence Pack.
- Updated PublicPredictionAssembler to expose fields in public API.
- Added comprehensive unit tests for all semantic cases and priority rules.

### File List

- `backend/app/prediction/schemas.py`
- `backend/app/prediction/turning_point_detector.py`
- `backend/app/prediction/daily_prediction_evidence_builder.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/tests/unit/prediction/test_turning_point_semantics.py`
- `backend/app/tests/unit/prediction/test_public_projection_evidence.py`
