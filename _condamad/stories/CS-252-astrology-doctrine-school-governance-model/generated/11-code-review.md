# CS-252 Implementation Review

Verdict: CLEAN

## Review Scope

- Story: `_condamad/stories/CS-252-astrology-doctrine-school-governance-model/00-story.md`.
- Source brief: `_story_briefs/cs-252-astrology-doctrine-school-governance-model.md`.
- Tracker row: `_condamad/stories/story-status.md` entry `CS-252`.
- Implementation: `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`.
- Tests: governance unit tests, architecture guard, and API neutrality checks.
- Evidence: CS-252 `evidence/` folder and `generated/10-final-evidence.md`.

## Findings

No actionable implementation issue remains.

Iteration 1 found stale review evidence: this file still described a pre-implementation drafting review and claimed a
`ready-to-dev` end state. The code, tests, story status, and tracker were already in implementation-review scope, so the stale
artifact was replaced by this implementation review and fresh validation evidence was added.

Iteration 2 found stale final-evidence wording: `generated/10-final-evidence.md` still said `Ready for review: yes` while
`00-story.md` and `_condamad/stories/story-status.md` were already `done`. The evidence status wording was corrected without
changing the brief, acceptance criteria, or implementation code.

## Acceptance Criteria Alignment

- AC1-AC2: all CS-240 rule families are declared once with source owner status and canonical owner fields.
- AC3: CS-241 F-003 weighting families expose mixed or DB ownership plus blockers where product decisions remain unresolved.
- AC4-AC6: doctrine decision status is separate from source ownership, transitions are enforced, and `needs-user-decision` is
  preserved with blockers.
- AC7: `test_astrology_doctrine_governance_guardrails.py` rejects unclassified threshold, weight, profile, school, or doctrine
  marker surfaces.
- AC8: governance entries keep future technique notes that cite CS-253 and traditional, modern, and forecasting use.
- AC9: API neutrality tests and runtime assertions prove the internal model is not exposed through routes or OpenAPI schemas.
- AC10: validation, before/after, guard, API neutrality, and review artifacts are present under the CS-252 capsule.

## Validation Evidence

Run from repository root after activating the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
ruff check backend
python -B -m pytest -q `
  backend\tests\unit\domain\astrology\test_astrology_doctrine_governance.py `
  backend\tests\architecture\test_astrology_doctrine_governance_guardrails.py `
  backend\tests\architecture\test_api_contract_neutrality.py
python -B -m pytest -q backend\tests
```

Result: PASS, 24 targeted tests passed; full backend suite PASS, 945 passed and 201 deselected.

```powershell
.\.venv\Scripts\Activate.ps1
python .agents\skills\condamad-story-writer\scripts\condamad_story_validate.py `
  _condamad\stories\CS-252-astrology-doctrine-school-governance-model\00-story.md
python .agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict `
  _condamad\stories\CS-252-astrology-doctrine-school-governance-model\00-story.md
```

Result: PASS.

Additional alignment validation after final-evidence correction:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format --check backend
```

Result: PASS, 1586 files already formatted.

```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH='backend'
python -B -c "from app.main import app; assert 'DoctrineGovernance' not in str(app.openapi())"
python -B -c "from app.main import app; assert not any('doctrine-governance' in getattr(r, 'path', '') for r in app.routes)"
```

Result: PASS.

```powershell
rg -n "doctrine-governance|DoctrineGovernance" backend\app\api frontend docs\db_seeder -g "*.py" -g "*.ts" -g "*.tsx" -g "*.json"
```

Result: PASS, no public exposure match.

## Guardrails

- RG-002: governance ownership stays under backend astrology runtime, not API, DB migration, frontend, or seed paths.
- RG-022: backend lint, tests, story validation, strict story lint, and persisted evidence are present.
- No registry propagation is required; the correction was local review-evidence staleness.

## Residual Risk

The architecture guard is intentionally strict: future astrology-domain files containing rule markers must be classified in
`GOVERNED_RULE_SOURCE_SURFACES`.
