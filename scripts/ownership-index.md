# Scripts Ownership Index

Ce registre est la source canonique d'ownership des fichiers racine sous
`scripts/`. Chaque ligne couvre exactement un chemin retourne par
`rg --files scripts`; aucun wildcard ni alias n'est autorise.

## Colonnes

| Column | Meaning |
|---|---|
| `script` | Chemin exact du fichier sous `scripts/`. |
| `family` | Famille canonique: `quality`, `security`, `db`, `perf`, `llm`, `dev` ou `story-tools`. |
| `owner` | Proprietaire fonctionnel du script. |
| `usage` | Usage nominal ou raison de conservation. |
| `validation_command` | Commande ciblee qui garde ou verifie le script. |
| `support_status` | Decision de support actuelle. |
| `decision` | Decision explicite pour eviter les statuts implicites. |

## Registry

| script | family | owner | usage | validation_command | support_status | decision |
|---|---|---|---|---|---|---|
| `scripts/activate-llm-release.ps1` | llm | LLM release operations | Active un profil de release LLM local. | `pytest -q app/tests/unit/test_scripts_ownership.py` | supported | keep |
| `scripts/backup-db.ps1` | db | Database operations | Cree une sauvegarde DB avec metadonnees. | `pytest -q app/tests/integration/test_backup_restore_scripts.py` | supported | keep |
| `scripts/backup-validate.ps1` | db | Database operations | Valide les sauvegardes avant restauration. | `pytest -q app/tests/integration/test_backup_restore_scripts.py` | supported | keep |
| `scripts/generate-performance-report.ps1` | perf | Performance operations | Produit un rapport de performance local. | `pytest -q app/tests/unit/test_scripts_ownership.py` | supported | keep |
| `scripts/generate-rgpd-evidence.ps1` | story-tools | Compliance evidence operations | Genere une preuve RGPD operationnelle. | `pytest -q app/tests/unit/test_scripts_ownership.py` | supported | keep |
| `scripts/llm-release-readiness.ps1` | llm | LLM release operations | Verifie la preparation d'une release LLM. | `pytest -q app/tests/unit/test_scripts_ownership.py` | supported-with-follow-up | keep-portability-follow-up |
| `scripts/load-test-critical-matrix.ps1` | perf | Performance operations | Orchestre la matrice de charge critique. | `pytest -q app/tests/unit/test_scripts_ownership.py` | supported | keep |
| `scripts/load-test-critical.ps1` | perf | Performance operations | Execute les scenarios de charge critiques. | `pytest -q app/tests/unit/test_scripts_ownership.py` | supported-with-follow-up | keep-scope-refactor-follow-up |
| `scripts/natal-cross-tool-report-dev.py` | dev | Local development diagnostics | Genere un rapport croise natal pour diagnostic dev. | `pytest -q app/tests/unit/test_scripts_ownership.py` | dev-only | keep-dev-only |
| `scripts/ownership-index.md` | story-tools | Script ownership governance | Registre canonique de l'ownership des fichiers sous scripts. | `pytest -q app/tests/unit/test_scripts_ownership.py` | supported | keep |
| `scripts/predeploy-check.ps1` | quality | Quality pipeline | Lance la verification pre-deploiement. | `pytest -q app/tests/integration/test_pipeline_scripts.py` | supported | keep |
| `scripts/quality-gate.ps1` | quality | Quality pipeline | Centralise les controles qualite backend/frontend. | `pytest -q app/tests/integration/test_pipeline_scripts.py` | supported | keep |
| `scripts/restore-db.ps1` | db | Database operations | Restaure une sauvegarde DB validee. | `pytest -q app/tests/integration/test_backup_restore_scripts.py` | supported | keep |
| `scripts/scan-secrets.ps1` | security | Security operations | Scanne les secrets avec allowlist explicite. | `pytest -q app/tests/integration/test_secrets_scan_script.py` | supported | keep |
| `scripts/secrets-scan-allowlist.txt` | security | Security operations | Allowlist du scan de secrets. | `pytest -q app/tests/integration/test_secrets_scan_script.py` | supported | keep |
| `scripts/security-findings-allowlist.txt` | security | Security operations | Allowlist des constats security verification. | `pytest -q app/tests/integration/test_security_verification_script.py` | supported | keep |
| `scripts/security-verification.ps1` | security | Security operations | Verifie les surfaces de securite applicative. | `pytest -q app/tests/integration/test_security_verification_script.py` | supported | keep |
| `scripts/start-dev-stack.ps1` | dev | Local development stack | Demarre la stack locale de developpement. | `pytest -q app/tests/unit/test_scripts_ownership.py` | supported-with-follow-up | keep-hardening-follow-up |
| `scripts/startup-smoke.ps1` | quality | Quality pipeline | Verifie le demarrage local apres lancement. | `pytest -q app/tests/unit/test_scripts_ownership.py` | supported | keep |
| `scripts/stripe-listen-webhook.ps1` | dev | Local Stripe webhook development | Lance l'ecoute Stripe locale sous PowerShell. | `pytest -q app/tests/unit/test_stripe_webhook_local_dev_assets.py` | supported | keep |
| `scripts/stripe-listen-webhook.sh` | dev | Local Stripe webhook development | Variante shell du listener Stripe local. | `pytest -q app/tests/unit/test_stripe_webhook_local_dev_assets.py` | needs-user-decision | blocked-support-decision |

## Support decisions

| Decision | Meaning |
|---|---|
| keep | Chemin conserve comme surface nominale. |
| keep-dev-only | Chemin conserve comme outil de developpement uniquement. |
| keep-portability-follow-up | Chemin conserve avec story de portabilite separee. |
| keep-scope-refactor-follow-up | Chemin conserve avec story de refactor de perimetre separee. |
| keep-hardening-follow-up | Chemin conserve avec story de durcissement separee. |
| blocked-support-decision | Chemin conserve sans trancher le support durable; decision utilisateur requise. |
