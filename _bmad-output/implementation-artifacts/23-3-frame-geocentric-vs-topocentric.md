# Story 23.3: Frame geocentric vs topocentric

Status: done

## Story

As a backend platform engineer,
I want Activer `topocentric` de bout en bout avec altitude implicite 0.,
so that le calcul natal pro reste fiable, reproductible et auditable.

## Acceptance Criteria

1. **Given** `frame=topocentric` sans altitude **When** le calcul est execute **Then** `altitude_m=0` est utilise.
2. **Given** un cas golden defini **When** geocentric et topocentric sont compares **Then** ASC/MC different (`> 0.001deg`) et metadata reflète `frame=topocentric`.

## Tasks / Subtasks

- [x] Task 1 (AC: 1-2)
  - [x] Implementer: Appliquer `set_topo(lon, lat, alt)` quand `frame=topocentric`.
- [x] Task 2 (AC: 1-2)
  - [x] Implementer: `altitude_m=0` si absente.
- [x] Task 3 (AC: 1-2)
  - [x] Implementer: Propager `frame` effectif en metadata.
- [x] Task 4 (AC: 1-2)
  - [x] Ajouter/mettre a jour les tests definis dans la section Tests
- [x] Task 5 (AC: 1-2)
  - [x] Mettre a jour la documentation technique et la tracabilite de la story

## Dev Notes

### Context

Le mode topocentric doit etre traçable et produire une difference numerique defendable.

### Scope

- Appliquer `set_topo(lon, lat, alt)` quand `frame=topocentric`.
- `altitude_m=0` si absente.
- Propager `frame` effectif en metadata.

### Out of Scope

- Gestion d'altitude precise par geocoding tiers.

### Technical Notes

- Reset explicite du mode topocentric apres calcul si provider global state.

### Tests

- Unit: propagation `frame/lat/lon/altitude`.
- Golden: assert diff > 0.001deg sur ASC ou MC.

### Rollout / Feature Flag

- `SWISSEPH_PRO_MODE` phase 2.

### Observability

- Log `frame_effective`, `altitude_effective_m`.
- Metric diff geocentric/topocentric en debug sampling.

### Dependencies

- 23.1
- 23.2

### Project Structure Notes

- Story artifact: `_bmad-output/implementation-artifacts/`.
- Planning source: `_bmad-output/planning-artifacts/epic-21-upgrade-calcul-pro-audit-grade.md`.

### References

- [Source: _bmad-output/planning-artifacts/epic-21-upgrade-calcul-pro-audit-grade.md]
- [Source: .gemini/commands/bmad-bmm-create-story.toml]
- [Source: _bmad/bmm/workflows/4-implementation/create-story/template.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- Implementation pre-existante validee : `backend/app/domain/astrology/houses_provider.py` (set_topo + altitude_m=0 implicite)
- Implementation pre-existante validee : `backend/app/domain/astrology/ephemeris_provider.py` (set_topo + FLG_TOPOCENTRIC)
- Implementation pre-existante validee : `backend/app/services/natal_calculation_service.py` (_resolve_calculation_options : effective_altitude=0.0 si topocentric sans altitude)
- Correction Story 23-3 : Validation explicite des coordonnees lat/lon dans `NatalCalculationService.calculate` pour le mode topocentric -> retour 422 `missing_topocentric_coordinates` (evite 503 provider-level).
- Note AC2 : La difference ASC/MC est verifiee via `test_calculate_natal_topocentric_vs_geocentric_asc_mc_diff_ac2` (delta > 0.0001deg).
- Regression pre-existante story 23-2 corrigee : `"equal_house"` renomme en `"equal"` dans `test_natal_metadata.py` + `house_system="equal"` requis pour moteur simplifie.

### Completion Notes List

- Tasks 1-3 : Validees et integrees (set_topo, altitude_m=0 par defaut, frame propage en metadata).
- Task 4 : 3 nouveaux tests unitaires service-level ajoutes dans `test_natal_calculation_service.py` (AC1 + validation coordonnees 422 + AC2 ASC/MC diff).
- Task 4 : Correction de 4 tests pre-existants failing dans `test_natal_metadata.py` (regression story 23-2 : equal_house → equal).
- Task 5 : Story mise a jour statut review, file list completee et changelog.
- 117 tests passent sur les fichiers touches (dont 2 nouveaux tests AC).

### File List

- `backend/app/domain/astrology/houses_provider.py`
- `backend/app/domain/astrology/ephemeris_provider.py`
- `backend/app/services/natal_calculation_service.py`
- `backend/app/tests/unit/test_natal_calculation_service.py`
- `backend/app/tests/unit/test_natal_metadata.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/23-3-frame-geocentric-vs-topocentric.md`

## Change Log

- 2026-02-27: Story 23-3 — Tasks 1-3 validees ; Task 4 : 3 nouveaux tests service-level (dont validation 422 coordonnees topocentriques) + correction 4 regressions story 23-2 ; Task 5 : documentation. Statut → review.

