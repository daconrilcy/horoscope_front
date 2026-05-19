# Implementation Plan

1. Inspect existing reference seed and SQLAlchemy model patterns.
2. Add Alembic migration for the new dignity reference/runtime tables.
3. Add SQLAlchemy models in the existing model namespace.
4. Update reference repository seed defaults to load the new JSON files in FK-safe order.
5. Add repositories for dignity reference lookup and chart planet dignity result persistence.
6. Add targeted tests for migration schema, seed population and repository behavior.
7. Run validation commands and complete final evidence.
