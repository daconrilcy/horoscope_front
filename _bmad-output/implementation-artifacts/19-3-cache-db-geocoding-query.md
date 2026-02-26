# Story 19.3: Cache DB `geocoding_query_cache` séparé du stockage canonique

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a système backend de géocodage,
I want un cache DB de requêtes distinct du stockage canonique des lieux,
so that les recherches sont performantes sans compromettre la stabilité des données de calcul.

## Acceptance Criteria

1. **Given** une recherche de lieu identique répétée **When** le cache est valide **Then** le backend renvoie la réponse depuis `geocoding_query_cache` sans appel upstream.
2. **Given** une entrée de cache expirée **When** une nouvelle recherche est lancée **Then** le backend ré-interroge Nominatim et rafraîchit le cache.
3. **Given** une place déjà résolue dans `geo_place_resolved` **When** le cache de recherche expire **Then** la place canonique persiste (pas de TTL).
4. **Given** une clé cache construite pour une recherche **When** elle est persistée **Then** `query_key` est un hash stable (ex: SHA256) d'un objet normalisé `{q_norm, country_code, lang, limit}`.
5. **Given** l'observabilité geocoding **When** une recherche est loggée **Then** les logs n'exposent pas `q` brut et utilisent `q_hash`/`query_key`.
6. **Given** un besoin de debug **When** `nocache=true` est fourni (usage dev/admin) **Then** le backend bypass le cache pour l'appel.
7. **Given** l'architecture géocodage **When** on lit le schéma DB **Then** `geocoding_query_cache` et `geo_place_resolved` sont explicitement séparées.

## Tasks / Subtasks

- [x] Task 1 — Ajouter table cache et TTL (AC: 1, 2, 4, 7)
  - [x] Migration Alembic `geocoding_query_cache` avec `query_key`, `response_json`, `expires_at`, `created_at`.
  - [x] Index sur `query_key` et `expires_at`.
  - [x] Nettoyage/invalidations minimales côté service.

- [x] Task 2 — Implémenter stratégie cache dans service geocoding (AC: 1, 2, 4, 6)
  - [x] Générer `query_key` via hash stable de l'objet normalisé (`q_norm`, langue, country code, limit).
  - [x] Lire/écrire cache avec TTL configurable.
  - [x] Bypass cache en cas de données invalides.
  - [x] Gérer `nocache=true` (guardé pour usage dev/admin).

- [x] Task 3 — Garantir séparation cache vs canonique (AC: 3, 7)
  - [x] Vérifier qu'aucune suppression cache n'affecte `geo_place_resolved`.
  - [x] Documenter ce contrat dans les services/tests.

- [x] Task 4 — Tests (AC: 1, 2, 3, 4, 5, 6, 7)
  - [x] Test hit cache.
  - [x] Test miss après expiration TTL.
  - [x] Test non-régression: place résolue conserve ses coordonnées après expiration cache.
  - [x] Test logs sans PII (`q` brut absent, `query_key` présent).
  - [x] Test bypass `nocache=true`.

## Dev Notes

### Règle d'architecture

- `geocoding_query_cache`: optimisation court terme (TTL).
- `geo_place_resolved`: vérité terrain long terme (pas de TTL).
- `query_key` doit rester court et stable (hash), pas de clé brute avec texte utilisateur.
- Logs et métriques: ne pas exposer la requête brute.

### Project Structure Notes

- `backend/migrations/versions/`
- `backend/app/services/`
- `backend/app/infra/db/models/`
- `backend/app/tests/unit/`

### References

- [Source: _bmad-output/planning-artifacts/epic-19-comment-lire-theme-natal-dans-l-app.md]
- [Source: _bmad-output/implementation-artifacts/19-4-modele-db-geo-place-resolved.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Fix datetime timezone-naive vs aware dans le test d'intégration `test_cache_written_after_miss` : SQLite retourne des datetimes naïfs, comparaison normalisée avec `.replace(tzinfo=timezone.utc)`.
- Review fix: `nocache=true` désormais restreint (support/ops ou token admin en environnement local/test avec fallback activé).
- Review fix: lecture cache durcie: payload cache corrompu loggé puis traité comme cache miss (pas de 500).

### Completion Notes List

- Modèle `GeocodingQueryCacheModel` créé avec colonnes `id`, `query_key` (SHA256, 64 chars), `response_json`, `expires_at`, `created_at`. Index sur `query_key` (unique) et `expires_at`.
- Migration Alembic `20260226_0024_add_geocoding_query_cache` avec upgrade/downgrade complets.
- Fonction `_build_query_key(q_norm, limit, country_code, lang)` — hash SHA256 stable de l'objet normalisé. Jamais la requête brute.
- `GeocodingService.search_with_cache(db, query, limit, nocache, ...)` : lecture cache si hit valide (expires_at > now), appel Nominatim si miss, upsert en cache. `nocache=True` bypass entièrement.
- Router `/v1/geocoding/search` mis à jour : paramètre `nocache` (bool, défaut `false`) restreint à support/ops ou token admin de dev/test.
- Le proxy passe aussi `country_code`/`lang` jusqu'à la construction de clé cache et à la requête Nominatim.
- Config `GEOCODING_CACHE_TTL_SECONDS` (défaut 3600s = 1h).
- Logs : `geocoding_search query_key=... nocache=...`, `geocoding_cache_hit query_key=...`, `geocoding_cache_miss query_key=...` — jamais la requête brute.
- Migration ajustée: suppression de redondance `UniqueConstraint` + index unique sur `query_key` (on conserve l'index unique).
- 45 tests geocoding (unitaires + intégration) passent.
- Séparation `geocoding_query_cache` / `geo_place_resolved` garantie structurellement et documentée.

### Change Log

- 2026-02-26 : Implémentation story 19-3 — cache DB geocoding avec TTL, query_key SHA256, nocache bypass, logs sans PII. 43 tests nouveaux/mis à jour.
- 2026-02-26 : Revue senior AI — correctifs P0/P1 appliqués (`nocache` sécurisé, fallback cache corrompu, test TTL renforcé, migration dédupliquée). 45 tests geocoding passent.

### File List

- `backend/app/infra/db/models/geocoding_query_cache.py` (new)
- `backend/app/infra/db/models/__init__.py` (modified)
- `backend/migrations/versions/20260226_0024_add_geocoding_query_cache.py` (modified)
- `backend/app/core/config.py` (modified — ajout `geocoding_cache_ttl_seconds`)
- `backend/app/services/geocoding_service.py` (modified — ajout `_build_query_key`, `search_with_cache`)
- `backend/app/api/v1/routers/geocoding.py` (modified — garde `nocache`, `country_code`, `lang`)
- `backend/app/tests/unit/test_geocoding_cache.py` (modified — cas cache corrompu + assertions appels enrichies)
- `backend/app/tests/integration/test_geocoding_api.py` (modified — accès `nocache` contrôlé + scénario TTL sur clé réelle)
- `_bmad-output/implementation-artifacts/19-3-cache-db-geocoding-query.md` (this file)

## Senior Developer Review (AI)

### Reviewer

Cyril (AI Senior Developer Review)

### Date

2026-02-26

### Outcome

Approve

### Summary

- Tous les points HIGH/MEDIUM de la revue ont été corrigés dans le code et couverts par tests.
- Vérification exécutée dans le venv:
  - `ruff check app/api/v1/routers/geocoding.py app/services/geocoding_service.py app/tests/unit/test_geocoding_cache.py app/tests/integration/test_geocoding_api.py migrations/versions/20260226_0024_add_geocoding_query_cache.py`
  - `pytest -q app/tests/unit/test_geocoding_cache.py app/tests/integration/test_geocoding_api.py`
- Résultat: lint OK, 45 tests passants.
