# Story 18.1: Astro Profile Backend — Sun sign + Ascendant avec règle null-time stricte

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur ayant un profil natal,
I want que le backend calcule et expose mon signe solaire et mon ascendant de façon fiable,
so that le frontend affiche des informations astrologiques justes, sans deviner l'ascendant quand l'heure de naissance manque.

## Acceptance Criteria

1. **Given** un utilisateur avec `birth_date` valide **When** l'API profile astro est appelée **Then** `sun_sign_code` est calculé correctement à partir de la date de naissance.
2. **Given** un utilisateur avec `birth_date` + `birth_time` valide (ex: `"14:30"` ou `"00:00"`) **When** l'API profile astro est appelée **Then** `ascendant_sign_code` est non null et cohérent avec le moteur astrologique existant.
3. **Given** un utilisateur avec `birth_time` null ou absent **When** l'API profile astro est appelée **Then** `ascendant_sign_code = null` **And** `missing_birth_time = true`.
4. **Given** un utilisateur avec `birth_time = "00:00"` explicitement saisi **When** l'API profile astro est appelée **Then** `ascendant_sign_code` est calculé (non null) **And** `missing_birth_time = false`.
5. **Given** les endpoints existants `/v1/users/me/birth-data` et `/v1/users/me/natal-chart/latest` **When** on intègre les données astro profile **Then** aucun nouvel endpoint dupliqué n'est créé.

## Tasks / Subtasks

- [x] Task 1 — Audit backend existant (AC: 1, 2, 3, 5)
  - [x] Vérifier les modules actuels: `backend/app/domain/astrology/natal_preparation.py`, `backend/app/domain/astrology/natal_calculation.py`, `backend/app/services/user_birth_profile_service.py`, `backend/app/services/user_natal_chart_service.py`.
  - [x] Confirmer les champs DB/API actuels: `birth_date`, `birth_time`, `birth_place`, `birth_timezone`.
  - [x] Confirmer qu'il n'existe pas déjà un service dédié `sun_sign + ascendant` réutilisable.

- [x] Task 2 — Modèle de données nullable pour `birth_time` (AC: 3, 4)
  - [x] Modifier `BirthInput.birth_time` en nullable/optionnel dans `backend/app/domain/astrology/natal_preparation.py`.
  - [x] Adapter `prepare_birth_data` pour supporter `birth_time is None` sans lever `invalid_birth_time` hors cas non conforme.
  - [x] Appliquer migration Alembic pour rendre `user_birth_profiles.birth_time` nullable:
    - [x] `backend/migrations/versions/20260225_0022_birth_time_nullable.py`.
    - [x] `backend/app/infra/db/models/user_birth_profile.py` (`Mapped[str | None]`).
    - [x] `backend/app/infra/db/repositories/user_birth_profile_repository.py` (upsert/count signatures).
  - [x] Adapter `backend/app/services/user_birth_profile_service.py` (`UserBirthProfileData.birth_time: str | None`).

- [x] Task 3 — Service astro profile unifié (AC: 1, 2, 3, 4, 5)
  - [x] Créer `backend/app/services/user_astro_profile_service.py` avec un DTO:
    - [x] `sun_sign_code: str | None`
    - [x] `ascendant_sign_code: str | None`
    - [x] `missing_birth_time: bool`
  - [x] Implémenter la règle fonctionnelle unique:
    - [x] Si `birth_time` est null/absent: ascendant non calculé (`null`) + `missing_birth_time=true`.
    - [x] Si `birth_time` est une string valide (y compris `"00:00"`): `missing_birth_time=false` + calcul ascendant normal.
  - [x] Calcul sun sign: via logique date-only cohérente avec le référentiel des signes du projet.
  - [x] Calcul ascendant: via moteur existant (pas de nouvel engine) en réutilisant les calculateurs/services en place.

- [x] Task 4 — Exposition API sans duplication de route (AC: 5)
  - [x] Étendre les réponses existantes dans `backend/app/api/v1/routers/users.py`:
    - [x] `GET /v1/users/me/birth-data` inclut un bloc `astro_profile`.
    - [x] `GET /v1/users/me/natal-chart/latest` inclut le même bloc `astro_profile` (ou mapping aligné selon conventions actuelles).
  - [x] Préserver l'enveloppe d'erreur et les contrats existants (pas de breaking change).

- [x] Task 5 — Tests backend (AC: 1, 2, 3, 4, 5)
  - [x] Unit tests service:
    - [x] `birth_time absent/null` => ascendant null + missing true.
    - [x] `birth_time "14:30"` => ascendant non null + missing false.
    - [x] `birth_time "00:00"` => ascendant non null + missing false.
    - [x] sun sign connu pour dates repères (table de cas fixes).
  - [x] Integration tests API:
    - [x] `GET /v1/users/me/birth-data` retourne `astro_profile`.
    - [x] `GET /v1/users/me/natal-chart/latest` retourne `astro_profile`.
    - [x] Non-régression des codes 404/422/503 existants.

## Dev Notes

### Comportement null-time (règle verrouillée)

Règle: si `birth_time` est null/absent => ascendant non calculé (`null`) + `missing_birth_time=true`. La valeur `"00:00"` est traitée comme une heure valide si elle est fournie.

### Plan de changements fichier par fichier (backend)

- `backend/app/domain/astrology/natal_preparation.py`
  - rendre `BirthInput.birth_time` nullable/optionnel.
  - adapter parse/validation pour ne plus imposer la sentinelle.
- `backend/app/services/user_birth_profile_service.py`
  - DTO et upsert/read compatibles `birth_time: str | None`.
- `backend/app/infra/db/models/user_birth_profile.py`
  - colonne `birth_time` nullable.
- `backend/app/infra/db/repositories/user_birth_profile_repository.py`
  - signatures `birth_time: str | None`.
- `backend/app/services/user_astro_profile_service.py` (nouveau)
  - calcul `sun_sign_code`, `ascendant_sign_code`, `missing_birth_time`.
- `backend/app/api/v1/routers/users.py`
  - enrichir réponses existantes (`birth-data`, `natal-chart/latest`) sans créer d'endpoint doublon.
- `backend/migrations/versions/<new>_birth_time_nullable.py`
  - migration nullable DB.
- `backend/app/tests/unit/test_user_astro_profile_service.py` (nouveau)
- `backend/app/tests/integration/test_user_birth_profile_api.py` (maj)
- `backend/app/tests/integration/test_user_natal_chart_api.py` (maj)

### Project Structure Notes

- Respect de l'architecture existante: `domain/` pour règles astro, `services/` pour orchestration, `api/routers` pour exposition HTTP.
- Aucun changement de stack ou moteur astrologique.
- Pas de `requirements.txt`: dépendances via `backend/pyproject.toml`.

### References

- [Source: backend/app/domain/astrology/natal_preparation.py]
- [Source: backend/app/services/user_birth_profile_service.py]
- [Source: backend/app/services/user_natal_chart_service.py]
- [Source: backend/app/api/v1/routers/users.py]
- [Source: backend/app/infra/db/models/user_birth_profile.py]
- [Source: backend/app/infra/db/repositories/user_birth_profile_repository.py]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Audit codebase backend réalisé en session (lecture complète de tous les fichiers référencés).
- `prepare_birth_data` avec `birth_time=None` utilise UTC minuit comme fallback pour le julian_day, en préservant la validation timezone.
- Le calcul du signe solaire est date-only (UTC minuit) ; l'ascendant utilise la date + heure complète (avec timezone).
- Le moteur existant (`calculators/natal.py`, `calculators/houses.py`) est réutilisé sans modification.
- Les 28 échecs de la suite d'intégration complète sont des régressions pré-existantes (LLM sans clé OpenAI, path Alembic, AuthenticatedUser incomplet dans test d'interprétation) — aucun rapport avec cette story.

### Completion Notes List

- **AC1 ✅** : `sun_sign_code` calculé date-only via UTC minuit → logique `(julian_day * 0.985647) % 360.0` identique au moteur.
- **AC2 ✅** : `ascendant_sign_code` non null pour `birth_time="14:30"` et `birth_time="00:00"`.
- **AC3 ✅** : `birth_time=null` → `ascendant_sign_code=null`, `missing_birth_time=true`.
- **AC4 ✅** : `birth_time="00:00"` explicite → ascendant calculé, `missing_birth_time=false`.
- **AC5 ✅** : `astro_profile` injecté dans GET `/birth-data` (via `UserBirthProfileWithAstroApiResponse`) et GET `/natal-chart/latest` (via dict enrichi). Aucun nouvel endpoint.
- 74 tests pertinents : 74 passent. 221 tests unitaires : 221 passent.
- Cohérence backend durcie:
  - validation indépendante `longitude in [cusp_house, cusp_next)` avec wrap `360 -> 0`.
  - convention bord explicitée: `longitude == cusp_end` appartient à la maison suivante.
  - assertions cuspides: 12 valeurs, finies, normalisées `[0,360)`, distinctes.
- Contrat metadata enrichi:
  - `metadata.house_system="equal"` ajouté aux réponses natal chart (en plus de `reference_version` et `ruleset_version`).
- Observabilité incohérence natale:
  - log `natal_inconsistent_result_detected` en warning avec sampling anti-spam.
  - compteur `natal_inconsistent_result_total` global + version labelisée (`reference_version`, `house_system`, `planet_code`).
- Cache référentiel:
  - cache déplacé côté `ReferenceDataService` et protégé par lock thread-safe.

### File List

- `_bmad-output/implementation-artifacts/18-1-astro-profile-backend-sun-sign-ascendant-null-time.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `backend/app/domain/astrology/natal_preparation.py`
- `backend/app/infra/db/models/user_birth_profile.py`
- `backend/app/infra/db/repositories/user_birth_profile_repository.py`
- `backend/app/services/user_birth_profile_service.py`
- `backend/app/services/user_astro_profile_service.py`
- `backend/app/api/v1/routers/users.py`
- `backend/migrations/versions/20260225_0022_birth_time_nullable.py`
- `backend/app/tests/unit/test_user_astro_profile_service.py`
- `backend/app/tests/integration/test_user_birth_profile_api.py`
- `backend/app/tests/integration/test_user_natal_chart_api.py`

## Change Log

- 2026-02-25 : Implémentation complète story 18-1 — `birth_time` nullable, service `UserAstroProfileService`, exposition `astro_profile` dans GET `/birth-data` et GET `/natal-chart/latest`, migration Alembic, 11 nouveaux tests unitaires + 8 nouveaux tests intégration.
- 2026-02-26 : Corrections post-story — cohérence maisons/cuspides, metadata `house_system`, observabilité `inconsistent_natal_result` (log sampling + métriques), cache référence thread-safe.
