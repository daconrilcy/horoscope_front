# Story Candidates - backend-tests

## SC-001 - Standardize backend pytest discovery

- Source finding: F-001
- Suggested story title: Collect every retained backend test in the standard pytest command
- Suggested archetype: test-guard-hardening
- Primary domain: backend tests
- Required contracts: pytest discovery, backend test command, regression guardrails RG-001..RG-009
- Draft objective: Ensure all retained backend test files are either collected by default or explicitly documented as opt-in suites.
- Must include: update `backend/pyproject.toml` or move files; remove missing `app/ai_engine/tests` entry or recreate it intentionally; prove zero retained tests sit outside default collection.
- Validation hints: `.\.venv\Scripts\Activate.ps1; cd backend; pytest --collect-only -q --ignore=.tmp-pytest`; static comparison of all `test_*.py` files against `testpaths`.
- Blockers: Confirm whether CI uses plain `pytest` from `backend` or a custom test target.

## SC-002 - Define canonical backend test topology

- Source finding: F-002
- Suggested story title: Converge backend test roots into a documented topology
- Suggested archetype: test-suite-topology-convergence
- Primary domain: backend tests
- Required contracts: monorepo test layout, backend architecture reference
- Draft objective: Reduce active backend test roots to a clear unit/integration/regression topology.
- Must include: decide canonical root names; migrate embedded domain tests; document allowed roots; add a guard that fails on unapproved test roots.
- Validation hints: `rg --files backend -g test_*.py -g *_test.py -g !backend/.tmp-pytest/**` grouped by parent directory.
- Blockers: None if the canonical topology is `backend/app/tests` plus explicitly scoped support roots; otherwise needs user architecture decision.

## SC-003 - Converge DB test fixtures

- Source finding: F-003
- Suggested story title: Replace global DB session monkeypatches with explicit test fixtures
- Suggested archetype: test-harness-convergence
- Primary domain: backend tests DB harness
- Required contracts: SQLite alignment fixture, Alembic head check, no direct production `SessionLocal` imports in tests
- Draft objective: Make DB-backed tests use one explicit session factory and remove legacy global rewiring.
- Must include: inventory direct `SessionLocal` imports; provide a canonical DB fixture/helper; migrate representative files first; preserve `ensure_configured_sqlite_file_matches_alembic_head` behavior.
- Validation hints: scan for `from app.infra.db.session import SessionLocal, engine`; run targeted DB integration tests; run full collect.
- Blockers: Some legacy tests may require staged migration before the global monkeypatch can be removed.

## SC-004 - Reclassify story-numbered regression guards

- Source finding: F-004
- Suggested story title: Rename and map story tests to durable backend invariants
- Suggested archetype: legacy-guard-convergence
- Primary domain: backend tests
- Required contracts: regression guardrails RG-001..RG-009, No Legacy / DRY audit contract
- Draft objective: Keep valuable no-regression protection while removing historical story-number ownership from active suite names.
- Must include: classify each `test_story_*.py` as keep, merge, rewrite, or remove-candidate; map kept tests to a durable invariant; preserve No Legacy guards before deleting any legacy test.
- Validation hints: zero unclassified `test_story_*.py` files; updated guard registry or audit trace; full collect remains stable.
- Blockers: Removal of legacy-compat tests needs product or architecture approval when the protected surface is still active.

## SC-005 - Extract shared test helpers from test modules

- Source finding: F-005
- Suggested story title: Remove cross-test-module imports
- Suggested archetype: test-helper-dry-convergence
- Primary domain: backend tests helpers
- Required contracts: DRY test helper ownership, pytest fixture boundaries
- Draft objective: Move reused builders and cleanup helpers from executable test modules into dedicated helper or fixture modules.
- Must include: replace the 9 current cross-test imports; keep helper names explicit; avoid importing executable test files from other test files.
- Validation hints: `rg -n "from app.tests.integration.test_|from app.tests.unit.test_|from app.tests.regression.test_|from tests.integration.test_" backend/app/tests backend/tests -g test_*.py` returns no hits.
- Blockers: None expected.

## SC-006 - Remove or implement no-op seed validation test

- Source finding: F-006
- Suggested story title: Replace the seed validation facade test with executable behavior
- Suggested archetype: facade-test-removal
- Primary domain: backend tests
- Required contracts: seed validation behavior, pytest assertion policy
- Draft objective: Ensure seed validation coverage either enforces the intended error or is removed as obsolete.
- Must include: decide expected seed validation outcome; add assertion or `pytest.raises`; delete the facade if the requirement no longer applies.
- Validation hints: targeted run for `backend/app/tests/unit/test_seed_validation.py`; scan for `assert True` and bare `pass` in tests.
- Blockers: Need confirmation whether required persona empty values are still a product rule.
