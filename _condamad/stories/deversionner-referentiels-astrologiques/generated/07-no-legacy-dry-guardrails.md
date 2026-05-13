# No Legacy / DRY Guardrails

- Canonical structural tables: `planets(code)`, `signs(code)`, `houses(number)`, `aspects(code)`, `astro_points(code)`.
- Forbidden: preserving `reference_version_id` as an active column, FK, relationship, filter, clone key, or uniqueness dimension on structural tables.
- Required: versioned semantics live on parametric tables and rulesets only.
- Forbidden: compatibility clone path that duplicates stable structure rows for new reference versions.
- Required negative evidence:
  - no model field `reference_version_id` on `PlanetModel`, `SignModel`, `HouseModel`, `AspectModel`, `AstroPointModel`;
  - no repository filter by `PlanetModel.reference_version_id`, `SignModel.reference_version_id`, `HouseModel.reference_version_id`, `AspectModel.reference_version_id`, `AstroPointModel.reference_version_id`;
  - no seed call to clone stable structural rows for V2.
- Allowed historical references: old Alembic migrations and CONDAMAD story evidence may mention the former schema.
