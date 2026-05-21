# Execution Brief

## Story

- Key: `CS-212-moon-phase-calculator`
- Objective: creer un calculateur domaine pur de phase lunaire natale depuis les longitudes Soleil/Lune.
- Closure type: full story closure, non audit.

## Boundaries

- In scope: `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`, export public dans `__init__.py`, tests unitaires cibles, evidence CONDAMAD.
- Out of scope: integration `NatalResult`, JSON public, API, DB, migrations, frontend, scoring, interpretation, ephemerides avancees, transits, progressions, eclipses et visibilite lunaire reelle.
- Guardrails: `RG-135`, `RG-136`, `RG-137`, `RG-138`, `RG-139`.

## Done Conditions

- `calculate_moon_phase_condition` retourne `MoonPhaseCondition` pour longitudes finies.
- Les bornes de phase, waxing/waning/exact, illumination et `phase_index` sont couvertes par tests.
- Les scans anti-dependances, anti-scoring, anti-interpretation et anti-integration adjacente sont executes.
- `ruff format .`, `ruff check .` et `pytest -q` sont executes apres activation du venv.
- `generated/10-final-evidence.md` et `story-status.md` sont synchronises.

## Halt Conditions

- Les contrats `MoonPhaseCondition`, `MoonPhaseKey` ou `WaxingWaningState` sont incompatibles avec la story.
- Une integration hors scope devient necessaire.
- Une validation requise echoue sans correction sure.
