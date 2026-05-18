# No Legacy / DRY Guardrails

- No hardcoded `PLANET_BODY_TYPES` constant in backend runtime code.
- No hardcoded `ASTROLOGICAL_ANGLE_POINT_CODES` in `aspect_reference.py`.
- Planet body classification must flow from DB-backed `planet_profiles.is_planet` and `class_code`.
- Angle point classification must flow from DB-backed `PredictionContext.angle_points`.
- Seed source remains the documented JSON; no duplicate requirements file or alternate seed path.

Negative evidence command:

```powershell
rg -n "PLANET_BODY_TYPES|ASTROLOGICAL_ANGLE_POINT_CODES" backend\app -g "*.py"
```
