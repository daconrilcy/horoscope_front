# Story 11.3: Instrumentation des experiments packaging/pricing

Status: review
<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a growth stakeholder,  
I want instrumenter les experiments d offres et pricing,  
so that les decisions commerciales reposent sur des donnees fiables.

## Acceptance Criteria

1. Given plusieurs variantes d offres activables, when les utilisateurs interagissent avec ces offres, then les KPI conversion/retention/revenu sont traces par variante.
2. Given les resultats d experimentation, when les stakeholders consultent les donnees, then les resultats sont exploitables pour arbitrage produit.

## Tasks / Subtasks

- [x] Cadrer le plan d experimentation packaging/pricing et les variants (AC: 1, 2)
  - [x] Definir les variants (plan, prix, limites, messaging) et leur identifiant stable
  - [x] Definir les populations ciblees et regles d affectation
  - [x] Definir les fenetres d activation/deactivation et garde-fous
- [x] Ajouter l instrumentation backend des evenements business critiques (AC: 1)
  - [x] Tracer les evenements d exposition d offre par variante
  - [x] Tracer les evenements de conversion (checkout/retry/plan-change) avec contexte variante
  - [x] Tracer les evenements de retention/usage pertinents relies a l offre
- [x] Garantir la qualite et la coherences des dimensions analytics (AC: 1, 2)
  - [x] Standardiser le schema d evenement (`event_name`, `event_version`, `variant_id`, `user_segment`, `timestamp`)
  - [x] Assurer correlation `request_id`/`user_id`/`plan_code` selon regles privacy
  - [x] Ajouter validations pour rejeter les payloads incomplets/invalides
- [x] Exposer une vue de synthese exploitable pour arbitrage (AC: 2)
  - [x] Produire des agregats par variante (conversion, revenu, retention)
  - [x] Ajouter filtres temporels et segmentation minimale
  - [x] Rendre visibles marges d erreur/insuffisance d echantillon si applicable
- [x] Ajouter garde-fous ops et rollback experiment (AC: 2)
  - [x] Ajouter kill-switch/feature-flag pour arret immediat d un variant
  - [x] Journaliser les activations/desactivations de variants
  - [x] Documenter procedure de rollback et criteres d arret
- [x] Couvrir par tests et quality checks (AC: 1, 2)
  - [x] Tests unitaires instrumentation/evenements/agregation
  - [x] Tests integration API et flux critiques pricing
  - [x] Verification lint/tests/scripts qualite projet applicables

## Dev Notes

- Story source: `_bmad-output/planning-artifacts/epics.md` (Epic 11, Story 11.3).
- Contexte: post-MVP, orientee mesure fiable de l impact business des variants d offres.
- Dependances directes:
  - `4-1-souscription-au-plan-payant-d-entree.md`
  - `4-2-quotas-journaliers-et-suivi-de-consommation.md`
  - `4-3-upgrade-modification-de-plan.md`
  - `7-5-facturation-hybride-fixe-volume.md`
  - `11-1-raffinement-multi-persona-astrologue.md`

### Technical Requirements

- Tracer les KPI business par variante sans casser les flux de facturation existants.
- Garantir la qualite des donnees collectees (schema stable + validations).
- Fournir une sortie exploitable pour arbitrage produit.

### Architecture Compliance

- Respecter la separation backend `api/core/domain/services/infra`.
- Reutiliser les conventions d observabilite/evenement existantes.
- Conserver les formats d erreurs et structures de reponses standardisees.

### Library / Framework Requirements

- Backend: FastAPI, SQLAlchemy, Pydantic.
- Frontend: React + TypeScript (si exposition UI de synthese/controle requise).
- Tests: Pytest backend, Vitest frontend.

### File Structure Requirements

- Cibles probables backend:
  - `backend/app/services/` (instrumentation et agregation)
  - `backend/app/api/v1/routers/` (endpoints ops/analytics si necessaires)
  - `backend/app/infra/db/models/` (eventuelles tables de tracking)
  - `backend/migrations/versions/` (si evolution schema)
  - `backend/app/tests/`
- Cibles probables frontend:
  - `frontend/src/api/`
  - `frontend/src/components/` ou `frontend/src/pages/`
  - `frontend/src/tests/`

### Testing Requirements

- Verifier:
  - instrumentation correcte des evenements par variante,
  - exactitude des agregats conversion/revenu/retention,
  - non-regression sur flux billing existants,
  - exploitabilite operationnelle des resultats.

### Previous Story Intelligence

- Epic 4 a etabli les parcours billing B2C.
- Epic 7.5 a etabli la facturation hybride B2B.
- Epic 10 a renforce observabilite/performance pour pilotage ops.

### Git Intelligence Summary

- Sequence recommandee: schema evenement -> instrumentation -> agregation -> exposition -> tests.
- Eviter les changements hors perimetre pricing/experimentation.

### Project Context Reference

- `AGENTS.md`: venv obligatoire, deltas minimaux, tests/lint obligatoires.

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 11, Story 11.3)
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/implementation-artifacts/4-1-souscription-au-plan-payant-d-entree.md`
- `_bmad-output/implementation-artifacts/4-2-quotas-journaliers-et-suivi-de-consommation.md`
- `_bmad-output/implementation-artifacts/4-3-upgrade-modification-de-plan.md`
- `_bmad-output/implementation-artifacts/7-5-facturation-hybride-fixe-volume.md`
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

- Story 11.3 implementee et passee en `review`.
- Ajout du service `PricingExperimentService` avec schema evenement versionne (`event_version=1.0`) et validation des payloads.
- Instrumentation pricing ajoutee sur les flux billing:
  - exposition offre (checkout/retry/plan-change),
  - conversion par type (`checkout`, `retry`, `plan_change`) et statut,
  - revenu en cents par variante,
  - retention/usage sur les vues subscription/quota.
- Ajout d un kill-switch via configuration (`PRICING_EXPERIMENT_ENABLED`) et garde-fou d echantillon (`PRICING_EXPERIMENT_MIN_SAMPLE_SIZE`).
- Ajout d un endpoint ops de synthese: `GET /v1/ops/monitoring/pricing-experiments-kpis`.
- Agregats exposes par variante: `exposures_total`, `conversions_total`, `conversion_rate`, `retention_events_total`, `revenue_cents_total`, `avg_revenue_per_conversion_cents`, `sample_size_is_low`.
- Validation locale executee dans le venv:
  - `ruff check ...` (fichiers modifies)
  - `pytest -q backend/app/tests/unit/test_pricing_experiment_service.py backend/app/tests/unit/test_ops_monitoring_service.py backend/app/tests/integration/test_ops_monitoring_api.py backend/app/tests/integration/test_billing_api.py`
  - Resultat: `36 passed`.

### File List

- `_bmad-output/implementation-artifacts/11-3-instrumentation-des-experiments-packaging-pricing.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/core/config.py`
- `backend/app/services/pricing_experiment_service.py`
- `backend/app/services/ops_monitoring_service.py`
- `backend/app/api/v1/routers/billing.py`
- `backend/app/api/v1/routers/ops_monitoring.py`
- `backend/app/main.py`
- `backend/app/tests/unit/test_pricing_experiment_service.py`
- `backend/app/tests/unit/test_ops_monitoring_service.py`
- `backend/app/tests/integration/test_ops_monitoring_api.py`
- `backend/app/tests/integration/test_billing_api.py`
- `docs/pricing-experiment-rollback.md`
