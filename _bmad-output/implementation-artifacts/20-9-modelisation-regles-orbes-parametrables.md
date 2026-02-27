# Story 20.9: Modélisation des règles d'orbes paramétrables

Status: done

## Story

As a astrologie-engine maintainer,
I want rendre les orbes d'aspects paramétrables dans la référence,
so that le calcul des aspects soit piloté par ruleset et non par une constante globale.

## Acceptance Criteria

1. **Given** une version de référence seedée **When** les aspects sont chargés **Then** chaque aspect majeur contient `angle` et `default_orb_deg`.
2. **Given** une configuration d'override d'orbe **When** elle est validée **Then** les valeurs invalides (<= 0 ou > 15) sont rejetées avec erreur explicite.
3. **Given** une version de référence existante **When** le seed/migration est exécuté **Then** aucune régression des codes aspects majeurs n'est introduite.

## Tasks / Subtasks

- [x] Task 1 (AC: 1, 3) Étendre le modèle de référence des aspects
  - [x] Ajouter `default_orb_deg` au modèle DB aspect + migration Alembic
  - [x] Définir les valeurs seed pour les 5 aspects majeurs
- [x] Task 2 (AC: 1) Exposer `default_orb_deg` dans le repository de référence
  - [x] Adapter les DTO/payloads retournés par `ReferenceRepository.get_reference_data`
- [x] Task 3 (AC: 2) Introduire la validation des règles d'orbe
  - [x] Ajouter validation centralisée des bornes d'orbe
  - [x] Mapper les erreurs en code métier explicite
- [x] Task 4 (AC: 1-3) Couverture tests
  - [x] Tests unitaires seed/référentiel (présence et validité des `default_orb_deg`)
  - [x] Test de rejet des valeurs invalides

### Review Follow-ups (AI)
- [ ] [AI-Review][MEDIUM] Intégrer `ReferenceDataService.validate_orb_overrides` dans un point d'entrée (API ou Service de calcul) lors de la story 20.10 ou 20.11.

## Dev Notes

- Point d'entrée actuel des aspects: `backend/app/infra/db/repositories/reference_repository.py`.
- Le calcul aval utilise `calculate_major_aspects`; cette story ne modifie pas encore la résolution d'orbe runtime.
- Conserver la compatibilité de lecture pour les payloads legacy sans `default_orb_deg` pendant transition.

### Project Structure Notes

- Backend uniquement sur cette story.
- Impact attendu: `infra/db/models`, `infra/db/repositories`, migration Alembic, tests unitaires.

### References

- [Source: _bmad-output/planning-artifacts/epic-20-orbes-parametrables-sidereal-topocentric.md#story-20-9--modèle-de-règles-daspects-paramétrables]
- [Source: backend/app/infra/db/repositories/reference_repository.py]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_reference_data_service.py app/tests/integration/test_reference_data_api.py app/tests/integration/test_reference_data_migrations.py`
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff format app/infra/db/models/reference.py app/infra/db/repositories/reference_repository.py app/services/reference_data_service.py app/tests/integration/test_reference_data_api.py app/tests/unit/test_reference_data_service.py migrations/versions/20260226_0027_add_default_orb_deg_to_aspects.py`
- `.\.venv\Scripts\Activate.ps1; cd backend; ruff check app/infra/db/models/reference.py app/infra/db/repositories/reference_repository.py app/services/reference_data_service.py app/tests/integration/test_reference_data_api.py app/tests/unit/test_reference_data_service.py migrations/versions/20260226_0027_add_default_orb_deg_to_aspects.py`
- `.\.venv\Scripts\Activate.ps1; cd backend; pytest -q` (échecs hors périmètre story: chat/guidance via provider OpenAI non configuré, geocoding cache logs)

### Completion Notes List
- Ajout de `default_orb_deg` au modèle `aspects` avec migration Alembic dédiée (`20260226_0027`).
- Seed de référence enrichi pour les 5 aspects majeurs avec orbes par défaut: conjunction 8, sextile 4, square 6, trine 6, opposition 8.
- `ReferenceRepository.get_reference_data` expose désormais `default_orb_deg` dans le payload `aspects`.
- Fix review: seed des 12 signes zodiacaux (plus seulement 2) pour fiabiliser le fallback `simplified`.
- Fix review: `ReferenceRepository.get_reference_data` reconstruit aussi les règles hiérarchiques persistées (`orb_luminaries`, `orb_pair_overrides`) depuis `astro_characteristics` (`entity_type="aspect"`).
- Ajout d’une validation centralisée `ReferenceDataService.validate_orb_overrides` avec bornes strictes `0 < orb <= 15` et erreur métier `invalid_orb_override`.
- Couverture tests ajoutée/étendue pour présence de `default_orb_deg`, stabilité des codes d’aspects majeurs et rejet des overrides invalides.

### File List
- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/services/reference_data_service.py`
- `backend/app/tests/integration/test_reference_data_api.py`
- `backend/app/tests/unit/test_reference_data_service.py`
- `backend/migrations/versions/20260226_0027_add_default_orb_deg_to_aspects.py`

### Change Log
- 2026-02-26: Implémentation complète story 20-9 (modèle DB + migration + repository + validation orbes + tests).
- 2026-02-26: Revue de code (AI) - Correction de la migration non suivie, consolidation des constantes d'orbes et amélioration de la sécurité du schéma (server_default).
- 2026-02-27: Correctifs post-review - seed 12 signes + exposition des traits d'orbes hiérarchiques persistés (`orb_luminaries`/`orb_pair_overrides`) dans le payload de référence.

## Senior Developer Review (AI)

### Findings Summary
- **Migration Suivie** [FIXED]: Le fichier de migration était orphelin, il a été ajouté au suivi Git.
- **Consolidation des Constantes** [FIXED]: Création de `app/core/constants.py` pour centraliser les orbes par défaut et éviter la duplication.
- **Sécurité du Schéma** [FIXED]: Ajout d'un `server_default` dans la migration pour garantir l'intégrité des futures données.
- **Messages d'Erreur** [FIXED]: Amélioration de la précision des messages de validation des orbes.
- **Dead Code (Validation)** [ACTION REQUIRED]: La méthode `validate_orb_overrides` est prête mais n'est pas encore consommée par une API.

### Outcome: Approved with follow-up
Les correctifs critiques ont été appliqués. Le code est robuste et prêt pour la suite de l'Epic 20.
