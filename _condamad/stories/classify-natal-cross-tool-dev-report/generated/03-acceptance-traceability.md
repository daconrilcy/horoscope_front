# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Le script refuse `CI=true` avec un message clair. | `backend/app/tests/unit/test_natal_cross_tool_report_dev_script.py` execute le script en subprocess avec `CI=true` et verifie le code retour 2 + message clair. | `pytest -q app/tests/unit/test_natal_cross_tool_report_dev_script.py` PASS. | PASS |
| AC2 | La commande dev documentee active le venv. | `docs/natal-pro-dev-guide.md` documente `.\.venv\Scripts\Activate.ps1` puis `python .\scripts\natal-cross-tool-report-dev.py ...`; `dev-only-contract.md` persiste le meme contrat. | `rg -n "natal-cross-tool-report-dev.py\|Activate.ps1" docs scripts/ownership-index.md backend/README.md` PASS. | PASS |
| AC3 | `app.tests.golden` reste limite au dev/test. | Garde AST dans `test_natal_cross_tool_report_dev_script.py` refuse les imports `app.tests.golden` hors `backend/app/tests` et confirme que le script dev-only est le seul import runtime-adjacent. | `pytest -q app/tests/unit/test_natal_cross_tool_report_dev_script.py` PASS; scan `rg` classe les hits. | PASS |
| AC4 | Aucun helper `cross_tool_report` duplique n'est cree. | Test dedie verifie l'absence de `scripts/cross_tool_report*.py` sous la racine et l'import du helper existant `scripts.cross_tool_report`. | `pytest -q app/tests/unit/test_natal_cross_tool_report_dev_script.py` PASS; `rg -n "cross_tool_report" scripts backend` classe les hits. | PASS |
| AC5 | La story valide. | Capsule CONDAMAD completee, traceability et final evidence renseignes. | `condamad_story_validate.py` PASS; `condamad_story_lint.py --strict` PASS. | PASS |
