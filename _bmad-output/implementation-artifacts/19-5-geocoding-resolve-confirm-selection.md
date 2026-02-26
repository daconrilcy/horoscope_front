# Story 19.5: Endpoint `POST /api/v1/geocoding/resolve` pour confirmer et persister le choix

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a système de profil natal,
I want un endpoint dédié pour confirmer le candidat choisi par l'utilisateur,
so that la place sélectionnée est persistée de façon canonique avant rattachement au profil.

## Acceptance Criteria

1. **Given** un body `{ provider, provider_place_id, snapshot? }` **When** `POST /api/v1/geocoding/resolve` est appelé **Then** le backend valide l'entrée et persiste/réutilise un `PlaceResolved`.
2. **Given** un `snapshot` fourni **When** la requête est validée **Then** `provider_place_id` est non vide, `lat/lon` sont valides, et `display_name` est une string exploitable.
3. **Given** un `snapshot` complet fourni **When** la requête est traitée **Then** le backend persiste directement sans nouvel appel upstream.
4. **Given** un `snapshot` absent **When** le backend traite la requête **Then** il appelle une stratégie unique `lookup/details` choisie, avec timeout strict et `retries=0`.
5. **Given** deux resolves simultanées sur la même place provider **When** elles sont traitées **Then** la réponse renvoie le même `PlaceResolved.id` (idempotence concurrente).
6. **Given** une persistance réussie **When** l'API répond **Then** la réponse contient l'objet `PlaceResolved` complet avec `id` interne.
7. **Given** BirthProfilePage **When** l'utilisateur confirme son lieu **Then** cette route est utilisée dans le flux normal.

## Tasks / Subtasks

- [ ] Task 1 — Créer contrat API `resolve` (AC: 1, 2, 6)
  - [ ] DTO request/response Pydantic.
  - [ ] Validation stricte des champs provider et identifiants.
  - [ ] Validation snapshot (`lat/lon`, `display_name`, `provider_place_id`).
  - [ ] Mapping d'erreurs cohérent (422/503/500 selon cas).

- [ ] Task 2 — Implémenter logique de persistance (AC: 1, 3, 4, 5)
  - [ ] Voie `snapshot` direct + validation.
  - [ ] Voie `provider_place_id` seul avec lookup/details.
  - [ ] Timeout strict upstream et retries=0.
  - [ ] Réutilisation entrée existante via contrainte unique.
  - [ ] Gérer concurrence pour garantir le même `id`.

- [ ] Task 3 — Intégrer frontend (AC: 7)
  - [ ] Brancher BirthProfilePage sur `resolve` au moment de la sélection.
  - [ ] Stocker l'id résolu côté flux de sauvegarde profil.
  - [ ] Gérer loading/error UX.

- [ ] Task 4 — Tests API/front (AC: 1, 2, 3, 4, 5, 6, 7)
  - [ ] Test resolve avec snapshot.
  - [ ] Test resolve sans snapshot (lookup provider mocké).
  - [ ] Test validation snapshot invalide (lat/lon/id/display_name).
  - [ ] Test concurrence: deux resolves simultanées => même `PlaceResolved.id`.
  - [ ] Test front: appel resolve puis sauvegarde profil avec FK.

## Dev Notes

### Contrat fonctionnel

- Endpoint cible: `POST /api/v1/geocoding/resolve`.
- Entrée minimale: `provider`, `provider_place_id`.
- `snapshot` facultatif pour éviter un second appel upstream.
- En absence de snapshot, choisir explicitement `lookup` ou `details` (pas les deux) pour simplifier le comportement.

### Project Structure Notes

- Backend:
  - `backend/app/api/v1/routers/`
  - `backend/app/services/`
  - `backend/app/infra/db/repositories/`
- Frontend:
  - `frontend/src/api/`
  - `frontend/src/pages/BirthProfilePage.tsx`
  - `frontend/src/tests/`

### References

- [Source: _bmad-output/planning-artifacts/epic-19-comment-lire-theme-natal-dans-l-app.md]
- [Source: _bmad-output/implementation-artifacts/19-2-backend-geocoding-search-proxy-nominatim.md]
- [Source: _bmad-output/implementation-artifacts/19-4-modele-db-geo-place-resolved.md]

## Dev Agent Record

### Agent Model Used

gpt-5-codex

### Debug Log References

- Story 19.5 créée pour formaliser le point de confirmation de sélection.

### Completion Notes List

- N/A (story de cadrage, non implémentée).

### File List

- `_bmad-output/implementation-artifacts/19-5-geocoding-resolve-confirm-selection.md`
