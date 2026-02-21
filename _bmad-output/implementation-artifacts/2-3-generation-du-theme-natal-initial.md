# Story 2.3: Generation du theme natal initial

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,  
I want lancer la generation de mon theme natal depuis mon profil,  
so that j obtiens ma premiere valeur rapidement.

## Acceptance Criteria

1. Given des donnees natales completes et valides, when l utilisateur declenche la generation, then le moteur retourne un resultat structure.
2. La reponse inclut les metadonnees de version du moteur/referentiel.
3. Si le moteur est indisponible ou depasse le delai cible, le systeme retourne une erreur explicite avec option de relance sans perte de contexte.

## Tasks / Subtasks

- [x] Ajouter un service applicatif de generation depuis profil utilisateur (AC: 1, 2, 3)
  - [x] Recuperer le profil natal courant de l utilisateur authentifie
  - [x] Construire un `BirthInput` a partir du profil et appeler `NatalCalculationService.calculate`
  - [x] Persister la trace via `ChartResultService.persist_trace`
  - [x] Retourner `chart_id` + resultat structure + metadonnees (`reference_version`, `ruleset_version`)
- [x] Exposer endpoint API v1 securise de generation initiale (AC: 1, 2, 3)
  - [x] Ajouter `POST /v1/users/me/natal-chart`
  - [x] Exiger JWT access token valide via dependance auth existante
  - [x] Standardiser enveloppes succes/erreur (`data/meta`, `error`)
- [x] Implementer la gestion explicite des erreurs et delais (AC: 3)
  - [x] Mapper absence de profil natal vers erreur metier stable (`birth_profile_not_found`)
  - [x] Mapper indisponibilite/timeout moteur vers erreur retryable (`natal_engine_unavailable` ou `natal_generation_timeout`)
  - [x] Retourner des details actionnables pour relance sans resaisie des donnees
- [x] Garantir la coherence de versions et tracabilite (AC: 2)
  - [x] Verifier que les versions issues du resultat sont exposees dans la reponse API
  - [x] Reutiliser le pattern de hash input + trace deja present dans `chart_results`
- [x] Tester et valider (AC: 1, 2, 3)
  - [x] Tests unitaires service (profil manquant, succes, mapping erreurs)
  - [x] Tests integration API (`401`, `404`, `422/503`, succes avec metadata versions)
  - [x] Validation finale: `ruff check .` + `pytest -q`

## Dev Notes

- Story backend prioritaire.
- S appuyer sur les composants deja disponibles:
  - `UserBirthProfileService` (Story 2.2)
  - `NatalCalculationService` (Story 1.4)
  - `ChartResultService` (Story 1.5)
- Eviter toute duplication de logique de calcul: l orchestration doit rester en couche `services`.

### Technical Requirements

- Endpoint versionne `/v1` et securise JWT.
- Latence cible percue: gestion explicite des erreurs de timeout/indisponibilite.
- Reponse de succes doit inclure:
  - identifiant de trace (`chart_id`)
  - resultat natal structure
  - metadata de version (`reference_version`, `ruleset_version`)

### Architecture Compliance

- Respect strict `api -> services -> domain -> infra`.
- Aucun acces DB direct dans le router.
- Conserver le format d erreur unifie:
  - `error.code`
  - `error.message`
  - `error.details`
  - `error.request_id`

### Library / Framework Requirements

- FastAPI + Pydantic pour contrats API.
- SQLAlchemy Session injectee via `get_db_session`.
- Reutiliser la dependance auth existante `require_authenticated_user`.

### File Structure Requirements

- Cibles recommandees:
  - `backend/app/services/user_natal_chart_service.py`
  - `backend/app/api/v1/routers/users.py` (nouvelle route `POST /me/natal-chart`)
  - `backend/app/tests/unit/test_user_natal_chart_service.py`
  - `backend/app/tests/integration/test_user_natal_chart_api.py`

### Testing Requirements

- Unit:
  - profil natal inexistant => erreur metier stable
  - generation nominale => resultat + versions exposes
  - indisponibilite/timeout moteur => erreur retryable
- Integration:
  - `POST /v1/users/me/natal-chart` sans token => `401`
  - token valide + profil valide => `200`
  - token valide + profil absent => `404`
  - indisponibilite/timeout simule => `422` ou `503` selon mapping decide
- Validation finale:
  - `ruff check .`
  - `pytest -q`

### Previous Story Intelligence

- Story 2.1 a etabli JWT access/refresh + RBAC minimal.
- Story 2.2 a etabli le profil natal utilisateur et la dependance auth reusable.
- Story 1.4/1.5 ont deja les patterns de calcul et de tracabilite; les reutiliser sans diverger.

### Git Intelligence Summary

- Le socle backend actuel est deja structure autour des conventions API/erreurs unifiees.
- Prioriser des ajouts incrementaux dans `users.py` et un service d orchestration dedie.

### Project Context Reference

- Aucun `project-context.md` detecte; source d autorite = PRD + Architecture + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 2, Story 2.3)
- Architecture patterns: `_bmad-output/planning-artifacts/architecture.md`
- Story precedente auth: `_bmad-output/implementation-artifacts/2-1-inscription-et-authentification-utilisateur-jwt.md`
- Story precedente profil natal: `_bmad-output/implementation-artifacts/2-2-saisie-et-gestion-des-donnees-natales.md`
- Services existants:
  - `backend/app/services/natal_calculation_service.py`
  - `backend/app/services/chart_result_service.py`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Dev-story workflow execution for Story 2.3
- `ruff check .`
- `pytest -q`

### Completion Notes List

- Added `UserNatalChartService` orchestrating profile lookup, natal calculation, and trace persistence.
- Added authenticated endpoint `POST /v1/users/me/natal-chart`.
- Added explicit timeout/engine-unavailable error mapping with retryable details.
- Added metadata exposure (`reference_version`, `ruleset_version`) in success response.
- Added unit and integration tests for nominal and failure paths.
- Added active timeout checkpoints during natal computation orchestration to fail fast when timeout budget is exceeded.
- Clarified review scope to backend source files for this story because repository-wide frontend deletions are unrelated to Story 2.3.

### File List

- _bmad-output/implementation-artifacts/2-3-generation-du-theme-natal-initial.md
- backend/app/services/user_natal_chart_service.py
- backend/app/services/natal_calculation_service.py
- backend/app/domain/astrology/natal_calculation.py
- backend/app/api/v1/routers/users.py
- backend/app/tests/unit/test_user_natal_chart_service.py
- backend/app/tests/integration/test_user_natal_chart_api.py
