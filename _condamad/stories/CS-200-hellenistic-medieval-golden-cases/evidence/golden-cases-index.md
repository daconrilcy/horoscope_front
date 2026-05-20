# Golden Cases Index

Ce dossier contient les cas golden traditionnels de CS-200. Aucun cas ne
modifie la doctrine: les fixtures explicitent les entrees et les assertions,
puis les calculateurs runtime canoniques produisent les sorties observees.

## Snapshot Policy

- `golden-cases-before.json` est un marqueur JSON valide d'absence de suite
  golden preexistante.
- `golden-cases-after.json` est le premier snapshot runtime curaté.
- Les flottants inclus sont arrondis a 6 decimales.
- Les ids DB, timestamps, traces ephemerides completes, hashes et labels
  localises non contractuels sont exclus.

## Cases

| Case | Fixture type | Provenance | Invariants locked |
|---|---|---|---|
| G1 | Synthetic domain | Soleil en maison 10 via `SectCalculator` et `AstrologyRuntimeReference`. | `dignities.sect.chart_sect=day`, `sun_horizon_position=above_horizon`, `sun_above_horizon=true`, basis/reference stable. |
| G2 | Synthetic domain | Soleil en maison 2 via `SectCalculator` et `AstrologyRuntimeReference`. | `dignities.sect.chart_sect=night`, `sun_horizon_position=below_horizon`, `sun_above_horizon=false`, basis/reference stable. |
| G3 | Synthetic domain | Soleil diurne dans theme diurne via `PlanetDignityScoringService`. | `PlanetSectCondition` diurne `in_sect`, flags coherents, scores runtime stables. |
| G4 | Synthetic domain | Lune nocturne dans theme nocturne via `PlanetDignityScoringService`. | `PlanetSectCondition` nocturne `in_sect`, flags coherents. |
| G5 | Synthetic domain | Jupiter diurne dans theme nocturne via scoring puis `AdvancedConditionEngine`. | `PlanetSectCondition.out_of_sect` et condition avancee `out_of_sect`. |
| G6 | Synthetic domain | Lune nocturne dans theme diurne via scoring puis `AdvancedConditionEngine`. | `PlanetSectCondition.out_of_sect` et condition avancee `out_of_sect`. |
| G7 | Synthetic domain | Soleil en secte, au-dessus de l'horizon et signe yang via `AdvancedConditionEngine`. | Emission de `hayz` quand les facteurs hors-secte matchent. |
| G8 | Synthetic domain | Soleil en secte mais signe non conforme au hayz. | `is_in_sect=true` sans condition avancee `hayz`. |
| G9 | Synthetic domain | Lune en maison de joie depuis `AccidentalDignityCalculator` et `PlanetConditionProfileService`. | `planetary_joy`, score accidentel et contribution de profil restent stables. |
| G10 | Synthetic domain | Mercure avec regle runtime `chart_sect_code=all`. | `intrinsic_sect=common`, `planet_sect_condition=variable_by_condition`, flags faux. |
| G11 | Synthetic domain | Soleil en Lion via `EssentialDignityCalculator`. | `domicile`, `essential_score=5` et axes de scoring essentiels positifs. |
| G12 | Integrated natal + downstream fixture | `build_natal_result` moteur simplifie, `NatalResult`, `build_chart_json`, dominance et adaptateur. | Propagation vers `dignity_sect`, `sect_condition`, `advanced_conditions`, profils, signaux, `dominant_planets`, `interpretation_adapter` et JSON public. |

## Runtime Ownership

- Secte chart-level: `backend/app/domain/astrology/dignities/sect_calculator.py`
- Condition de secte planetaire:
  `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py`
- Dignites essentielles et accidentelles:
  `backend/app/domain/astrology/dignities/*_dignity_calculator.py`
- Hayz et hors-secte: `backend/app/domain/astrology/advanced_conditions/**`
- Profils et signaux: `backend/app/domain/astrology/condition/**`
- Dominantes: `backend/app/domain/astrology/dominance/**`
- Adaptateur interpretatif:
  `backend/app/domain/astrology/interpretation_adapters/**`
- Projection publique: `backend/app/services/chart/json_builder.py`
