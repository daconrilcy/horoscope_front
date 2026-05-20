<!-- Synthese de validation CS-199 pour l'integration avancee de secte. -->

# Advanced Sect Validation

## Resultat

- Outcome: PASS.
- CS-199 targeted outcome: PASS.
- Full repository outcome: PASS.
- `out_of_sect` est derive de `PlanetSectCondition.is_out_of_sect`.
- `hayz` exige `PlanetSectCondition.is_in_sect` et conserve les facteurs non-secte via les regles runtime hayz evaluees dans `advanced_conditions`.
- Les regles d'horizon consommees par hayz sont bornees au meme systeme runtime que la regle hayz retenue.
- `PlanetSectCondition` manquant declenche une erreur explicite.
- Public shape: `dignities.sect` et `dignities.planets[*].sect_condition` restent inchanges.
- Score delta: aucun delta attendu ou observe sur les cas equivalents; seuls les chemins source-of-truth changent.

## Tests

| Commande | Resultat | Resume |
|---|---|---|
| `.\.venv\Scripts\Activate.ps1; pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py backend/tests/unit/domain/astrology/test_hayz_calculator.py backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_dignity_reference_seed.py::test_reference_seed_populates_astral_dignity_tables` | PASS | 50 passed |
| `.\.venv\Scripts\Activate.ps1; ruff check --fix backend/app/tests/unit/test_dignity_reference_seed.py; ruff format .; ruff check .` | PASS | Import trie, format stable, all checks passed |
| `.\.venv\Scripts\Activate.ps1; pytest -q` | PASS | 2765 passed, 1 skipped, 1177 deselected |
| `.\.venv\Scripts\Activate.ps1; python -c "from app.main import app; print(app.title)"` | PASS | FastAPI app imports and reports `horoscope-backend` |

## Scans

| Scan | Resultat | Classification |
|---|---|---|
| `rg -n "SectCalculator" backend/app/domain/astrology/condition backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters backend/app/services/chart -g "*.py"` | zero hit | PASS |
| `rg -n "PlanetSectConditionCalculator|planet_sect_condition_calculator" backend/app/domain/astrology/condition backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters backend/app/services/chart -g "*.py"` | zero hit | PASS |
| `rg -n "DIURNAL_PLANETS|NOCTURNAL_PLANETS|SECT_PLANETS|DAY_SECT_PLANETS|NIGHT_SECT_PLANETS|ABOVE_HORIZON_HOUSES|BELOW_HORIZON_HOUSES" backend/app -g "*.py"` | zero hit | PASS |
| `rg -n "\b7,\s*8,\s*9,\s*10,\s*11,\s*12\b|\b1,\s*2,\s*3,\s*4,\s*5,\s*6\b" backend/app/domain/astrology backend/app/services/chart -g "*.py"` | zero hit | PASS |
| `rg -n "sect_legacy|legacy_sect|sect_code|chart_sect_code|planet_sect_code|planet_sect_legacy|sect_score_legacy|legacy_planet_sect" backend/app backend/tests -g "*.py"` | hits existants | Allowed runtime/reference/test terminology; no new public legacy field or downstream recalculation introduced. |
| `$forbidden = "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|OpenAI|AIEngineAdapter|chat\.completions|prompt"; rg -n $forbidden backend/app/domain/astrology/dignities backend/app/domain/astrology/advanced_conditions backend/app/domain/astrology/condition backend/app/domain/astrology/dominance backend/app/domain/astrology/interpretation_adapters -g "*.py"` | hits existants `prompt_hint` | Allowed runtime-backed signal field in condition contracts/builder; no LLM provider, prompt builder or sect doctrine introduced. |

## Evidence

- `advanced-sect-scoring-before.json` and `advanced-sect-scoring-after.json` are valid JSON.
- Both snapshots include `dignities.sect`, `dignities.planets[*].sect_condition`, `advanced_conditions`, `planet_condition_profiles`, `planet_condition_signals`, `dominant_planets` and `interpretation_adapter`.
- No score delta for equivalent cases. The after snapshot records `score_delta: 0` for the relevant equivalent paths.
- The seed-count review blocker was resolved by aligning `backend/app/tests/unit/test_dignity_reference_seed.py` with the 42 accidental dignity rules present in the canonical seed data.
