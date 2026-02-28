# Horoscope backend

## Deployment

Pour le déploiement en production sur VPS, voir le guide complet: [docs/deploy-vps.md](../docs/deploy-vps.md)

Quick start production:
```bash
# Build frontend
cd frontend && npm ci && npm run build && cd ..

# Configurer les variables d'environnement
cp .env.example .env
nano .env  # Configurer les secrets

# Démarrer en production
docker compose -f docker-compose.prod.yml up -d --build

# Vérifier le status
curl http://localhost/health
```

## Run

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m uvicorn app.main:app --reload
```

## Quality

**🚀 [Natal Pro Dev Guide](../docs/natal-pro-dev-guide.md) (Settings, Errors, Validation)** — *Reference for audit-grade astrology calculation.*

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
pytest -q
```

Note:
- Executer les tests backend de maniere sequentielle (une seule commande `pytest` a la fois) pour eviter les collisions SQLite sur les suites integration qui recreent le schema.

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

## Swiss Ephemeris (prod)

Guide dev pro (settings, erreurs 422/503, validation Golden Pro):
- [docs/natal-pro-dev-guide.md](../docs/natal-pro-dev-guide.md)

Variables de packaging/runtime:
- `SWISSEPH_ENABLED`
- `SWISSEPH_PRO_MODE` (active la validation stricte des fichiers requis)
- `EPHEMERIS_PATH`
- `EPHEMERIS_PATH_VERSION`
- `EPHEMERIS_PATH_HASH`
- `EPHEMERIS_REQUIRED_FILES` (liste CSV des fichiers requis)

Traçabilité temporelle optionnelle (story 22.2):
- Les endpoints `POST /v1/astrology-engine/natal/prepare` et `POST /v1/astrology-engine/natal/calculate` acceptent `tt_enabled` (bool, défaut `false`).
- Quand `tt_enabled=true` (ou `SWISSEPH_PRO_MODE=true`), la réponse expose `data.delta_t_sec`, `data.jd_tt`, `data.time_scale="TT"` et les mêmes champs dans `meta`.
- La valeur de ΔT est calculée via les approximations polynomiales de la NASA (Espenak & Meeus) couvrant les périodes historiques (-500 à 2150+) avec une précision adaptée à l'audit astrologique.
- Quand `tt_enabled=false`, `delta_t_sec` et `jd_tt` valent `null` et `time_scale="UT"`.

## Cross-Tool Drift Report (dev-only)

Script local de comparaison externe (hors CI), base sur le dataset golden pro:

```powershell
.\.venv\Scripts\Activate.ps1
python .\scripts\natal-cross-tool-report-dev.py --format both --output-dir .\artifacts\cross-tool
```

Options utiles:
- `--limit 10` pour un run rapide local.
- `--format json|markdown|both`.

Sorties:
- `artifacts/cross-tool/cross-tool-drift-report.json`
- `artifacts/cross-tool/cross-tool-drift-report.md`

Important:
- Outil strictement **dev-only**.
- Refuse de s'executer si une variable CI est detectee (`CI=true`, `GITHUB_ACTIONS=true`, etc.).

## Secrets Rotation

Secrets minimum requis hors environnements locaux/test (staging, production):
- `JWT_SECRET_KEY`
- `API_CREDENTIALS_SECRET_KEY`
- `LLM_ANONYMIZATION_SALT`
- `REFERENCE_SEED_ADMIN_TOKEN`

Rotation grace period (without immediate service interruption):
- `JWT_PREVIOUS_SECRET_KEYS` (comma-separated previous JWT secrets)
- `API_CREDENTIALS_PREVIOUS_SECRET_KEYS` (comma-separated previous API credential HMAC secrets)

Reference data seed/clone access:
- Preferred: bearer token with role `ops`.
- Local/test fallback only (explicit opt-in): `x-admin-token` (`REFERENCE_SEED_ADMIN_TOKEN`) with `ENABLE_REFERENCE_SEED_ADMIN_FALLBACK=1`.
