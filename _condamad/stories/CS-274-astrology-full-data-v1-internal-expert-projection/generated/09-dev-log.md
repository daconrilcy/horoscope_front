# Dev Log

## Preflight

- Repository root: `C:\dev\horoscope_front`.
- Initial `git status --short`: dirty worktree already contained many modified/untracked files from prior stories; CS-274 files were not dirty before this run.
- Story registry row confirmed for `CS-274`, target path and source brief.
- Capsule was missing required generated files; repaired with `condamad_prepare.py --repair-generated-only` and validated with `condamad_validate.py`.
- Issue encountered: an initial prepare command created a case-only parallel capsule path; on Windows this removed the target folder during cleanup. The tracked target files were restored immediately with `git restore`, then the correct capsule repair was run.

## Search evidence

- Scoped source/dependency lookup covered CS-256, CS-271, CS-273, CS-266, CS-272 and the projection registry.
- Existing architecture guard already forbids `astrology_full_data` from public OpenAPI projection tokens.

## Implementation notes

- Created one canonical contract document: `docs/architecture/astrology-full-data-v1-contract.md`.
- Aligned existing projection registry with one internal-only row for `astrology_full_data`.
- Added targeted unit tests in `backend/tests/unit/test_astrology_full_data_contract.py`.
- No runtime builder, route, DB model, migration, frontend source, RBAC activation, serializer or generated client was added.

## Commands run

| Command | Result | Notes |
|---|---|---|
| `. .\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --root . --repair-generated-only _condamad\stories\CS-274-astrology-full-data-v1-internal-expert-projection --with-optional` | PASS | Capsule repaired. |
| `. .\.venv\Scripts\Activate.ps1; python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-274-astrology-full-data-v1-internal-expert-projection` | PASS | Capsule structure valid. |
| `. .\.venv\Scripts\Activate.ps1; ruff format backend\tests\unit\test_astrology_full_data_contract.py` | PASS | Scoped format. |
| `. .\.venv\Scripts\Activate.ps1; ruff check .` | PASS | Full lint. |
| `. .\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\unit\test_astrology_full_data_contract.py --tb=short` | PASS | 8 passed. |
| `. .\.venv\Scripts\Activate.ps1; python -B -m pytest -q backend\tests\architecture\test_api_contract_neutrality.py --tb=short` | PASS | 19 passed. |
| `. .\.venv\Scripts\Activate.ps1; python -B -m pytest -q --tb=short` | PASS | 3215 passed, 1 skipped, 1191 deselected. |

## Final `git status --short`

- CS-274 changed files: `docs/architecture/astrology-full-data-v1-contract.md`, `docs/architecture/official-product-primitives-public-projections.md`, `backend/tests/unit/test_astrology_full_data_contract.py`, CS-274 generated/evidence files.
- Pre-existing dirty app-root files remain recorded in `evidence/app-surface-status.txt`.
