# Story 20.9: Modélisation des règles d'orbes paramétrables

Status: ready-for-dev

## Story

As a astrologie-engine maintainer,
I want rendre les orbes d'aspects paramétrables dans la référence,
so that le calcul des aspects soit piloté par ruleset et non par une constante globale.

## Acceptance Criteria

1. **Given** une version de référence seedée **When** les aspects sont chargés **Then** chaque aspect majeur contient `angle` et `default_orb_deg`.
2. **Given** une configuration d'override d'orbe **When** elle est validée **Then** les valeurs invalides (<= 0 ou > 15) sont rejetées avec erreur explicite.
3. **Given** une version de référence existante **When** le seed/migration est exécuté **Then** aucune régression des codes aspects majeurs n'est introduite.

## Tasks / Subtasks

- [ ] Task 1 (AC: 1, 3) Étendre le modèle de référence des aspects
  - [ ] Ajouter `default_orb_deg` au modèle DB aspect + migration Alembic
  - [ ] Définir les valeurs seed pour les 5 aspects majeurs
- [ ] Task 2 (AC: 1) Exposer `default_orb_deg` dans le repository de référence
  - [ ] Adapter les DTO/payloads retournés par `ReferenceRepository.get_reference_data`
- [ ] Task 3 (AC: 2) Introduire la validation des règles d'orbe
  - [ ] Ajouter validation centralisée des bornes d'orbe
  - [ ] Mapper les erreurs en code métier explicite
- [ ] Task 4 (AC: 1-3) Couverture tests
  - [ ] Tests unitaires seed/référentiel (présence et validité des `default_orb_deg`)
  - [ ] Test de rejet des valeurs invalides

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

### Completion Notes List

### File List
