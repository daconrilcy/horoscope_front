# Story 19.6: Rattacher le profil de naissance à `geo_place_resolved` (source-of-truth)

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a utilisateur,
I want que mon lieu de naissance soit mémorisé par une référence stable vers un lieu résolu,
so that mes calculs futurs restent identiques et plus précis.

## Acceptance Criteria

1. **Given** la sauvegarde d'un profil de naissance **When** un lieu résolu est confirmé **Then** le profil stocke `birth_place_resolved_id` (FK vers `geo_place_resolved`).
2. **Given** la lecture du profil utilisateur **When** l'API répond **Then** elle renvoie `birth_place_text` et un objet `birth_place_resolved` complet (ids provider, `display_name`, `latitude`, `longitude`, timezone si disponible).
3. **Given** un profil existant non migré **When** `birth_place_resolved_id` est null **Then** l'API reste compatible en renvoyant `birth_place_text` et `birth_place_resolved=null`.
4. **Given** une édition du lieu de naissance **When** l'utilisateur choisit un nouveau lieu **Then** le FK `birth_place_resolved_id` est remplacé par la nouvelle référence.
5. **Given** les calculs astrologiques **When** un `birth_place_resolved_id` est présent **Then** les coordonnées utilisées proviennent du lieu résolu référencé.
6. **Given** les calculs astrologiques accurate **When** le FK est absent **Then** le comportement est explicite: exigence FK (ou fallback temporaire lat/lon legacy documenté) **And** si le mode accurate exige le FK l'API de génération renvoie `422` avec `code=missing_birth_place_resolved` (pas de 500).

## Tasks / Subtasks

- [x] Task 1 — Étendre modèle profil de naissance (AC: 1, 3, 4)
  - [x] Migration ajoutant `birth_place_resolved_id` (+ FK) et `birth_place_text` si nécessaire.
  - [x] Mise à jour modèle SQLAlchemy et repository.
  - [x] Gestion de compatibilité pour anciens enregistrements.

- [x] Task 2 — Adapter API profil utilisateur (AC: 2, 3)
  - [x] Étendre schémas de réponse (`/v1/users/me/birth-data`).
  - [x] Retourner l'objet `birth_place_resolved`.
  - [x] Retourner explicitement `birth_place_resolved=null` pour profils legacy.
  - [x] Conserver `birth_timezone` user-facing et préparer l'alignement `timezone_iana`.

- [x] Task 3 — Brancher pipeline de calcul natal (AC: 5, 6)
  - [x] Priorité aux coordonnées du lieu résolu.
  - [x] Décider et documenter le comportement sans FK (exiger FK ou fallback legacy temporaire).
  - [x] Si exigence FK en mode accurate: renvoyer une erreur fonctionnelle `422 missing_birth_place_resolved`.

- [x] Task 4 — Tests (AC: 1, 2, 3, 4, 5, 6)
  - [x] Test upsert profil avec FK.
  - [x] Test GET profil renvoyant texte + objet résolu.
  - [x] Test GET profil legacy renvoyant `birth_place_resolved=null`.
  - [x] Test remplacement FK lors d'une édition.
  - [x] Test mode accurate sans FK: `422` avec `code=missing_birth_place_resolved`.

## Dev Notes

### Règles de données

- `birth_place_text` sert l'UX; `birth_place_resolved_id` sert la reproductibilité calculatoire.
- Ne pas casser les profils existants sans lieu résolu (migration progressive).
- Le contrat API doit conserver `birth_place_text` pour éviter une régression UX.

### Project Structure Notes

- `backend/app/infra/db/models/user_birth_profile.py`
- `backend/app/infra/db/repositories/user_birth_profile_repository.py`
- `backend/app/services/user_birth_profile_service.py`
- `backend/app/api/v1/routers/users.py`
- `backend/app/tests/`

### References

- [Source: _bmad-output/planning-artifacts/epic-19-comment-lire-theme-natal-dans-l-app.md]
- [Source: backend/app/services/user_birth_profile_service.py]
- [Source: backend/app/api/v1/routers/users.py]

## Dev Agent Record

### Agent Model Used

gpt-5-codex

### Debug Log References

- Story 19.6 créée pour établir une source-of-truth durable côté profil.

### Completion Notes List

- `birth_place_resolved_id` ajouté au modèle `user_birth_profiles` avec migration dédiée + FK nullable vers `geo_place_resolved`.
- API `GET /v1/users/me/birth-data` enrichie avec `birth_place_text`, `birth_place_resolved_id` et `birth_place_resolved` (objet complet ou `null` pour legacy).
- `PUT /v1/users/me/birth-data` valide désormais la présence du lieu résolu quand `place_resolved_id` est fourni.
- Pipeline natal: priorité aux coordonnées du lieu résolu quand FK présent; fallback legacy `birth_lat/birth_lon` conservé si FK absent.
- Mode `accurate` ajouté à `POST /v1/users/me/natal-chart`: renvoie `422` + `code=missing_birth_place_resolved` si FK absent.
- Validation exécutée: `ruff format .`, `ruff check .`, tests ciblés story (`71 passed`) + tests unitaires géo reliés (`90 passed` incluant `test_geo_place_resolved.py`).
- Suite backend complète lancée: échecs préexistants hors périmètre story (provider OpenAI non configuré et quelques tests de logs géocoding).
- Passe post-review exécutée: corrections des tests frontend alignées avec le flux `geocoding/search -> geocoding/resolve` et avec le payload `generateNatalChart` (`accurate` explicite).
- Validation finale post-fix: backend ciblé story (`72 passed`) et frontend ciblé story (`68 passed`).

### File List

- `_bmad-output/implementation-artifacts/19-6-rattachement-birth-profile-place-resolved.md`
- `backend/migrations/versions/20260226_0026_add_birth_place_resolved_fk_to_user_birth_profiles.py`
- `backend/app/infra/db/models/user_birth_profile.py`
- `backend/app/infra/db/repositories/user_birth_profile_repository.py`
- `backend/app/services/user_birth_profile_service.py`
- `backend/app/api/v1/routers/users.py`
- `backend/app/services/user_natal_chart_service.py`
- `backend/app/tests/unit/test_user_birth_profile_service.py`
- `backend/app/tests/unit/test_user_natal_chart_service.py`
- `backend/app/tests/integration/test_user_birth_profile_api.py`
- `backend/app/tests/integration/test_user_natal_chart_api.py`
- `backend/app/main.py`
- `frontend/src/api/birthProfile.ts`
- `frontend/src/api/geocoding.ts`
- `frontend/src/api/natalChart.ts`
- `frontend/src/pages/BirthProfilePage.tsx`
- `frontend/src/tests/BirthProfilePage.test.tsx`
- `frontend/src/tests/natalChartApi.test.tsx`

## Change Log

- 2026-02-26: Implémentation complète de la story 19.6 (FK profil → `geo_place_resolved`, enrichissement API profil, branchement pipeline natal, mode `accurate` avec erreur métier `missing_birth_place_resolved`, couverture de tests associée).
- 2026-02-26: Code Review Follow-up - Ajout des tests manquants (AC5 et mode dégradé), fix de la FK orpheline (logs), exposition de `accurate` côté Frontend.
- 2026-02-26: Passe de vérification post-review - correction des tests frontend (`BirthProfilePage`, `natalChartApi`) et validation ciblée backend/frontend sans échec.
