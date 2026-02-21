# Story 2.5: Coherence inter-sessions des resultats

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a support user,  
I want garantir qu a entrees identiques le resultat reste coherent entre sessions,  
so that la confiance utilisateur soit maintenue.

## Acceptance Criteria

1. Given un meme profil natal et une meme version de regles, when le theme est regenere, then la sortie reste coherente.
2. Tout ecart est tracable via versioning/audit.

## Tasks / Subtasks

- [x] Definir la verification de coherence inter-sessions (AC: 1, 2)
  - [x] Reutiliser `input_hash` + `reference_version` + `ruleset_version` comme invariants de coherence
  - [x] Introduire une comparaison explicite entre resultat courant et dernier resultat equivalent
  - [x] Definir un code d etat metier stable en cas d ecart (`natal_result_mismatch`)
- [x] Ajouter un service metier de controle de coherence (AC: 1, 2)
  - [x] Ajouter `verify_consistency_for_user(...)` dans `user_natal_chart_service` (ou service dedie)
  - [x] Rechercher les derniers `chart_results` comparables pour un meme utilisateur
  - [x] Lever une erreur metier explicite quand les resultats divergent a invariants identiques
- [x] Exposer endpoint API v1 pour support/ops (AC: 2)
  - [x] Ajouter `GET /v1/users/{user_id}/natal-chart/consistency` (RBAC `support`/`ops`)
  - [x] Retourner statut detaille (`consistent: true|false`, identifiants charts compares, versions, hash)
  - [x] Conserver enveloppes API standardisees (`data/meta`, `error`)
- [x] Garantir la tracabilite complete en cas d ecart (AC: 2)
  - [x] Retourner `chart_id` source/cible et metadonnees versionnees
  - [x] Inclure un motif de divergence lisible (hash mismatch, payload mismatch, version mismatch)
- [x] Tester et valider (AC: 1, 2)
  - [x] Tests unitaires sur service de coherence (cas coherent + mismatch)
  - [x] Tests integration API (acces RBAC, coherent/incoherent, utilisateur sans historique)
  - [x] Validation finale: `ruff check .` + `pytest -q`

## Dev Notes

- Story backend prioritaire.
- Le socle de traçabilité existe déjà:
  - `ChartResultService.compute_input_hash`
  - `chart_results` avec `chart_id`, `reference_version`, `ruleset_version`, `input_hash`, `result_payload`, `user_id`
- Ne pas recalculer de logique astrologique dans la couche API; orchestrer via services.

### Technical Requirements

- Conserver la déterminisme des résultats pour entrées identiques.
- Détecter et exposer explicitement tout écart.
- API versionnée `/v1`, sécurisée JWT + RBAC (`support`, `ops`).

### Architecture Compliance

- Respect strict `api -> services -> domain -> infra`.
- Aucun accès DB direct depuis router.
- Utiliser le modèle d erreur stable (`error.code`, `message`, `details`, `request_id`).

### Library / Framework Requirements

- FastAPI + Pydantic pour contrats API.
- SQLAlchemy pour lecture `chart_results`.
- Réutiliser `require_authenticated_user` et RBAC existant.

### File Structure Requirements

- Cibles recommandées:
  - `backend/app/services/user_natal_chart_service.py`
  - `backend/app/infra/db/repositories/chart_result_repository.py`
  - `backend/app/api/v1/routers/users.py` (ou router support dédié)
  - `backend/app/tests/unit/test_user_natal_chart_service.py`
  - `backend/app/tests/integration/test_user_natal_chart_api.py`

### Testing Requirements

- Unit:
  - résultats identiques => `consistent = true`
  - mismatch de payload/hash à versions identiques => `consistent = false`
  - absence de données comparables => erreur métier stable
- Integration:
  - endpoint consistency sans token => `401`
  - rôle `user` non autorisé => `403`
  - rôle `support`/`ops` autorisé => `200`
  - mismatch détecté => réponse traçable explicite
- Validation finale:
  - `ruff check .`
  - `pytest -q`

### Previous Story Intelligence

- Story 2.3: génération initiale et traçabilité des résultats.
- Story 2.4: restitution latest chart + lien `chart_results.user_id`.
- Le projet dispose déjà des primitives de hash/version nécessaires à cette story.

### Git Intelligence Summary

- Le pattern actuel est: router mince + orchestration service + repository ciblé.
- Cette story doit rester incrémentale sans casser les endpoints `me/natal-chart` existants.

### Project Context Reference

- Aucun `project-context.md` détecté; source d autorité = PRD + Architecture + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.5)
- Architecture: `_bmad-output/planning-artifacts/architecture.md`
- Stories précédentes:
  - `_bmad-output/implementation-artifacts/2-3-generation-du-theme-natal-initial.md`
  - `_bmad-output/implementation-artifacts/2-4-restitution-lisible-du-theme-natal.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Create-story workflow execution

### Completion Notes List

- Ajout de `verify_consistency_for_user` avec invariants `input_hash + reference_version + ruleset_version` et comparaison payload normalisee.
- Endpoint support/ops `GET /v1/users/{user_id}/natal-chart/consistency` complete avec reponse traceable en cas de mismatch.
- Couverture de tests et validation locale effectuees (`ruff check .`, `pytest -q`).
- Motifs de divergence explicites couverts et exposes: `payload_mismatch`, `version_mismatch`, `hash_mismatch`.
- Recherche du dernier resultat equivalent conservee (pas de regression sur les cas avec historique intermediaire non comparable).

### File List

- _bmad-output/implementation-artifacts/2-5-coherence-inter-sessions-des-resultats.md
- backend/app/infra/db/repositories/chart_result_repository.py
- backend/app/services/user_natal_chart_service.py
- backend/app/api/v1/routers/users.py
- backend/app/tests/unit/test_user_natal_chart_service.py
- backend/app/tests/integration/test_user_natal_chart_api.py
