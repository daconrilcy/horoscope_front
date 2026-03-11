# Story 41.7: Sécurisation technique hash, timezone et DTO publics

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a équipe produit et technique travaillant sur l’horoscope du jour,
I want sécuriser les invariants techniques immédiats du pipeline daily sans changer le contrat fonctionnel,
so that les calculs intraday restent temporellement exacts, les runs soient dédupliqués de manière fiable, et les DTO publics aient une sémantique stable.

## Acceptance Criteria

1. Le raffinement temporel à 1 minute ne mélange plus UTC et heure locale:
   - `TemporalSampler.refine_around()` produit des `SamplePoint` cohérents avec le fuseau utilisateur ou
   - le chemin de raffinement ne dépend plus d’un `local_time` incorrect injecté comme donnée métier
   - les événements raffinés restent alignés avec `meta.timezone`

2. Le calcul du hash d’entrée de prédiction est unifié dans un module partagé:
   - `DailyPredictionService` et `EngineOrchestrator` utilisent la même fonction
   - la sérialisation canonique est unique et documentée
   - aucun écart de hash n’existe entre service applicatif et moteur pour un même `EngineInput`

3. Les types publics liés aux turning points sont normalisés:
   - `severity` est manipulée en `float` côté domaine
   - `severity` est exposée en `float` côté DTO public
   - les variantes debug et publique n’ont plus de divergence de type inutile

4. Le changement ne modifie pas le comportement produit attendu de `/v1/predictions/daily` hors corrections de cohérence:
   - pas de régression de cache/réutilisation liée au hash
   - pas de décalage de turning points dû au fuseau lors du raffinement
   - pas de rupture FastAPI/Pydantic sur les réponses publiques

5. Des tests ciblés couvrent les trois chantiers:
   - tests unitaires sur le hash partagé
   - tests unitaires ou d’intégration sur le raffinement temporel, y compris un cas avec changement d’heure
   - tests DTO/API sur la normalisation `severity: float`
   - tests de compatibilité avec des runs déjà persistés pour éviter faux négatifs de réutilisation ou collisions logiques après déploiement

## Tasks / Subtasks

- [x] Task 1: Corriger l’invariant timezone du raffinement fin (AC: 1)
  - [x] Analyser `TemporalSampler.refine_around()` et le point d’injection dans `EngineOrchestrator`
  - [x] Choisir une stratégie unique: propager `tz_name` ou supprimer la dépendance métier au `local_time` dans ce chemin
  - [x] Ajouter des tests sur un cas utilisateur avec timezone non UTC
  - [x] Ajouter au moins un cas couvrant un changement d’heure

- [x] Task 2: Extraire un calcul de hash partagé (AC: 2, 4)
  - [x] Créer `backend/app/prediction/input_hash.py`
  - [x] Déplacer la logique canonique de hash dans une seule fonction publique
  - [x] Remplacer `_compute_input_hash()` et `_compute_hash()` par l’utilitaire partagé
  - [x] Couvrir le cas de sérialisation stable des dates/enums/objets d’entrée

- [x] Task 3: Normaliser `severity` en float bout en bout (AC: 3, 4)
  - [x] Identifier les schémas domaine / debug / public concernés
  - [x] Supprimer les conversions en chaîne encore présentes dans la projection publique
  - [x] Vérifier la compatibilité avec les consommateurs frontend existants

- [x] Task 4: Vérifier la non-régression du pipeline daily (AC: 4, 5)
  - [x] Mettre à jour les tests backend pertinents
  - [x] Vérifier la compatibilité avec des runs déjà persistés et la réutilisation associée
  - [x] Exécuter lint et tests backend ciblés
  - [x] Vérifier qu’un appel `/v1/predictions/daily` reste sérialisable sans erreur

## Dev Notes

- Cette story est volontairement technique et à faible risque produit.
- Elle doit être traitée avant les gros chantiers de découpage de services et d’assembleur public.
- La priorité absolue est l’exactitude temporelle des événements raffinés; un bug de timezone ici contamine turning points, timeline, editorial et payload public.
- Le hash partagé doit devenir la seule source de vérité pour la déduplication de runs.
- La normalisation de `severity` doit rester additive dans l’esprit: simplifier et unifier, sans introduire de rupture de structure ailleurs.

### Project Structure Notes

- Fichiers backend directement concernés:
  - `backend/app/prediction/temporal_sampler.py`
  - `backend/app/prediction/engine_orchestrator.py`
  - `backend/app/prediction/input_hash.py` (nouveau)
  - `backend/app/services/daily_prediction_service.py`
  - `backend/app/api/v1/routers/predictions.py`
  - `backend/app/prediction/schemas.py`

### Technical Requirements

- L’utilitaire de hash doit être pur, déterministe, testable, et découplé d’une session DB.
- Le correctif timezone doit expliciter le fuseau de l’utilisateur et éviter toute comparaison implicite UTC/local.
- Les schémas publics FastAPI doivent rester explicites sur le type `float`.
- Toute évolution doit préserver la compatibilité avec les runs déjà persistés.

### Architecture Compliance

- Le routeur API ne doit pas absorber de nouvelle logique métier supplémentaire dans cette story.
- Le hash partagé doit réduire le couplage, pas créer une nouvelle dépendance circulaire service <-> moteur.
- Le correctif timezone doit rester dans la couche moteur / sampling / orchestration, pas être “réparé” côté UI.

### Library / Framework Requirements

- Python 3.13, FastAPI, Pydantic, SQLAlchemy existants uniquement.
- Aucun ajout de dépendance n’est requis pour cette story.

### File Structure Requirements

- Le nouvel utilitaire doit vivre dans `backend/app/prediction/input_hash.py`.
- Les tests associés doivent rejoindre les suites backend existantes `unit` ou `integration` selon le niveau.

### Testing Requirements

- Ajouter au minimum:
  - un test de hash identique entre service et orchestrateur
  - un test de raffinement sur un fuseau utilisateur explicite
  - un test de raffinement sur une transition DST
  - un test API/DTO garantissant `severity` numérique
  - un test de compatibilité sur réutilisation de runs déjà persistés
- Exécuter `ruff check` et `pytest` dans le venv.

### Previous Story Intelligence

- 41.4 et 41.6 ont déjà montré que des incohérences de timezone et de sémantique publique se répercutent immédiatement dans le dashboard daily. [Source: _bmad-output/implementation-artifacts/41-4-contrat-api-et-ui-centres-aide-decision-intraday.md]
- 41.6 a introduit une logique publique plus cohérente côté `/v1/predictions/daily`; cette story doit la stabiliser techniquement avant toute refonte structurelle. [Source: _bmad-output/implementation-artifacts/41-6-refactor-dashboard-moments-cles-et-agenda-du-jour.md]

### Git Intelligence Summary

- `3448e68 feat(daily): align agenda and turning points semantics` a déplacé de la sémantique produit côté backend public; les invariants techniques sous-jacents doivent maintenant être fiabilisés.
- `0aa358c feat(ui): refactor dashboard intraday hierarchy (Story 41.6)` a rendu les erreurs de cohérence temporelle plus visibles côté UI.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.
- Les règles actives du repo viennent de `AGENTS.md` et des artefacts BMAD existants.

### References

- [Source: user refactor plan 2026-03-10 — Phase 1 sécurisation technique immédiate]
- [Source: backend/app/prediction/temporal_sampler.py]
- [Source: backend/app/prediction/engine_orchestrator.py]
- [Source: backend/app/services/daily_prediction_service.py]
- [Source: backend/app/api/v1/routers/predictions.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story créée à partir du plan de refacto Epic 41 fourni le 2026-03-10.

### Completion Notes List

- Le pipeline daily utilise maintenant un hash d’entrée partagé et versionné, commun au service applicatif et à l’orchestrateur.
- La résolution de timezone a été durcie pour ignorer les valeurs non textuelles ou invalides avant validation `ZoneInfo`, ce qui élimine les crashes runtime et les fuites de `MagicMock` observées dans les suites QA.
- La projection publique normalise désormais `severity` et les payloads turning points sans divergence de type entre domaine, snapshot et API publique.
- Des vérifications ciblées ont été rejouées sur le pipeline `/v1/predictions/daily`, la réutilisation de runs et les suites daily prediction associées.

### File List

- `backend/app/prediction/input_hash.py`
- `backend/app/prediction/schemas.py`
- `backend/app/services/prediction_request_resolver.py`
- `backend/app/services/daily_prediction_service.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
- `backend/app/tests/integration/test_daily_prediction_api.py`
- `_bmad-output/implementation-artifacts/41-7-securisation-technique-hash-timezone-et-dto-publics.md`
