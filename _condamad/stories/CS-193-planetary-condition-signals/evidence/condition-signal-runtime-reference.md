# Condition Signal Runtime Reference Evidence

## Source Of Truth

- Table: `astral_planet_condition_signal_profiles`
- Model: `AstralPlanetConditionSignalProfileModel`
- Runtime contract: `PlanetConditionSignalProfileReferenceData`
- Runtime field: `AstrologyRuntimeReference.condition_signal_profiles`
- Seed source: `docs/db_seeder/astrology/astral_planet_condition_signal_profiles.json`

## Runtime Rows

The seed contains eight governed profiles covering the CS-192 axes:

| Axis | Signal code | Range | Use | Priority |
|---|---|---|---|---:|
| `functional_strength` | `functional_strength_high` | `[1.0, 100.0]` | `prioritize_condition_axis` | 10.0 |
| `functional_strength` | `functional_strength_low` | `[-100.0, -0.5]` | `qualify_condition_axis` | 20.0 |
| `visibility` | `visibility_high` | `[0.5, 100.0]` | `surface_condition_axis` | 30.0 |
| `stability` | `stability_high` | `[0.5, 100.0]` | `stabilize_condition_axis` | 40.0 |
| `intensity` | `intensity_high` | `[1.0, 100.0]` | `weight_condition_axis` | 50.0 |
| `coherence` | `coherence_high` | `[0.5, 100.0]` | `align_condition_axis` | 60.0 |
| `support` | `support_high` | `[0.5, 100.0]` | `support_condition_axis` | 70.0 |
| `constraint` | `constraint_high` | `[0.5, 100.0]` | `temper_condition_axis` | 80.0 |

## Validation

- `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py` passed with 22 tests.
- `pytest --long -q backend/app/tests/integration/test_reference_data_migrations.py` passed with 5 tests.
- Runtime integrity rejects `condition_axis="expression_quality"` because this axis is not present on `PlanetConditionProfile`.
