# Execution Brief

## Story key

`classify-natal-cross-tool-dev-report`

## Objective

Classer `scripts/natal-cross-tool-report-dev.py` comme outil dev backend explicite, documenter son execution avec venv actif, et verrouiller le refus CI ainsi que la frontiere d'import des fixtures golden.

## Boundaries

- Modifier uniquement la documentation, les gardes/tests et les artefacts de story necessaires.
- Ne pas transformer le script en endpoint, service runtime ou outil CI.
- Ne pas dupliquer `scripts.cross_tool_report`.
- Ne pas modifier les fixtures golden ni l'algorithme de rapport natal.

## Preflight

- Lire `AGENTS.md`.
- Lire `_condamad/stories/regression-guardrails.md`.
- Capturer `git status --short`.
- Capturer le baseline `rg -n "natal-cross-tool-report-dev|app\.tests\.golden|scripts\.cross_tool_report|CI" scripts backend docs _condamad`.

## Write rules

- Conserver l'import de fixtures uniquement dans le script dev-only et les tests.
- Ajouter une garde pytest deterministe pour le refus CI et la frontiere runtime.
- Documenter la commande PowerShell avec `.\.venv\Scripts\Activate.ps1`.
- Pas de nouvelle dependance.

## Done

- AC1 a AC5 traces avec preuve code et validation.
- Tests cibles, scans et lint passent dans le venv.
- `generated/10-final-evidence.md` est complete.
