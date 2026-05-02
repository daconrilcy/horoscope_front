# Evidence Log - scripts-ops

| ID | Evidence type | Command / Source | Path | Result | Summary |
|---|---|---|---|---|---|
| E-001 | inventory | `rg --files scripts` | `scripts/` | PASS | 21 fichiers a la racine: PowerShell ops/dev, allowlists, deux scripts Python et un shell Unix. |
| E-002 | structure | `Get-ChildItem -Recurse -File scripts` | `scripts/` | PASS | Aucun sous-dossier: qualite, securite, DB, perf, LLM, dev local et validateurs story cohabitent dans le meme namespace. |
| E-003 | reference-scan | scan repo-wide par nom de fichier | repository | PASS | Les scripts quality/security/backup/load/LLM sont references; `start-dev-stack.ps1` n'a pas de reference hors lui-meme; `validate_route_removal_audit.py` n'est reference que par une story CONDAMAD livree. |
| E-004 | guardrail-registry | `_condamad/stories/regression-guardrails.md` | `_condamad/stories/` | PASS | `RG-015` protege l'ownership des tests docs/scripts/secrets/security/ops; No Legacy applicable au scope scripts. |
| E-005 | test-inventory | `rg -n "backup-db\|restore-db\|backup-validate\|scan-secrets\|security-verification" backend/app/tests -g "test_*.py"` | `backend/app/tests` | PASS | Backup/restore, scan secrets et security verification ont des tests d'integration nommes. |
| E-006 | test-inventory | `backend/app/tests/integration/test_pipeline_scripts.py` | `backend/app/tests/integration` | PASS | `quality-gate.ps1` et `predeploy-check.ps1` sont testes avec binaires mockes et ordre d'execution verifie. |
| E-007 | test-inventory | `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py` | `backend/app/tests/unit` | PASS | Les deux scripts Stripe sont gardes pour une liste d'evenements identique, y compris le shell script. |
| E-008 | source-inspection | `scripts/start-dev-stack.ps1` | `scripts/` | FAIL | Le script exige Stripe CLI et ouvre toujours un onglet Stripe (`lines 17, 64, 103, 111`) sans test ni doc repo-wide identifiee. |
| E-009 | source-inspection | `scripts/load-test-critical.ps1` | `scripts/` | FAIL | Le script contient des marqueurs story/legacy et un scenario `privacy_delete_request` actif (`lines 417, 447, 450, 453, 459, 496, 562`). |
| E-010 | source-inspection | `scripts/stripe-listen-webhook.ps1`, `scripts/stripe-listen-webhook.sh` | `scripts/` | FAIL | Deux implementations quasi identiques pour une cible dev Windows/PowerShell; le `.sh` reste reference par docs/tests. |
| E-011 | source-inspection | `scripts/llm-release-readiness.ps1` | `scripts/` | FAIL | Le cache pytest est code en dur vers `C:\dev\horoscope_front\.pytest_cache_runtime` (`lines 51, 56, 62`). |
| E-012 | source-inspection | `scripts/natal-cross-tool-report-dev.py` | `scripts/` | FAIL | Script dev-only utile mais importe `app.tests.golden` et `scripts.cross_tool_report` (`lines 20, 21`), ce qui brouille l'ownership runtime/test/dev. |
| E-013 | source-inspection | `scripts/quality-gate.ps1`, `scripts/predeploy-check.ps1` | `scripts/` | PASS | Gate qualite, security pack, lint/tests backend/frontend, Alembic et build frontend centralises. |
| E-014 | source-inspection | `scripts/validate_route_removal_audit.py` | `scripts/` | FAIL | Validateur specialise d'une story historique; seules references actives dans `_condamad/stories/remove-historical-facade-routes/**`. |
| E-015 | source-inspection | `scripts/backup-db.ps1`, `restore-db.ps1`, `backup-validate.ps1` | `scripts/` | PASS | Outillage DB documente, teste, avec HMAC metadata et validation avant restore. |
| E-016 | source-inspection | `scripts/scan-secrets.ps1`, `security-verification.ps1`, allowlists | `scripts/` | PASS | Outillage securite integre au quality gate, allowlists explicites et tests d'integration. |
