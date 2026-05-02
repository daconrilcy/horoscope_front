# CONDAMAD Audit Report - scripts-ops

## Scope

- Domain target: `scripts/`
- Archetype: `legacy-surface-audit` avec dimensions No Legacy / DRY / ownership.
- Mode: read-only pour le code applicatif; seuls les artefacts d'audit sous `_condamad/audits/**` sont crees.
- Guardrails consulted: `_condamad/stories/regression-guardrails.md`, notamment `RG-015`.

## Executive Verdict

`scripts/` reste un dossier operationnel utile, pas un dossier a purger en bloc. Les scripts qualite, securite, DB, predeploy, RGPD, release LLM et charge ont des usages documentes ou des tests. Le probleme principal est l'absence d'organisation canonique et la presence de surfaces legacy ponctuelles dans la racine.

## Findings

| ID | Severity | Summary | Status |
|---|---|---|---|
| F-001 | High | `validate_route_removal_audit.py` est un validateur story-specifique reste dans la racine `scripts/`. | action |
| F-002 | Medium | `stripe-listen-webhook.sh` duplique le `.ps1` malgre la cible Windows/PowerShell. | needs-user-decision |
| F-003 | Medium | Dossier plat sans ownership visible pour les familles quality/security/db/perf/llm/dev/story-tools. | action |
| F-004 | Medium | `start-dev-stack.ps1` utile mais non reference, non teste, et Stripe obligatoire. | action |
| F-005 | Medium | `load-test-critical.ps1` melange scenarios legacy, LLM, B2B, monitoring et delete privacy. | action |
| F-006 | Low | `llm-release-readiness.ps1` contient un chemin local absolu. | action |
| F-007 | Low | `natal-cross-tool-report-dev.py` depend de fixtures de test depuis la racine scripts. | action |
| F-008 | Info | Les scripts quality/security/DB/predeploy sont actifs, gardes et a conserver. | observation |

## Useful Scripts

| Script | Classification | Evidence |
|---|---|---|
| `quality-gate.ps1` | utile / canonique | E-006, E-013 |
| `predeploy-check.ps1` | utile / canonique | E-006, E-013 |
| `startup-smoke.ps1` | utile / support predeploy | E-003 |
| `scan-secrets.ps1` | utile / securite | E-016 |
| `security-verification.ps1` | utile / securite | E-016 |
| `secrets-scan-allowlist.txt` | utile / securite | E-016 |
| `security-findings-allowlist.txt` | utile / securite | E-016 |
| `backup-db.ps1` | utile / ops DB | E-015 |
| `backup-validate.ps1` | utile / ops DB | E-015 |
| `restore-db.ps1` | utile / ops DB | E-015 |
| `generate-rgpd-evidence.ps1` | utile / preuve ops RGPD | E-003 |
| `llm-release-readiness.ps1` | utile avec correctif portabilite | E-003, E-011 |
| `activate-llm-release.ps1` | utile / release LLM | E-003 |
| `load-test-critical.ps1` | utile avec refactor scope | E-003, E-009 |
| `load-test-critical-matrix.ps1` | utile / wrapper perf | E-003 |
| `generate-performance-report.ps1` | utile / helper perf | E-003, E-009 |
| `stripe-listen-webhook.ps1` | utile / dev local Stripe | E-007, E-010 |
| `start-dev-stack.ps1` | utile avec durcissement | E-008 |
| `natal-cross-tool-report-dev.py` | utile dev-only avec classement | E-012 |

## Legacy / Obsolete Candidates

| Script | Decision | Evidence | Blocker |
|---|---|---|---|
| `validate_route_removal_audit.py` | supprimer ou relocaliser | E-003, E-014 | Confirmer que l'audit historique n'a plus besoin d'une commande racine. |
| `stripe-listen-webhook.sh` | needs-user-decision | E-007, E-010 | Docs/tests le gardent actif; decision support bash requise. |

## Recommended Order

1. Retirer ou relocaliser `validate_route_removal_audit.py`.
2. Decider du statut de `stripe-listen-webhook.sh`.
3. Ajouter un registre d'ownership des scripts avant tout deplacement massif.
4. Durcir `start-dev-stack.ps1` et corriger le chemin absolu de `llm-release-readiness.ps1`.
5. Factoriser les scenarios de `load-test-critical.ps1`.

## Validation Notes

- No application code was changed.
- Python validation commands for this audit must be run after activating `.venv` according to repository rules.
