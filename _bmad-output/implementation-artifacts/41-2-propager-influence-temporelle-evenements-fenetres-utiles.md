# Story 41.2 : Propager l'influence temporelle des événements sur de vraies fenêtres utiles

Status: backlog

## Story

En tant que concepteur du moteur de prédiction,
je veux qu'un événement influence une fenêtre temporelle montante, culminante puis descendante au lieu d'un unique bucket de 15 minutes,
afin que la timeline intraday reflète des créneaux réellement exploitables par l'utilisateur.

## Acceptance Criteria

### AC1 — Un événement ne vit plus sur un seul step

- [ ] Les événements significatifs influencent plusieurs steps autour de leur instant central
- [ ] Le moteur supporte au minimum un profil “montée / pic / décroissance” déterministe
- [ ] Le comportement reste testable sans aléa

### AC2 — La durée d'influence dépend du type d'événement

- [ ] Les aspects exacts influencent une fenêtre plus large que `planetary_hour_change`
- [ ] Les événements secondaires ont un rayon d'influence plus court et/ou une amplitude réduite
- [ ] La logique est paramétrable côté ruleset ou clairement encapsulée

### AC3 — Les signaux intraday deviennent lisibles

- [ ] Les `notes_by_step` montrent de vraies séquences de montée / plateau / retombée pour les événements structurants
- [ ] La timeline n'est plus dominée par des impulsions ponctuelles isolées

### AC4 — L'explicabilité reste intacte

- [ ] Les contributions propagées restent retraçables au driver source
- [ ] Le mode debug permet toujours de comprendre pourquoi un step a bougé

### AC5 — Non-régression moteur

- [ ] Les suites ciblées du moteur restent vertes
- [ ] Des tests unitaires couvrent le kernel temporel et ses cas limites

## Tasks / Subtasks

### T1 — Concevoir un modèle d'influence temporelle

- [ ] Définir un profil d'influence par famille d'événements
- [ ] Choisir comment répartir amplitude et durée sur les steps voisins
- [ ] Documenter l'approche retenue

### T2 — Mettre à jour l'orchestrateur

- [ ] Remplacer l'affectation au seul `nearest_step_index`
- [ ] Propager les contributions sur plusieurs steps
- [ ] Préserver la structure `events_by_step` / `contributions_by_step`

### T3 — Garder la compatibilité avec calibration et explainability

- [ ] Vérifier l'impact sur `TemporalAggregator`, `PercentileCalibrator` et `ExplainabilityBuilder`
- [ ] Ajuster les tests si nécessaire

### T4 — Tests

- [ ] Ajouter des tests sur l'étalement temporel
- [ ] Vérifier l'effet attendu sur les signaux par step

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

GPT-5 Codex

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2026-03-09 : Story créée à partir de l'audit intraday produit/backend.
