<!-- Plan de validation executable pour CS-162. -->

# Validation Plan

## Environment assumptions

- OS: Windows / PowerShell.
- Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Backend working directory for Python commands: `backend`.

## Targeted checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Resolver and orb inheritance | `pytest -q app/tests/unit/test_aspect_orb_overrides.py app/tests/unit/test_prediction_reference_repository.py` | `backend` | yes | all tests pass |
| Reference payload and seed contract | `pytest -q app/tests/unit/test_reference_data_service.py app/tests/integration/test_seed_31_prediction_v2.py` | `backend` | yes | all tests pass |
| Alembic schema and migration guard | `pytest -q app/tests/integration/test_reference_data_migrations.py` | `backend` | yes | all tests pass |

## Architecture / import guards

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| No `copy_rules_from` in active JSON | `rg -n "copy_rules_from" "..\docs\recherches astro\astral_aspect_orb_rules.json"` | `backend` | yes | zero hits |
| Astrology domain does not import prediction | `rg -n "app\.domain\.prediction|app\.services\.prediction" app/domain/astrology -g "*.py"` | `backend` | yes | zero hits |
| RG-091 classification scan | `rg -n "astro_characteristics|AstroCharacteristicModel" app tests` | `backend` | yes | only expected guard/test references |

## Documentation scans

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Aspect doc inheritance title | `rg -n "Héritage des systèmes astrologiques" "..\docs\recherches astro\tables-aspects-et-roles.md"` | `backend` | yes | at least one hit |
| House doc inheritance title | `rg -n "Héritage des systèmes astrologiques" "..\docs\recherches astro\tables-maisons-et-roles.md"` | `backend` | yes | at least one hit |
| Planet doc inheritance title | `rg -n "Héritage des systèmes astrologiques" "..\docs\recherches astro\tables-planetes-et-roles.md"` | `backend` | yes | at least one hit |
| System mappings in docs | `rg -n "hellenistic.*traditional|medieval.*traditional" "..\docs\recherches astro\tables-aspects-et-roles.md" "..\docs\recherches astro\tables-maisons-et-roles.md" "..\docs\recherches astro\tables-planetes-et-roles.md"` | `backend` | yes | expected mappings present |

## Quality checks

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Format | `ruff format .` | `backend` | yes | no format errors |
| Lint | `ruff check .` | `backend` | yes | no lint errors |

## Diff review

| Purpose | Command | Working directory | Required | Expected result |
|---|---|---|---:|---|
| Whitespace/conflict markers | `git diff --check` | repo root | yes | no errors |
| Diff scope | `git diff --stat` | repo root | yes | only story files changed |
| Worktree status | `git status --short` | repo root | yes | expected story changes only |

## Commands that may be skipped only with justification

- Full `pytest -q` from `backend` may be skipped if targeted integration coverage is complete and runtime is prohibitive; record risk if skipped.
