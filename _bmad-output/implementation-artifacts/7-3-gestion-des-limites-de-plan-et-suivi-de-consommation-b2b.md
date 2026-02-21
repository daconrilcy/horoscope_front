# Story 7.3: Gestion des limites de plan et suivi de consommation B2B

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an enterprise admin,  
I want consulter mes volumes consommes et limites contractuelles,  
so that je pilote mon usage et mes couts.

## Acceptance Criteria

1. Given un contrat B2B actif, when l admin consulte les metriques de consommation, then les volumes (par periode et cumules) et limites contractuelles sont visibles et coherents.
2. Given un plan B2B avec regles de limites, when les appels API sont effectues, then la consommation est comptabilisee de maniere fiable par compte/credential et exposee via endpoint versionne `/v1`.
3. Given un depassement de limite contractuelle, when un appel est tente, then le systeme applique la regle prevue (blocage ou overage) et renvoie une erreur/reponse standardisee avec `code`, `message`, `details`, `request_id`.
4. Given des operations de suivi de consommation, when elles sont executees, then les metriques techniques minimales (volume, depassement, erreurs) et les traces d audit pertinentes sont disponibles.

## Tasks / Subtasks

- [x] Definir le modele de consommation B2B et ses regles de limites (AC: 1, 2, 3)
  - [x] Introduire/adapter les objets metier de quota B2B (limite contractuelle, consommation periode, mode overage/block)
  - [x] Aligner le modele avec les plans B2B existants (sans dupliquer le modele B2C)
  - [x] Garantir la compatibilite avec PostgreSQL + Redis pour compteurs et fenetres temporelles
- [x] Mettre en place le comptage de consommation sur appels B2B (AC: 2, 3)
  - [x] Brancher le comptage sur les endpoints B2B existants (notamment `/v1/b2b/astrology/weekly-by-sign`)
  - [x] Incrementer de facon atomique par compte et credential
  - [x] Retourner une erreur standardisee en cas de limite depassee si mode blocant
- [x] Exposer les endpoints B2B de suivi de consommation (AC: 1, 2, 3)
  - [x] Ajouter un routeur/versionnement `/v1/b2b/usage/*` (ou extension du routeur B2B existant)
  - [x] Fournir un endpoint de resume de consommation (periode courante, limite, restant, depassement)
  - [x] Assurer un contrat de reponse explicite et stable (`data` + `meta.request_id`)
- [x] Integrer observabilite et audit sur le suivi des limites (AC: 4)
  - [x] Ajouter compteurs techniques minimaux (`b2b_usage_events_total`, `b2b_quota_exceeded_total`, erreurs)
  - [x] Journaliser les cas de depassement et decisions appliquees (block/overage)
  - [x] Auditer les actions sensibles de gestion de limites/capacites si exposees
- [x] Ajouter un panneau frontend de suivi consommation B2B (AC: 1, 3)
  - [x] Ajouter client API dans `frontend/src/api/` pour recuperer les metriques B2B
  - [x] Ajouter panneau React (loading/error/empty) pour visualiser limite/consommation/restant
  - [x] Afficher les erreurs standardisees B2B remontees par l API
- [x] Tester et valider la story (AC: 1, 2, 3, 4)
  - [x] Unit tests backend: regles quota B2B (in limit, exceeded, overage allowed, blocked)
  - [x] Integration tests backend: 200/401/403/429/422 + format erreur uniforme + `request_id`
  - [x] Tests frontend: rendu metriques + etats `loading/error/empty`
  - [x] Validation finale: `ruff check backend` + `pytest -q backend` + `npm run lint` + `npm test -- --run`

## Dev Notes

- Story source: Epic 7 Story 7.3 (FR40), dependante de Story 7.1 (credentials) et Story 7.2 (consommation API B2B authentifiee).
- Objectif principal: ajouter la couche "usage/limits" B2B sans casser les contrats deja exposes en 7.2.
- Contraintes critiques:
  - conserver API versionnee `/v1` et enveloppe d erreur standard
  - reutiliser auth B2B API key existante (ne pas recreer une auth parallele)
  - garantir comptage fiable et explicable (audit/metriques)

### Technical Requirements

- Comptage de consommation B2B par compte et credential avec source de verite claire.
- Regles de limites contractuelles explicites (blocage ou overage), appliquees uniformement.
- Contrat d erreur standard `code/message/details/request_id` sur depassement/deni.
- Metriques techniques minimales sur volume et depassement.

### Architecture Compliance

- Respect `api -> services -> domain -> infra`.
- Reutiliser les briques des stories 7.1/7.2:
  - `enterprise_credentials_service`
  - dependance `require_authenticated_b2b_client`
  - routeurs B2B versionnes
- Appuyer les compteurs de quotas/rate limits sur Redis comme decrit par l architecture.
- Maintenir separation claire entre logiques B2C quotas et logique B2B contractuelle.

### Library / Framework Requirements

- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic, Redis.
- Frontend: React + TypeScript + TanStack Query.
- Tests: Pytest backend, Vitest + Testing Library frontend.

### File Structure Requirements

- Backend (cibles probables):
  - `backend/app/api/v1/routers/` (usage/limits B2B)
  - `backend/app/services/` (service quotas/consommation B2B)
  - `backend/app/core/` (integration rate-limit/quota commune si necessaire)
  - `backend/app/tests/unit/`
  - `backend/app/tests/integration/`
- Frontend (cibles probables):
  - `frontend/src/api/`
  - `frontend/src/components/`
  - `frontend/src/tests/`

### Testing Requirements

- Unit:
  - comptage consommation et calcul restant
  - depassement limite en mode blocage
  - depassement limite en mode overage
- Integration:
  - appels B2B authentifies avec consommation incrementee
  - lecture metriques B2B selon compte
  - erreurs standardisees au depassement (avec `request_id`)
- Frontend:
  - rendu limite/consommation/restant
  - gestion `loading/error/empty`
  - affichage propre des erreurs standardisees

### Previous Story Intelligence

- Story 7.2 a etabli:
  - endpoint B2B `weekly-by-sign` avec auth API key et enveloppe d erreur uniforme
  - rate limiting global/account/credential
  - metriques B2B de base + audit des echecs auth
- Pour 7.3:
  - brancher le suivi de consommation directement sur ces flux existants
  - eviter toute rupture de contrat front/back deja en place
  - etendre les tests integration B2B existants plutot que dupliquer des suites

### Git Intelligence Summary

- Les derniers travaux sont axes robustesse tests + coherences d integration.
- Continuer avec petits deltas, couverture tests forte, et contrats API explicites.

### Project Context Reference

- Aucun `project-context.md` detecte; sources d autorite = PRD + Architecture + UX + Epics.

### References

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 7, Story 7.3)
- PRD: `_bmad-output/planning-artifacts/prd.md` (FR40, NFR12, NFR17, NFR18)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (API versioning `/v1`, Redis counters, quotas/rate-limits, observabilite)
- Story precedente: `_bmad-output/implementation-artifacts/7-2-consommation-api-astrologie-authentifiee.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `_bmad/bmm/workflows/4-implementation/create-story/workflow.yaml`
- `_bmad/bmm/workflows/4-implementation/create-story/instructions.xml`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/planning-artifacts/epics.md`

### Completion Notes List

- Modele de consommation B2B ajoute avec persistance quotidienne par compte/credential (`enterprise_daily_usages`) et resume journalier/mensuel.
- Service `B2BUsageService` implemente avec politiques de limite configurables (`block`/`overage`) et compteurs d observabilite.
- Endpoint versionne `GET /v1/b2b/usage/summary` ajoute et protege par API key B2B.
- Endpoint B2B astrologie branche sur la consommation B2B avec retour standardise `b2b_quota_exceeded` en cas de blocage.
- Frontend ajoute: client API `b2bUsage`, panneau `B2BUsagePanel` et integration dans `App`.
- Tests ajoutes backend (unit + integration) et frontend (panel), validation complete executee.

### File List

- `backend/app/core/config.py`
- `backend/app/infra/db/models/enterprise_usage.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/services/b2b_usage_service.py`
- `backend/app/api/v1/routers/b2b_usage.py`
- `backend/app/api/v1/routers/b2b_astrology.py`
- `backend/app/api/v1/routers/__init__.py`
- `backend/app/main.py`
- `backend/app/tests/unit/test_b2b_usage_service.py`
- `backend/app/tests/integration/test_b2b_astrology_api.py`
- `frontend/src/api/b2bUsage.ts`
- `frontend/src/components/B2BUsagePanel.tsx`
- `frontend/src/tests/B2BUsagePanel.test.tsx`
- `frontend/src/App.tsx`
