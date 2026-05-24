# No Legacy / DRY Guardrails

## Canonical path

- Doctrine and school governance model: `backend/app/domain/astrology/runtime/astrology_doctrine_governance.py`
- Unit validation: `backend/tests/unit/domain/astrology/test_astrology_doctrine_governance.py`
- Reintroduction guard: `backend/tests/architecture/test_astrology_doctrine_governance_guardrails.py`
- API neutrality: `backend/tests/architecture/test_api_contract_neutrality.py`

## Forbidden surfaces confirmed

- No compatibility wrapper, shim, alias, fallback resolver, or duplicate active governance registry was added.
- Unknown rule family lookup raises `AstrologyDoctrineGovernanceError`.
- Duplicate or unknown declarations fail registry construction.
- `needs-user-decision` is preserved with blockers; no implicit doctrine choice is made.
- No frontend, API router, DB schema, migration, seed, narration, threshold, or weight behavior was changed.

## Negative evidence

- `rg -n "doctrine-governance|DoctrineGovernance" <existing api/frontend/alembic/db_seeder paths>` returned `PASS: no matches`.
- `backend\alembic` is absent, so the scan used existing paths only.
