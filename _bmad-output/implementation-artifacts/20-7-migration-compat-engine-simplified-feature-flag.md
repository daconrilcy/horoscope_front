# Story 20.7: Migration/compat — SwissEph par défaut, simplified conservé sous feature flag

Status: done

## Title

Basculer la source de vérité sur SwissEph tout en conservant un mode comparaison dev-only avec le moteur simplified.

## Context

La migration doit rester maîtrisée: le moteur simplified reste utile pour debug/comparaison, sans être la vérité produit.

## Scope

- Définir stratégie de sélection moteur:
  - défaut `swisseph`
  - fallback ou override `simplified` via feature flag interne
- Ajouter un endpoint ou param interne dev-only pour comparer `simplified` vs `swisseph` sur un même input.
- Produire un diff structuré minimal (positions et maisons clés).
- Protéger la fonctionnalité de comparaison hors production.

## Out of scope

- Exposition publique grand public d'un mode multi-engine.
- Support long terme de plusieurs engines équivalents.

## Acceptance Criteria

1. **Given** la configuration par défaut **When** une requête natal est calculée **Then** `engine=swisseph` est utilisé comme source de vérité.
2. **Given** le feature flag de compat activé **When** une requête interne demande `simplified` **Then** le pipeline peut exécuter l'ancien moteur sans casser le contrat de réponse.
3. **Given** le mode comparaison dev-only **When** il est appelé **Then** la réponse contient un diff explicite `simplified_vs_swisseph` et n'est pas accessible en production.
4. **Given** SwissEph activé **When** l'API répond **Then** metadata indique toujours l'engine réellement utilisé.

## Technical Notes

- Restreindre l'accès compare via env + auth interne.
- Ajouter garde-fou pour empêcher activation en prod (`ENV=production`).
- Journaliser uniquement des écarts agrégés sans PII.

## Tests

- Tests unitaires sélection engine par config.
- Test d'intégration endpoint/param compare dev-only.
- Test de sécurité: compare inaccessible en production.

## Rollout/Feature flag

- `NATAL_ENGINE_DEFAULT=swisseph`.
- `NATAL_ENGINE_SIMPLIFIED_ENABLED=true` uniquement dev/staging.
- `NATAL_ENGINE_COMPARE_ENABLED=true` uniquement dev.

---

## Tasks / Subtasks

- [x] Task 1: Implémenter la stratégie de sélection engine configurable
  - [x] 1.1 Ajouter les flags `NATAL_ENGINE_DEFAULT`, `NATAL_ENGINE_SIMPLIFIED_ENABLED`, `NATAL_ENGINE_COMPARE_ENABLED` dans `Settings`.
  - [x] 1.2 Centraliser la résolution d’engine dans `NatalCalculationService`.
  - [x] 1.3 Basculer le comportement par défaut vers `swisseph` quand activé/configuré.
  - [x] 1.4 Conserver fallback `simplified` si SwissEph indisponible.

- [x] Task 2: Ajouter l’override interne `simplified` derrière feature flag
  - [x] 2.1 Étendre `NatalCalculationService.calculate(...)` avec `engine_override` + `internal_request`.
  - [x] 2.2 Bloquer `engine_override=simplified` hors appel interne, hors env non-prod, ou si flag désactivé.
  - [x] 2.3 Garantir un code d’erreur explicite (`natal_engine_override_forbidden`).

- [x] Task 3: Exposer un endpoint compare dev-only protégé
  - [x] 3.1 Ajouter `POST /v1/astrology-engine/natal/compare`.
  - [x] 3.2 Restreindre aux rôles `support|ops`.
  - [x] 3.3 Bloquer en production ou si compare flag désactivé (`endpoint_not_available`).
  - [x] 3.4 Retourner un diff structuré `simplified_vs_swisseph` (positions + maisons + summary).
  - [x] 3.5 Journaliser uniquement des écarts agrégés (pas de PII).

- [x] Task 4: Aligner la metadata engine réelle et tests
  - [x] 4.1 N’exposer `meta.ephemeris_path_version` que si `result.engine == "swisseph"`.
  - [x] 4.2 Ajouter/mettre à jour tests unitaires et intégration pour AC1–AC4.
  - [x] 4.3 Corriger les mocks de tests impactés par la signature de `calculate(...)`.

## Dev Notes

- La résolution d’engine est désormais centralisée dans `NatalCalculationService._resolve_engine(...)`.
- Le chemin `accurate=True` reste supporté; la source de vérité par défaut est pilotée par `NATAL_ENGINE_DEFAULT`.
- L’endpoint compare est volontairement restreint (auth + rôle + garde env/flag) pour éviter une exposition publique.

## Dev Agent Record

### Implementation Plan

1. Ajouter les nouveaux flags de configuration.
2. Refactorer la sélection d’engine + override interne dans le service natal.
3. Ajouter endpoint compare dev-only et builder de diff minimal.
4. Adapter metadata et couverture de tests.
5. Exécuter lint/tests dans le venv et documenter les limites de la suite complète.

### Completion Notes

- Implémentation complète de la story 20-7 côté backend:
  - `Settings` enrichi avec les flags engine migration/compat.
  - Sélection d’engine refactorée avec override interne sécurisé.
  - Endpoint compare dev-only ajouté avec diff `simplified_vs_swisseph`.
  - Metadata `ephemeris_path_version` alignée avec l’engine réellement utilisé.
- Tests ajoutés/ajustés:
  - Unit: sélection default/override engine.
  - Integration: compare endpoint (succès dev + refus production).
  - Non-régression: mocks `mock_calculate(..., **kwargs)` dans tests geo.
- Validation locale:
  - Ruff check OK sur fichiers modifiés.
  - Tests ciblés story 20-7 OK.
  - Suite backend complète lancée: échecs préexistants hors scope (LLM provider non configuré, logs geocoding cache, etc.).

## File List

- `backend/app/core/config.py` (modifié)
- `backend/app/services/natal_calculation_service.py` (modifié)
- `backend/app/api/v1/routers/astrology_engine.py` (modifié)
- `backend/app/services/user_natal_chart_service.py` (modifié)
- `backend/app/api/v1/routers/users.py` (modifié)
- `backend/app/domain/astrology/natal_calculation.py` (modifié)
- `backend/app/tests/unit/test_natal_pipeline_swisseph.py` (modifié)
- `backend/app/tests/integration/test_natal_calculate_api.py` (modifié)
- `backend/app/tests/integration/test_natal_chart_accurate_api.py` (nouveau)
- `backend/app/tests/unit/test_settings.py` (modifié)
- `backend/app/tests/unit/test_geo_place_resolved.py` (modifié)
- `_bmad-output/implementation-artifacts/20-7-migration-compat-engine-simplified-feature-flag.md` (modifié)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modifié)

## Change Log

- 2026-02-26 : Story 20-7 implémentée (migration/compat engine)
  - Ajout des flags `NATAL_ENGINE_DEFAULT`, `NATAL_ENGINE_SIMPLIFIED_ENABLED`, `NATAL_ENGINE_COMPARE_ENABLED`.
  - Migration de la sélection d’engine vers SwissEph par défaut (configurable).
  - Ajout endpoint compare dev-only sécurisé avec diff structuré `simplified_vs_swisseph`.
  - Alignement metadata engine réel + tests unitaires/intégration.
