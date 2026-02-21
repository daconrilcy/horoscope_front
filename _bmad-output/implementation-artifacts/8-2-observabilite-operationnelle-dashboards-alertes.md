# Story 8.2: Observabilite operationnelle (dashboards + alertes)

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an operations user,  
I want disposer de dashboards et alertes sur les parcours critiques,  
so that je detecte rapidement les degradations de service.

## Acceptance Criteria

1. Given des metriques et logs structures emis par les services, when les dashboards et regles d alerting sont configures, then les KPI critiques (latence, erreurs, disponibilite, quotas) sont visibles.
2. Given des alertes configurees, when un seuil critique est depasse, then l alerte est actionnable avec un contexte minimal exploitable.

## Tasks / Subtasks

- [x] Definir le scope observabilite MVP+ pour Epic 8.2 (AC: 1, 2)
  - [x] Lister les parcours critiques: auth, billing/quota, chat, privacy, natal chart, b2b
  - [x] Definir les KPI minimaux par parcours (latence p95, taux d erreur, disponibilite)
  - [x] Documenter les seuils d alerte initiaux et leur rational
- [x] Implementer les metriques backend manquantes (AC: 1)
  - [x] Standardiser les compteurs erreurs par endpoint/operation
  - [x] Exposer les mesures latence sur endpoints critiques
  - [x] Ajouter les dimensions minimales utiles (route, status_code, operation, role/plan si pertinent)
- [x] Completer les logs structures operationnels (AC: 1, 2)
  - [x] Garantir `request_id` sur tous les logs d erreur critiques
  - [x] Ajouter les champs de contexte incidents (endpoint, actor_role, error_code)
  - [x] Verifier l absence de donnees sensibles dans les logs
- [x] Construire les dashboards operationnels (AC: 1)
  - [x] Dashboard API health: disponibilite, latence, volume, erreurs 4xx/5xx
  - [x] Dashboard metier: quotas, incidents privacy, taux de fallback/recovery chat
  - [x] Dashboard B2B: erreurs auth API key, volume usage, saturation quotas
- [x] Mettre en place les regles d alerting actionnables (AC: 2)
  - [x] Alerte disponibilite API en degradation
  - [x] Alerte taux erreurs 5xx depasse seuil
  - [x] Alerte latence p95 depasse seuil sur endpoints critiques
  - [x] Alerte saturation quota / derive rate-limit anormale
- [x] Valider la chaine de detection et triage (AC: 2)
  - [x] Simuler au moins un scenario par type d alerte
  - [x] Verifier que chaque alerte inclut contexte minimal (service, endpoint, request_id, severite)
  - [x] Documenter un mini runbook de triage pour ops/support

## Dev Notes

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 8, Story 8.2)
- Contexte: suite directe de `8-1` (quality gates), focus sur exploitation production.
- Contraintes explicites connues:
  - Backend Python avec venv obligatoire pour commandes Python.
  - Frontend React/Vite deja en place.
  - Deploiement cible initial: Docker Compose single host.
  - Observabilite MVP attendue: logs structures + metriques + erreurs.

### Technical Requirements

- KPI critiques minimum a couvrir:
  - latence (p50/p95) endpoints critiques
  - taux erreurs (4xx/5xx) par endpoint
  - disponibilite service (/health + endpoints majeurs)
  - quotas (consommation, blocages, depassements)
- Alertes actionnables:
  - seuil explicite
  - severite
  - contexte minimal exploitable (service, endpoint, request_id ou corr_id)
- Instrumentation compatible deploiement Compose single host.

### Architecture Compliance

- Respecter la structure monorepo existante (`backend/`, `frontend/`, `scripts/`).
- S appuyer sur les modules existants `backend/app/infra/observability/*`.
- Ne pas exposer de donnees sensibles dans metriques/logs.

### Library / Framework Requirements

- Backend: Python 3.13, FastAPI, Pydantic, SQLAlchemy.
- Observabilite: instrumentation existante du projet (logs structures, metriques, erreurs).
- Infra: Docker Compose (single host).

### File Structure Requirements

- Cibles probables:
  - `backend/app/infra/observability/metrics.py`
  - `backend/app/infra/observability/errors.py`
  - `backend/app/main.py` (middleware/log context si besoin)
  - `scripts/` (checks ou smoke observabilite)
  - `_bmad-output/planning-artifacts/` (doc dashboards/alertes)

### Testing Requirements

- Verifier au moins:
  - emissions metriques sur parcours critiques
  - presence des champs logs requis sur erreurs critiques
  - declenchement/suppression alerte sur scenarios simules

### Previous Story Intelligence

- Story 8.1 a verrouille les quality gates et le predeploy check.
- Les regressions historiques du projet concernent surtout erreurs API et coherences cross-modules.
- Les checks automatiques evitent les regressions d observabilite si instrumentes dans tests/scripts.

### Git Intelligence Summary

- Le projet est en phase post-MVP de durcissement production.
- Priorite immediate: visibilite ops actionnable avant nouvelles optimisations infra.

### Project Context Reference

- Instructions de travail: `AGENTS.md` (venv obligatoire, lint/tests avant conclusion, stack imposee).
- Change proposal approuve: `_bmad-output/planning-artifacts/sprint-change-proposal-2026-02-20.md`.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 8, Story 8.2)
- `_bmad-output/planning-artifacts/architecture.md` (observabilite, NFR, deployment)
- `AGENTS.md` (workflow dev local, qualite, commandes)
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

- Middleware HTTP d instrumentation ajoute dans `backend/app/main.py` (compteurs + latence + header `X-Request-Id`).
- Service ops etendu avec `get_operational_summary` et alertes actionnables basees sur seuils.
- Endpoint API ops ajoute: `GET /v1/ops/monitoring/operational-summary`.
- Regles d alerte et triage documentes dans `_bmad-output/planning-artifacts/ops-observability-runbook.md`.
- Tests backend ajoutes/mis a jour (unit + integration + health) et valides.
- Code review de cloture: aucun point High/Medium/Low restant.

### File List

- `_bmad-output/implementation-artifacts/8-2-observabilite-operationnelle-dashboards-alertes.md`
- `backend/app/main.py`
- `backend/app/core/request_id.py`
- `backend/app/infra/observability/metrics.py`
- `backend/app/services/ops_monitoring_service.py`
- `backend/app/api/v1/routers/ops_monitoring.py`
- `backend/app/tests/test_health.py`
- `backend/app/tests/unit/test_ops_monitoring_service.py`
- `backend/app/tests/integration/test_ops_monitoring_api.py`
- `_bmad-output/planning-artifacts/ops-observability-runbook.md`
