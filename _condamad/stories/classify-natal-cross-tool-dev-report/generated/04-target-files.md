# Target Files

## Must read

- `AGENTS.md`
- `_condamad/stories/regression-guardrails.md`
- `scripts/natal-cross-tool-report-dev.py`
- `backend/scripts/cross_tool_report.py`
- `backend/app/tests/golden`
- `scripts/ownership-index.md`
- `backend/README.md`
- `docs/natal-pro-dev-guide.md`
- `backend/app/tests/unit/test_cross_tool_report.py`

## Must search

- `rg -n "natal-cross-tool-report-dev|app\.tests\.golden|scripts\.cross_tool_report|CI" scripts backend docs _condamad`
- `rg -n "app\.tests\.golden" backend/app scripts -g "*.py"`
- `rg -n "cross_tool_report" scripts backend`
- `rg -n "natal-cross-tool-report-dev.py|Activate.ps1" docs scripts/ownership-index.md backend/README.md`

## Likely modified

- `scripts/natal-cross-tool-report-dev.py`
- `docs/natal-pro-dev-guide.md`
- `backend/app/tests/unit/test_natal_cross_tool_report_dev_script.py`
- `_condamad/stories/classify-natal-cross-tool-dev-report/dev-only-contract.md`
- `_condamad/stories/classify-natal-cross-tool-dev-report/import-baseline.txt`
- `_condamad/stories/classify-natal-cross-tool-dev-report/import-after.txt`
- generated capsule files

## Forbidden unless justified

- `backend/app/services`
- `frontend/src`
- `backend/app/tests/golden`
- Dependency manifests
