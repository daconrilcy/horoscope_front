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

Note:
- La pile locale de prédiction quotidienne attend actuellement `ACTIVE_REFERENCE_VERSION=2.0.0` et `RULESET_VERSION=2.0.0`.
- Les rulesets `1.0.0` (legacy) et `2.0.0` (canonique) sont seedés sur la référence `2.0.0` via [`backend/scripts/seed_31_prediction_reference_v2.py`](./scripts/seed_31_prediction_reference_v2.py).
- `backend/.env.example` et `backend/.env` doivent rester alignés sur cette paire tant que le seed/runtime n'a pas changé.
- En environnement local SQLite, le bootstrap runtime répare désormais le schéma manquant au démarrage et ré-amorce automatiquement la référence/ruleset actifs si `2.0.0` est absent ou partiellement seedé.
- Si `/dashboard` ou `/v1/predictions/daily` échouait auparavant avec `version_missing`, `ruleset_missing` ou `compute_failed` sur une base locale partiellement seedée, un simple redémarrage du backend suffit maintenant dans la majorité des cas pour remettre la base locale en état.

### Transition de versioning (Ruleset 2.0.0)

Le ruleset `2.0.0` est désormais la version canonique alignée sur la référence `2.0.0`.
Le ruleset `1.0.0` est conservé pour la lecture des données historiques mais déclenche un log de `DEPRECATION`.

**Runbook de transition (Dev/Local) :**
1. Mettre à jour votre `.env` local :
   ```env
   ACTIVE_REFERENCE_VERSION=2.0.0
   RULESET_VERSION=2.0.0
   ```
2. Re-seeder la référence V2 pour inclure le ruleset canonique :
   ```bash
   python -m scripts.seed_31_prediction_reference_v2
   ```
   *Note : Le script gère la réparation automatique si la version est déverrouillée.*
3. Si la base SQLite locale est ancienne ou incomplète, relancer simplement le backend après mise à jour du code :
   ```powershell
   .\.venv\Scripts\Activate.ps1
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```
   Le démarrage applique désormais la réparation locale du schéma et du seed intraday avant les appels auth et prediction. Si le calcul daily rencontre encore un contexte de prédiction incomplet (`planet_profiles`, `house_profiles`, etc.), le service déclenche un auto-heal local puis retente le calcul une fois.

**Calibration et QA :**
- Les jobs de calibration et les tests QA doivent utiliser la paire canonique `reference=2.0.0` / `ruleset=2.0.0`.
- `ruleset=1.0.0` reste réservé aux lectures historiques et aux scénarios de compatibilité explicitement legacy.
- Une `ACTIVE_REFERENCE_VERSION` invalide fait désormais échouer immédiatement les jobs de calibration au lieu de basculer silencieusement sur la référence liée au ruleset.
- Pour diagnostiquer un appel résiduel en legacy, filtrez les logs `prediction.run` sur `ruleset_version="1.0.0"` puis corrigez la config ou le test concerné.

Pour plus de détails sur la stratégie de versionnement, voir [`docs/architecture/prediction-versioning-transition.md`](../docs/architecture/prediction-versioning-transition.md).

Reference data seed/clone access:


**🚀 [Natal Pro Dev Guide](../docs/natal-pro-dev-guide.md) (Settings, Errors, Validation)** — *Reference for audit-grade astrology calculation.*

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
python .\scripts\check_feature_scope_registry.py
pytest -q
```

Note:
- Executer les tests backend de maniere sequentielle (une seule commande `pytest` a la fois) pour eviter les collisions SQLite sur les suites integration qui recreent le schema.

## Quality Gate (repository)

```powershell
.\scripts\quality-gate.ps1
```

Ce quality gate exécute aussi la validation statique obligatoire du registre de scope via `python backend/scripts/check_feature_scope_registry.py`.

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
  -BaseUrl "http://127.0.0.1:8001" `
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
  -PostRestoreHealthUrl "http://127.0.0.1:8001/health"
```

## Load Testing (Story 8.4)

Run a short critical-flow load campaign against a running backend:

```powershell
.\scripts\load-test-critical.ps1 -BaseUrl "http://127.0.0.1:8001" -Profile smoke -OutputPath "artifacts/load-test-report.json"
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
.\scripts\load-test-critical-matrix.ps1 -BaseUrl "http://127.0.0.1:8001" -OutputDir "artifacts/load-test-matrix"
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

...

## Ops Review Queue Alerting (Story 61.39)

Le script d'émission d'alertes SLA pour la review queue ops est conçu pour être exécuté périodiquement via un scheduler externe (cron).

```powershell
# Exécution normale (commit DB + envoi webhook/logs)
python scripts/run_ops_review_queue_alerts.py

# Mode simulation (pas d'écriture DB, pas de webhook)
python scripts/run_ops_review_queue_alerts.py --dry-run
```

Configuration via variables d'environnement :
- `OPS_REVIEW_QUEUE_ALERTS_ENABLED=True`
- `OPS_REVIEW_QUEUE_ALERT_WEBHOOK_URL` (Optionnel : URL POST JSON)
- `OPS_REVIEW_QUEUE_ALERT_BASE_URL` (Optionnel : Liens cliquables dans les alertes)

Retry batch des alertes échouées :

```powershell
# Exemple de job périodique
python scripts/retry_ops_review_queue_alerts.py --limit 50

# Vérification sans effet de bord
python scripts/retry_ops_review_queue_alerts.py --dry-run
```

Consultation ops des alertes canoniques :

```text
GET /v1/ops/entitlements/mutation-audits/alerts/summary
GET /v1/ops/entitlements/mutation-audits/alerts
POST /v1/ops/entitlements/mutation-audits/alerts/retry-batch
POST /v1/ops/entitlements/mutation-audits/alerts/handle-batch
POST /v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handle
GET /v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/handling-history
GET /v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/attempts
POST /v1/ops/entitlements/mutation-audits/alerts/{alert_event_id}/retry
```

Les endpoints `summary` et `list` sont read-only, filtrables et réservés aux rôles `ops` et `admin`.
L'endpoint `retry-batch` applique toujours le filtre implicite `delivery_status=failed`, impose un body JSON avec `limit` obligatoire (`1..100`) et doit être déclaré avant les routes `/{alert_event_id}/...`.
L'endpoint `handle-batch` permet d'appliquer en masse un handling `suppressed` ou `resolved` sur des alertes filtrées, avec `limit` obligatoire (`1..200`), règle no-op sur l'état/commentaire/clé de suppression, et support `dry_run` fidèle sans écriture DB.
L'endpoint `handle` permet de qualifier une alerte en `suppressed` ou `resolved` avec commentaire ops et clé de suppression; les alertes `suppressed` ou `resolved` sont exclues du retry batch et `GET /alerts` expose aussi un état virtuel `pending_retry` pour les alertes `failed` sans handling.
L'endpoint `handling-history` expose l'historique append-only des transitions de handling, paginé via `limit` / `offset`, trié par `handled_at DESC, id DESC`, avec propagation du `request_id` et règle no-op sur les re-posts identiques.

Règles de suppression réutilisables (Story 61.46) :

```text
GET    /v1/ops/entitlements/alerts/suppression-rules
POST   /v1/ops/entitlements/alerts/suppression-rules
PATCH  /v1/ops/entitlements/alerts/suppression-rules/{id}
DELETE /v1/ops/entitlements/alerts/suppression-rules/{id}
```

Les opérateurs peuvent définir des règles durables pour ignorer automatiquement des alertes (ex: filtrage par `feature_code` ou `plan_code`). Les alertes matchées par une règle active sont marquées `suppressed` (source `rule`) et sont automatiquement exclues des retries batch et unitaires.

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
