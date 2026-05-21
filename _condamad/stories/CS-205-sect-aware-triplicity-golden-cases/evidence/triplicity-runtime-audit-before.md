<!-- Audit runtime avant implementation CS-205. -->

# CS-205 Triplicity Runtime Audit Before

## Scope

- Story: `CS-205-sect-aware-triplicity-golden-cases`
- Runtime field: `AstrologyRuntimeReference.dignity_reference.triplicity_rulers`
- Canonical calculator: `EssentialDignityCalculator`
- Canonical orchestration: `PlanetDignityScoringService`
- Chart sect source: `ChartSectResult.chart_sect`

## Runtime load path

- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
  loads `triplicity_rulers` through `_load_triplicity_rulers`.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
  maps payload key `triplicity_rulers` to `TriplicityRulerReferenceData`.
- `backend/app/domain/astrology/runtime/runtime_reference.py` exposes
  `PlanetDignityReferenceSet.triplicity_rulers`.
- CS-205 uses `tests.unit.domain.astrology.fixtures.triplicity_seed_cases.seed_backed_triplicity_reference`
  to map the canonical seed JSON rows into `TriplicityRulerReferenceData`.

## Runtime assignments observed

The default unit fixture includes:

| Element | Sect | Planet | Role | System |
|---|---|---|---|---|
| fire | day | jupiter | principal | traditional |
| fire | all | saturn | participating | traditional |

This default unit fixture is recorded as historical context only. CS-205 golden
cases do not use it as the source of truth.

The CS-205 seed-backed fixture maps the canonical seed rows for fire as:

| Element | Sect | Planet | Role | System |
|---|---|---|---|---|
| fire | day | sun | primary | traditional |
| fire | night | jupiter | primary | traditional |
| fire | all | saturn | participating | traditional |

The persisted seed reference
`docs/db_seeder/astrology/astral_triplicity_ruler_assignments.json` contains
day, night and participating roles for fire, earth, air and water. CS-205 does
not modify that seed.

## Participant status

- Runtime participant role is present in the canonical seed as `sect_code == "all"` and
  `role_code == "participating"`.
- `EssentialDignityCalculator` applies any ruler whose `sect_code` is the active
  chart sect or `all`.
- The active `traditional_standard` profile scores `triplicity` with score `3`.
- Therefore the participant is supported and applied in the dedicated CS-205
  seed-backed fixture.

## Before state

- No dedicated CS-205 test module existed before implementation.
- No dedicated CS-205 persistent snapshot existed before implementation.
- Existing CS-200 G13/G14 tests are useful baseline evidence but are not a
  dedicated CS-205 evidence artifact.

## No-change expectations

- No production code change.
- No seed or migration change.
- No public JSON change.
- No score change except the new dedicated test assertions documenting current
  runtime behavior.
