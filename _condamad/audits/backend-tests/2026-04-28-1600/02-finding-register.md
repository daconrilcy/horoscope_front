# Finding Register - backend-tests

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | High | High | missing-guard | backend tests | E-003, E-004 | 304 static tests in 64 files are outside default pytest collection, including LLM and architecture guards. | Converge pytest discovery: either move these files under configured roots or update `testpaths` and CI so every retained test is collected by the standard backend command. | yes |
| F-002 | High | High | missing-canonical-owner | backend tests | E-001, E-003, E-004 | The suite has no single ownership model: active tests live under `backend/app/tests`, `backend/tests`, and an embedded domain test folder. | Define one canonical backend test topology and migrate non-canonical roots with compatibility only through explicit, temporary story scope. | yes |
| F-003 | High | High | data-integrity-risk | backend tests DB harness | E-007 | Global DB monkeypatching and multiple SQLite setup strategies make isolation hard to reason about and preserve legacy direct imports. | Centralize DB fixtures around one session/engine access pattern; remove direct `SessionLocal` imports from tests before removing the global monkeypatch. | yes |
| F-004 | Medium | High | legacy-surface | backend tests | E-005, E-010 | Story-numbered and legacy-heavy tests preserve valuable guardrails but obscure whether they still protect current application behavior or old migration states. | Reclassify story tests into canonical guard suites, keep the invariants mapped to RG-001..RG-009, and retire only tests whose protected surface has an approved replacement. | yes |
| F-005 | Medium | High | duplicate-responsibility | backend tests helpers | E-008 | Test modules import helpers from other test modules, which couples suite order and makes helper ownership implicit. | Extract reused builders/helpers into dedicated `helpers` or fixture modules and remove cross-test-module imports. | yes |
| F-006 | Medium | High | missing-test-coverage | backend tests | E-006 | `test_seed_validation_required_persona_empty_allowed` is a facade that always passes while documenting missing implementation. | Replace it with a real assertion against the intended seed validation behavior, or delete it if the requirement is obsolete. | yes |
| F-007 | Low | Medium | needs-user-decision | backend tests operational scope | E-009 | Some backend tests validate docs, PR templates, scripts, and pipeline behavior; these may be valid but they blur application-test ownership. | needs-user-decision: decide whether these remain in backend pytest, move to a quality/ops suite, or become CI script checks outside app tests. | needs-user-decision |

## F-001 - Default pytest discovery excludes active test files

- Severity: High
- Confidence: High
- Category: missing-guard
- Domain: backend tests
- Evidence: E-003, E-004
- Expected rule: Every retained backend test must be collected by the standard backend test command or explicitly documented as an opt-in suite.
- Actual state: `backend/pyproject.toml` default `testpaths` omit `backend/tests/unit`, `backend/tests/llm_orchestration`, and `backend/app/domain/llm/prompting/tests`; one configured path, `app/ai_engine/tests`, does not exist.
- Impact: 304 static tests in 64 files are outside default pytest collection, including LLM and architecture guards.
- Recommended action: Converge pytest discovery: either move these files under configured roots or update `testpaths` and CI so every retained test is collected by the standard backend command.
- Story candidate: yes
- Suggested archetype: test-guard-hardening

## F-002 - Backend tests have no canonical root ownership

- Severity: High
- Confidence: High
- Category: missing-canonical-owner
- Domain: backend tests
- Evidence: E-001, E-003, E-004
- Expected rule: Backend test files should live under a small, documented topology with clear unit/integration/regression ownership.
- Actual state: Tests are split across `backend/app/tests`, `backend/tests`, and an embedded `backend/app/domain/llm/prompting/tests` folder.
- Impact: The suite has no single ownership model: active tests live under `backend/app/tests`, `backend/tests`, and an embedded domain test folder.
- Recommended action: Define one canonical backend test topology and migrate non-canonical roots with compatibility only through explicit, temporary story scope.
- Story candidate: yes
- Suggested archetype: test-suite-topology-convergence

## F-003 - DB test harness preserves legacy direct SessionLocal imports

- Severity: High
- Confidence: High
- Category: data-integrity-risk
- Domain: backend tests DB harness
- Evidence: E-007
- Expected rule: Tests should use one explicit DB fixture/session access path and avoid process-global session rewiring.
- Actual state: `backend/app/tests/conftest.py` creates a temp SQLite file and globally replaces `app.infra.db.session.engine` and `SessionLocal` because many legacy tests import them directly. Additional conftests also perform SQLite alignment and `create_all`.
- Impact: Global DB monkeypatching and multiple SQLite setup strategies make isolation hard to reason about and preserve legacy direct imports.
- Recommended action: Centralize DB fixtures around one session/engine access pattern; remove direct `SessionLocal` imports from tests before removing the global monkeypatch.
- Story candidate: yes
- Suggested archetype: test-harness-convergence

## F-004 - Story-numbered legacy guards need canonical triage

- Severity: Medium
- Confidence: High
- Category: legacy-surface
- Domain: backend tests
- Evidence: E-005, E-010
- Expected rule: Regression guards should be named by durable invariant, not only by historical story number, and legacy removal tests should map to current protected surfaces.
- Actual state: 44 story-named files and 262 story-named tests remain. Many legacy hits likely protect RG-001 through RG-009, but others may only preserve migration-era states.
- Impact: Story-numbered and legacy-heavy tests preserve valuable guardrails but obscure whether they still protect current application behavior or old migration states.
- Recommended action: Reclassify story tests into canonical guard suites, keep the invariants mapped to RG-001..RG-009, and retire only tests whose protected surface has an approved replacement.
- Story candidate: yes
- Suggested archetype: legacy-guard-convergence

## F-005 - Tests import helpers from other test modules

- Severity: Medium
- Confidence: High
- Category: duplicate-responsibility
- Domain: backend tests helpers
- Evidence: E-008
- Expected rule: Reusable test setup should live in helper or fixture modules, not in executable test modules.
- Actual state: 9 cross-test imports were found, including imports from billing API tests, ops alert retry tests, and regression tests.
- Impact: Test modules import helpers from other test modules, which couples suite order and makes helper ownership implicit.
- Recommended action: Extract reused builders/helpers into dedicated `helpers` or fixture modules and remove cross-test-module imports.
- Story candidate: yes
- Suggested archetype: test-helper-dry-convergence

## F-006 - One no-op facade test always passes

- Severity: Medium
- Confidence: High
- Category: missing-test-coverage
- Domain: backend tests
- Evidence: E-006
- Expected rule: A collected test must assert behavior or explicitly skip with a tracked reason.
- Actual state: `backend/app/tests/unit/test_seed_validation.py` contains a single test with `pass` and a comment saying the seed script does not yet raise `SeedValidationError`.
- Impact: `test_seed_validation_required_persona_empty_allowed` is a facade that always passes while documenting missing implementation.
- Recommended action: Replace it with a real assertion against the intended seed validation behavior, or delete it if the requirement is obsolete.
- Story candidate: yes
- Suggested archetype: facade-test-removal

## F-007 - Operational docs/scripts tests need ownership decision

- Severity: Low
- Confidence: Medium
- Category: needs-user-decision
- Domain: backend tests operational scope
- Evidence: E-009
- Expected rule: Backend application tests should have a documented boundary from docs, PR-template, script, and release-pipeline checks.
- Actual state: Several backend tests validate documentation files, PR template governance, PowerShell scripts, backup/restore scripts, secret scans, and security verification scripts.
- Impact: Some backend tests validate docs, PR templates, scripts, and pipeline behavior; these may be valid but they blur application-test ownership.
- Recommended action: needs-user-decision: decide whether these remain in backend pytest, move to a quality/ops suite, or become CI script checks outside app tests.
- Story candidate: needs-user-decision
- Suggested archetype: quality-suite-ownership-decision
