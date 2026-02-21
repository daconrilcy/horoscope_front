# Story 8.4: Tests de charge et de concurrence des flux critiques

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a platform engineer,  
I want mesurer le comportement sous charge des endpoints critiques,  
so that nous validions la tenue en charge et les limites.

## Acceptance Criteria

1. Given un plan de tests de charge cible, when les scenarios chat/privacy/b2b/billing sont executes, then les resultats de performance et points de saturation sont traces.
2. Given les resultats des tests de charge, when l analyse est finalisee, then des actions de tuning priorisees sont produites.

## Tasks / Subtasks

- [x] Definir le plan de charge et de concurrence des parcours critiques (AC: 1)
  - [x] Identifier les endpoints/scenarios cibles: chat, privacy (export/suppression), billing/quota, b2b API
  - [x] Definir profils de charge (ramp-up, plateau, spike) et concurrence cible par scenario
  - [x] Definir les KPI mesures: latence p50/p95/p99, throughput, taux d erreur, saturation rate-limit/quota
- [x] Mettre en place le harness de test de charge (AC: 1)
  - [x] Ajouter des scripts de charge reproductibles dans `scripts/` (avec parametres d environnement)
  - [x] Prevoir l authentification / generation de tokens / API keys pour scenarios proteges
  - [x] Capturer les resultats bruts de run (json/csv/log) pour analyse
- [x] Executer les campagnes sur environnement cible de reference (AC: 1)
  - [x] Campagne parcours chat conversationnel
  - [x] Campagne parcours privacy et billing/quota
  - [x] Campagne endpoints B2B et limites de plan
  - [x] Documenter les points de saturation observes
- [x] Corréler les resultats avec l observabilite existante (AC: 1)
  - [x] Verifier les metriques ops (`/v1/ops/monitoring/operational-summary`) pendant les runs
  - [x] Associer latence/erreurs aux endpoints et classes de statut
  - [x] Identifier les goulets (DB, cache Redis, rate-limit, appels LLM)
- [x] Produire un plan de tuning priorise (AC: 2)
  - [x] Etablir top 5 actions avec impact attendu, effort, risque
  - [x] Classer les actions en quick wins vs optimisations structurelles
  - [x] Definir criteres de re-test pour valider les gains
- [x] Ajouter une validation minimale en CI locale (AC: 1, 2)
  - [x] Ajouter un mode smoke/perf court non destructif executable localement
  - [x] Documenter procedure d execution + interpretation des resultats

## Dev Notes

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 8, Story 8.4)
- Contexte: suite de `8-1` (quality gates), `8-2` (observabilite) et `8-3` (backup/restore), focus sur performance operationnelle.
- Contraintes explicites connues:
  - Backend Python avec venv obligatoire pour commandes Python.
  - Deploiement cible initial: Docker Compose single host.
  - API REST versionnee avec rate limiting global + par user/plan.
  - Observabilite operationnelle deja en place pour analyser les runs.

### Technical Requirements

- Couvrir les flux critiques sous charge:
  - chat/conversation
  - privacy export/suppression
  - billing/quota
  - b2b API
- Mesurer au minimum:
  - latence p50/p95/p99
  - taux erreurs 4xx/5xx
  - throughput
  - signaux de saturation (quotas/rate-limits/retries)
- Produire des resultats exploitables et reproductibles.

### Architecture Compliance

- Respecter la structure monorepo (`backend/`, `frontend/`, `scripts/`).
- Reutiliser les metriques/logs existants sans introduire d instrumentation parallelle incoherente.
- Rester compatible avec deploiement Docker Compose single host.

### Library / Framework Requirements

- Backend: Python 3.13, FastAPI, SQLAlchemy, Redis.
- Observabilite: stack actuelle du projet (logs structures + metriques + erreurs).
- Outil de charge: au choix de l implementation, mais scripts reproductibles requis.

### File Structure Requirements

- Cibles probables:
  - `scripts/load-test-*.ps1` ou equivalent
  - `backend/app/tests/integration/` (smoke/perf court)
  - `_bmad-output/planning-artifacts/` (rapport de campagne et plan de tuning)
  - `backend/README.md` (instructions d execution)

### Testing Requirements

- Verifier au minimum:
  - execution d un run de charge sur chaque flux critique
  - capture des metriques/resultats sans erreur de harness
  - generation d un plan de tuning priorise base sur donnees mesurees

### Previous Story Intelligence

- `8-1` fournit les quality gates et scripts de verification predeploy.
- `8-2` fournit dashboards/alertes et endpoint ops de synthese.
- `8-3` fournit runbooks de reprise pour reinitialiser proprement l environnement avant campagne.

### Git Intelligence Summary

- Projet en phase de durcissement post-MVP.
- Priorite immediate: etablir des limites de charge factuelles et prioriser les optimisations.

### Project Context Reference

- Instructions de travail: `AGENTS.md` (venv obligatoire, lint/tests avant conclusion, stack imposee).
- Change proposal approuve: `_bmad-output/planning-artifacts/sprint-change-proposal-2026-02-20.md`.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 8, Story 8.4)
- `_bmad-output/planning-artifacts/architecture.md` (NFR performance, rate-limiting, observabilite)
- `_bmad-output/planning-artifacts/ops-observability-runbook.md`
- `AGENTS.md`
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

- Harness de charge ajoute: `scripts/load-test-critical.ps1` (chat/privacy/billing + b2b optionnel), avec export JSON des resultats.
- Test d integration smoke charge/concurrence ajoute: `backend/app/tests/integration/test_load_smoke_critical_flows.py`.
- Couverture des flux critiques verifiee en mode non destructif avec verification p95 et absence de 5xx.
- Template de rapport/tuning ajoute: `_bmad-output/planning-artifacts/performance-load-test-report-template.md`.
- Documentation d execution ajoutee dans `backend/README.md`.
- Execution reelle validee sur backend live local, rapport produit: `artifacts/load-test-report.json`.
- Correctif applique au script pour serialiser `recommendations` en tableau JSON (`[]`) plutot que `null`.
- Rapport de campagne et plan de tuning initial rediges: `_bmad-output/planning-artifacts/performance-load-test-report-2026-02-20.md`.
- Harness enrichi avec profils phases `ramp_up/plateau/spike` et KPI throughput.
- Flux privacy suppression ajoute via `POST /v1/privacy/delete` avec gestion des statuts attendus.
- Correlation ops implementee via snapshots pre/post sur `/v1/ops/monitoring/operational-summary` (token ops).
- Campagne complete executee avec B2B actif + ops correlation + rapport mis a jour.

### Findings Addressed

- [HIGH] Scenario B2B execute dans la campagne reelle (plus de gap de couverture AC1).
- [HIGH] Flux privacy suppression couvert dans le harness et le rapport.
- [HIGH] KPI throughput calcule et trace par scenario.
- [HIGH] Correlation ops executee et documentee (pre/post run).
- [MEDIUM] Profils ramp-up/plateau/spike implementes explicitement dans le runner.

### File List

- `_bmad-output/implementation-artifacts/8-4-tests-de-charge-et-de-concurrence-des-flux-critiques.md`
- `scripts/load-test-critical.ps1`
- `backend/app/tests/integration/test_load_smoke_critical_flows.py`
- `_bmad-output/planning-artifacts/performance-load-test-report-template.md`
- `_bmad-output/planning-artifacts/performance-load-test-report-2026-02-20.md`
- `backend/README.md`
