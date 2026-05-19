<!-- Brief d'execution CONDAMAD pour cadrer l'implementation de CS-194. -->

# Execution Brief

- Story key: `CS-194-dominant-planets-engine`
- Objective: ajouter un moteur backend factuel `PlanetDominanceEngine` alimente par un referentiel DB/runtime `astral_dominance_factor_types`.
- Boundaries: backend only; no frontend, route API, LLM, prompt, prediction, narration or compatibility shim.
- Required precondition: `CS-193` must be `done` and `NatalResult.condition_signals` plus `planet_condition_signals` must exist before application edits.
- Canonical owners:
  - DB/model/repository: `backend/app/infra/db/**`, `backend/migrations/**`
  - runtime contracts: `backend/app/domain/astrology/runtime/runtime_reference.py`
  - dominance engine: `backend/app/domain/astrology/dominance/**`
  - natal integration: `backend/app/domain/astrology/natal_calculation.py`
  - public projection: `backend/app/services/chart/json_builder.py`
- Halt conditions: missing CS-193 precondition, unavailable reference seed, contradictory ACs, new dependency requirement, repeated validation failure without safe fix.
- Done: all ACs have code evidence, validation evidence, No Legacy scans, before/after artifacts, final review evidence, and story status synchronized.
