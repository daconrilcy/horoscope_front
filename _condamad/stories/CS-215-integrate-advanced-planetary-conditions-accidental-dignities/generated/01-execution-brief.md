<!-- Brief d'execution CONDAMAD pour CS-215. -->

# Execution Brief - CS-215

## Objective

Integrer les conditions planetaires avancees deja calculees par CS-214 dans le
score de dignite accidentelle, via des modificateurs purs situes dans
`backend/app/domain/astrology/dignities`.

## Boundaries

- Modifier uniquement le domaine `dignities` et le branchement minimal dans
  `natal_calculation.py`.
- Ne pas modifier API, DB, migrations, frontend, projection JSON publique,
  services chart, calculateurs `planetary_conditions` ou moteur narratif.
- Ne pas recalculer les conditions CS-209 a CS-214.
- Les modificateurs doivent rester factuels, configurables et non textuels.

## Done When

- AC1 a AC19 ont une preuve de code et de validation.
- `RG-142` est couvert par tests et scans.
- `ruff check .`, `ruff check backend`, `ruff format backend` et `pytest -q`
  passent sous venv.
- `generated/10-final-evidence.md` et `evidence/validation.md` sont complets.

## Halt Conditions

- Necessite de modifier API/DB/frontend/projection publique.
- Necessite de creer un fallback, alias, shim ou second moteur.
- Validation ciblee ou globale en echec sans correction sure.
