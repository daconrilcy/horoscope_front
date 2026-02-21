# Story 9.3: Preuves operationnelles RGPD (export/suppression/audit)

Status: review
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a compliance stakeholder,  
I want produire des preuves de conformite RGPD sur les flux implementes,  
so that la conformite puisse etre demontree en audit.

## Acceptance Criteria

1. Given les parcours privacy et audit actifs, when un dossier de preuve est genere, then il inclut export, suppression, et traces d audit associees.
2. Given le processus de collecte defini, when il est rejoue a l identique, then la collecte est reproductible.

## Tasks / Subtasks

- [x] Definir le perimetre exact des preuves RGPD attendues (AC: 1)
  - [x] Lister les flux cibles: export des donnees, suppression des donnees, journalisation des actions sensibles
  - [x] Definir les evidences minimales exigibles par flux (requete, execution, statut, horodatage, acteur)
  - [x] Documenter les preconditions et limites (donnees minimales, roles requis, retention)
- [x] Produire un dossier de preuve standardise et horodate (AC: 1)
  - [x] Generer un artefact consolide (format machine-readable + format lisible ops/compliance)
  - [x] Inclure les preuves export/suppression liees a un meme utilisateur de test
  - [x] Inclure les traces d audit correlees (request_id / actor / action / resultat)
- [x] Garantir la reproductibilite du processus de collecte (AC: 2)
  - [x] Definir un script/runbook unique de generation du dossier de preuve
  - [x] Rendre le process idempotent (relance sans divergence de structure)
  - [x] Verifier la reproductibilite sur au moins deux executions successives
- [x] Integrer les preuves dans le workflow qualite operationnel (AC: 1, 2)
  - [x] Ajouter verification minimale dans `predeploy-check` ou runbook d exploitation
  - [x] Definir la localisation/versionnage des artefacts de preuve
  - [x] Documenter la procedure de consultation pour support/ops/compliance
- [x] Couvrir par tests et non-regressions (AC: 1, 2)
  - [x] Ajouter tests d integration pour valider la presence des trois volets (export, suppression, audit)
  - [x] Ajouter test de reproductibilite (meme structure attendue sur executions repetees)
  - [x] Verifier les cas d erreur explicites (donnees absentes, droits insuffisants, preuve partielle)

## Dev Notes

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 9, Story 9.3).
- Story precedente directe: `9-2-pack-de-verification-securite-sast-deps-pentest.md` (en review), qui a deja consolide les mecanismes de verification securite.
- Dependances fonctionnelles deja implementees a exploiter:
  - `5-1-export-et-suppression-des-donnees-personnelles.md`
  - `5-2-anonymisation-llm-et-audit-des-actions-sensibles.md`

### Technical Requirements

- Le dossier de preuve doit couvrir explicitement:
  - preuve d export de donnees,
  - preuve de suppression de donnees,
  - preuve d audit associee.
- La collecte doit etre automatisable et rejouable sans intervention manuelle lourde.
- Les preuves ne doivent pas exposer de donnees sensibles en clair hors necessite d audit.

### Architecture Compliance

- Respecter les patterns API et erreurs standardises (`/v1`, modele `error.code/message/details/request_id`).
- Reutiliser les services privacy/audit existants au lieu de duplicer la logique.
- Conserver la separation de responsabilites `api/core/domain/services/infra`.

### Library / Framework Requirements

- Backend: FastAPI + Pydantic + SQLAlchemy + Alembic (conformes architecture).
- Scripting ops: PowerShell dans `scripts/` pour alignement avec les gates existants.
- Aucun nouvel outil externe obligatoire si les composants actuels couvrent le besoin.

### File Structure Requirements

- Cibles probables:
  - `backend/app/services/privacy_service.py`
  - `backend/app/services/audit_service.py`
  - `backend/app/api/v1/routers/privacy.py`
  - `scripts/` (script de generation dossier de preuve RGPD)
  - `artifacts/` (sortie des preuves operationnelles)
  - `backend/app/tests/integration/` (tests de dossier de preuve et reproductibilite)
  - `backend/README.md` ou runbook dedie (procedure d execution)

### Testing Requirements

- Verifier au minimum:
  - generation d un dossier contenant export + suppression + audit,
  - reproductibilite du dossier sur relance,
  - gestion des erreurs coherente quand un des volets est indisponible.

### Previous Story Intelligence

- 9.1 a durci la gestion des secrets et la traçabilite des actions sensibles.
- 9.2 a introduit la verification securite standardisee et les artefacts de remediation.
- Cette story doit capitaliser sur ces fondations pour produire des preuves conformite orientees audit.

### Git Intelligence Summary

- Le lot Epic 9 est traite incrementalement en hardening post-MVP.
- Les derniers changements ont renforce scripts de gate, securite et auditabilite; la story 9.3 doit rester dans cette logique incrementaliste.

### Latest Tech Information

- Pas de dependance framework nouvelle imposee par la story.
- Priorite a la stabilite/reproductibilite du processus de preuve sur la stack actuelle.

### Project Context Reference

- `AGENTS.md` impose:
  - activation du venv pour toute commande Python,
  - lint/tests obligatoires,
  - verification locale avant conclusion.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 9, Story 9.3)
- `_bmad-output/planning-artifacts/prd.md` (FR29, FR30, FR32, FR33; NFR7, NFR8)
- `_bmad-output/planning-artifacts/architecture.md` (Security & Privacy, Process Patterns, Error Handling)
- `_bmad-output/implementation-artifacts/5-1-export-et-suppression-des-donnees-personnelles.md`
- `_bmad-output/implementation-artifacts/5-2-anonymisation-llm-et-audit-des-actions-sensibles.md`
- `_bmad-output/implementation-artifacts/9-1-durcissement-de-la-gestion-des-secrets-et-rotation.md`
- `_bmad-output/implementation-artifacts/9-2-pack-de-verification-securite-sast-deps-pentest.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- `_bmad/bmm/workflows/4-implementation/create-story/workflow.yaml`
- `_bmad/bmm/workflows/4-implementation/create-story/instructions.xml`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/prd.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Completion Notes List

- Ajout d un endpoint ops/support `GET /v1/privacy/evidence/{target_user_id}` qui consolide preuves export/suppression/audit.
- Ajout d un service de consolidation `PrivacyService.get_compliance_evidence` avec validation d incomplétude explicite (`privacy_evidence_incomplete`).
- Ajout d un script operationnel reproductible `scripts/generate-rgpd-evidence.ps1` pour generer un dossier JSON + Markdown.
- Ajout d une couverture integration dediee (succes, reproductibilite, erreurs) via `test_privacy_evidence_api.py`.
- Ajout d un runbook d exploitation RGPD et documentation backend associee.
- Validation complete via `quality-gate` (backend + frontend + securite): OK.

### File List

- `_bmad-output/implementation-artifacts/9-3-preuves-operationnelles-rgpd-export-suppression-audit.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/services/privacy_service.py`
- `backend/app/api/v1/routers/privacy.py`
- `backend/app/tests/integration/test_privacy_evidence_api.py`
- `scripts/generate-rgpd-evidence.ps1`
- `_bmad-output/planning-artifacts/rgpd-operational-evidence-runbook.md`
- `backend/README.md`
