<!-- Rapport d'audit CONDAMAD du domaine prediction. -->

# Audit Report - `backend/app/prediction`

## Scope

- Target domain: `backend/app/prediction`
- Archetypes used: legacy-surface-audit, dependency-direction-audit, service-boundary-audit, domain-purity-audit
- Mode: read-only for application code
- Output folder: `_condamad/audits/prediction/2026-05-03-2214`

## Expected Responsibility

Le dossier audite ne doit pas rester un package racine sous `backend/app`. Les responsabilites doivent converger vers les owners deja presents:

- `api`: adaptateurs HTTP et contrats exposes si necessaire.
- `infra`: DB, repositories, modeles, clients externes et persistence.
- `domain`: calcul pur, invariants, taxonomies et objets metier.
- racine/app services: orchestration applicative dans `services`.
- `ops`: scripts, jobs, bootstrap, seeds et outillage operationnel.

## Current State

`backend/app/prediction` contient 40 fichiers Python et 16 templates editoriaux. Les fichiers les plus references sont `schemas.py`, `context_loader.py`, `public_projection.py`, `persisted_snapshot.py`, `persistence_service.py` et `engine_orchestrator.py` (E-004).

Les fichiers reellement canoniques aujourd'hui sont:

| Current file(s) | Canonical role today | Target owner recommended |
|---|---|---|
| `aggregator.py`, `temporal_kernel.py`, `temporal_sampler.py`, `event_detector.py`, `transit_signal_builder.py`, `intraday_activation_builder.py`, `impulse_signal_builder.py`, `contribution_calculator.py`, `domain_router.py`, `natal_sensitivity.py`, `regime_segmenter.py`, `turning_point_detector.py`, `decision_window_builder.py`, `calibrator.py`, `relative_scoring_calculator.py` | Calcul prediction et scoring. | `backend/app/domain/prediction` si le choix produit confirme que ce moteur est du domaine pur. |
| `schemas.py`, `persisted_snapshot.py`, `persisted_baseline.py`, `persisted_relative_score.py`, `input_hash.py`, `exceptions.py` | Contrats internes et read models. | Split: contrats purs vers `domain/prediction`; read models DB vers `infra/db` ou `services/prediction/types`. |
| `engine_orchestrator.py` | Orchestration du moteur et assemblage V2/V3. | `services/prediction` pour orchestration; algorithmes purs vers `domain/prediction`. |
| `context_loader.py` | Chargement contexte DB. | `infra/db` adapter + interface appelee par `services/prediction`. |
| `persistence_service.py` | Persistence des sorties moteur. | `infra/db`/repository adapter ou `services/prediction` selon la convention choisie. |
| `public_projection.py`, `public_astro_daily_events.py`, `public_astro_vocabulary.py`, `public_domain_taxonomy.py`, `public_label_catalog.py`, `public_score_mapper.py` | Projection publique V4 et taxonomies publiques. | Taxonomies pures en `domain`; payload/API contracts en `services/api_contracts`; assemblage en `services/prediction`. |
| `editorial_builder.py`, `editorial_service.py`, `editorial_template_engine.py`, `editorial_templates/**` | Editorial deterministe localise. | `services/prediction/editorial` ou `domain/prediction/editorial` pour templates purs; pas a la racine `app.prediction`. |
| `astrologer_prompt_builder.py` | Payload factuel pour narration horoscope. | `services/llm_generation/horoscope_daily` ou sous-namespace LLM deja canonique. |
| `astro_calculator.py`, `enriched_astro_events_builder.py` | Calcul astro Swiss Ephemeris. | `domain/astrology` ou `domain/prediction/astrology` avec dependance native assumee. |

Fichiers legacy/obsolete identifies:

- Obsolete supprime: `backend/app/prediction/llm_narrator.py`, deja absent et protege par RG-016/RG-017 (E-009, E-011).
- Legacy actif: `EngineOutput`, `PersistablePredictionBundle.to_engine_output`, aliases `V3DailyMetrics.intensity_20/confidence_20`, `TimeBlock`, `_build_v3_legacy_core`, argument `engine_output` de `PredictionPersistenceService.save`, payload public `categories` conserve pour retrocompatibilite (E-008).
- Legacy a classifier: fallbacks d'evenements, fallbacks de calibrage, compatibilites tests/fixtures et chemins `engine_output` dans projection publique.

## Findings Summary

| ID | Severity | Category | Summary |
|---|---|---|---|
| F-001 | High | boundary-violation | Package racine multi-couches. |
| F-002 | High | dependency-direction-violation | Dependances infra/runtime dans prediction. |
| F-003 | High | legacy-surface | Legacy restant hors `llm_narrator`. |
| F-004 | Medium | duplicate-responsibility | Projection publique proprietaire de trop de comportements. |
| F-005 | Medium | runtime-contract-drift | Bug probable `PublicAstroFoundationPolicy`. |
| F-006 | Medium | data-integrity-risk | Session DB partagee dans thread de calcul. |
| F-007 | Medium | missing-guard | Pas de guard anti-croissance pour `app.prediction`. |
| F-008 | Low | observability-gap | Trace IDs LLM generes localement dans projection. |

## Recommended Refactor Path

1. Ajouter une garde anti-croissance de `backend/app/prediction` avant les deplacements.
2. Corriger le bug `PublicAstroFoundationPolicy` avec tests cibles.
3. Classer toutes les surfaces legacy restantes dans un registre.
4. Extraire `context_loader.py` et `persistence_service.py` vers infra/services.
5. Separer projection publique deterministe et enrichissement LLM.
6. Deplacer progressivement le moteur pur vers `domain/prediction`.
7. Remplacer les imports consommateurs, puis supprimer le package racine `app.prediction`.

## Evidence and Outputs

- Evidence log: `01-evidence-log.md`
- Finding register: `02-finding-register.md`
- Story candidates: `03-story-candidates.md`
- Risk matrix: `04-risk-matrix.md`
- Executive summary: `05-executive-summary.md`
