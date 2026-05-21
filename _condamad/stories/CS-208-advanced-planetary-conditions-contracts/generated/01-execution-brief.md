# Execution Brief - CS-208

## Objective

Creer le package domaine pur
`backend/app/domain/astrology/planetary_conditions` avec des enums `StrEnum`
et huit dataclasses immutables pour les futures conditions planetaires avancees.

## Boundaries

- In scope: `planetary_conditions/__init__.py`, `planetary_conditions/contracts.py`,
  `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`,
  evidence CS-208 et statut CONDAMAD.
- Out of scope: calculateurs, scoring, interpretation, prompt, API, DB,
  migrations, `NatalResult`, JSON public, frontend et seeders.
- Guardrails applicables: `RG-107`, `RG-118`, `RG-119`, `RG-120`, `RG-122`,
  `RG-128`, `RG-129`, `RG-134`, `RG-135`.

## Done Conditions

- Les contrats publics sont importables, frozen, slots et typees sans `Any`.
- Les collections publiques sont des tuples ou `Mapping`.
- Les scans interdits retournent zero hit dans le nouveau package.
- Les tests cibles, lint, full pytest et validation story passent dans le venv.
- `generated/10-final-evidence.md` et `story-status.md` sont synchronises.

## Halt Conditions

- Besoin d'ajouter une dependance externe.
- Besoin de modifier un moteur ou une projection hors scope.
- Validation requise impossible sans blocker environnemental.
