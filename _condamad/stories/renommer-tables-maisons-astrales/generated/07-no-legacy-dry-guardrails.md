# No Legacy / DRY Guardrails

## Canonical SQL names

- `astral_houses`
- `astral_prediction_daily_house_profiles`
- `astral_house_category_weights`

## Forbidden active legacy names

- `__tablename__ = "houses"`
- `__tablename__ = "house_profiles"`
- `__tablename__ = "house_category_weights"`
- `ForeignKey("houses.id")`
- Head-schema tests asserting the old SQL names exist.

## Allowed historical references

- Earlier Alembic migrations that created or transformed the historical schema.
- Downgrade body of the new rename migration.
- CONDAMAD story/evidence files.
- Runtime JSON or Python domain fields named `houses`, `house_profiles`, or `house_category_weights` when they are not SQL table names.

## Required evidence

- Targeted pytest for model/repository and migrations.
- Negative scan for active SQL old names in `backend/app` and active tests.
- Diff review confirming no alias, shim, fallback, or duplicate table path.

## Review checklist

- One active SQL name per renamed table.
- Foreign keys point to `astral_houses.id`.
- Existing Python public object names are unchanged where they are domain concepts.
- No compatibility table, view, dual-read, or fallback is introduced.
