# Story 19.6: Rattacher le profil de naissance à `geo_place_resolved` (source-of-truth)

Status: ready-for-dev

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

- [ ] Task 1 — Étendre modèle profil de naissance (AC: 1, 3, 4)
  - [ ] Migration ajoutant `birth_place_resolved_id` (+ FK) et `birth_place_text` si nécessaire.
  - [ ] Mise à jour modèle SQLAlchemy et repository.
  - [ ] Gestion de compatibilité pour anciens enregistrements.

- [ ] Task 2 — Adapter API profil utilisateur (AC: 2, 3)
  - [ ] Étendre schémas de réponse (`/v1/users/me/birth-data`).
  - [ ] Retourner l'objet `birth_place_resolved`.
  - [ ] Retourner explicitement `birth_place_resolved=null` pour profils legacy.
  - [ ] Conserver `birth_timezone` user-facing et préparer l'alignement `timezone_iana`.

- [ ] Task 3 — Brancher pipeline de calcul natal (AC: 5, 6)
  - [ ] Priorité aux coordonnées du lieu résolu.
  - [ ] Décider et documenter le comportement sans FK (exiger FK ou fallback legacy temporaire).
  - [ ] Si exigence FK en mode accurate: renvoyer une erreur fonctionnelle `422 missing_birth_place_resolved`.

- [ ] Task 4 — Tests (AC: 1, 2, 3, 4, 5, 6)
  - [ ] Test upsert profil avec FK.
  - [ ] Test GET profil renvoyant texte + objet résolu.
  - [ ] Test GET profil legacy renvoyant `birth_place_resolved=null`.
  - [ ] Test remplacement FK lors d'une édition.
  - [ ] Test mode accurate sans FK: `422` avec `code=missing_birth_place_resolved`.

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

- N/A (story de cadrage, non implémentée).

### File List

- `_bmad-output/implementation-artifacts/19-6-rattachement-birth-profile-place-resolved.md`
