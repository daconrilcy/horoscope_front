# CS-214 Execution Brief

## Objectif

Integrer les calculateurs purs CS-209 a CS-213 dans le runtime natal via
`calculate_advanced_planetary_conditions`, puis exposer le resultat en attribut
runtime optionnel `NatalResult.advanced_planetary_conditions`.

## Limites

- Domaine unique: `backend/app/domain/astrology`.
- Aucun frontend, API, DB, migration, JSON builder, dignites, scoring ou texte
  interpretatif.
- Le pipeline natal construit seulement les mappings de positions/vitesses,
  appelle l'orchestrateur et injecte le resultat.

## Done Conditions

- Orchestrateur pur et factory de signaux sous `planetary_conditions`.
- Bundles Soleil/Lune inclus, phase lunaire globale calculee si possible.
- Vitesses absentes tolerees avec `motion=None`.
- Bloc exclu du dump JSON public Pydantic pour respecter le non-goal JSON.
- Tests cibles, `ruff format .`, `ruff check .`, `pytest -q`, scans RG-141 et
  validation de story passent.
