# Story 41.2 : Propager l'influence temporelle des événements sur de vraies fenêtres utiles

Status: done

## Story

En tant que concepteur du moteur de prédiction,
je veux qu'un événement influence une fenêtre temporelle montante, culminante puis descendante au lieu d'un unique bucket de 15 minutes,
afin que la timeline intraday reflète des créneaux réellement exploitables par l'utilisateur.

## Acceptance Criteria

### AC1 — Un événement ne vit plus sur un seul step

- [x] Les événements significatifs influencent plusieurs steps autour de leur instant central
- [x] Le moteur supporte au minimum un profil "montée / pic / décroissance" déterministe
- [x] Le comportement reste testable sans aléa

### AC2 — La durée d'influence dépend du type d'événement

- [x] Les aspects exacts influencent une fenêtre plus large que `planetary_hour_change`
- [x] Les événements secondaires ont un rayon d'influence plus court et/ou une amplitude réduite
- [x] La logique est paramétrable côté ruleset ou clairement encapsulée

### AC3 — Les signaux intraday deviennent lisibles

- [x] Les `notes_by_step` montrent de vraies séquences de montée / plateau / retombée pour les événements structurants
- [x] La timeline n'est plus dominée par des impulsions ponctuelles isolées

### AC4 — L'explicabilité reste intacte

- [x] Les contributions propagées restent retraçables au driver source
- [x] Le mode debug permet toujours de comprendre pourquoi un step a bougé

### AC5 — Non-régression moteur

- [x] Les suites ciblées du moteur restent vertes
- [x] Des tests unitaires couvrent le kernel temporel et ses cas limites

## Tasks / Subtasks

### T1 — Concevoir un modèle d'influence temporelle

- [x] Définir un profil d'influence par famille d'événements
- [x] Choisir comment répartir amplitude et durée sur les steps voisins
- [x] Documenter l'approche retenue

### T2 — Mettre à jour l'orchestrateur

- [x] Remplacer l'affectation au seul `nearest_step_index`
- [x] Propager les contributions sur plusieurs steps
- [x] Préserver la structure `events_by_step` / `contributions_by_step`

### T3 — Garder la compatibilité avec calibration et explainability

- [x] Vérifier l'impact sur `TemporalAggregator`, `PercentileCalibrator` et `ExplainabilityBuilder`
- [x] Ajuster les tests si nécessaire

### T4 — Tests

- [x] Ajouter des tests sur l'étalement temporel
- [x] Vérifier l'effet attendu sur les signaux par step

## Dev Notes

- Le problème audit actuel est l'affectation d'un événement à un unique step via `nearest_step_index`, ce qui produit un signal trop impulsionnel pour une lecture produit.
- Cette story doit rester backend-only et ne pas changer encore le contrat frontend final.

### Fichiers probables à toucher

- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/prediction/contribution_calculator.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
- `backend/app/tests/unit/test_daily_prediction_service.py`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

Aucun blocage notable. Le seul ajustement a été la mise à jour du test `test_run_integrates_prediction_scoring_pipeline_with_lowercase_reference_codes` : l'étalement des contributions lisse les notes_by_step sur la mini-grille 4-steps du test, supprimant le TP et réduisant le nombre de blocs à 1 (comportement correct et attendu).

### Completion Notes List

- **T1** : Créé `backend/app/prediction/temporal_kernel.py` — kernel triangulaire normalisé avec `_FAMILY_HALF_WIDTH` mappant chaque type d'événement de la taxonomie V2 à un rayon en steps (half-width). Profil : `weight(d) = max(0, 1 - d/(hw+1))`, normalisé pour que ΣW = 1.0 (conservation d'énergie).
- **T2** : Modifié `_build_prediction_outputs` dans `engine_orchestrator.py` — `contribution_totals_by_step` utilise maintenant `spread_event_weights()` ; `events_by_step` et `contributions_by_step` restent au step central (traceabilité).
- **T3** : `TemporalAggregator`, `ExplainabilityBuilder` et `PercentileCalibrator` : aucune modification nécessaire — structures identiques, la normalisation préserve les totaux journaliers.
- **T4** : 20 tests unitaires dans `test_temporal_kernel.py` (normalisation, fenêtres par type, profil montée/descente, bords, conservation d'énergie) + ajustement du test d'orchestrateur existant.

### File List

- `backend/app/prediction/temporal_kernel.py` (nouveau)
- `backend/app/prediction/engine_orchestrator.py` (modifié)
- `backend/app/tests/unit/test_temporal_kernel.py` (nouveau)
- `backend/app/tests/unit/test_engine_orchestrator.py` (modifié)

## Change Log

- 2026-03-09 : Story créée à partir de l'audit intraday produit/backend.
- 2026-03-09 : Implémentation complète — kernel temporel triangulaire normalisé + propagation multi-steps dans l'orchestrateur + 20 tests unitaires. (claude-sonnet-4-6)
