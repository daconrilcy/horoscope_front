# Story 9.1: Durcissement de la gestion des secrets et rotation

Status: review
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a security engineer,  
I want formaliser la gestion des secrets et leur rotation,  
so that le risque de compromission soit reduit.

## Acceptance Criteria

1. Given les secrets applicatifs et integrations externes, when la politique de stockage/rotation est appliquee, then aucun secret n est expose en clair dans le code ou logs.
2. Given une procedure de rotation periodique, when elle est executee, then les secrets concernes sont rotates sans interruption fonctionnelle majeure et la procedure est testee/documentee.

## Tasks / Subtasks

- [x] Inventorier et classifier les secrets critiques (AC: 1)
  - [x] Lister secrets backend/frontend/infra (JWT, DB, API keys, credentials B2B)
  - [x] Classer par criticite, proprietaire, frequence de rotation cible
  - [x] Identifier les chemins de fuite potentiels (code, logs, artefacts, docs)
- [x] Durcir la configuration et l injection des secrets (AC: 1)
  - [x] Verifier qu aucun secret n est en dur dans le code/app config
  - [x] Centraliser la lecture des secrets via variables d environnement
  - [x] Renforcer la validation au demarrage si secret manquant/invalide
- [x] Ajouter des controles automatiques anti-exposition (AC: 1)
  - [x] Ajouter un scan repository pour motifs de secrets connus (regex + allowlist)
  - [x] Integrer le scan dans quality gate/predeploy
  - [x] Ajouter tests de non-regression pour tokens/credentials de fallback
- [x] Formaliser et outiller la rotation des secrets (AC: 2)
  - [x] Definir procedure de rotation JWT secret (double-fenetre ou strategy compatible)
  - [x] Definir procedure de rotation API keys enterprise et credentials externes
  - [x] Ajouter scripts/checklists ops de rotation et verification post-rotation
- [x] Tester la procedure de rotation bout-en-bout (AC: 2)
  - [x] Simuler une rotation sur environnement local/staging
  - [x] Verifier continuity des flux critiques (auth, billing, chat, b2b)
  - [x] Documenter impacts, rollback et preuves d execution
- [x] Documenter la politique et les runbooks (AC: 1, 2)
  - [x] Ajouter politique de gestion des secrets (stockage, acces, rotation)
  - [x] Ajouter runbook de rotation avec prerequis et etapes
  - [x] Ajouter checklist de verification post-rotation

## Dev Notes

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 9, Story 9.1)
- Contexte: suite du lot Production Readiness (Epic 8), focalise sur hardening securite.
- Contraintes explicites connues:
  - Backend Python avec venv obligatoire pour commandes Python.
  - Stack cible: FastAPI + PostgreSQL + Redis + JWT + RBAC.
  - Deploiement initial Docker Compose single host.

### Technical Requirements

- Aucun secret sensible en clair dans code, logs, examples commites.
- Procedure de rotation reproductible, testee et rollbackable.
- Verification automatique integree aux gates qualite.

### Architecture Compliance

- Respecter architecture monorepo (`backend/`, `frontend/`, `scripts/`).
- Conserver compatibilite des contrats API et des flux auth existants.
- Ne pas introduire de mecanisme proprietaire non necessaire au MVP.

### Library / Framework Requirements

- Backend: Python 3.13, FastAPI, Pydantic, SQLAlchemy.
- Outillage qualite: scripts PowerShell existants (`quality-gate`, `predeploy-check`).
- Infra: Docker Compose, variables d environnement.

### File Structure Requirements

- Cibles probables:
  - `backend/app/core/config.py` (validation secrets)
  - `scripts/quality-gate.ps1` / `scripts/predeploy-check.ps1` (scan secrets)
  - `scripts/` (outils rotation/checks)
  - `_bmad-output/planning-artifacts/` (policy + runbooks)
  - `backend/README.md` (instructions rotation/verification)

### Testing Requirements

- Verifier au minimum:
  - scan anti-secrets efficace sur patterns cibles
  - absence de fallback credentials en production path
  - rotation testee sans regression sur flux critiques

### Previous Story Intelligence

- Epic 8 a etabli quality gates, observabilite et resilience ops.
- Ces briques doivent etre reutilisees pour tracer et valider la rotation.

### Git Intelligence Summary

- Projet en phase de hardening post-MVP.
- Priorite immediate: reduire surface de risque secrets avant scale.

### Project Context Reference

- Instructions de travail: `AGENTS.md` (venv obligatoire, lint/tests avant conclusion).
- Epics source: `_bmad-output/planning-artifacts/epics.md`.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 9, Story 9.1)
- `_bmad-output/planning-artifacts/architecture.md` (NFR securite, secrets, conformite)
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

- Suppression des secrets fallback hardcodes en non-production via generation dynamique en memoire.
- Support de rotation avec grace period ajoute:
  - JWT verification multi-cles (`JWT_PREVIOUS_SECRET_KEYS`)
  - HMAC credentials B2B multi-cles (`API_CREDENTIALS_PREVIOUS_SECRET_KEYS`)
- Scan anti-secrets implemente (`scripts/scan-secrets.ps1`) avec allowlist et integration dans `scripts/quality-gate.ps1`.
- Variables d environnement de secrets et rotation explicitees dans `.env.example`.
- Documentation politique/runbook de rotation ajoutee et README backend mis a jour.
- Tests unitaires/integration ajoutes/mis a jour et valides (`22 passed`).

### File List

- `_bmad-output/implementation-artifacts/9-1-durcissement-de-la-gestion-des-secrets-et-rotation.md`
- `backend/app/core/config.py`
- `backend/app/core/security.py`
- `backend/app/services/enterprise_credentials_service.py`
- `scripts/scan-secrets.ps1`
- `scripts/secrets-scan-allowlist.txt`
- `scripts/quality-gate.ps1`
- `.env.example`
- `backend/README.md`
- `_bmad-output/planning-artifacts/secrets-management-and-rotation-runbook.md`
- `backend/app/tests/unit/test_settings.py`
- `backend/app/tests/unit/test_auth_service.py`
- `backend/app/tests/unit/test_enterprise_credentials_service.py`
- `backend/app/tests/integration/test_secrets_scan_script.py`
