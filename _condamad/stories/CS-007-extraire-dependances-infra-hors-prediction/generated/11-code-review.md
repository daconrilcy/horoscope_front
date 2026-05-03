# CONDAMAD Code Review

## Review target

- Story: `_condamad/stories/CS-007-extraire-dependances-infra-hors-prediction/00-story.md`
- Status at review start: `done`
- Review date: 2026-05-04
- Verdict: `ACCEPTABLE_WITH_LIMITATIONS`

## Inputs reviewed

- Story contract and acceptance criteria.
- Capsule files `03-acceptance-traceability.md`, `06-validation-plan.md`, `07-no-legacy-dry-guardrails.md`, `10-final-evidence.md`.
- Baseline and after artifacts `infra-dependency-before.md` and `infra-dependency-after.md`.
- Regression guardrails registry, especially `RG-011`, `RG-026`, and `RG-027`.
- Current diff for prediction services, pure prediction contracts, moved modules, import consumers, tests, and governance files.
- Reviewer-run validation commands listed below.

## Diff summary

- `backend/app/prediction/context_loader.py` and `backend/app/prediction/persistence_service.py` are deleted.
- Canonical implementations now live under `backend/app/services/prediction/context_loader.py` and `backend/app/services/prediction/persistence_service.py`.
- Consumers import the canonical service paths.
- `LoadedPredictionContext` and `CalibrationData` are pure contracts in `backend/app/prediction/context.py`.
- `backend/app/prediction/calibrator.py` no longer imports infra DTOs.
- `backend/app/prediction/public_projection.py` no longer imports or annotates SQLAlchemy `Session`.
- `backend/app/tests/unit/test_daily_prediction_guardrails.py` enforces the prediction namespace inventory and forbidden infra imports without an allowlist.

## Findings

No actionable findings remain.

## Acceptance audit

- AC1: Passes. `app.prediction` has no SQLAlchemy, `Session`, listed repositories, or `from app.infra` hits. The AST guard has no allowlist.
- AC2: Passes. Context and persistence tests passed, including session-backed integration tests.
- AC3: Passes. Old import paths `app.prediction.context_loader` and `app.prediction.persistence_service` returned zero hits under `app tests`.
- AC4: Passes. `backend/prediction` does not exist.
- AC5: Passes. Before/after artifacts exist; after artifact records zero forbidden hits.

Applicable guardrails:

- `RG-011`: covered by `pytest -q app/tests/unit/test_backend_db_test_harness.py`.
- `RG-026`: covered by `test_daily_prediction_guardrails.py` and old-path scans.
- `RG-027`: covered by `test_daily_prediction_guardrails.py` and the zero-hit infra scan.

## Validation audit

Reviewer commands were run with the repository venv activated for all Python commands:

```powershell
.\.venv\Scripts\Activate.ps1; cd backend; ruff format --check app tests
.\.venv\Scripts\Activate.ps1; cd backend; ruff check app tests
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/unit/test_context_loader.py app/tests/unit/test_daily_prediction_service.py app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_backend_db_test_harness.py
.\.venv\Scripts\Activate.ps1; cd backend; pytest -q app/tests/integration/test_prediction_persistence.py app/tests/integration/test_engine_persistence_e2e.py
cd backend; rg -n "sqlalchemy|Session|DailyPredictionRepository|PredictionReferenceRepository|PredictionRulesetRepository|from app\.infra" app/prediction -g "*.py"
cd backend; rg -n "app\.prediction\.context_loader|app\.prediction\.persistence_service" app tests
.\.venv\Scripts\Activate.ps1; cd backend; python -c "import os; assert not os.path.exists('prediction')"
.\.venv\Scripts\Activate.ps1; cd backend; python -c "from app.main import app; print(len(app.routes))"
git diff --check
```

Results:

- Ruff format check: passed, `1080 files already formatted`.
- Ruff lint: passed.
- Unit/context/service/guard/RG-011 tests: `44 passed`.
- Persistence/e2e integration tests: `12 passed`.
- Forbidden infra scan: zero hits, command exit `1`.
- Removed old import path scan: zero hits, command exit `1`.
- No root `backend/prediction`: passed.
- App import: passed, `220` routes registered.
- `git diff --check`: passed with Git LF-to-CRLF warnings only.

Full backend `pytest -q` was not rerun in this review. Previous capsule evidence records a timeout after 304 seconds, and the required story-critical targeted checks passed.

## DRY / No Legacy audit

- No legacy facade, wrapper, alias, fallback, or re-export remains for `app.prediction.context_loader` or `app.prediction.persistence_service`.
- There is no duplicate active context loader or persistence service under `app.prediction`.
- The infra-boundary guard now blocks the forbidden imports without classified exceptions.
- The pure `CalibrationData` move avoids keeping a domain dependency on `app.infra.db.repositories.prediction_schemas`.

## Residual risks

- The repository worktree is broad and includes unrelated modified files and untracked CONDAMAD story folders CS-008 through CS-013; this review scoped them out except where CS-007 evidence references them.
- Full backend `pytest -q` remains unverified in this review due the previously observed runtime timeout.

## Verdict

`ACCEPTABLE_WITH_LIMITATIONS`

No blocking, material, or low code-review findings remain for CS-007. The story can stay `done`; the only limitation is the documented absence of a fresh full-suite `pytest -q`.
