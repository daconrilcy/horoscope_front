# Deployment Guide

## Local Compose Deployment
`docker-compose.yml` defines:
- `backend` service built from `backend/Dockerfile`
- `frontend` service on Node image, mounting `frontend/`

### Start
```powershell
docker compose up -d
```

### Stop
```powershell
docker compose down
```

## Health Check
- Backend healthcheck performs HTTP call to `/health`
- Frontend service depends on backend healthy status

## Predeploy Safety
Run repository checks before shipping:
```powershell
.\scripts\predeploy-check.ps1
```

## Rollback Minimal
```powershell
docker compose down
docker compose up -d
.\scripts\startup-smoke.ps1
```

## Backup/Restore
- Backup: `scripts/backup-db.ps1`
- Validate backup integrity: `scripts/backup-validate.ps1`
- Restore: `scripts/restore-db.ps1`
