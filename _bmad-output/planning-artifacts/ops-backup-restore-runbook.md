# Ops Backup / Restore Runbook (Story 8.3)

## Scope

Assets critiques:
- Base de donnees applicative (SQLite local de dev, PostgreSQL en cible)
- Fichiers de configuration runtime (`backend/.env` non versionne, variables d environnement)
- Artefacts de deploiement (`docker-compose.yml`, scripts ops)

## RPO / RTO initiaux (single host)

- RPO cible: <= 24h (backup quotidien minimum)
- RTO cible: <= 60 min (restauration + verification service)

Ces objectifs sont initiaux et doivent etre recalibres selon charge reelle.

## Commandes standard

Prerequis integrite metadata:

```powershell
$env:BACKUP_METADATA_HMAC_KEY="<backup_integrity_key>"
```

### 1) Backup DB

```powershell
.\scripts\backup-db.ps1 -Mode auto
```

Ce backup inclut aussi (par defaut) un archive runtime dans `backups/runtime`.

Validation integrite:

```powershell
.\scripts\backup-validate.ps1 -BackupFile .\backups\db\<backup_file>
```

### 2) Restore DB

```powershell
.\scripts\restore-db.ps1 -BackupFile .\backups\db\<backup_file> -Mode auto
```

Restore complet avec assets runtime + healthcheck:

```powershell
.\scripts\restore-db.ps1 `
  -BackupFile .\backups\db\<backup_file> `
  -RuntimeBackupFile .\backups\runtime\<runtime_backup_file> `
  -Mode auto `
  -PostRestoreHealthUrl "http://127.0.0.1:8000/health"
```

Mode non interactif (CI/exercice):

```powershell
$env:RESTORE_ALLOW_NONINTERACTIVE="1"
.\scripts\restore-db.ps1 -BackupFile .\backups\db\<backup_file> -Mode auto -Force
```

## Verification post-restore

1. Health backend:
```powershell
Invoke-WebRequest http://127.0.0.1:8000/health
```
2. Smoke front/back:
```powershell
.\scripts\startup-smoke.ps1
```
3. Observabilite ops:
- verifier `/v1/ops/monitoring/operational-summary`
- absence d alertes critiques nouvelles liees au restore

## Exercice restore (preuve operationnelle)

Frequence recommandee: mensuelle (minimum trimestrielle).

Procedure:
1. Executer un backup fresh (`backup-db.ps1`).
2. Simuler une perte/corruption de donnees sur environnement de test.
3. Restaurer via `restore-db.ps1`.
4. Executer verification post-restore complete.
5. Archiver la preuve de l exercice:
   - horodatage
   - identifiant backup restaure
   - duree totale (objectif RTO)
   - resultat des checks health/smoke/monitoring
   - ecarts et actions correctives

Test automatise E2E PostgreSQL (opt-in, destructif):

```powershell
$env:RUN_POSTGRES_BACKUP_RESTORE_E2E="1"
$env:BACKUP_RESTORE_E2E_ALLOW_DESTRUCTIVE="YES"
$env:BACKUP_RESTORE_E2E_DATABASE_URL="postgresql://user:pass@localhost:5432/disposable_db"
.\.venv\Scripts\Activate.ps1
pytest -q backend/app/tests/integration/test_backup_restore_scripts.py -k real_cli_opt_in
```

## Scenarios incidents majeurs

### A) DB indisponible / corruption logique
1. Stopper ecritures (freeze operationnel).
2. Prendre snapshot backup immediat.
3. Restaurer dernier backup valide.
4. Verifier health + endpoints critiques + monitoring.
5. Ouvrir incident RCA.

### B) Backend non demarrable
1. Verifier logs backend et variables d environnement.
2. Redemarrer conteneur/service.
3. Si echec persistant, rollback version + restauration DB si migration partielle.
4. Valider `startup-smoke`.

### C) Frontend inaccessible
1. Verifier conteneur frontend / port 5173.
2. Verifier backend joignable et CORS.
3. Redemarrer frontend puis smoke.
4. En cas d echec, rollback artefact front.

### D) Credentials / tokens invalides en masse
1. Verifier expiration/rotation secrets JWT/API.
2. Verifier horloge systeme.
3. Si secret compromis: rotation controlee + invalidation sessions.
4. Superviser erreurs auth apres mitigation.

## Checklist post-incident

- [ ] Service backend healthy
- [ ] Frontend accessible
- [ ] Endpoints critiques revalides (auth, billing/quota, chat, privacy, natal)
- [ ] Monitoring stable (pas d alerte critique persistante)
- [ ] Incident documente (cause, impact, actions, prevention)
