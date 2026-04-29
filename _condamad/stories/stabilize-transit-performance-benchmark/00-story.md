# Story stabilize-transit-performance-benchmark: Stabilize V3 transit performance benchmark in backend pytest

Status: ready-for-review

## 1. Objective

Stabiliser le test backend `test_v3_layers_performance_benchmark`.
La suite standard `pytest -q` ne doit plus echouer sur une fluctuation locale de
temps wall-clock, mais les budgets V3 doivent rester declares, mesurables et
executables volontairement.

## 2. Trigger / Source

- Source type: bug
- Source reference: `_condamad/stories/guard-backend-pytest-test-roots/generated/10-final-evidence.md`
- Reason for change: la suite complete a echoue une fois sur
  `app/tests/unit/test_transit_performance.py::test_v3_layers_performance_benchmark`
  avec `104.02ms` contre un budget strict de `100ms`.
  Le meme test isole est ensuite repasse; le signal est donc sensible a la
  charge locale et rend la suite standard non deterministe.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: backend V3 prediction performance tests
- In scope:
  - Stabiliser `backend/app/tests/unit/test_transit_performance.py`.
  - Conserver les assertions de diagnostics `budget_target_ms` et `sample_count`.
  - Implementer un mode explicite pour le benchmark wall-clock strict via
    `RUN_PERF_BENCHMARKS=1`.
  - Ajouter une garde ou un scan qui empeche le retour d'une assertion wall-clock brute dans la suite standard.
  - Micro-optimiser `backend/app/prediction/transit_signal_builder.py` uniquement si le changement est local, mesure, sans changement metier, et prouve par tests.
- Out of scope:
  - Modifier les budgets produits `TransitSignalBuilder.TARGET_BUDGET_MS` ou `IntradayActivationBuilder.TARGET_BUDGET_MS` pour masquer le probleme.
  - Reprendre l'algorithme V3 complet.
  - Modifier les guards de topologie backend.
  - Ajouter un framework de benchmark externe.
  - Changer le comportement fonctionnel des predictions V3.
- Explicit non-goals:
  - Ne pas affaiblir `RG-010`, `RG-013` ou `RG-014`.
  - Ne pas retirer toute couverture performance; le benchmark strict doit rester executable volontairement.
  - Ne pas ajouter de tolerance arbitraire sans preuve ou sans separation entre suite standard et benchmark volontaire.

## 4. Operation Contract

- Operation type: update
- Primary archetype: test-guard-hardening
- Archetype reason: la story durcit un test backend pour supprimer un faux negatif non deterministe tout en gardant une garde de performance explicite.
- Behavior change allowed: constrained
- Behavior change constraints:
  - La suite standard peut cesser d'echouer sur une mesure wall-clock stricte.
  - Les diagnostics de budget exposes par les builders doivent rester identiques.
  - Le benchmark strict doit rester disponible via une commande explicite.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: la correction necessite de changer les budgets V3, de supprimer completement la couverture performance, ou d'introduire une dependance de benchmark.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La source observable est l'execution pytest effective du test standard et du benchmark explicite. |
| Baseline Snapshot | yes | Il faut capturer le comportement avant/apres du benchmark et de la suite standard. |
| Ownership Routing | no | Aucun deplacement de responsabilite applicative ou de module n'est requis. |
| Allowlist Exception | yes | Le benchmark wall-clock strict doit etre une exception exacte et volontaire, pas un comportement implicite de la suite standard. |
| Contract Shape | no | Aucun contrat API, DTO, OpenAPI, payload ou type frontend n'est touche. |
| Batch Migration | no | Une seule surface de test est concernee. |
| Reintroduction Guard | yes | Une garde doit empecher le retour d'une assertion wall-clock brute dans le test standard. |
| Persistent Evidence | yes | La story doit persister les preuves de baseline et de validation finale dans son capsule. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - execution pytest de `backend/app/tests/unit/test_transit_performance.py`.
  - execution standard `pytest -q` depuis `backend`.
  - AST guard or targeted parser/scan over `backend/app/tests/unit/test_transit_performance.py` for forbidden raw wall-clock assertions in the standard test path.
- Secondary evidence:
  - scan cible du fichier de test pour les assertions wall-clock interdites.
  - diagnostics runtime `budget_target_ms` et `sample_count` retournes par les builders.
- Static scans alone are not sufficient for this story because:
  - le probleme observe vient du comportement d'execution sous charge, pas seulement du texte du test.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/stabilize-transit-performance-benchmark/performance-benchmark-before.md`
- Comparison after implementation:
  - `_condamad/stories/stabilize-transit-performance-benchmark/performance-benchmark-after.md`
- Expected invariant:
  - les diagnostics de budget restent presents et le benchmark strict reste executable volontairement.
- Allowed differences:
  - l'assertion wall-clock stricte peut etre retiree de la suite standard ou conditionnee par un marqueur/env var explicite.
  - une micro-optimisation locale peut reduire le temps mesure sans modifier les sorties fonctionnelles attendues.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: aucun module, route, namespace ou responsabilite applicative ne change de proprietaire.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/tests/unit/test_transit_performance.py` | `RUN_PERF_BENCHMARKS=1` | Benchmark strict volontaire. | Permanent. |

Rules:

- no wildcard;
- no suite-wide skip;
- no silent pass when the explicit benchmark command is requested;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Benchmark baseline | `_condamad/stories/stabilize-transit-performance-benchmark/performance-benchmark-before.md` | Capturer l'etat initial du test. |
| Benchmark after | `_condamad/stories/stabilize-transit-performance-benchmark/performance-benchmark-after.md` | Prouver suite standard et benchmark explicite. |
| Final evidence | `_condamad/stories/stabilize-transit-performance-benchmark/generated/10-final-evidence.md` | Relier AC, fichiers modifies, commandes et limites. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture/test guard that fails if the forbidden flaky surface is reintroduced.

The guard must check at least one deterministic source:

- targeted pytest test in `backend/app/tests/unit/test_transit_performance.py`
- targeted scan for raw wall-clock assertions against `TARGET_BUDGET_MS`
- explicit benchmark command documentation in the final evidence

Required forbidden examples:

- `assert dur_t < TransitSignalBuilder.TARGET_BUDGET_MS` without `RUN_PERF_BENCHMARKS=1`
- `assert dur_a < IntradayActivationBuilder.TARGET_BUDGET_MS` without `RUN_PERF_BENCHMARKS=1`
- replacing the failure with an unconditional `pytest.skip`
- raising `TARGET_BUDGET_MS` only to make the test pass

Guard evidence:

- Evidence profile: `reintroduction_guard`.
- Command:
  `rg -n "assert dur_.*< .*TARGET_BUDGET_MS" backend/app/tests/unit/test_transit_performance.py`
- Expected result: zero active standard-suite assertions, or every hit classified
  as part of the explicit benchmark path.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/tests/unit/test_transit_performance.py` -
  the test measures `dur_t`, `dur_a`, and `dur_agg` with `time.perf_counter()`.
  It asserts raw duration thresholds against both V3 builder budgets.
- Evidence 2: `backend/app/prediction/transit_signal_builder.py` -
  `TARGET_BUDGET_MS = 100.0`; `_continuous_base_signal()` calls `_f_orb`
  once for the guard and again in the returned product.
- Evidence 3: `_condamad/stories/guard-backend-pytest-test-roots/generated/10-final-evidence.md` -
  full `pytest -q` failed once at `104.02ms` versus `100ms`.
  The isolated rerun of the same benchmark passed.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consulted before story scope was finalized.

## 6. Target State

After implementation:

- `pytest -q` no longer fails because of a local wall-clock fluctuation in the V3 performance benchmark.
- The standard test still proves the V3 builders expose the expected budget diagnostics and sample counts.
- A strict wall-clock benchmark remains executable through a deliberate command or marker.
- Any micro-optimization preserves existing functional outputs and is covered by the targeted test.
- The final evidence records both standard-suite validation and explicit benchmark validation.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-010` - validation must keep backend pytest collection stable because the story changes a collected backend test.
  - `RG-014` - the corrected test must not become a no-op, direct `pass`, or nominal `assert True`.
- Non-applicable invariants:
  - `RG-013` - no cross-test helper import surface is changed.
  - `RG-011` - no DB harness or fixture ownership is touched.
- Required regression evidence:
  - `pytest -q app/tests/unit/test_transit_performance.py`
  - `pytest -q app/tests/unit/test_backend_noop_tests.py`
  - `pytest --collect-only -q --ignore=.tmp-pytest`
- Allowed differences:
  - the strict wall-clock assertion may move behind an explicit benchmark command or marker.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Standard pytest is not gated by raw wall-clock assertions. | Evidence profile: `reintroduction_guard`; targeted pytest plus duration-assertion scan. |
| AC2 | Standard test still validates V3 performance diagnostics. | Evidence profile: `runtime_openapi_contract`; targeted pytest verifies diagnostics. |
| AC3 | Strict wall-clock benchmark remains opt-in. | Evidence profile: `allowlist_register_validated`; run `RUN_PERF_BENCHMARKS=1` targeted pytest. |
| AC4 | Performance budgets are not raised or hidden to pass tests. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "TARGET_BUDGET_MS = " app/prediction`. |
| AC5 | Backend regression guardrails remain intact. | Evidence profile: `reintroduction_guard`; run noop guard, collect-only, and `ruff check .`. |

## 8. Implementation Tasks

- [x] Task 1 - Capture benchmark baseline (AC: AC1, AC3, AC4)
  - [x] Subtask 1.1 - Persist the observed failure and current test structure in `performance-benchmark-before.md`.
  - [x] Subtask 1.2 - Record current budget constants and current standard-suite assertion behavior.

- [x] Task 2 - Stabilize the standard test path (AC: AC1, AC2)
  - [x] Subtask 2.1 - Refactor `test_v3_layers_performance_benchmark` so standard pytest validates diagnostics and sample counts deterministically.
  - [x] Subtask 2.2 - Condition the strict wall-clock assertion behind `RUN_PERF_BENCHMARKS=1`, without unconditional skip.

- [x] Task 3 - Preserve explicit performance signal (AC: AC3, AC4)
  - [x] Subtask 3.1 - Document `$env:RUN_PERF_BENCHMARKS='1'; pytest -q app/tests/unit/test_transit_performance.py`.
  - [x] Subtask 3.2 - If a local micro-optimization is applied, prove the builder outputs still satisfy existing tests.

- [x] Task 4 - Add anti-regression evidence (AC: AC1, AC5)
  - [x] Subtask 4.1 - Add or document a deterministic scan/guard against raw wall-clock budget assertions in the standard test path.
  - [x] Subtask 4.2 - Run targeted tests, collection, lint, and RG-014 guard.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/tests/unit/test_transit_performance.py` as the single owner of V3 layer performance test coverage.
  - `TransitSignalBuilder.TARGET_BUDGET_MS` and `IntradayActivationBuilder.TARGET_BUDGET_MS` as the declared budgets.
  - Existing pytest mechanisms for markers or environment checks if already present in the repository.
- Do not recreate:
  - a second V3 performance test file with duplicate setup unless the existing file becomes unreadable.
  - a custom benchmark framework.
  - a separate copy of the mock V3 context outside this test without a reuse reason.
- Shared abstraction allowed only if:
  - the current test setup becomes duplicated inside the same file and a local helper reduces duplication without changing behavior.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- unconditional `pytest.skip` for `test_v3_layers_performance_benchmark`
- direct `assert True` or `pass` replacing performance checks
- raising `TransitSignalBuilder.TARGET_BUDGET_MS` or `IntradayActivationBuilder.TARGET_BUDGET_MS` only to pass tests
- adding new benchmark dependencies
- changing prediction business outputs as part of test stabilization

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

- Canonical ownership: not applicable

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `_condamad/stories/guard-backend-pytest-test-roots/generated/10-final-evidence.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/unit/test_transit_performance.py`
- `backend/app/prediction/transit_signal_builder.py`
- `backend/app/prediction/intraday_activation_builder.py`
- `backend/pyproject.toml`

## 19. Expected Files to Modify

Likely files:

- `backend/app/tests/unit/test_transit_performance.py` - stabilize standard test assertions and preserve explicit benchmark path.
- `_condamad/stories/stabilize-transit-performance-benchmark/performance-benchmark-before.md` - persist baseline evidence.
- `_condamad/stories/stabilize-transit-performance-benchmark/performance-benchmark-after.md` - persist final validation evidence.

Likely tests:

- `backend/app/tests/unit/test_transit_performance.py` - primary targeted test.
- `backend/app/tests/unit/test_backend_noop_tests.py` - guard against no-op test regression.

Files not expected to change:

- `backend/pyproject.toml` - no collection or dependency change expected.
- `backend/app/tests/unit/test_backend_test_topology.py` - topology guard is out of scope.
- `frontend/` - no frontend surface is affected.
- `requirements.txt` - must not be created.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_transit_performance.py
pytest -q app/tests/unit/test_backend_noop_tests.py
pytest --collect-only -q --ignore=.tmp-pytest
rg -n "assert dur_.*< .*TARGET_BUDGET_MS" app/tests/unit/test_transit_performance.py
pytest -q
```

The final evidence must also document this explicit strict benchmark command:
`$env:RUN_PERF_BENCHMARKS='1'; pytest -q app/tests/unit/test_transit_performance.py`.
If full `pytest -q` fails outside this story, record the failing test, rerun the
targeted failure when safe, and classify the result.

## 22. Regression Risks

- Risk: le benchmark strict disparait completement.
  - Guardrail: AC3 exige une commande ou un marqueur explicite et une preuve persistante.
- Risk: le test devient un no-op pour faire passer la suite.
  - Guardrail: `pytest -q app/tests/unit/test_backend_noop_tests.py` et `RG-014`.
- Risk: une tolerance arbitraire masque une vraie regression de performance.
  - Guardrail: AC4 interdit de relever les budgets sans decision utilisateur et impose la conservation du signal explicite.
- Risk: une micro-optimisation modifie les sorties V3.
  - Guardrail: targeted test plus suite backend; si une sortie fonctionnelle change, stopper et documenter le blocker.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respecter l'activation du venv avant toute commande Python.
- Ne pas creer de `requirements.txt`.
- Ne pas modifier les budgets V3 sans decision utilisateur explicite.

## 24. References

- `_condamad/stories/guard-backend-pytest-test-roots/generated/10-final-evidence.md` - source de l'echec full suite observe.
- `backend/app/tests/unit/test_transit_performance.py` - test a stabiliser.
- `backend/app/prediction/transit_signal_builder.py` - budget transit et opportunite de micro-optimisation locale.
- `backend/app/prediction/intraday_activation_builder.py` - budget activation a conserver.
- `_condamad/stories/regression-guardrails.md` - invariants RG-010 et RG-014.
