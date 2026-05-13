# House Strength Contract After CS-160

## Runtime shape after implementation

- `HouseStrengthRuntimeData` is a frozen dataclass.
- Runtime fields:
  - `normalized_score: float`
  - `dominant: bool`
  - `reasons: tuple[HouseStrengthReason, ...]`
  - `level: HouseStrengthLevel`
  - `modifiers: HouseStrengthModifiers`
- `score` remains available as a property returning `normalized_score` for the
  stable public JSON field `strength.score`.

## Canonical reasons

- `HouseStrengthReason.BASELINE_HOUSE`
- `HouseStrengthReason.ANGULAR_HOUSE`
- `HouseStrengthReason.SUCCEDENT_HOUSE`
- `HouseStrengthReason.CADENT_HOUSE`
- `HouseStrengthReason.OCCUPANTS_PRESENT`
- `HouseStrengthReason.STELLIUM_PRESENT`
- `HouseStrengthReason.LUMINARY_PRESENT`
- `HouseStrengthReason.RULER_IN_ANGULAR_HOUSE`
- `HouseStrengthReason.RULER_IN_OWN_SIGN`
- `HouseStrengthReason.ASC_ANGLE_PROXIMITY`
- `HouseStrengthReason.MC_ANGLE_PROXIMITY`

## Baseline comparison

- Dominant angular stellium fixture:
  - before score: `1.0`
  - after normalized score / public score: `1.0`
  - after level: `dominant`
- Empty cadent fixture:
  - before score: `0.05`
  - after normalized score / public score: `0.05`
  - after level: `low`

## Public serialization

- `strength.score` remains numeric and stable.
- `strength.reasons` remains a list of string values.
- `strength.level` is added as a compatible qualitative field.
