# Target Files

## Must read

- `AGENTS.md`
- `_condamad/stories/formalize-scripts-ownership/00-story.md`
- `_condamad/audits/scripts-ops/2026-05-02-1847/00-audit-report.md`
- `_condamad/audits/scripts-ops/2026-05-02-1847/01-evidence-log.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/unit/test_scripts_ownership.py`

## Must search

- `rg --files scripts`
- `rg -n "ownership-index|scripts_ownership|formalize-scripts-ownership" .`
- `rg -n "legacy|compat|shim|fallback|deprecated|alias" scripts backend/app/tests/unit/test_scripts_ownership.py`

## Likely modified

- `scripts/ownership-index.md`
- `backend/app/tests/unit/test_scripts_ownership.py`
- `_condamad/stories/formalize-scripts-ownership/scripts-inventory-baseline.txt`
- `_condamad/stories/formalize-scripts-ownership/scripts-inventory-after.txt`
- `_condamad/stories/formalize-scripts-ownership/generated/*.md`
- `_condamad/stories/regression-guardrails.md`

## Forbidden unless directly justified

- Script executable behavior under `scripts/*.ps1`, `scripts/*.py`, `scripts/*.sh`
- API routes and OpenAPI contracts
- Frontend source files
- Dependency manifests

## Existing tests to inspect first

- `backend/app/tests/unit/test_scripts_ownership.py`
- `backend/app/tests/unit/test_backend_quality_test_ownership.py`
- `backend/app/tests/integration/test_pipeline_scripts.py`
- `backend/app/tests/integration/test_secrets_scan_script.py`
- `backend/app/tests/integration/test_security_verification_script.py`
