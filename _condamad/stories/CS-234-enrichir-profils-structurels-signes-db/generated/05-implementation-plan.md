# Implementation Plan

## Architecture finding

`astral_sign_profiles` already owns canonical sign structure for element, modality, polarity and editorial keywords. The smallest coherent extension is to keep that owner and add dedicated structural taxonomies plus non-null profile references.

## Selected approach

- Extend `docs/db_seeder/astrology/astral_structural_reference_catalog.json` with sign structural rows and taxonomy code lists.
- Add SQLAlchemy taxonomy models and relationships in `backend/app/infra/db/models/reference.py`.
- Add Alembic migration `20260523_0137_enrich_astral_sign_profiles.py`.
- Update `ensure_astral_sign_profiles` to sync the new references from the structural catalog.
- Extend integration and unit tests for schema, codes and model contract.

## No Legacy stance

- No public JSON or frontend change.
- No local mapping in `backend/app/domain/astrology` or `backend/app/services/natal`.
- No old `signs` or `sign_rulerships` table restored.
