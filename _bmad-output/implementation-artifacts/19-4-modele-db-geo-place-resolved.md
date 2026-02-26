# Story 19.4: Modèle DB `geo_place_resolved` canonique pour calculs reproductibles

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a système de calcul astrologique,
I want persister un lieu de naissance résolu de manière canonique et stable,
so that les futurs calculs d'éphémérides/maisons restent reproductibles entre sessions.

## Acceptance Criteria

1. **Given** une sélection utilisateur d'un lieu géocodé **When** le backend persiste la résolution **Then** une entrée `geo_place_resolved` est créée (ou réutilisée) avec les champs minimum demandés.
2. **Given** le schéma DB `geo_place_resolved` **When** les colonnes sont définies **Then** `latitude/longitude` respectent des contraintes de plage (`[-90,90]`, `[-180,180]`) avec type numérique stable (DECIMAL ou double) et `country_code` suit une convention ISO2 unique (lowercase ou uppercase fixée).
3. **Given** le provider actuel **When** une ligne est persistée **Then** `provider` est borné à la valeur supportée (`nominatim`) via validation applicative (et/ou contrainte DB).
4. **Given** deux résolutions concurrentes pour le même couple (`provider`, `provider_place_id`) **When** elles sont traitées simultanément **Then** une seule ligne est créée et réutilisée (idempotence transactionnelle).
5. **Given** un lieu résolu persisté **When** les calculs natals lisent les coordonnées **Then** la source de vérité est `geo_place_resolved.latitude/longitude`.
6. **Given** un lieu résolu persisté **When** l'API de lecture le renvoie **Then** on retrouve `provider_place_id`, `osm_type`, `osm_id`, `display_name`, `timezone_iana`, `timezone_source` et `timezone_confidence`.

## Tasks / Subtasks

- [x] Task 1 — Créer la table `geo_place_resolved` (AC: 1, 2, 3, 4)
  - [x] Ajouter migration Alembic avec colonnes: identité provider, coordonnées, hiérarchie géo, timezone, qualité/stabilité, timestamps.
  - [x] Créer modèle SQLAlchemy correspondant.
  - [x] Ajouter index/contraintes recommandés (`provider+provider_place_id`, lookup coords, normalized query).
  - [x] Ajouter checks plage lat/lon et convention explicite `country_code`.

- [x] Task 2 — Implémenter repository/service de persistance (AC: 1, 3, 4, 6)
  - [x] Upsert/reuse par clé unique provider.
  - [x] Validation et normalisation des champs.
  - [x] Calcul/stockage `raw_hash` du payload provider.
  - [x] Gérer la concurrence (transaction + unique constraint + retry minimal).

- [x] Task 3 — Brancher la lecture lat/lon canonique (AC: 5)
  - [ ] Adapter services de préparation/calcul natal pour lire depuis le FK résolu quand disponible (reporté à la story 19-6).
  - [x] Maintenir compatibilité transitoire si anciens profils sans FK.

- [x] Task 4 — Tests de persistance et stabilité (AC: 1, 2, 3, 4, 5, 6)
  - [x] Test création place résolue complète.
  - [x] Test idempotence/reuse via unique constraint y compris en concurrence.
  - [x] Test source-of-truth lat/lon sur sessions multiples.

## Dev Notes

### Schéma minimal attendu

- Identité: `provider`, `provider_place_id`, `osm_type`, `osm_id`, `display_name`, `type`, `class`, `importance`, `place_rank`.
- Coordonnées: `latitude`, `longitude`.
- Hiérarchie: `country_code`, `country`, `state`, `county`, `city`, `postcode`.
- Timezone: `timezone_iana`, `timezone_source`, `timezone_confidence`.
- Qualité: `normalized_query`, `query_language`, `query_country_code`, `raw_hash`, `created_at`, `updated_at`.
- Convention explicite à verrouiller: case de `country_code` (ISO2) et type lat/lon (DECIMAL ou double).

### Project Structure Notes

- `backend/migrations/versions/`
- `backend/app/infra/db/models/`
- `backend/app/infra/db/repositories/`
- `backend/app/services/`
- `backend/app/tests/unit/` et `backend/app/tests/integration/`

### References

- [Source: _bmad-output/planning-artifacts/epic-19-comment-lire-theme-natal-dans-l-app.md]
- [Source: backend/app/infra/db/models/user_birth_profile.py]
- [Source: backend/migrations/versions/20260225_0023_add_birth_profile_location_fields.py]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Convention choisie : `country_code` en UPPERCASE ISO2 (ex: "FR", "DE"), normalisé dans `GeoPlaceResolvedCreateData.__post_init__`.
- Type coordonnées : `Numeric(10, 7)` (DECIMAL stable, précision 7 décimales = sub-métrique).
- Task 3 implémentée avec propagation minimaliste : `birth_lat/birth_lon` passés depuis le profil vers `BirthInput` dans `UserNatalChartService.generate_for_user`. La résolution via FK `geo_place_resolved` sera complétée en story 19-6.
- `place_type` et `place_class` utilisés comme noms de colonnes (évitent les mots réservés SQL `type` et Python `class`).

### Completion Notes List

- Migration `20260226_0025` créée : table `geo_place_resolved` avec UniqueConstraint `(provider, provider_place_id)`, CheckConstraints lat/lon range + provider = 'nominatim', Index `(latitude, longitude)`, Index `normalized_query`.
- Modèle `GeoPlaceResolvedModel` avec colonnes complètes (26 colonnes) conforme au schéma minimal.
- `GeoPlaceResolvedRepository.find_or_create()` : idempotent via lookup pré-insertion + rollback+retry sur `IntegrityError` pour les cas de concurrence.
- `raw_hash` = SHA256(json.dumps(raw_payload, sort_keys=True)) — traçabilité provider.
- `UserNatalChartService.generate_for_user` mis à jour pour propager `birth_lat/birth_lon` au `BirthInput` (transitoire — FK sera ajouté en 19-6).
- 18 tests unitaires passent (0 régressions).
- 66 tests d'intégration pertinents passent (natal, birth_profile, geocoding).
- Correctif review: `GeoPlaceResolvedRepository.find_or_create()` utilise désormais un savepoint (`begin_nested`) pour éviter `rollback()` global en cas de collision concurrente.
- Correctif review: ajout endpoint `GET /v1/geocoding/resolved/{place_resolved_id}` pour exposer les champs de lecture canonique demandés par AC6.
- Correctif review: ajout de tests dédiés au chemin `IntegrityError` (concurrence) et à l'API de lecture de lieu résolu (200/404).

### File List

- `backend/migrations/versions/20260226_0025_add_geo_place_resolved.py` (new)
- `backend/app/infra/db/models/geo_place_resolved.py` (new)
- `backend/app/infra/db/models/__init__.py` (modified — ajout GeoPlaceResolvedModel)
- `backend/app/infra/db/repositories/geo_place_resolved_repository.py` (new)
- `backend/app/services/user_natal_chart_service.py` (modified — propagation birth_lat/lon)
- `backend/app/tests/unit/test_geo_place_resolved.py` (new)
- `backend/app/api/v1/routers/geocoding.py` (modified — endpoint GET /v1/geocoding/resolved/{place_resolved_id})
- `backend/app/tests/integration/test_geocoding_api.py` (modified — tests endpoint resolved place)
- `_bmad-output/implementation-artifacts/19-4-modele-db-geo-place-resolved.md` (this file)

## Change Log

- 2026-02-26: Story implémentée (claude-sonnet-4-6) — création table canonique geo_place_resolved, repository idempotent, propagation lat/lon pipeline natal, 18 tests unitaires.
- 2026-02-26: Revue senior (codex) — correction chemin concurrence sans rollback global, ajout lecture API canonique AC6, renforcement tests concurrence + API.

## Senior Developer Review (AI)

- Date: 2026-02-26
- Reviewer: Codex (GPT-5)
- Outcome: Changes Requested (partially fixed in this pass)

### Findings traités dans ce passage

1. `find_or_create()` faisait un `rollback()` global sur `IntegrityError` (risque transactionnel) → corrigé via savepoint (`begin_nested`).
2. AC6 demandait une lecture API d'un lieu canonique persisté → corrigé avec `GET /v1/geocoding/resolved/{place_resolved_id}`.
3. Couverture de concurrence incomplète → corrigée avec test du chemin `IntegrityError` + re-lookup.
4. Story/File List incomplète → mise à jour des fichiers modifiés et du change log.

### Point restant

- Le sous-item Task 3 "lecture via FK `geo_place_resolved`" reste reporté à la story 19-6 (FK non présent dans `user_birth_profiles` à ce stade).
