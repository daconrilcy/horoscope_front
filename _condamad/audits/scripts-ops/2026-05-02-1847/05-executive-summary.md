# Executive Summary - scripts-ops

Audit read-only du dossier `scripts/` realise avec le skill `condamad-domain-auditor`.

## Verdict

Le dossier est utile mais trop plat. Les scripts critiques qualite, securite et DB sont actifs, documentes et testes. Les surfaces a traiter sont surtout du legacy d'organisation: un validateur story-specifique reste a la racine, un doublon shell Stripe survit malgre la cible Windows, et plusieurs scripts dev/perf/LLM ont besoin d'un owner ou d'une garde plus explicite.

## Scripts a conserver

- `quality-gate.ps1`, `predeploy-check.ps1`, `startup-smoke.ps1`
- `scan-secrets.ps1`, `security-verification.ps1`, `secrets-scan-allowlist.txt`, `security-findings-allowlist.txt`
- `backup-db.ps1`, `backup-validate.ps1`, `restore-db.ps1`
- `load-test-critical.ps1`, `load-test-critical-matrix.ps1`, `generate-performance-report.ps1` avec refactor d'organisation
- `llm-release-readiness.ps1`, `activate-llm-release.ps1` avec correction de portabilite
- `generate-rgpd-evidence.ps1`
- `stripe-listen-webhook.ps1`
- `start-dev-stack.ps1` avec Stripe optionnel et doc
- `natal-cross-tool-report-dev.py` avec classement dev-only explicite

## Scripts candidats suppression ou decision

- Supprimer ou relocaliser: `validate_route_removal_audit.py`.
- Decision utilisateur: `stripe-listen-webhook.sh`; supprimer si Windows/PowerShell strict, conserver seulement si support bash explicite.

## Organisation recommandee

Priorite pragmatique: commencer par un registre d'ownership sans casser les chemins documentes, puis deplacer seulement les scripts qui ne sont pas references par CI/docs ou qui ont une story dediee. Categories proposees: `quality`, `security`, `db`, `perf`, `llm`, `dev`, `story-tools`.

## Validation

Audit base sur inventaire, scans de references repo-wide, lecture source et inventaire des tests. Aucun script applicatif n'a ete modifie.
