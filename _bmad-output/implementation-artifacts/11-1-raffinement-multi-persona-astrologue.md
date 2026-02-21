# Story 11.1: Raffinement multi-persona astrologue

Status: review
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a product owner,  
I want enrichir les personas astrologues et leurs parametres,  
so that l experience conversationnelle gagne en personnalisation.

## Acceptance Criteria

1. Given la configuration persona existante, when de nouveaux profils sont introduits, then ils sont parametrables, testables et rollbackables.
2. Given les nouveaux profils deployes, when les interactions sont observees, then leur impact qualite est mesurable via KPI.

## Tasks / Subtasks

- [x] Etendre le modele persona pour le multi-profil (AC: 1)
  - [x] Definir les nouveaux attributs/versioning necessaires (ton, prudence, style, scope, fallback policy)
  - [x] Garantir compatibilite ascendante avec le profil actif actuel
  - [x] Prevoir rollback simple vers profil precedent
- [x] Ajouter la gestion applicative des profils personas (AC: 1)
  - [x] Ajouter services/use-cases de creation, activation, archivage et restauration de profil
  - [x] Verifier coherences RBAC (ops/support) pour les operations sensibles
  - [x] Assurer idempotence et validations robustes des payloads
- [x] Integrer le multi-persona dans les flux chat/guidance (AC: 1)
  - [x] Propager la selection persona dans la construction des prompts
  - [x] Assurer fallback propre si persona invalide/inactif
  - [x] Garantir non-regression sur parcours conversationnels existants
- [x] Instrumenter la mesure d impact qualite par persona (AC: 2)
  - [x] Ajouter metriques par profil (volume, erreurs, hors-scope, latence, recovery success)
  - [x] Exposer dimensions persona dans les vues ops pertinentes
  - [x] Verifier exploitabilite pour comparaison entre profils
- [x] Documenter gouvernance et exploitation des personas (AC: 1, 2)
  - [x] Documenter conventions de creation/validation des profils
  - [x] Definir garde-fous et procedure de rollback operationnelle
  - [x] Lister KPI de decision produit pour itérations futures
- [x] Couvrir par tests et quality checks (AC: 1, 2)
  - [x] Ajouter/mettre a jour tests unitaires backend (services persona/chat/guidance)
  - [x] Ajouter/mettre a jour tests integration API (CRUD/activation persona + impact conversation)
  - [x] Executer lint/tests/scripts qualite projet applicables

## Dev Notes

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 11, Story 11.1).
- Contexte: le socle persona existe deja (stories Epic 3 et 6); cette story industrialise le multi-profil et sa mesure.
- Dependances directes:
  - `3-7-parametrage-des-bornes-de-persona-astrologue.md`
  - `6-2-monitoring-qualite-conversationnelle-et-pilotage-ops.md`
  - `10-3-tuning-performance-guide-par-slo.md`

### Technical Requirements

- Introduire des profils personas supplementaires sans casser le comportement actuel.
- Rendre les profils testables et rollbackables.
- Mesurer explicitement l impact qualite par profil pour pilotage produit.

### Architecture Compliance

- Respecter la separation backend `api/core/domain/services/infra`.
- Conserver conventions API v1, format erreurs standardise, et observabilite existante.
- Eviter les refactors massifs hors perimetre persona/observabilite.

### Library / Framework Requirements

- Backend: FastAPI, SQLAlchemy, Pydantic, Alembic.
- Frontend: React + TypeScript (si exposition UI de selection persona requise).
- Tests: Pytest backend, Vitest frontend.

### File Structure Requirements

- Cibles probables backend:
  - `backend/app/services/persona_config_service.py`
  - `backend/app/services/chat_guidance_service.py`
  - `backend/app/services/guidance_service.py`
  - `backend/app/api/v1/routers/ops_persona.py`
  - `backend/app/infra/db/models/persona_config.py`
  - `backend/migrations/versions/` (si evolution schema)
  - `backend/app/tests/`
- Cibles probables frontend:
  - `frontend/src/api/` et `frontend/src/pages/` (si ajustements UX persona)

### Testing Requirements

- Verifier:
  - parametrage multi-profil et activation/restauration,
  - rollback fiable vers profil precedent,
  - non-regression fonctionnelle chat/guidance,
  - disponibilite de KPI qualite par persona.

### Previous Story Intelligence

- 3.7 a etabli le socle de configuration persona.
- 6.2 a etabli la mesure ops de qualite conversationnelle.
- 10.3 a introduit des pratiques de tuning/mesure a conserver.

### Git Intelligence Summary

- Sequence recommandee: modele -> services -> integration chat/guidance -> metriques -> tests/documentation.
- Maintenir un delta minimal et coherent.

### Project Context Reference

- `AGENTS.md`: validation locale obligatoire, deltas minimaux, lisibilite et maintenabilite.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 11, Story 11.1)
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/implementation-artifacts/3-7-parametrage-des-bornes-de-persona-astrologue.md`
- `_bmad-output/implementation-artifacts/6-2-monitoring-qualite-conversationnelle-et-pilotage-ops.md`
- `_bmad-output/implementation-artifacts/10-3-tuning-performance-guide-par-slo.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `_bmad/bmm/workflows/4-implementation/create-story/workflow.yaml`
- `_bmad/bmm/workflows/4-implementation/create-story/instructions.xml`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Completion Notes List

- Story 11.1 implementee et passee en `review`.
- Modele persona et migration etendus avec `profile_code`, `display_name`, `fallback_policy`.
- Service persona refactorise pour gerer list/create/activate/archive/restore/rollback avec validations fortes.
- Router ops persona etendu avec endpoints de cycle de vie profil et audit systematique.
- Flux chat/guidance instrumentes avec dimensions `persona_profile` pour latence et qualite.
- Endpoint ops monitoring `/v1/ops/monitoring/persona-kpis` ajoute.
- Documentation de gouvernance ajoutee: `docs/persona-governance.md`.
- Verification locale executee dans le venv: `ruff format`, `ruff check`, `pytest` cible (63 tests passants).

### File List

- `_bmad-output/implementation-artifacts/11-1-raffinement-multi-persona-astrologue.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/infra/db/models/persona_config.py`
- `backend/app/services/persona_config_service.py`
- `backend/app/api/v1/routers/ops_persona.py`
- `backend/app/services/chat_guidance_service.py`
- `backend/app/services/guidance_service.py`
- `backend/app/services/ops_monitoring_service.py`
- `backend/app/api/v1/routers/ops_monitoring.py`
- `backend/migrations/versions/20260220_0020_extend_persona_configs_multi_profile.py`
- `backend/app/tests/unit/test_persona_config_service.py`
- `backend/app/tests/integration/test_ops_persona_api.py`
- `backend/app/tests/unit/test_chat_guidance_service.py`
- `backend/app/tests/unit/test_guidance_service.py`
- `backend/app/tests/unit/test_ops_monitoring_service.py`
- `backend/app/tests/integration/test_ops_monitoring_api.py`
- `docs/persona-governance.md`
