# Execution Brief

## Objective

Implementer CS-218 en migrant la frontiere d'entree du moteur d'aspects natal
vers `NatalResult.chart_objects` / `ChartObjectRuntimeData`, avec selection par
`capabilities.supports_aspects` et projection unique vers
`AspectBodyRuntimeData`.

## Boundaries

- Scope applicatif: `backend/app/domain/astrology/calculators`,
  `backend/app/domain/astrology/natal_calculation.py` et tests domaine associes.
- Hors scope: API, frontend, DB, migrations, JSON public, dignites, dominance,
  conditions planetaires avancees et interpretation.
- Aucun nouveau package ou dossier racine backend.

## Done Conditions

- Le flux natal appelle `calculate_major_aspects` avec des corps projetes depuis
  `chart_objects`.
- Le selector filtre uniquement `supports_aspects=True`.
- Les erreurs longitude manquante et codes dupliques sont explicites.
- Les collections historiques de `NatalResult` restent presentes.
- `RG-145` reste enregistre et couvert par tests/scans.
- Tests cibles, lint, suite backend et scans story passent ou sont classes.

## Halt Conditions

- Besoin de conserver `planet_positions` comme source active parallele.
- Changement public OpenAPI/frontend/DB requis.
- Exception, fallback, shim ou builder specialise necessaire pour passer.
