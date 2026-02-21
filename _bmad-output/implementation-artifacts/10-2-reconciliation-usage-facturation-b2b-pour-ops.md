# Story 10.2: Reconciliation usage/facturation B2B pour ops

Status: review
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an operations user,  
I want suivre la coherence entre consommation et facturation B2B,  
so that les ecarts soient detectes avant impact client.

## Acceptance Criteria

1. Given les donnees usage et billing B2B, when la vue de reconciliation est consultee, then les ecarts sont identifies et traces.
2. Given des ecarts identifies sur un compte/periode, when l operateur analyse la situation, then les actions de correction sont explicites.

## Tasks / Subtasks

- [x] Cartographier les sources de verite usage vs facturation et les regles d ecart (AC: 1)
  - [x] Identifier les tables/endpoints utilises pour la consommation B2B
  - [x] Identifier les tables/endpoints utilises pour la facturation B2B
  - [x] Definir les regles de comparaison (periode, unite, arrondis, mode limite, overage)
- [x] Implementer un service backend de reconciliation B2B (AC: 1)
  - [x] Calculer les ecarts par compte/periode (usage mesure vs facturee)
  - [x] Classifier les ecarts (none/minor/major) avec seuils explicites
  - [x] Retourner un schema stable pour exploitation ops (`data + meta.request_id`)
- [x] Exposer des endpoints ops dedies reconciliation (AC: 1, 2)
  - [x] Endpoint liste des ecarts avec filtres (periode, severite, compte)
  - [x] Endpoint detail d un ecart (elements de calcul, trace de source)
  - [x] Standardiser les erreurs (`code/message/details/request_id`)
- [x] Ajouter actions de correction explicites (AC: 2)
  - [x] Definir les actions autorisees (recalcul, re-sync, marquage investigue, annotation)
  - [x] Journaliser chaque action ops dans l audit trail
  - [x] Rendre visible l etat d avancement de correction
- [x] Ajouter une vue ops/frontend de reconciliation (AC: 1, 2)
  - [x] Tableau des ecarts avec filtres et tri
  - [x] Vue detail avec comparaison usage/facturation
  - [x] Etats `loading/error/empty` et affichage `request_id`
- [x] Couvrir par tests et validation finale (AC: 1, 2)
  - [x] Unit tests service reconciliation (calcul ecarts, seuils, classifications)
  - [x] Integration tests API ops reconciliation (auth/role, erreurs, pagination/filtres)
  - [x] Tests frontend ops (liste/detail, erreurs, actions)
  - [x] Executer quality checks projet applicables

## Dev Notes

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 10, Story 10.2).
- Contexte: la story 10.1 a renforce la non-regression frontend B2B; 10.2 cible la pilotabilite ops de la coherence business.
- Dependances directes:
  - `7-3-gestion-des-limites-de-plan-et-suivi-de-consommation-b2b.md`
  - `7-5-facturation-hybride-fixe-volume.md`
  - `6-2-monitoring-qualite-conversationnelle-et-pilotage-ops.md`

### Technical Requirements

- La reconciliation doit comparer usage et facturation sur un meme perimetre temporel et contractuel.
- Les ecarts doivent etre tracables, classifies et consultables via endpoints ops.
- Les actions de correction doivent etre explicites, auditees et idempotentes quand applicable.

### Architecture Compliance

- Respecter la separation backend `api/core/domain/services/infra`.
- Reutiliser les modeles/services usage et billing existants; eviter la duplication des calculs.
- Conserver les conventions API v1 et le format d erreur standardise.

### Library / Framework Requirements

- Backend: FastAPI, SQLAlchemy, Pydantic, Alembic.
- Frontend: React + TypeScript + TanStack Query.
- Tests: Pytest backend, Vitest frontend.

### File Structure Requirements

- Cibles probables backend:
  - `backend/app/services/` (service reconciliation)
  - `backend/app/api/v1/routers/` (routeur ops reconciliation)
  - `backend/app/tests/unit/` et `backend/app/tests/integration/`
- Cibles probables frontend:
  - `frontend/src/api/`
  - `frontend/src/components/` ou `frontend/src/pages/`
  - `frontend/src/tests/`

### Testing Requirements

- Verifier:
  - detection d ecarts sur cas nominaux et limites,
  - absence de faux positifs sur donnees coherentes,
  - gestion des erreurs ops (auth/role/validation),
  - rendu UI ops complet des etats et des actions de correction.

### Previous Story Intelligence

- 7.3 a fourni la base de consommation B2B.
- 7.5 a fourni la base de facturation hybride et les snapshots de calcul.
- 10.2 doit reconciler ces deux couches avec une vue ops exploitable.

### Git Intelligence Summary

- Continuer en increments: service -> API -> UI -> tests -> quality gates.
- Minimiser les changements transverses hors scope reconciliation.

### Project Context Reference

- `AGENTS.md`: stack imposee, validation locale obligatoire, minimiser le delta.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 10, Story 10.2)
- `_bmad-output/planning-artifacts/architecture.md` (patterns API, observabilite, ops)
- `_bmad-output/implementation-artifacts/7-3-gestion-des-limites-de-plan-et-suivi-de-consommation-b2b.md`
- `_bmad-output/implementation-artifacts/7-5-facturation-hybride-fixe-volume.md`
- `_bmad-output/implementation-artifacts/6-2-monitoring-qualite-conversationnelle-et-pilotage-ops.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `_bmad/bmm/workflows/4-implementation/dev-story/workflow.yaml`
- `_bmad/bmm/workflows/4-implementation/dev-story/instructions.xml`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/services/b2b_reconciliation_service.py`
- `backend/app/api/v1/routers/b2b_reconciliation.py`

### Completion Notes List

- Service backend de reconciliation ajoute avec calcul des ecarts usage/facturation par compte et periode, severite `none/minor/major`, et traces de sources.
- Endpoints ops ajoutes: liste des ecarts, detail d un ecart, execution des actions de correction (`recalculate`, `resync`, `mark_investigated`, `annotate`).
- Audit trail complete pour les lectures et actions de reconciliation (target_type dedie + `request_id`).
- Panneau frontend ops ajoute pour charger les ecarts, consulter le detail et executer les actions avec etats `loading/error/empty`.
- Validation executee:
  - `.\.venv\Scripts\Activate.ps1; ruff check backend/app`
  - `.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests/unit/test_b2b_reconciliation_service.py backend/app/tests/integration/test_b2b_reconciliation_api.py`
  - `.\.venv\Scripts\Activate.ps1; pytest -q backend/app/tests` (357 passed, 2 skipped)
  - `npm run lint`
  - `npm run test -- --run`

### File List

- `_bmad-output/implementation-artifacts/10-2-reconciliation-usage-facturation-b2b-pour-ops.md`
- `backend/app/main.py`
- `backend/app/api/v1/routers/b2b_reconciliation.py`
- `backend/app/services/b2b_reconciliation_service.py`
- `backend/app/tests/integration/test_b2b_reconciliation_api.py`
- `backend/app/tests/unit/test_b2b_reconciliation_service.py`
- `frontend/src/App.tsx`
- `frontend/src/api/b2bReconciliation.ts`
- `frontend/src/components/B2BReconciliationPanel.tsx`
- `frontend/src/tests/B2BReconciliationPanel.test.tsx`
- `frontend/src/tests/b2bReconciliationApi.test.ts`

## Change Log

- 2026-02-20: Implementation completee de la story 10.2 (backend reconciliation + API ops + UI ops + tests backend/frontend).
