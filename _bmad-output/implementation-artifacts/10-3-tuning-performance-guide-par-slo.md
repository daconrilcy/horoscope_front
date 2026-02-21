# Story 10.3: Tuning performance guide par SLO

Status: review
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a platform engineer,  
I want optimiser DB/cache/retries selon des SLO explicites,  
so that la performance reste stable sous croissance.

## Acceptance Criteria

1. Given des SLO definis pour les parcours critiques, when les optimisations sont appliquees, then les metriques montrent un gain mesurable.
2. Given les changements de tuning effectues, when les decisions sont revues, then les arbitrages cout/latence sont documentes.

## Tasks / Subtasks

- [x] Etablir les SLO cibles et baseline de performance sur parcours critiques (AC: 1)
  - [x] Definir les SLO (latence p95/p99, taux erreur, disponibilite) pour chat, billing, privacy, b2b API
  - [x] Capturer baseline avant optimisation via metriques existantes et tests de charge
  - [x] Formaliser les seuils d acceptation et budget de degradation
- [x] Optimiser la couche DB sur endpoints critiques (AC: 1)
  - [x] Identifier les requetes lentes (profiling SQLAlchemy/DB)
  - [x] Ajouter/ajuster index et plans de requetes pertinents
  - [x] Verifier absence de regressions fonctionnelles et gain de latence mesurable
- [x] Optimiser strategie cache et invalidation (AC: 1)
  - [x] Identifier les reponses a forte frequence reutilisables (Redis/memoization)
  - [x] Ajuster TTL/invalidation pour eviter stale data et recalculs inutiles
  - [x] Mesurer reduction de charge DB et amelioration latence
- [x] Ajuster retries/timeouts/backoff des integrations externes (AC: 1)
  - [x] Harmoniser timeouts client API/LLM avec SLO cibles
  - [x] Appliquer retries bornes + backoff jitter sur flux tolerants
  - [x] Verifier impact sur taux erreur et latence percue
- [x] Instrumenter et valider les gains de tuning (AC: 1)
  - [x] Ajouter/adapter metriques manquantes pour suivre les optimisations
  - [x] Executer campagne de tests de charge/concurrence post-tuning
  - [x] Comparer baseline vs post-tuning avec un recap chiffre
- [x] Documenter les arbitrages cout/latence et recommandations (AC: 2)
  - [x] Documenter decisions prises (trade-offs, raisons, limites)
  - [x] Formaliser garde-fous et rollback criteria
  - [x] Proposer backlog de tuning restant priorise
- [x] Couvrir par tests et quality checks (AC: 1, 2)
  - [x] Mettre a jour tests unit/integration impactes
  - [x] Verifier non-regression end-to-end sur flux critiques
  - [x] Executer lint/tests/scripts qualite projet applicables

## Dev Notes

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 10, Story 10.3).
- Contexte: 10.1 a renforce la couverture front B2B, 10.2 a apporte la pilotabilite ops de reconciliation; 10.3 cible la stabilite performance sous croissance.
- Dependances directes:
  - `8-2-observabilite-operationnelle-dashboards-alertes.md`
  - `8-4-tests-de-charge-et-de-concurrence-des-flux-critiques.md`
  - `10-2-reconciliation-usage-facturation-b2b-pour-ops.md`

### Technical Requirements

- Les optimisations doivent etre guidees par SLO explicites et verifiables.
- Les gains doivent etre mesures avant/apres avec indicateurs quantifies.
- Les arbitrages cout/latence doivent etre explicitement traces.

### Architecture Compliance

- Respecter la separation backend `api/core/domain/services/infra`.
- Prioriser des optimisations locales et incrementales sans refactor massif hors scope.
- Conserver conventions API v1, format erreurs standardise, et observabilite existante.

### Library / Framework Requirements

- Backend: FastAPI, SQLAlchemy, Pydantic, Alembic, Redis.
- Frontend: React + TypeScript + TanStack Query (si ajustements timeout/retry cote front).
- Tests: Pytest backend, Vitest frontend, scripts de charge existants.

### File Structure Requirements

- Cibles probables backend:
  - `backend/app/services/`
  - `backend/app/infra/db/`, `backend/alembic/` (si index/migrations)
  - `backend/app/infra/observability/`
  - `backend/app/tests/`
- Cibles probables frontend:
  - `frontend/src/api/` (timeouts/retries)
  - `frontend/src/tests/` (non-regression)
- Documentation:
  - `_bmad-output/implementation-artifacts/10-3-tuning-performance-guide-par-slo.md`
  - eventuels artefacts de mesures dans `_bmad-output/planning-artifacts/` ou `artifacts/`

### Testing Requirements

- Verifier:
  - gains mesurables sur metriques SLO ciblees,
  - non-regression fonctionnelle des parcours critiques,
  - robustesse sous charge/concurrence representative,
  - tracabilite des decisions de tuning.

### Previous Story Intelligence

- 8.2 fournit la base de metriques/alertes.
- 8.4 fournit la base de scenarios de charge et de saturation.
- 10.2 apporte un flux ops supplementaire a inclure dans la verification de performance.

### Git Intelligence Summary

- Sequence recommandee: baseline -> tuning DB/cache/retry -> mesures -> documentation arbitrages.
- Minimiser les changements hors perimetre SLO/performance.

### Project Context Reference

- `AGENTS.md`: validation locale obligatoire, deltas minimaux, lisibilite et maintenabilite.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 10, Story 10.3)
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/implementation-artifacts/8-2-observabilite-operationnelle-dashboards-alertes.md`
- `_bmad-output/implementation-artifacts/8-4-tests-de-charge-et-de-concurrence-des-flux-critiques.md`
- `_bmad-output/implementation-artifacts/10-2-reconciliation-usage-facturation-b2b-pour-ops.md`
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

- Ajout d un cache TTL court sur le statut d abonnement avec invalidation explicite sur checkout/retry/plan-change.
- Suppression d un aller-retour DB sur `/v1/billing/quota` en reutilisant l abonnement deja charge.
- Ajout de backoff/jitter configurable pour retries guidance (`CHAT_LLM_RETRY_BACKOFF_*`).
- Ajout d indexes composites sur conversations/messages/privacy/subscriptions/usage B2B pour accelerer les tris et filtres critiques.
- Ajout d une migration Alembic dediee (`20260220_0019_add_performance_indexes.py`).
- Validation locale: `ruff format`, `ruff check`, tests unitaires et integration critiques passes.

### File List

- `_bmad-output/implementation-artifacts/10-3-tuning-performance-guide-par-slo.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/core/config.py`
- `backend/app/services/billing_service.py`
- `backend/app/services/quota_service.py`
- `backend/app/services/guidance_service.py`
- `backend/app/api/v1/routers/billing.py`
- `backend/app/infra/db/models/chat_conversation.py`
- `backend/app/infra/db/models/chat_message.py`
- `backend/app/infra/db/models/privacy.py`
- `backend/app/infra/db/models/billing.py`
- `backend/app/infra/db/models/enterprise_usage.py`
- `backend/migrations/versions/20260220_0019_add_performance_indexes.py`
- `_bmad-output/planning-artifacts/performance-slo-tuning-report-2026-02-20.md`
- `backend/app/tests/unit/test_billing_service.py`
- `backend/app/tests/unit/test_quota_service.py`
- `backend/app/tests/unit/test_guidance_service.py`
