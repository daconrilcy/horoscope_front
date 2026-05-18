# Execution Brief - CS-189

## Objectif

Brancher les etoiles fixes au runtime daily sans catalogue local: le repository
charge le contrat DB-backed enrichi, le builder applique orbe/magnitude/poids
depuis le ruleset, et le routage utilise une configuration explicite.

## Bornes

- Domaine: `backend/app/domain/prediction` et contrats infra/services associes.
- Hors scope: frontend, API publique, `domain/astrology`, migrations de schema.
- Guardrails applicables: `RG-035`, `RG-095`, `RG-108`, `RG-110`, `RG-112`,
  `RG-113`, `RG-117`.

## Done

- AC1-AC7 traces dans `03-acceptance-traceability.md`.
- Tests ciblés et scans RG-117 executes dans le venv.
- Evidence before/after et guard evidence presentes.
- Story status synchronise via `_condamad/stories/story-status.md`.
