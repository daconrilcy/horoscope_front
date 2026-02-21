# Horoscope backend

## Run

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m uvicorn app.main:app --reload
```

## Quality

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
pytest -q
```

## Quality Gate (repository)

```powershell
.\scripts\quality-gate.ps1
```

Run standalone secrets scan:

```powershell
.\scripts\scan-secrets.ps1
```

Run standalone security verification pack (SAST + deps + remediation plan):

```powershell
.\scripts\security-verification.ps1
```

Generate RGPD operational evidence dossier (export/delete/audit):

```powershell
.\scripts\generate-rgpd-evidence.ps1 `
  -BaseUrl "http://127.0.0.1:8000" `
  -AccessToken "<SUPPORT_OR_OPS_ACCESS_TOKEN>" `
  -TargetUserId 42
```

## Predeploy Check (repository)

```powershell
.\scripts\predeploy-check.ps1
```

## Backup / Restore DB (repository)

Backup:

```powershell
.\scripts\backup-db.ps1 -Mode auto
```

Notes:
- Inclut aussi (par defaut) un backup des assets runtime critiques (`backend/.env`, `docker-compose.yml`, `backend/alembic.ini`) dans `backups/runtime`.
- Requiert `BACKUP_METADATA_HMAC_KEY` pour signer la metadata de backup.

Validation:

```powershell
.\scripts\backup-validate.ps1 -BackupFile .\backups\db\<backup_file>
```

Restore:

```powershell
.\scripts\restore-db.ps1 -BackupFile .\backups\db\<backup_file> -Mode auto
```

Restore complet (DB + runtime + verification health):

```powershell
.\scripts\restore-db.ps1 `
  -BackupFile .\backups\db\<backup_file> `
  -RuntimeBackupFile .\backups\runtime\<runtime_backup_file> `
  -Mode auto `
  -PostRestoreHealthUrl "http://127.0.0.1:8000/health"
```

## Load Testing (Story 8.4)

Run a short critical-flow load campaign against a running backend:

```powershell
.\scripts\load-test-critical.ps1 -BaseUrl "http://127.0.0.1:8000" -Profile smoke -OutputPath "artifacts/load-test-report.json"
```

Le runner execute des phases `ramp_up`, `plateau`, `spike` et mesure aussi le throughput (req/s).

Optional B2B scenario (requires enterprise API key):

```powershell
.\scripts\load-test-critical.ps1 -B2BApiKey "<enterprise_api_key>"
```

Ops correlation snapshot (pre/post run):

```powershell
.\scripts\load-test-critical.ps1 -OpsAccessToken "<ops_access_token>" -OpsWindow "24h"
```

Require B2B scenario (fail if key missing):

```powershell
.\scripts\load-test-critical.ps1 -Profile nominal -RequireB2B -B2BApiKey "<enterprise_api_key>"
```

Run full matrix (`smoke` + `nominal` + `stress`):

```powershell
.\scripts\load-test-critical-matrix.ps1 -BaseUrl "http://127.0.0.1:8000" -OutputDir "artifacts/load-test-matrix"
```

Short automated smoke check (non-destructive) in test suite:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/app/tests/integration/test_load_smoke_critical_flows.py
```

Optional real PostgreSQL E2E validation (destructive, disposable DB only):

```powershell
$env:RUN_POSTGRES_BACKUP_RESTORE_E2E="1"
$env:BACKUP_RESTORE_E2E_ALLOW_DESTRUCTIVE="YES"
$env:BACKUP_RESTORE_E2E_DATABASE_URL="postgresql://user:pass@localhost:5432/disposable_db"
.\.venv\Scripts\Activate.ps1
pytest -q backend/app/tests/integration/test_backup_restore_scripts.py -k real_cli_opt_in
```

## Rollback minimal (post-deploy)

En cas d'echec immediat apres deploiement:

```powershell
docker compose down
docker compose up -d
```

Puis verifier:

```powershell
.\scripts\startup-smoke.ps1
```

## Dependency Sync

Le backend est defini via `pyproject.toml`.
Pour les environnements conteneurises, l image installe le package local avec `pip install .`.

## Secrets Rotation

Secrets minimum requis en production:
- `JWT_SECRET_KEY`
- `API_CREDENTIALS_SECRET_KEY`
- `LLM_ANONYMIZATION_SALT`
- `REFERENCE_SEED_ADMIN_TOKEN`

Rotation grace period (without immediate service interruption):
- `JWT_PREVIOUS_SECRET_KEYS` (comma-separated previous JWT secrets)
- `API_CREDENTIALS_PREVIOUS_SECRET_KEYS` (comma-separated previous API credential HMAC secrets)
