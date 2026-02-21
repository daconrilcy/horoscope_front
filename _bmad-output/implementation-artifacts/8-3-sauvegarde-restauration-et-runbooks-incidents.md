# Story 8.3: Sauvegarde/restauration et runbooks incidents

Status: done
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an operations user,  
I want valider des procedures de backup/restore et de gestion incident,  
so that la recuperation soit maitrisee en cas de panne.

## Acceptance Criteria

1. Given un environnement de production cible, when un exercice de restauration est execute, then la restauration des donnees critiques est verifiee.
2. Given les scenarios d incidents majeurs, when la documentation ops est consultee, then un runbook incident actionnable est disponible.

## Tasks / Subtasks

- [x] Definir le perimetre backup/restore des donnees critiques (AC: 1)
  - [x] Identifier les assets critiques: PostgreSQL, configurations runtime, secrets references, artefacts applicatifs
  - [x] Definir les objectifs RPO/RTO initiaux et hypotheses d exploitation
  - [x] Formaliser les formats de sauvegarde et conventions de nommage/version
- [x] Implementer les scripts de sauvegarde (AC: 1)
  - [x] Ajouter un script backup PostgreSQL utilisable en local/ops (`scripts/backup-db.ps1`)
  - [x] Ajouter un script backup compose (volumes/fichiers critiques) si necessaire
  - [x] Verifier l integrite minimale des archives generees
- [x] Implementer les scripts de restauration (AC: 1)
  - [x] Ajouter un script restore PostgreSQL (`scripts/restore-db.ps1`)
  - [x] Ajouter des garde-fous (confirmation explicite, validations pre-restore)
  - [x] Verifier la remise en service applicative apres restore
- [x] Documenter les runbooks incidents majeurs (AC: 2)
  - [x] Incident DB indisponible / corruption logique
  - [x] Incident backend non demarrable
  - [x] Incident frontend inaccessible
  - [x] Incident credentials/token invalides en masse
- [x] Valider les scenarios de test de recuperation (AC: 1, 2)
  - [x] Simuler un scenario restore complet et verifier KPI minimum de reprise
  - [x] Documenter les ecarts constates et actions correctives
  - [x] Ajouter checklist de verification post-incident

## Dev Notes

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 8, Story 8.3)
- Contexte: suite de 8-1 (quality gates) et 8-2 (observabilite), focus resilience operations.
- Contraintes explicites connues:
  - Backend Python avec venv obligatoire pour commandes Python.
  - Deploiement cible initial: Docker Compose single host.
  - Observabilite deja en place pour confirmer etat post-restore.

### Technical Requirements

- Backup/restore testables sur environnement local representatif.
- Procedure deterministic et reproductible.
- Validation post-restore obligatoire (health backend + endpoints critiques + checks metier minimaux).
- Runbooks actionnables: etapes, prerequis, commandes, points de verification, rollback.

### Architecture Compliance

- Respecter la structure monorepo existante (`backend/`, `frontend/`, `scripts/`).
- Ne pas contourner Alembic/SQLAlchemy pour etat schema.
- Rester compatible Docker Compose single host.

### Library / Framework Requirements

- Backend: Python 3.13, PostgreSQL, Alembic.
- Infra: Docker Compose.
- Scripting ops: PowerShell (Windows cible).

### File Structure Requirements

- Cibles probables:
  - `scripts/backup-db.ps1`
  - `scripts/restore-db.ps1`
  - `scripts/backup-validate.ps1` (optionnel)
  - `backend/README.md` (section backup/restore)
  - `_bmad-output/planning-artifacts/` (runbooks incidents)

### Testing Requirements

- Verifier au moins:
  - un backup complet reussi
  - un restore complet reussi
  - application operationnelle apres restore
  - documentation runbook exploitable par un ops non auteur

### Previous Story Intelligence

- 8-1 a formalise les quality gates predeploy.
- 8-2 a ajoute la couche observabilite operationnelle et alertes.
- 8-3 doit reutiliser ces briques pour valider la reprise en condition degradee.

### Git Intelligence Summary

- Projet en phase de durcissement post-MVP.
- Priorite immediate: fiabilite de recuperation avant tests de charge (8-4).

### Project Context Reference

- Instructions de travail: `AGENTS.md` (venv obligatoire, lint/tests avant conclusion, stack imposee).
- Change proposal approuve: `_bmad-output/planning-artifacts/sprint-change-proposal-2026-02-20.md`.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 8, Story 8.3)
- `_bmad-output/planning-artifacts/architecture.md` (deploiement et operations)
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

- Story creee pour couvrir resilience operationnelle (backup/restore + runbooks incidents).
- Taches structurees pour execution dev + verification code-review.
- Scripts de backup/restore/validation implementes pour SQLite et PostgreSQL avec metadata SHA256.
- Runbook ops ajoute avec procedures de reprise et checklist post-incident.
- Durcissement complete: metadata signee HMAC (`BACKUP_METADATA_HMAC_KEY`) et validation obligatoire.
- Backup et restore des assets runtime critiques ajoutes (archive runtime + restauration optionnelle).
- Restore PostgreSQL durci avec snapshot pre-restore systematique.
- Verification post-restore applicative ajoutee via healthcheck HTTP optionnel.
- Tests d integration scripts renforces et passants.

### Findings Addressed

- [HIGH] AC1 completee avec backup runtime (`backups/runtime`) + restauration runtime optionnelle.
- [HIGH] Remise en service post-restore verifiable via `-PostRestoreHealthUrl` + test dedie.
- [MEDIUM] Metadata d integrite renforcee avec signature HMAC verifiee.
- [MEDIUM] Garde-fou PostgreSQL ajoute: snapshot pre-restore automatique.

### File List

- `_bmad-output/implementation-artifacts/8-3-sauvegarde-restauration-et-runbooks-incidents.md`
- `_bmad-output/planning-artifacts/ops-backup-restore-runbook.md`
- `scripts/backup-db.ps1`
- `scripts/backup-validate.ps1`
- `scripts/restore-db.ps1`
- `backend/app/tests/integration/test_backup_restore_scripts.py`
- `backend/README.md`
