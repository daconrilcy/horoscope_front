# Validation Evidence

Date: 2026-05-24

Environment:

- Repository root: `C:\dev\horoscope_front`
- Python commands run after `.\.venv\Scripts\Activate.ps1`
- `PYTHONPATH=backend` set where application imports required it

Commands:

- Capsule prepare command: PASS, generated a derived capsule; generated files copied into the target CS-252 capsule.
- Capsule validate command: PASS.
- Targeted `ruff format` command on modified Python files: PASS.
- Targeted governance/API pytest command: PASS, 24 passed.
- `ruff check backend`: PASS.
- Full backend pytest command: PASS, 945 passed and 201 deselected.
- OpenAPI schema assertion: PASS.
- Route assertion: PASS.
- Governance status scan: PASS, statuses found in canonical runtime model and tests.
- Public exposure scan on existing API/frontend/db-seeder paths: PASS, no matches.
- Future temporal technique citation scan: PASS.
- Rule marker scan: PASS, markers are governed by the AST guard and registry.

Notes:

- `backend\alembic` does not exist in this repository; the negative public-exposure scan was run on existing paths only.
- No frontend, DB schema, migration, seed, API route, auth, i18n, style, build, narration, threshold, or weight value was changed.

## Review/fix validation — 2026-05-24

Finding corrected:

- Replaced stale pre-implementation draft review evidence with a fresh implementation review in
  `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/generated/11-code-review.md`.
- Corrected `generated/10-final-evidence.md` so its status wording matches the `done` status in the story and tracker.

Commands run after `.\.venv\Scripts\Activate.ps1`:

- `ruff check backend`: PASS.
- Targeted governance/API pytest command: PASS, 24 passed.
- Full backend pytest command: PASS, 945 passed and 201 deselected.
- Story validation: PASS.
- Strict story lint: PASS.
- Runtime OpenAPI and route assertions: PASS.
- Public exposure scan for `doctrine-governance|DoctrineGovernance`: PASS, no matches.

## Brief alignment validation — 2026-05-24

Commands run after `.\.venv\Scripts\Activate.ps1`:

- Story validation: PASS.
- Strict story lint: PASS.
- `ruff check backend`: PASS.
- `ruff format --check backend`: PASS, 1586 files already formatted.
- Targeted governance/API pytest command: PASS, 24 passed.
- Runtime OpenAPI and route assertions: PASS.
- Public exposure scan for `doctrine-governance|DoctrineGovernance`: PASS, no matches.
