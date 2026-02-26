# Story 19.2: Backend Geocoding Search Proxy (Nominatim)

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur qui saisit son lieu de naissance,
I want que la recherche de lieux passe par un endpoint backend,
so that l'application reste robuste, conforme aux contraintes provider, et prête à persister des résultats canoniques.

## Acceptance Criteria

1. **Given** une requête de recherche de lieu **When** le frontend appelle l'API backend **Then** l'API interroge Nominatim côté serveur et non plus depuis le navigateur.
2. **Given** un appel upstream Nominatim **When** la requête est émise **Then** le backend force `format=jsonv2` et `addressdetails=1`.
3. **Given** une requête de recherche **When** le backend valide l'entrée **Then** la query est normalisée (trim, collapse spaces), sa longueur minimale est appliquée (>=2), et `limit` est borné entre 1 et 10.
4. **Given** un résultat de recherche **When** l'API répond **Then** chaque `results[]` inclut au minimum: `provider`, `provider_place_id`, `osm_type`, `osm_id`, `type`, `class`, `display_name`, `lat`, `lon`, `importance`, `place_rank`, et les champs `address` utiles (`country_code`, `country`, `state`, `county`, `city`, `postcode`).
5. **Given** un timeout, une erreur upstream ou une réponse invalide **When** l'API backend échoue **Then** le contrat d'erreur est stable avec codes: `invalid_geocoding_query` (422), `geocoding_rate_limited` ou `geocoding_client_rate_limited` (429), `geocoding_provider_unavailable` (503).
6. **Given** le frontend BirthProfilePage **When** l'utilisateur recherche un lieu **Then** il consomme exclusivement l'endpoint backend et n'appelle plus `nominatim.openstreetmap.org` en direct.

## Tasks / Subtasks

- [x] Task 1 — Créer le router geocoding backend (AC: 1, 2, 3, 5)
  - [x] Ajouter `GET /api/v1/geocoding/search` (ou préfixe v1 aligné projet).
  - [x] Implémenter timeout, validation input, normalisation query.
  - [x] Forcer `format=jsonv2` et `addressdetails=1` vers upstream.
  - [x] Mapper proprement les erreurs upstream vers erreurs API stables.

- [x] Task 2 — Définir le contrat de réponse persistable (AC: 4)
  - [x] Créer DTO/Pydantic pour `GeocodingSearchResult`.
  - [x] Mapper `jsonv2` Nominatim vers les champs nécessaires à `geo_place_resolved`.
  - [x] Garantir le typage (`lat/lon` numériques) et les champs optionnels.

- [x] Task 3 — Intégrer frontend sur le proxy backend (AC: 6)
  - [x] Remplacer `frontend/src/api/geocoding.ts` (appel direct) par appel API interne.
  - [x] Adapter BirthProfilePage et les tests front associés.
  - [x] Vérifier l'UX des états loading/error/not_found.

- [x] Task 4 — Tests backend et frontend (AC: 1, 2, 3, 4, 5, 6)
  - [x] Tests unitaires mapping Nominatim -> DTO.
  - [x] Tests intégration endpoint search (succès + erreurs 422/429/503 + timeout).
  - [x] Tests front non-régression: aucune requête directe à Nominatim.

## Dev Notes

### Contraintes techniques

- Respecter l'architecture existante (`api/v1/routers`, `services`, `infra`).
- Préparer la réponse pour persistance sans second appel upstream.
- Ne pas introduire de duplication de clients HTTP géocodage.
- `User-Agent` et contact Nominatim doivent être configurables via settings (pas hardcodés).

### Project Structure Notes

- Backend:
  - `backend/app/api/v1/routers/`
  - `backend/app/services/`
  - `backend/app/tests/unit/` et `backend/app/tests/integration/`
- Frontend:
  - `frontend/src/api/geocoding.ts`
  - `frontend/src/pages/BirthProfilePage.tsx`
  - `frontend/src/tests/`

### References

- [Source: _bmad-output/planning-artifacts/epic-19-comment-lire-theme-natal-dans-l-app.md]
- [Source: _bmad-output/implementation-artifacts/14-1-geocodage-lieu-naissance-nominatim.md]
- [Source: frontend/src/api/geocoding.ts]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Fix `json.loads` déplacé dans le second bloc `try` (parsing/mapping) pour capturer `JSONDecodeError` (sous-classe de `ValueError`) → test `test_search_raises_provider_unavailable_on_invalid_json` qui échouait initialement.

### Completion Notes List

- Endpoint `GET /v1/geocoding/search` implémenté via `urllib.request` stdlib (aucune dépendance de production ajoutée).
- DTOs Python migrés vers Pydantic (`GeocodingAddress`, `GeocodingSearchResult`) avec alias `class`.
- `GeocodingError.code` côté frontend changé de type littéral `"service_unavailable"` vers `string` pour supporter les codes backend multiples.
- Champ `class` (mot réservé Python) mappé via attribut `class_` (alias `"class"`) dans le DTO Pydantic.
- Paramètres Nominatim (`nominatim_url`, `nominatim_user_agent`, `nominatim_contact`, `nominatim_timeout_seconds`) ajoutés dans `Settings`.
- 38 tests backend geocoding passent (23 unit + 15 integration). 1072 tests frontend passent.
- Validation upstream durcie: rejet des payloads partiels/invalides (ids/champs texte/champs numériques requis) avec mapping 503 stable.
- Gestion d'annulation frontend alignée: `geocodeCity` retourne `null` sur abort externe explicite (pas d'erreur service artificielle).

### File List

- `_bmad-output/implementation-artifacts/19-2-backend-geocoding-search-proxy-nominatim.md`
- `backend/app/core/config.py` (modifié — ajout settings Nominatim)
- `backend/app/services/geocoding_service.py` (nouveau)
- `backend/app/api/v1/routers/geocoding.py` (nouveau)
- `backend/app/main.py` (modifié — include_router geocoding)
- `backend/app/tests/unit/test_geocoding_service.py` (nouveau)
- `backend/app/tests/integration/test_geocoding_api.py` (nouveau)
- `frontend/src/api/geocoding.ts` (modifié — proxy backend)
- `frontend/src/tests/geocodingApi.test.ts` (réécrit)
- `frontend/src/tests/BirthProfilePage.test.tsx` (modifié — mocks format backend)

### Change Log

- 2026-02-26: Implémentation complète story 19-2 (claude-sonnet-4-6)
  - Backend proxy Nominatim créé (`geocoding_service.py`, router, settings)
  - Frontend migré vers l'endpoint backend
  - 38 tests backend + 56 tests frontend ciblés passent (1072 total frontend)
- 2026-02-26: Correctifs suite code review (GPT-5 Codex)
  - Migration DTOs geocoding vers Pydantic + sérialisation alias `"class"`
  - Validation stricte des champs upstream Nominatim requis
  - Alignement de la sémantique d'annulation frontend (`AbortSignal` externe)
  - Mise à jour des tests unitaires/intégration geocoding

## Senior Developer Review (AI)

Date: 2026-02-26  
Reviewer: Codex (GPT-5)

- Résultat: Approved after fixes.
- Points corrigés:
  - Contrat DTO backend aligné Pydantic (Task 2 conforme).
  - Validation upstream renforcée pour éviter des résultats partiels incohérents.
  - Sémantique d'annulation frontend alignée avec la doc (`null` sur abort externe).
  - Tests mis à jour et repassés sur le scope geocoding.
- Note de contexte: le repository contient des modifications parallèles hors story 19-2; la review et les correctifs ont été limités au périmètre fonctionnel geocoding.
