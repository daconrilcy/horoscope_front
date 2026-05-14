<!-- Carte des fichiers et recherches cibles pour CS-162. -->

# Target Files

## Must read

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/tests/unit/test_aspect_orb_overrides.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `backend/app/tests/unit/test_reference_data_service.py`
- `backend/app/tests/integration/test_seed_31_prediction_v2.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `docs/recherches astro/astral_aspect_orb_rules.json`
- `docs/recherches astro/tables-aspects-et-roles.md`
- `docs/recherches astro/tables-maisons-et-roles.md`
- `docs/recherches astro/tables-planetes-et-roles.md`

## Must search

- `rg -n "copy_rules_from|inherits_from|astral_system_code" "docs/recherches astro/astral_aspect_orb_rules.json"`
- `rg -n "astral_aspect_orb_rules|astral_systems|159|79|inherits|copy_rules_from" backend/app/tests`
- `rg -n "app\.domain\.prediction|app\.services\.prediction" backend/app/domain/astrology -g "*.py"`
- `rg -n "astro_characteristics|AstroCharacteristicModel" backend/app backend/tests`

## Likely modified

- `backend/app/infra/db/models/reference.py`
- `backend/migrations/versions/20260514_0105_add_astral_system_inheritance.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/tests/unit/test_aspect_orb_overrides.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `backend/app/tests/unit/test_reference_data_service.py`
- `backend/app/tests/integration/test_seed_31_prediction_v2.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `docs/recherches astro/astral_aspect_orb_rules.json`
- `docs/recherches astro/tables-aspects-et-roles.md`
- `docs/recherches astro/tables-maisons-et-roles.md`
- `docs/recherches astro/tables-planetes-et-roles.md`
- `_condamad/stories/CS-162-heriter-regles-orbes-systemes-astrologiques/*.md`
- `_condamad/stories/CS-162-heriter-regles-orbes-systemes-astrologiques/generated/*.md`

## Forbidden unless justified

- `frontend/**`
- `backend/app/domain/prediction/**`
- `backend/app/services/chart/json_builder.py`
- `backend/app/api/**`
- New Python dependency files or `requirements.txt`
