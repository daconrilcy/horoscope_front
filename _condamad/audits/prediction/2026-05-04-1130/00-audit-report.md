<!-- Rapport d'audit CONDAMAD de recontrole du domaine prediction. -->

# Audit Report - `backend/app/prediction`

## Scope

- Target domain: `backend/app/prediction`
- Reference audit: `_condamad/audits/prediction/2026-05-03-2214`
- Archetypes used: legacy-surface-audit, dependency-direction-audit, service-boundary-audit, domain-purity-audit
- Mode: read-only for application code
- Output folder: `_condamad/audits/prediction/2026-05-04-1130`

## Expected Responsibility

Le dossier racine `backend/app/prediction` doit disparaitre a terme. Les responsabilites restantes doivent etre reparties uniquement dans les racines backend acceptees:

| Target root | Expected ownership for current prediction code |
|---|---|
| `backend/app/domain` | Calcul pur, dataclasses metier, scoring, temporalite, detection d'evenements, taxonomies deterministes et erreurs metier. |
| `backend/app/services` | Orchestration de cas d'usage, compute runner, reuse/fallback policies, assemblage applicatif et enrichissement public deterministe. |
| `backend/app/infra` | Repositories, modeles SQLAlchemy, adapters DB, DTO de persistence si leur forme est liee au stockage. |
| `backend/app/api` | Adaptateurs HTTP uniquement, sans dependance directe au namespace legacy `app.prediction` apres migration. |
| `backend/app/core` | Configuration, horloge, request/trace IDs, erreurs transverses. |
| `backend/app/ops` | Bootstrap, seed, generation QA/datasets et jobs operationnels. |

## Status of Previous Story Candidates

Les stories issues de l'audit precedent sont marquees `done` dans `_condamad/stories/story-status.md`:

- CS-006: namespace racine `app.prediction`.
- CS-007: extraction des dependances infra hors prediction.
- CS-008: classification/reduction des compatibilites legacy.
- CS-009: separation projection publique / enrichissement LLM.
- CS-010: correction `astro_foundation`.
- CS-011: session DB non partagee dans le calcul threade.
- CS-012: garde anti-croissance.
- CS-013: propagation request_id/trace_id.

Les tests cibles confirment ce statut: `40 passed` sur les guards prediction, compute runner, service prediction et `astro_foundation` (E-002). Les scans confirment aussi que les dependances infra interdites et le runtime LLM ne sont pas revenus sous `backend/app/prediction` (E-005, E-006, E-013).

## Current State

Le package `backend/app/prediction` existe toujours avec 39 fichiers Python et 16 templates editoriaux (E-003). Il est maintenant plus pur qu'au precedent audit: `context_loader.py`, `persistence_service.py` et l'ancien `engine_orchestrator.py` ne sont plus sous ce dossier, et aucun import SQLAlchemy/infra/API/LLM runtime interdit n'est detecte sous `backend/app/prediction`.

Le blocage restant est structurel:

- `backend/app/services/prediction/engine_orchestrator.py` importe encore massivement les modules `app.prediction.*` pour le moteur pur (E-007).
- Les routeurs `public/predictions.py` et `internal/llm/qa.py` importent directement `PersistedPredictionSnapshot` et `PublicPredictionAssembler` depuis `app.prediction` (E-008).
- Des repositories infra importent encore des DTO/read models depuis `app.prediction` (E-009).
- Il n'existe pas encore de `backend/app/domain/prediction` ni de `backend/app/infra/prediction` pour recevoir les responsabilites restantes (E-010).
- Les tests et guards pointent encore sur `app.prediction`; une suppression physique casserait la suite sans migration coordonnee des imports et des allowlists (E-011).

## Findings Summary

| ID | Severity | Category | Summary |
|---|---|---|---|
| F-001 | High | boundary-violation | Le namespace racine `backend/app/prediction` reste actif malgre la cible de suppression. |
| F-002 | High | missing-canonical-owner | Le moteur pur n'a pas encore d'owner canonique sous `backend/app/domain`. |
| F-003 | Medium | dependency-direction-violation | L'infra DB depend encore de DTO/read models situes dans `app.prediction`. |
| F-004 | Medium | boundary-violation | Les routeurs API importent encore des classes de projection et snapshots depuis `app.prediction`. |
| F-005 | Medium | missing-guard | Les guards actuels bloquent la croissance, mais pas encore l'extinction du dossier. |
| F-006 | Info | no-legacy-dry | Les corrections CS-006 a CS-013 sont confirmees par tests et scans cibles. |

## Deletion Path for `backend/app/prediction`

Ordre recommande pour supprimer le dossier sans facade de compatibilite:

1. Creer le package cible `backend/app/domain/prediction` et y migrer le moteur pur: `aggregator`, `temporal_*`, `event_detector`, `transit_signal_builder`, `intraday_activation_builder`, `impulse_signal_builder`, `contribution_calculator`, `domain_router`, `natal_sensitivity`, `regime_segmenter`, `turning_point_detector`, `decision_window_builder`, `calibrator`, `relative_scoring_calculator`, `schemas`, `context`, `category_codes`, `input_hash`, `exceptions`, `explainability`, `daily_prediction_evidence_builder`.
2. Migrer les calculs astrologiques purs vers `backend/app/domain/astrology` ou un sous-package `backend/app/domain/prediction/astrology`, en alignant avec le domaine astrology deja existant.
3. Migrer les DTO/read models de persistence: soit vers `backend/app/infra/db/repositories/prediction_schemas.py` si leur forme est DB-facing, soit vers `backend/app/domain/prediction` s'ils restent purs et consommes par les services.
4. Migrer la projection publique deterministe vers `backend/app/services/prediction/public_projection.py` ou `backend/app/services/api_contracts/public/predictions_projection.py`; les routeurs ne doivent plus importer `app.prediction`.
5. Migrer l'editorial deterministe et les templates vers `backend/app/services/prediction/editorial` ou `backend/app/domain/prediction/editorial` selon la decision d'ownership.
6. Migrer `astrologer_prompt_builder.py` vers `backend/app/services/llm_generation/horoscope_daily`, car il construit le payload factuel de narration.
7. Mettre a jour les tests, la garde `test_daily_prediction_guardrails.py` et l'allowlist CS-012 pour devenir une garde d'extinction: zero fichier sous `backend/app/prediction`, zero import `app.prediction`.
8. Supprimer `backend/app/prediction/__init__.py` et le dossier entier apres zero-hit repo-wide.

## Evidence and Outputs

- Evidence log: `01-evidence-log.md`
- Finding register: `02-finding-register.md`
- Story candidates: `03-story-candidates.md`
- Risk matrix: `04-risk-matrix.md`
- Executive summary: `05-executive-summary.md`
