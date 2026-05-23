# Target Files

## Must inspect before implementation

- `AGENTS.md` files in scope
- Files and directories named by `../00-story.md`
- Existing tests near the affected code

## Required searches before editing

```bash
rg "<main symbol or feature name>" .
rg "legacy|compat|shim|fallback|deprecated|alias" .
```

Adapt searches to the story and repository layout.

## Likely modified files

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/__init__.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/migrations/versions/20260523_0137_enrich_astral_sign_profiles.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `docs/db_seeder/astrology/astral_structural_reference_catalog.json`
- `_condamad/stories/CS-234-enrichir-profils-structurels-signes-db/evidence/**`

## Forbidden or high-risk files

- `frontend/src/**` - out of scope.
- `backend/app/domain/astrology/**` - no local structural mapping.
- `backend/app/services/natal/**` - no local structural mapping.
- `backend/app/api/**` - no API/public JSON change.
