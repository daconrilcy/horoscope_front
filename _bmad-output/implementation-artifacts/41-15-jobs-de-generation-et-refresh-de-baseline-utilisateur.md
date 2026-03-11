# Story 41.15: Jobs de génération et refresh de baseline utilisateur

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a platform engineer,
I want générer et rafraîchir les baselines utilisateur de façon asynchrone,
so that la calibration relative soit disponible sans ajouter de latence bloquante à l’inscription ni à la consultation quotidienne.

## Acceptance Criteria

1. Un job asynchrone peut générer la baseline utilisateur 12 mois après disponibilité du thème natal.

2. Un mécanisme de refresh explicite existe pour les changements impactants:
   - `reference_version`
   - `ruleset_version`
   - `house_system_effective`
   - données natales modifiées

3. Le job est idempotent et observable:
   - relance sans doublons silencieux
   - logs structurés explicites
   - statut ou timestamp de fraîcheur lisible

4. Le produit ne bloque pas sur la baseline:
   - l’inscription / création du profil natal reste non bloquante
   - `/v1/predictions/daily` fonctionne même en absence de baseline

5. Des tests couvrent:
   - déclenchement nominal
   - relance idempotente
   - refresh après changement de version
   - fallback produit sans baseline disponible

## Tasks / Subtasks

- [x] Task 1: Définir le job de génération initiale (AC: 1, 4)
  - [x] Ajouter le job backend dédié
  - [x] Brancher son déclenchement depuis le bon point du cycle de vie utilisateur
  - [x] Garder l’expérience non bloquante

- [x] Task 2: Implémenter la stratégie de refresh (AC: 2, 3)
  - [x] Détecter les changements invalidants
  - [x] Ajouter la relance ou l’invalidation de baseline
  - [x] Empêcher les doublons silencieux

- [x] Task 3: Ajouter l’observabilité opérationnelle (AC: 3)
  - [x] Logs structurés
  - [x] Indicateurs de fraîcheur / version
  - [x] Messages explicites en cas d’échec ou de fallback

- [x] Task 4: Couvrir les scénarios d’exploitation (AC: 5)
  - [x] Tests de job
  - [x] Tests d’idempotence
  - [x] Tests fallback sans baseline
  - [x] Tests refresh/invalidation

## Dev Notes

- Cette story transforme la baseline relative en capacité opérationnelle exploitable à l’échelle produit.
- Le déclenchement doit rester asynchrone et simple à observer.
- La disponibilité de la baseline ne doit jamais devenir une condition bloquante pour le daily.
- Le refresh doit rester explicitement lié aux changements de contexte métier, pas à un heuristique opaque.

### Project Structure Notes

- Fichiers backend principaux:
  - `backend/app/jobs/` (nouveau job baseline)
  - `backend/app/services/` (service de baseline déjà introduit)
  - points d’entrée profil natal / onboarding si déclenchement nécessaire
  - éventuelle observabilité/logging applicative

### Technical Requirements

- Le job doit être idempotent.
- Le fallback sans baseline doit être explicite et sûr.
- La stratégie de refresh doit être versionnée et testable.
- Les logs doivent permettre de distinguer:
  - baseline générée
  - baseline obsolète
  - baseline absente
  - refresh déclenché

### Architecture Compliance

- La génération de baseline est une responsabilité opérationnelle backend, pas une responsabilité du routeur ou du frontend.
- Les workflows d’inscription et de daily consomment cette capacité sans être couplés à son implémentation détaillée.

### Library / Framework Requirements

- Réutiliser la stack backend existante uniquement.
- Aucun ajout de dépendance externe requis si le mécanisme de job existant suffit.

### File Structure Requirements

- Le job doit vivre dans la couche jobs backend existante.
- Les règles d’invalidation et de refresh doivent rester côté service, pas dupliquées dans les handlers.

### Testing Requirements

- Couvrir:
  - déclenchement initial
  - refresh
  - idempotence
  - fallback sans baseline
- Exécuter `ruff check` et `pytest` dans le venv.

### Previous Story Intelligence

- 37.2 a déjà introduit un job de génération de dataset calibration; cette story peut réutiliser des patterns de job, d’observabilité et de reprise. [Source: _bmad-output/implementation-artifacts/37-2-job-generation-rawday-calibration.md]
- 39.2 et 39.3 ont centralisé les versions actives prediction; cette story doit s’appuyer sur cette source de vérité pour l’invalidation baseline. [Source: _bmad-output/implementation-artifacts/39-2-basculer-la-configuration-runtime-et-centraliser-les-versions-actives.md]

### Git Intelligence Summary

- Les flows backend existants supportent déjà des jobs de données et de calibration; le bon pattern ici est d’étendre cette discipline plutôt que d’injecter un recalcul synchrone dans les chemins utilisateurs.

### Project Context Reference

- Aucun `project-context.md` détecté dans le repo.
- Les règles actives du repo viennent de `AGENTS.md`, de `epics.md` et de la spec `_bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md`.

### References

- [Source: _bmad-output/planning-artifacts/epic-41-relative-calibration-spec.md]
- [Source: _bmad-output/implementation-artifacts/37-2-job-generation-rawday-calibration.md]
- [Source: _bmad-output/implementation-artifacts/39-2-basculer-la-configuration-runtime-et-centraliser-les-versions-actives.md]
- [Source: backend/app/jobs/generate_daily_calibration_dataset.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story créée à partir de la spec de calibration relative Epic 41 rédigée le 2026-03-10.

### Completion Notes List

- Le refresh ne se déclenche plus depuis `birth-data`; il attend un thème natal exploitable et part depuis la génération du thème.
- La sélection des utilisateurs à rafraîchir tient compte du `house_system_effective`, des changements de version actifs et de la fraîcheur réelle du dernier thème natal.
- L’upsert des baselines gère maintenant les courses concurrentes sans doublon silencieux.
- Les tests couvrent le nominal, l’idempotence, le changement de house system, le changement de versions actives et le fallback daily sans baseline.

### File List

- `_bmad-output/implementation-artifacts/41-15-jobs-de-generation-et-refresh-de-baseline-utilisateur.md`
- `backend/app/api/v1/routers/users.py`
- `backend/app/infra/db/repositories/user_prediction_baseline_repository.py`
- `backend/app/jobs/refresh_user_baselines.py`
- `backend/app/tests/integration/test_user_baseline_refresh_job.py`
- `backend/app/tests/unit/test_daily_prediction_service.py`
