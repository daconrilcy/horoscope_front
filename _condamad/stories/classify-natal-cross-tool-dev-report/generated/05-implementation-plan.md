# Implementation Plan

## Findings

- `backend/scripts/cross_tool_report.py` contient deja `ensure_dev_only_runtime`, qui refuse `CI`, `GITHUB_ACTIONS`, `GITLAB_CI` et `BUILD_BUILDID`.
- `scripts/natal-cross-tool-report-dev.py` utilise le helper existant via `scripts.cross_tool_report` apres insertion de `backend/` dans `sys.path`.
- `backend/README.md` documente deja une commande avec activation du venv; une doc sous `docs/` rendra la preuve plus visible.
- `scripts/ownership-index.md` classe deja le script en `dev-only`.

## Changes

- Ajouter une docstring francaise au script dev-only pour clarifier le contrat.
- Ajouter une section dev-only dans `docs/natal-pro-dev-guide.md`.
- Ajouter `backend/app/tests/unit/test_natal_cross_tool_report_dev_script.py`.
- Persister `import-baseline.txt`, `import-after.txt` et `dev-only-contract.md`.

## Tests

- `pytest -q app/tests/unit/test_natal_cross_tool_report_dev_script.py`
- `pytest -q app/tests/unit/test_cross_tool_report.py`
- Scans `rg` cibles.
- Ruff et suite backend.

## Rollback

- Supprimer le test dedie, retirer la section de doc, et restaurer la docstring du script si la classification est rejetee.
