# Story 41.8: Découpage du service applicatif daily prediction

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a équipe backend maintenant le cas d’usage horoscope du jour,
I want découper `DailyPredictionService` en responsabilités applicatives explicites,
so that la résolution de requête, la réutilisation, l’exécution moteur et le fallback deviennent lisibles, testables et modifiables sans effet de bord.

## Acceptance Criteria

1. `DailyPredictionService` devient une façade orchestratrice mince:
   - résolution de la requête
   - décision de réutilisation
   - exécution du calcul
   - persistance
   - fallback sur dernier run disponible si applicable

2. La logique de résolution des entrées est extraite dans un composant dédié:
   - profil utilisateur
   - timezone
   - localisation
   - date locale
   - version de référence / ruleset
   - thème natal
   - construction de `EngineInput`
   - retour d’un objet explicite de type `ResolvedPredictionRequest` ou équivalent

3. La politique de réutilisation des runs est isolée dans un composant dédié:
   - détection d’un run réutilisable par hash
   - gestion des drapeaux `read_only`, `compute_if_missing`, `force_recompute`
   - décision de recalcul si run stale/incomplet selon les règles existantes
   - retour d’un objet explicite de type `ReuseDecision` ou équivalent

4. L’exécution moteur et la gestion de timeout sont encapsulées dans un composant dédié:
   - l’orchestrateur n’est plus appelé directement depuis le service principal
   - les contraintes documentées de thread/session SQLAlchemy restent explicites
   - le comportement fonctionnel reste inchangé
   - le résultat d’exécution est porté par un objet explicite de type `ComputeResult` ou équivalent

5. La politique de fallback est isolée:
   - fallback vers le dernier run disponible avant la date demandée uniquement dans les cas actuellement autorisés
   - aucune confusion avec la réutilisation technique par hash
   - la décision est portée par un objet explicite de type `FallbackDecision` ou équivalent

6. Des tests de service couvrent les chemins principaux:
   - réutilisation nominale
   - recalcul nominal
   - fallback après échec moteur/persistance

## Tasks / Subtasks

- [ ] Task 1: Extraire le resolver de requête (AC: 1, 2)
  - [ ] Créer `backend/app/services/prediction_request_resolver.py`
  - [ ] Migrer les helpers `_resolve_profile`, `_resolve_timezone`, `_resolve_location`, `_resolve_date`, `_resolve_natal_chart`
  - [ ] Produire un objet de décision/entrée explicite exploitable par le service principal

- [ ] Task 2: Extraire la politique de réutilisation (AC: 1, 3)
  - [ ] Créer `backend/app/services/prediction_run_reuse_policy.py`
  - [ ] Encapsuler les règles actuelles de stale/incomplet et de réutilisation par hash
  - [ ] Séparer clairement décision de réutilisation et lecture de fallback
  - [ ] Retourner un `ReuseDecision` explicite plutôt que des booléens implicites

- [ ] Task 3: Extraire l’exécution moteur (AC: 1, 4)
  - [ ] Créer `backend/app/services/prediction_compute_runner.py`
  - [ ] Déplacer `_compute_with_timeout()` et l’orchestration d’exécution associée
  - [ ] Documenter les limites connues de thread safety
  - [ ] Retourner un `ComputeResult` explicite

- [ ] Task 4: Extraire la politique de fallback (AC: 1, 5)
  - [ ] Créer `backend/app/services/prediction_fallback_policy.py`
  - [ ] Déplacer la logique de récupération du dernier run exploitable après échec
  - [ ] Préserver la sémantique métier existante
  - [ ] Retourner un `FallbackDecision` explicite

- [ ] Task 5: Réduire `DailyPredictionService` à une façade lisible et couverte par tests (AC: 1, 6)
  - [ ] Simplifier `get_or_compute()`
  - [ ] Mettre à jour les tests de service/intégration
  - [ ] Vérifier la non-régression de `/v1/predictions/daily`

## Dev Notes

- Cette story ne doit pas changer le contrat HTTP ni la sémantique produit des réponses.
- Le but est de rendre explicites des responsabilités déjà présentes de manière implicite dans la classe actuelle.
- Le découpage doit éviter les “classes fourre-tout”; chaque composant doit rester petit, testable et sans dépendances inutiles.
- Le fallback n’est pas une forme de réutilisation par hash: ces deux concepts doivent être distincts dans le code.

### Project Structure Notes

- Fichiers backend principaux:
  - `backend/app/services/daily_prediction_service.py`
  - `backend/app/services/prediction_request_resolver.py` (nouveau)
  - `backend/app/services/prediction_run_reuse_policy.py` (nouveau)
  - `backend/app/services/prediction_compute_runner.py` (nouveau)
  - `backend/app/services/prediction_fallback_policy.py` (nouveau)

### Technical Requirements

- Préserver le comportement de `get_or_compute()` à contrat constant.
- Garder la gestion du timeout et les limitations de session DB explicites.
- Les objets échangés entre composants doivent être typés et explicites autant que possible.
- Éviter les booléens ou tuples ad hoc entre composants extraits; préférer des objets de décision nommés.
- Éviter toute dépendance circulaire entre service, policies et couche prediction.

### Architecture Compliance

- Cette story prépare explicitement l’architecture cible “service applicatif mince + composants spécialisés”.
- Les composants créés restent dans `app/services/`, pas dans le routeur ni dans la couche UI.
- Le moteur de prédiction reste la source de calcul; le service n’en duplique pas la logique.

### Library / Framework Requirements

- Réutiliser les dépendances backend existantes uniquement.
- Aucun changement de stack ou de framework.

### File Structure Requirements

- Les nouveaux composants applicatifs doivent vivre dans `backend/app/services/`.
- Les tests doivent compléter les suites de service/intégration existantes sans recréer un harness parallèle.

### Testing Requirements

- Ajouter des tests sur:
  - réutilisation par hash
  - recalcul forcé
  - fallback après exception de calcul
- Exécuter `ruff check` et `pytest` dans le venv.

### Previous Story Intelligence

- 36.1 a introduit le service applicatif daily prediction; cette story en est le refactor structurel, sans re-spécifier le produit. [Source: _bmad-output/implementation-artifacts/36-1-service-applicatif-daily-prediction.md]
- Les évolutions 41.4 à 41.6 ont accru la complexité de la projection publique; maintenir un service monolithique augmente désormais le risque de régression. [Source: _bmad-output/implementation-artifacts/41-4-contrat-api-et-ui-centres-aide-decision-intraday.md]

### Git Intelligence Summary

- `9921bdc Stabilize daily prediction dashboard flow` et `3448e68 feat(daily): align agenda and turning points semantics` indiquent que la stabilisation récente a surtout porté sur le comportement; cette story vise la maintenabilité.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.
- Les règles actives du repo viennent de `AGENTS.md` et des artefacts BMAD existants.

### References

- [Source: user refactor plan 2026-03-10 — Phase 2 découpage de DailyPredictionService]
- [Source: backend/app/services/daily_prediction_service.py]
- [Source: backend/app/api/v1/routers/predictions.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story créée à partir du plan de refacto Epic 41 fourni le 2026-03-10.

### Completion Notes List

- Story prête pour un refactor comportementalement neutre du service applicatif horoscope du jour.

### File List

- `_bmad-output/implementation-artifacts/41-8-decoupage-service-applicatif-daily-prediction.md`
