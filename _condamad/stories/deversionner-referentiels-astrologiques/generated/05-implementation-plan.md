# Implementation Plan

1. Update structural SQLAlchemy models to remove `reference_version_id`, relationships to `ReferenceVersionModel`, and locked-version update hooks.
2. Add `reference_version_id` to profiles and point/aspect/profile tables that currently depend on structural version filtering, while keeping stable FK references to structure rows.
3. Rewrite reference and prediction repositories so structural queries are global and versioned queries filter their own versioned tables.
4. Rewrite the prediction seed repair path to purge versioned rows only and ensure stable structural defaults exist without cloning them per version.
5. Add Alembic migration that deduplicates structural rows, remaps FKs, adds version columns to profile tables, drops structural version columns, and creates stable unique constraints.
6. Update tests and add architecture/schema guards for no structural `reference_version_id`.
7. Run targeted tests, No Legacy scans, ruff format/check, and broader backend tests if feasible.

Rollback: Alembic downgrade recreates structural version columns and versioned uniqueness, with stable rows assigned to the first available reference version.
