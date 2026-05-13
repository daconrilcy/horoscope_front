# House Strength Contract Before CS-160

## Runtime shape observed before implementation

- `HouseStrengthRuntimeData` fields:
  - `score: float`
  - `dominant: bool`
  - `reasons: list[str]`
- No qualitative `level` field exists.
- `score` is used as a float but the runtime field name does not state that the
  scale is normalized.

## Reason literals observed

- `baseline_house`
- `angular_house`
- `succedent_house`
- `cadent_house`
- `occupants_present`
- `stellium_present`
- `luminary_present`
- `ruler_in_angular_house`
- `ruler_in_own_sign`
- `asc_angle_proximity`
- `mc_angle_proximity`

## Baseline examples

- Dominant angular stellium fixture: score `1.0`, dominant `True`.
- Empty cadent fixture: score `0.05`, dominant `False`.
